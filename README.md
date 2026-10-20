# Building Component Graph System (BCGS)

**Turn building components into graphs, predict energy use, explain predictions, and compare material options.**

[中文说明](README.zh-CN.md) · [Input format](docs/data-format.md) · [Python & CLI guide](docs/usage.md) · [Web interface](web/README.md)

BCGS is a Python toolkit with an optional Vue / Three.js interface. The package includes a small building example, the original Enhanced GAT checkpoint, and example material tables. Inference runs on CPU; Rhino, Grasshopper, and EnergyPlus are not required to try the included example.

```text
Component properties + connections
               ↓
         Building graph
          ↙          ↘
   Energy prediction  Feature / connection explanations
          ↓
   Material options → Energy–cost trade-offs
```

## Install and run

Python 3.10 or newer. Install PyTorch for your machine first; this CPU setup is sufficient:

```bash
git clone https://github.com/YantingShen-dev/BuildingComponentGraphSystem.git
cd BuildingComponentGraphSystem
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

```bash
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install .
bcgs demo
```

The included example has **19 components, 102 undirected connections, and 26 encoded features**. Its reference prediction is approximately **508.0457** in the checkpoint's annual EUI target units, kWh/(m²·year). This is a reproducibility check, not a measured energy benchmark. See the [model notes](docs/models.md) before applying the checkpoint to a new project.

## Use your own building

Export the example and replace its component rows and adjacency matrix:

```bash
bcgs demo --export-input my-building.json
bcgs validate my-building.json
bcgs predict my-building.json --output prediction.json
bcgs explain my-building.json --epochs 100 --output explanation.json
```

You can also pass a directory containing headerless `node.xlsx` and `adjmatrix.xlsx`. Energy simulation labels are not needed for inference. The [data format](docs/data-format.md) specifies column order, category values, and units.

```python
from bcgs import BuildingGraph, EnergyPredictor, load_example

building = load_example()  # Or BuildingGraph.from_json("my-building.json")
predictor = EnergyPredictor()

print(predictor.predict(building))
explanation = predictor.explain(building, epochs=100)
```

## Compare materials

```bash
python -m pip install ".[optimize]"
bcgs optimize examples/building.json --population-size 20 --generations 5 --output options.json
```

Results contain nondominated energy–cost candidates and their complete graph inputs. The supplied prices are illustrative; use your own tables for project-specific comparisons. [Optimization assumptions and Python example →](docs/usage.md#material-optimization)

## Optional web interface

The existing interface supports building modeling, graph inspection, prediction, explanation, and material comparison.

```bash
python -m pip install ".[web]"
bcgs serve
```

In a second terminal, with Node.js 20+:

```bash
cd web/frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. Both prediction and optimization use the same API on port 5000. [Configuration and deployment →](web/README.md)

## Package contents

```text
src/bcgs/       Graph encoding, GAT inference, explanations, optimization, CLI/API
examples/       Small building input and Python walkthrough
docs/           Input contract, usage, model notes, migration notes
web/            Optional Vue interface and API entry point
tests/          Prediction regression, input validation, explanation, optimization, API
```

Only the **building-level ENB checkpoint** is included. Multi-scale CAADRIA models and the AEI / UFUG workflows are related research, not installed features of this release.

## Papers and citation

| Relationship | Paper |
|---|---|
| Core BCGS method | [Building energy modeling with replaceable components using graph attention networks — Energy & Buildings](https://doi.org/10.1016/j.enbuild.2025.116584) |
| Multi-scale extension | [Multi-Scale Graph Embedding and Explainability Consistency for Building Energy Modeling — CAADRIA 2026](https://www.caadria2026.org/paper-session) — conference listing, paper #56 |
| Related visual representation method | [Decoupling visual semantics via explicit representation learning for urban building energy modeling — Advanced Engineering Informatics](https://doi.org/10.1016/j.aei.2026.105335) |
| Related urban morphology application | [Revealing nonlinear impact disparities of vegetation-building configurations on carbon sequestration efficiency through representation learning — Urban Forestry & Urban Greening](https://doi.org/10.1016/j.ufug.2026.129292) |

For use of the included model, cite the ENB paper:

```bibtex
@article{shen2025bcgs,
  title = {Building energy modeling with replaceable components using graph attention networks},
  author = {Shen, Yanting and Zhu, Junlin and Zhang, Qibo and Huang, Chenyu and Ye, Jiahong and Yao, Jiawei},
  journal = {Energy and Buildings},
  volume = {349},
  pages = {116584},
  year = {2025},
  doi = {10.1016/j.enbuild.2025.116584}
}
```

[MIT license](LICENSE) · [Citation metadata](CITATION.cff) · [Report an issue](https://github.com/YantingShen-dev/BuildingComponentGraphSystem/issues)
