"""End-to-end contract tests. No training data, network, or GPU is required."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd
import torch

from bcgs import BuildingGraph, EnergyPredictor, FEATURE_NAMES, load_example
from bcgs.cli import main
from bcgs.optimization import MaterialOptimizer, equivalent_conductivity
from bcgs.server import create_app

torch.set_num_threads(1)
REFERENCE = json.loads((Path(__file__).parent / "reference.json").read_text())


class InputTests(unittest.TestCase):
    def test_feature_order_and_original_graph(self):
        graph = load_example().to_pyg()
        self.assertEqual(graph.x.shape, (19, 26))
        self.assertEqual(graph.num_edges, REFERENCE["directed_edges"])
        np.testing.assert_allclose(graph.x[0], REFERENCE["first_node_features"])

    def test_excel_and_json_roundtrip(self):
        original = load_example()
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original.to_json(folder / "building.json")
            self.assertEqual(original.to_dict(), BuildingGraph.from_json(folder / "building.json").to_dict())
            # Include a trailing simulation label; the loader must ignore it.
            pd.DataFrame([row + [9999] for row in original.node_data]).to_excel(folder / "node.xlsx", header=False, index=False)
            pd.DataFrame(original.adj_matrix).to_excel(folder / "adjmatrix.xlsx", header=False, index=False)
            np.testing.assert_allclose(original.to_pyg().x, BuildingGraph.from_excel(folder).to_pyg().x)

    def test_invalid_inputs_are_rejected(self):
        sample = load_example().to_dict()
        invalid = []
        for column, value in [(1, "unknown"), (4, float("nan")), (6, 1.5), (15, 9), (4, -1)]:
            data = deepcopy(sample)
            data["node_data"][0][column] = value
            invalid.append(data)
        data = deepcopy(sample)
        data["adj_matrix"][0][1] = 1 - data["adj_matrix"][1][0]
        invalid.append(data)
        data = deepcopy(sample)
        data["adj_matrix"].pop()
        invalid.append(data)
        invalid.extend([{}, None, {"node_data": [], "adj_matrix": []}])
        for payload in invalid:
            with self.subTest(payload=str(payload)[:80]), self.assertRaises(ValueError):
                BuildingGraph.from_dict(payload)

    def test_single_node_prediction_input(self):
        row = load_example().node_data[0]
        graph = BuildingGraph([row], [[1]]).to_pyg()
        self.assertEqual(tuple(graph.edge_index.shape), (2, 0))


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.predictor = EnergyPredictor()
        cls.building = load_example()

    def test_original_prediction(self):
        self.assertAlmostEqual(self.predictor.predict(self.building), REFERENCE["prediction"], delta=0.002)

    def test_node_order_invariance(self):
        nodes = self.building.node_data[::-1]
        adjacency = np.asarray(self.building.adj_matrix)[::-1, ::-1].tolist()
        self.assertAlmostEqual(self.predictor.predict(BuildingGraph(nodes, adjacency)), REFERENCE["prediction"], delta=0.002)

    def test_explanation_preserves_model_and_rng(self):
        before = torch.random.get_rng_state().clone()
        result = self.predictor.explain(self.building, epochs=5, seed=42)
        self.assertTrue(torch.equal(before, torch.random.get_rng_state()))
        self.assertEqual(len(result["node_importance"]["Node_ID"]), 19)
        self.assertEqual(set(result["feature_importance"]), set(FEATURE_NAMES))
        matrix = np.asarray(result["edge_matrix"])
        self.assertEqual(matrix.shape, (19, 19))
        self.assertTrue(np.isfinite(matrix).all())
        np.testing.assert_allclose(matrix, matrix.T)
        self.assertTrue((matrix[np.asarray(self.building.adj_matrix) == 0] == 0).all())
        self.assertAlmostEqual(self.predictor.predict(self.building), REFERENCE["prediction"], delta=0.002)

    def test_optimization_export_and_reproducibility(self):
        optimizer = MaterialOptimizer(self.predictor)
        solutions = optimizer.optimize(self.building, population_size=4, generations=1, seed=7)
        self.assertTrue(solutions)
        for solution in solutions:
            building = BuildingGraph.from_dict(solution)
            self.assertAlmostEqual(self.predictor.predict(building), solution["energy"], delta=0.001)
            for raw, display in zip(building.node_data, solution["nodes"]):
                self.assertEqual(raw[10], display["Con"])
                self.assertEqual(raw[11], display["Thi"])
            for other in solutions:
                dominates = (
                    other["energy"] <= solution["energy"] and other["cost"] <= solution["cost"]
                    and (other["energy"] < solution["energy"] or other["cost"] < solution["cost"])
                )
                self.assertFalse(dominates)
        again = optimizer.optimize(self.building, population_size=4, generations=1, seed=7)
        self.assertEqual(solutions, again)

    def test_layer_conductivity_and_small_combined_subface(self):
        self.assertAlmostEqual(equivalent_conductivity(0.2, 1.0, 0.1, 0.05), 0.3 / 2.2)
        rows = deepcopy(self.building.node_data)
        rows[0][6], rows[0][7] = 3, 1.0
        building = BuildingGraph(rows, self.building.adj_matrix)
        optimizer = MaterialOptimizer(self.predictor)
        candidate, cost, _ = optimizer._decode([0.1, 0, 0, 0, 0] * len(rows), building, 0)
        self.assertEqual(candidate.node_data[0][9], 0)
        self.assertTrue(np.isfinite(cost))


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = create_app().test_client()

    def test_prediction_and_materials(self):
        self.assertEqual(self.client.get("/health").status_code, 200)
        payload = self.client.get("/example").get_json()
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.get_json()["prediction"], REFERENCE["prediction"], delta=0.002)
        response = self.client.get("/materials/wall_select.xlsx")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.startswith(b"PK"))
        response.close()

    def test_explanation_contract_and_optimization(self):
        payload = {**load_example().to_dict(), "explain": True, "explainer_epochs": 2}
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        result = response.get_json()["explanation"]
        self.assertEqual(len(result["node_importance"]["Node_ID"]), 19)
        payload = {**load_example().to_dict(), "population_size": 4, "generations": 1}
        response = self.client.post("/optimize", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["pareto_solutions"])

    def test_bad_request_is_400(self):
        for payload in ({}, None, {"node_data": [], "adj_matrix": []}):
            response = self.client.post("/predict", data=json.dumps(payload), content_type="application/json")
            self.assertEqual(response.status_code, 400)
        response = self.client.post("/optimize", json={**load_example().to_dict(), "population_size": 1})
        self.assertEqual(response.status_code, 400)


class CliTests(unittest.TestCase):
    def test_demo_export_and_predict(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path, output_path = Path(tmp) / "sample.json", Path(tmp) / "prediction.json"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["demo", "--export-input", str(input_path)]), 0)
            self.assertEqual(main(["predict", str(input_path), "--output", str(output_path)]), 0)
            result = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertAlmostEqual(result["prediction"], REFERENCE["prediction"], delta=0.002)

    def test_invalid_file_has_nonzero_exit(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(main(["predict", "does-not-exist.json"]), 2)


if __name__ == "__main__":
    unittest.main()
