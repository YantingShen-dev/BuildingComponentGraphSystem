"""Material search with one shared decoder for evaluation and exported designs."""

from copy import deepcopy
from pathlib import Path
import random

import numpy as np
import pandas as pd
from deap import base, tools

from .data import ASSETS, BuildingGraph


class _Fitness(base.Fitness):
    weights = (-1.0, -1.0)


class _Individual(list):
    def __init__(self, values=()):
        super().__init__(values)
        self.fitness = _Fitness()


def equivalent_conductivity(wall_thickness, wall_conductivity, insulation_thickness, insulation_conductivity):
    """k_eq = total thickness / sum(layer thickness / layer conductivity)."""
    if min(wall_conductivity, insulation_conductivity) <= 0:
        raise ValueError("Material conductivity must be positive.")
    resistance = wall_thickness / wall_conductivity + insulation_thickness / insulation_conductivity
    if resistance <= 0:
        raise ValueError("The layered construction must have positive thickness.")
    return (wall_thickness + insulation_thickness) / resistance


class MaterialOptimizer:
    """NSGA-II with the original material tables; prices are illustrative inputs."""

    def __init__(self, predictor, materials_dir=None):
        self.predictor = predictor
        root = Path(materials_dir) if materials_dir else ASSETS / "materials"
        specifications = {
            "wall_select": ["Con", "Price", "Material"],
            "heatPreserve": ["Con", "Price", "Material"],
            "face": ["SA", "Price", "Material"],
            "window": ["SCon", "SSHGC", "Price", "glassType", "frameType"],
            "door": ["SCon", "Price", "Material"],
        }
        self.tables = {}
        for name, columns in specifications.items():
            table = pd.read_excel(root / f"{name}.xlsx")
            if table.empty or not set(columns) <= set(table.columns):
                raise ValueError(f"{name}.xlsx requires rows and columns {columns}.")
            for column in columns:
                if column in {"Con", "Price", "SA", "SCon", "SSHGC"}:
                    values = pd.to_numeric(table[column], errors="raise")
                    if not np.isfinite(values).all() or (values < 0).any():
                        raise ValueError(f"{name}.{column} must be finite and non-negative.")
                    if column == "Con" and (values == 0).any():
                        raise ValueError(f"{name}.Con must be positive.")
                    table[column] = values
            self.tables[name] = table

    def _decode(self, individual, building, wall_type):
        """Return exactly the rows used to score the candidate, plus display metadata."""
        rows = deepcopy(building.node_data)
        wall = self.tables["wall_select"].iloc[wall_type]
        total_cost, nodes = 0.0, []
        for i, row in enumerate(rows):
            thickness, face_id, insulation_id, window_id, door_id = individual[5*i:5*i+5]
            face = self.tables["face"].iloc[face_id]
            insulation = self.tables["heatPreserve"].iloc[insulation_id]
            window = self.tables["window"].iloc[window_id]
            door = self.tables["door"].iloc[door_id]
            original_thickness = row[11]
            sub_type, sub_area = row[6], row[7]
            door_area = sub_area if sub_type == 2 else min(1.8, sub_area) if sub_type == 3 else 0.0
            window_area = sub_area - door_area if sub_type in (1, 3) else 0.0
            row[8] = float((window["SCon"] * window_area + door["SCon"] * door_area) / sub_area) if sub_type else 0.0
            row[9] = float(window["SSHGC"] * window_area / sub_area) if sub_type else 0.0
            row[10] = float(equivalent_conductivity(original_thickness, wall["Con"], thickness, insulation["Con"]))
            row[11] = original_thickness + thickness
            row[13] = float(face["SA"])
            total_cost += (
                wall["Price"] * row[4] * original_thickness
                + insulation["Price"] * row[4] * thickness
                + face["Price"] * row[4]
                + window["Price"] * window_area + door["Price"] * door_area
            )
            nodes.append({
                "Type": row[1], "Out": row[3], "Area": row[4], "SI": row[5],
                "SType": sub_type, "SArea": sub_area, "SCon": row[8], "SSHGC": row[9],
                "Con": row[10], "Thi": row[11], "WThi": original_thickness, "PThi": thickness,
                "TA": row[12], "SA": row[13], "VA": row[14], "Dir": row[15],
                "WMat": str(wall["Material"]), "PMat": str(insulation["Material"]),
                "FMat": str(face["Material"]),
                "DMat": str(door["Material"]) if door_area else "None",
                "WGMat": str(window["glassType"]) if window_area else "None",
                "WFMat": str(window["frameType"]) if window_area else "None",
            })
        return BuildingGraph(rows, building.adj_matrix), float(total_cost), nodes

    def optimize(self, building, wall_type=0, population_size=20, generations=5, seed=42,
                 thickness_bounds=(0.01, 0.2), progress=None):
        if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**32:
            raise ValueError("seed must be an integer between 0 and 4294967295.")
        for label, value, low, high in (
            ("population_size", population_size, 4, 200), ("generations", generations, 1, 100),
            ("wall_type", wall_type, 0, len(self.tables["wall_select"])-1),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
                raise ValueError(f"{label} must be an integer between {low} and {high}.")
        low, high = map(float, thickness_bounds)
        if not np.isfinite([low, high]).all() or not 0 < low <= high:
            raise ValueError("thickness_bounds must be positive finite values in ascending order.")
        rng = random.Random(seed)
        counts = [len(self.tables[k]) for k in ("face", "heatPreserve", "window", "door")]

        def create():
            return _Individual([
                value for _ in building.node_data
                for value in [rng.uniform(low, high), *(rng.randrange(count) for count in counts)]
            ])

        def score(individual):
            candidate, cost, _ = self._decode(individual, building, wall_type)
            individual.fitness.values = (self.predictor.predict(candidate), cost)

        population = [create() for _ in range(population_size)]
        for individual in population:
            score(individual)
        population = tools.selNSGA2(population, population_size)
        archive = tools.ParetoFront()
        archive.update(population)
        for generation in range(1, generations+1):
            offspring = []
            while len(offspring) < population_size:
                child = deepcopy(rng.choice(population))
                other = rng.choice(population)
                for i in range(len(child)):
                    if rng.random() < 0.5:
                        child[i] = other[i]
                    if rng.random() < 0.2:
                        child[i] = rng.uniform(low, high) if i % 5 == 0 else rng.randrange(counts[i % 5 - 1])
                score(child)
                offspring.append(child)
            archive.update(offspring)
            population = tools.selNSGA2(population + offspring, population_size)
            if progress:
                progress({"generation": generation, "generations": generations, "solutions": len(archive)})
        results = []
        for individual in archive:
            candidate, cost, nodes = self._decode(individual, building, wall_type)
            results.append({
                "energy": float(individual.fitness.values[0]), "cost": cost,
                "nodes": nodes, **candidate.to_dict(),
            })
        return sorted(results, key=lambda item: (item["energy"], item["cost"]))
