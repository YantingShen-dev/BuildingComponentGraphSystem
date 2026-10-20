<p align="center">
  <img src="docs/assets/hero.svg" alt="BCGS 建筑构件图工具包：从建筑构件到能耗分析" width="100%">
</p>

<p align="center">
  <a href="https://bcgs.vercel.app/"><img src="docs/assets/button-demo.svg" alt="打开在线演示" width="184"></a>
  <a href="#安装与首次运行"><img src="docs/assets/button-start.svg" alt="快速开始" width="184"></a>
  <a href="docs/usage.md"><img src="docs/assets/button-docs.svg" alt="API 与文档" width="184"></a>
  <a href="#对应论文"><img src="docs/assets/button-papers.svg" alt="阅读论文" width="184"></a>
</p>

<p align="center"><b>Python 3.10+ &nbsp; · &nbsp; CPU 可运行 &nbsp; · &nbsp; 内附模型与样例</b><br>
<a href="LICENSE"><b>仅限非商业研究 · 禁止商业使用</b></a><br>
<a href="README.md">English</a> &nbsp; / &nbsp; <a href="docs/data-format.md">输入数据格式</a> &nbsp; / &nbsp; <a href="web/README.md">本地启动网页</a></p>

## 从建筑构件出发，分析能耗

**将建筑构件及其连接关系转换为图，进行能耗预测、结果解释和材料方案比较。**

工具包附带一个小型建筑样例、原版 Enhanced GAT 权重和示例材料表。CPU 即可运行预测；体验样例无需安装 Rhino、Grasshopper 或 EnergyPlus。

<img src="docs/assets/workflow.svg" alt="四步工作流：构件图编码、年度 EUI 预测、特征与连接解释、能耗与材料成本比较。" width="100%">

## 先看它怎么用

### 01 · 搭建三维体块

创建房间、调整尺寸与位置，组合成连通的建筑。

<a href="web/frontend/public/videos/page1.mp4"><img src="docs/assets/modeling.gif" alt="BCGS 实际操作录像：创建、缩放与拼接三维建筑体块。" width="100%"></a>

<table>
<tr>
<td width="50%"><b>02 · 编辑构件</b><br>设置墙体、门窗与材料属性，检查图输入。</td>
<td width="50%"><b>03 · 查看预测与解释</b><br>在分析界面中查看构件特征与连接关系。</td>
</tr>
<tr>
<td><a href="web/frontend/public/videos/page2.mp4"><img src="docs/assets/components.gif" alt="构件编辑录像：墙面、门窗与属性表。" width="100%"></a></td>
<td><a href="web/frontend/public/videos/page3.mp4"><img src="docs/assets/explanations.gif" alt="原有分析界面的构件与连接解释录像。" width="100%"></a></td>
</tr>
<tr>
<td><a href="web/frontend/public/videos/page2.mp4">观看完整构件编辑演示 →</a></td>
<td><a href="web/frontend/public/videos/page3.mp4">观看完整分析演示 →</a></td>
</tr>
</table>

<sub>动图节选自原有网页的真实操作录像，以 2 倍速播放，用来展示操作方式，并非本版样例的计算结果。当前工具包采用标准解释掩码，数值与优化行为可能和录像不同，详见<a href="docs/migration.md">迁移说明</a>。<a href="docs/assets/README.md">静态图与素材来源</a>。</sub>

**使用入口：** [打开已有在线演示 ↗](https://bcgs.vercel.app/) · [本地启动网页](web/README.md) · [安装 Python 工具包 ↓](#安装与首次运行)。线上演示是已有部署，其 API 可用性和版本可能与本地代码不同。

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

### 构件 → 节点，连接 → 边

墙体、屋顶、地面成为图中的节点；几何、材料与开口信息成为节点属性。

<img src="docs/assets/component-graph.png" alt="ENB 论文图 3：建筑构件拆解为图节点、连接关系和几何、热工及开口属性。" width="100%">

<sub>图源：Shen et al., <i>Energy &amp; Buildings</i> 349 (2025), 116584，图 3。<a href="https://doi.org/10.1016/j.enbuild.2025.116584">阅读核心方法论文 ↗</a></sub>

### 接入自己的数据

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

| 发表来源 / 与工具的关系 | 论文 | 跳转 |
|---|---|---|
| **Energy & Buildings**<br>核心构件图方法 | Building energy modeling with replaceable components using graph attention networks | **[阅读&nbsp;↗](https://doi.org/10.1016/j.enbuild.2025.116584)** |
| **CAADRIA 2026**<br>多尺度扩展 | Multi-Scale Graph Embedding and Explainability Consistency for Building Energy Modeling | **[#56&nbsp;↗](https://www.caadria2026.org/paper-session)** |
| **Advanced Engineering Informatics**<br>相关视觉表征方法 | Decoupling visual semantics via explicit representation learning for urban building energy modeling | **[阅读&nbsp;↗](https://doi.org/10.1016/j.aei.2026.105335)** |
| **Urban Forestry & Urban Greening**<br>相关城市形态应用 | Revealing nonlinear impact disparities of vegetation-building configurations on carbon sequestration efficiency through representation learning | **[阅读&nbsp;↗](https://doi.org/10.1016/j.ufug.2026.129292)** |

CAADRIA 链接跳转至官方会议论文列表，对应编号 #56。

使用本工具的构件图与能耗模型时，请引用 ENB 论文。[BibTeX](README.md#papers-and-citation) · [CITATION.cff](CITATION.cff)

## 使用许可

**允许非商业研究使用，禁止商业使用。**

本版本使用自定义的 [BCGS 非商业研究许可](LICENSE)。允许在许可条件下开展研究、复现、修改及免费分享；商业产品、收费服务、商业项目及面向商业利益的研发均不在授权范围内。分享原版或修改版时，须保留许可及署名，并继续遵守非商业研究限制。使用本项目发表研究成果时须引用相应论文。

这是“源码可用、仅限非商业研究”的项目，不属于 OSI 定义的开源许可。第三方依赖和论文图片保留各自的授权条款；新许可不追溯撤销旧版已授予的 MIT 权利。详见[中文授权说明](docs/licensing.zh-CN.md)。
