"""The original 16-column input contract and checkpoint-compatible encoding."""

from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np
import pandas as pd
import torch
from torch_geometric.data import Data

ASSETS = Path(__file__).resolve().parent / "assets"
RAW_COLUMNS = (
    "Name", "ConstructionName", "ZoneName", "OutsideBoundaryCondiction",
    "Area", "SI", "Subface", "SubfaceArea", "SubRes", "SubSHGC", "Res",
    "Thickness", "ThermalAbsorptance", "SolarAbsorptance", "VisiblAbsorptance", "Direction",
)
NUMERIC_INDICES = (4, 5, 7, 8, 9, 10, 11, 12, 13, 14)
CATEGORIES = {
    1: ("exterior", "interior", "ground", "roof"),
    3: ("Outdoors", "Surface", "Ground"),
    6: (0, 1, 2, 3),
    15: (0, 1, 2, 3, 4),
}
FEATURE_NAMES = (
    *(RAW_COLUMNS[i] for i in NUMERIC_INDICES),
    "exterior", "interior", "ground", "roof",
    "Outdoors", "Surface", "Ground",
    "NoSubface", "Window", "Door", "Window&Door",
    "NoDirection", "East", "South", "West", "North",
)


@dataclass
class BuildingGraph:
    """One building. Rows in node_data and adj_matrix must have identical order."""

    node_data: list
    adj_matrix: list

    def __post_init__(self):
        try:
            rows = [list(row) for row in self.node_data]
        except TypeError as exc:
            raise ValueError("node_data must be a non-empty array of 16-column rows.") from exc
        if not rows or any(len(row) != 16 for row in rows):
            raise ValueError("node_data must be a non-empty array of 16-column rows.")
        for i, row in enumerate(rows):
            for col in (*NUMERIC_INDICES, 6, 15):
                try:
                    value = float(row[col])
                except (ValueError, TypeError) as exc:
                    raise ValueError(f"Node {i}: {RAW_COLUMNS[col]} must be numeric.") from exc
                if not np.isfinite(value):
                    raise ValueError(f"Node {i}: {RAW_COLUMNS[col]} must be finite.")
                row[col] = value
            for col, choices in CATEGORIES.items():
                if row[col] not in choices:
                    raise ValueError(f"Node {i}: {RAW_COLUMNS[col]} must be one of {choices}.")
            row[6], row[15] = int(row[6]), int(row[15])
            if row[4] <= 0 or row[5] <= 0:
                raise ValueError(f"Node {i}: Area and SI must be positive.")
            if any(row[c] < 0 for c in NUMERIC_INDICES):
                raise ValueError(f"Node {i}: physical properties cannot be negative.")
            if row[6] and row[7] <= 0:
                raise ValueError(f"Node {i}: a window or door requires positive SubfaceArea.")
        try:
            adj = np.asarray(self.adj_matrix, dtype=float)
        except (TypeError, ValueError) as exc:
            raise ValueError("adj_matrix must be a square binary matrix.") from exc
        if adj.shape != (len(rows), len(rows)):
            raise ValueError(f"adj_matrix must have shape {len(rows)} x {len(rows)}.")
        if not np.isin(adj, (0, 1)).all():
            raise ValueError("adj_matrix must contain only 0 and 1.")
        if not np.array_equal(adj, adj.T):
            raise ValueError("adj_matrix must be symmetric (an undirected component graph).")
        self.node_data = rows
        self.adj_matrix = adj.astype(int).tolist()

    @classmethod
    def from_dict(cls, payload):
        if not isinstance(payload, dict) or not {"node_data", "adj_matrix"} <= payload.keys():
            raise ValueError("Input must contain node_data and adj_matrix.")
        return cls(payload["node_data"], payload["adj_matrix"])

    @classmethod
    def from_json(cls, path):
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8-sig")))

    @classmethod
    def from_excel(cls, directory):
        """Read headerless node.xlsx and adjmatrix.xlsx; hourly labels are not required."""
        directory = Path(directory)
        nodes = pd.read_excel(directory / "node.xlsx", header=None, usecols=range(16))
        adjacency = pd.read_excel(directory / "adjmatrix.xlsx", header=None)
        return cls(nodes.values.tolist(), adjacency.values.tolist())

    def to_dict(self):
        return {"node_data": self.node_data, "adj_matrix": self.adj_matrix}

    def to_json(self, path):
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    def to_pyg(self):
        """Encode 10 numerical fields + 16 categorical indicators in the original order."""
        features = []
        for row in self.node_data:
            features.append(
                [row[c] for c in NUMERIC_INDICES]
                + [float(row[col] == value) for col, values in CATEGORIES.items() for value in values]
            )
        adj = np.asarray(self.adj_matrix)
        source, target = np.where(adj == 1)
        keep = source != target  # GATConv adds its own self-loops.
        return Data(
            x=torch.tensor(features, dtype=torch.float32),
            edge_index=torch.tensor(np.stack([source[keep], target[keep]]), dtype=torch.long),
        )


def load_example():
    """Load the small building distributed with the wheel."""
    return BuildingGraph.from_json(ASSETS / "example.json")
