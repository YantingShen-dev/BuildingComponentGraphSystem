# 建筑构件图工具包 BCGS

**将建筑构件及其连接关系转换为图，进行能耗预测、结果解释和材料方案比较。**

[English](README.md) · [数据格式](docs/data-format.md) · [调用说明](docs/usage.md) · [可选网页界面](web/README.md)

工具包附带一个小型建筑样例、原版 Enhanced GAT 权重和示例材料表。CPU 即可运行预测；体验样例无需安装 Rhino、Grasshopper 或 EnergyPlus。

## 安装与首次运行

需要 Python 3.10 或更新版本：

```bash
git clone https://github.com/YantingShen-dev/BuildingComponentGraphSystem.git
cd BuildingComponentGraphSystem
python -m venv .venv
```

激活环境：Windows PowerShell 使用 `.\.venv\Scripts\Activate.ps1`；macOS / Linux 使用 `source .venv/bin/activate`。

```bash
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install .
bcgs demo
```

样例有 19 个构件、102 条无向连接，编码后每个构件有 26 个特征。原权重的参考预测值约为 **508.0457**，目标为年度 EUI，单位 kWh/(m²·年)。该数值用于检查安装和预测是否一致，不是实测能耗或新的精度验证。

## 换成自己的建筑

```bash
bcgs demo --export-input my-building.json
bcgs validate my-building.json
bcgs predict my-building.json --output prediction.json
bcgs explain my-building.json --epochs 100 --output explanation.json
```

修改导出的 JSON，提供构件属性及对称邻接矩阵。也可以传入包含无表头 `node.xlsx` 和 `adjmatrix.xlsx` 的目录，无需提供能耗标签。[字段顺序、类别编码与单位](docs/data-format.md)

```python
from bcgs import BuildingGraph, EnergyPredictor, load_example

building = load_example()
# building = BuildingGraph.from_json("my-building.json")
predictor = EnergyPredictor()
prediction = predictor.predict(building)
explanation = predictor.explain(building, epochs=100)
```

## 材料优化与网页

```bash
python -m pip install ".[optimize]"
bcgs optimize examples/building.json --population-size 20 --generations 5 --output options.json
```

优化结果包含能耗—成本候选方案，以及可直接重新预测的节点和邻接矩阵。示例材料价格不能代替实际项目报价；[优化假设与调用方式](docs/usage.md#material-optimization)中说明了搜索范围。

网页为可选功能：

```bash
python -m pip install ".[web]"
bcgs serve
```

另开终端，使用 Node.js 20+：

```bash
cd web/frontend
npm ci
npm run dev
```

打开 `http://localhost:5173`。预测与优化统一使用 5000 端口，详见[网页配置](web/README.md)。

## 模型范围

当前提供 ENB 对应的建筑整体能耗模型。构件字段、气候背景和目标定义应与模型训练设置匹配；详见[模型说明](docs/models.md)。解释结果是模型的重要性掩码，不能直接解释为热流或因果效应。

CAADRIA 多尺度模型以及 AEI、UFUG 工作流属于相关研究，尚未打包为本版本功能。

## 对应论文

- **核心方法 · ENB**：[Building energy modeling with replaceable components using graph attention networks](https://doi.org/10.1016/j.enbuild.2025.116584)
- **多尺度扩展 · CAADRIA 2026**：[Multi-Scale Graph Embedding and Explainability Consistency for Building Energy Modeling](https://www.caadria2026.org/paper-session)（会议论文列表，编号 #56）
- **视觉表征 · AEI**：[Decoupling visual semantics via explicit representation learning for urban building energy modeling](https://doi.org/10.1016/j.aei.2026.105335)
- **城市形态应用 · UFUG**：[Revealing nonlinear impact disparities of vegetation-building configurations on carbon sequestration efficiency through representation learning](https://doi.org/10.1016/j.ufug.2026.129292)

使用本工具的构件图与能耗模型时，请引用 ENB 论文。[BibTeX](README.md#papers-and-citation) · [CITATION.cff](CITATION.cff) · [MIT 许可证](LICENSE)
