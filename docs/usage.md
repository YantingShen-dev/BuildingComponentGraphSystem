# Python and command line

Install from the repository with `python -m pip install .`.
Every CLI command also works as `python -m bcgs ...`.

## Prediction

```python
from bcgs import BuildingGraph, EnergyPredictor, load_example

building = load_example()
# building = BuildingGraph.from_excel("my-building")
# building = BuildingGraph.from_json("my-building.json")
predictor = EnergyPredictor(device="cpu")
annual_eui = predictor.predict(building)
graph = building.to_pyg()  # torch_geometric.data.Data: x and edge_index
```

Reuse the predictor to avoid repeatedly loading weights. A custom checkpoint must have the same architecture and 26-feature encoding:

```bash
bcgs predict examples/building.json --checkpoint /path/to/model.pth --device cpu
```

Use `--device cuda` only with a suitable CUDA installation and PyTorch build.

## Explanations

```python
explanation = predictor.explain(building, epochs=100, seed=42)
print(explanation["feature_importance"])
```

- `node_importance`: feature name → node index → attribute-mask value; `Node_ID` preserves indices for the web table.
- `feature_importance`: mean attribute-mask value over all nodes.
- `edge_matrix`: symmetric N × N edge-mask values; non-edges remain zero.
- `epochs` and `seed`: recorded settings.

These are unsigned GNNExplainer masks, not energy flows, signed changes, or causal effects. Increasing epochs increases computation; compare explanations using the same settings. A five-epoch smoke test checks execution, not explanation convergence.

This implementation uses PyG attribute masks directly. It does not reproduce the previous web implementation's custom perturbation tables or the paper's complete analysis protocol.

## Material optimization

Install the extra with `python -m pip install ".[optimize]"`.

```python
from bcgs.optimization import MaterialOptimizer

optimizer = MaterialOptimizer(predictor)
solutions = optimizer.optimize(
    building,
    wall_type=0,
    population_size=20,
    generations=5,
    thickness_bounds=(0.01, 0.2),
    seed=42,
)
first = solutions[0]
reloaded = BuildingGraph.from_dict(first)
assert abs(predictor.predict(reloaded) - first["energy"]) < 1e-3
```

The search varies insulation thickness, insulation, finish, window, and door materials for each component. The base wall material is a common **zero-based row index** in `wall_select.xlsx`; `wall_type=0` means the first row, not its `ID` value. This simplified search applies to all supplied components. It does not enforce component-specific construction regulations or change geometry.

Outputs include `energy`, `cost`, display-oriented `nodes`, and full `node_data` / `adj_matrix` inputs. Evaluation and export use the same decoder without rounding thermal properties.

Assumptions inherited from the example material workflow:

- Equivalent opaque conductivity is `total thickness / sum(layer thickness / layer conductivity)`.
- For a combined window-and-door subface, door area is `min(1.8 m², total subface area)`; the remainder is window area.
- Wall and insulation prices multiply area × thickness; finishes and windows/doors multiply area.
- The cost model is an illustrative comparison. No currency conversion, inflation, labor, maintenance, daylight, or embodied-carbon objective is included.
- Outputs are nondominated candidates found within a finite search, not a proof of global optimality.
- Fixing the seed makes the CPU search reproducible within the same numerical environment.

To supply your own material tables:

```bash
bcgs optimize examples/building.json --materials-dir my-materials --wall-type 0 --output options.json
```

| File | Required columns |
|---|---|
| wall_select.xlsx | Material, Con, Price |
| heatPreserve.xlsx | Material, Con, Price |
| face.xlsx | Material, SA, Price |
| window.xlsx | glassType, frameType, SCon, SSHGC, Price |
| door.xlsx | Material, SCon, Price |

Use the first worksheet with headers. Conductivities must be positive; numeric values and prices must be finite and non-negative.

## HTTP API

Install `.[web]`, then run `bcgs serve`. The service listens on `127.0.0.1:5000`.

| Request | Result |
|---|---|
| GET /health | Loaded service and device |
| GET /example | Bundled building input |
| GET /materials/wall_select.xlsx | Base material choices for the web interface |
| POST /predict | `prediction`; optionally `explanation` |
| POST /optimize | `success`, `pareto_solutions` |

POST the same `node_data` and `adj_matrix` arrays. For prediction, add `"explain": true` and optionally `explainer_epochs` / `seed`. For optimization, add `wall_type`, `population_size`, `generations`, and optionally `seed`. Responses are JSON; use `stream: false`. Malformed building data returns HTTP 400.

The development API serializes model operations because explanations temporarily modify PyG hooks. It is intended for local use. Use an appropriate WSGI deployment and access controls if exposing your own instance.

## Tests

With the web extra installed:

```bash
python -m unittest discover -s tests -v
```

Tests cover feature order, the original sample prediction, Excel/JSON loading, invalid inputs, explanation output, optimizer export consistency, HTTP responses, and CLI behavior.
