# GCN Building Energy Prediction and Interpretation System

## 📋 Project Overview

This is a **Graph Convolutional Network (GCN)** based building energy prediction and interpretation system. The system is specifically designed for component-level building energy prediction, capable of analyzing spatial relationships between building components and providing interpretability analysis of prediction results.

### 🎯 Key Features

1. **Building Energy Prediction**: Predicts total building energy consumption based on component features and spatial relationships
2. **Model Interpretability**: Analyzes the importance of each component feature and inter-component relationships to prediction results
3. **RESTful API Service**: Provides Web API interfaces supporting real-time prediction and interpretation
4. **Data Processing Tools**: Supports automatic conversion and processing of Excel data formats

### 🏗️ Technical Architecture

- **Deep Learning Framework**: PyTorch + PyTorch Geometric
- **Network Architecture**: Enhanced GCN based on GAT (Graph Attention Network)
- **API Framework**: Flask + CORS
- **Data Processing**: Pandas + NumPy
- **Interpretability**: GNNExplainer + Perturbation Analysis

---

## 🔧 Environment Setup

### System Requirements

- Python 3.9+
- CUDA 11.6+ (GPU support)
- Memory: 8GB+ (16GB+ recommended)

### Dependency Installation

Install using conda environment manager (recommended):

```bash
# Create and activate conda environment
conda env create -f env.yml
conda activate gcn_archi
```

Or install dependencies manually:

```bash
# Create virtual environment
conda create -n gcn_archi python=3.9
conda activate gcn_archi

# Install PyTorch (CUDA version)
conda install pytorch=1.13.1 pytorch-cuda=11.6 -c pytorch -c nvidia

# Install PyTorch Geometric
pip install torch-geometric==2.6.1

# Install other dependencies
pip install pandas numpy flask flask-cors openpyxl matplotlib
```

---

## 📁 Project Structure

```
gcn_backend-gpu-/
├── 🧠 Core Model Files
│   ├── GCN9.py                      # Enhanced GAT-GCN model definition
│   ├── GraphDataConstruct.py        # Graph data construction (for prediction)
│   └── GraphDataConstruct_explain.py# Graph data construction (for explanation)
│
├── 🔮 Prediction Functions
│   ├── predict.py                   # Single sample prediction script
│   └── predict_api.py              # Prediction API service
│
├── 🔍 Interpretation Functions
│   ├── GCN_explainer.py            # GCN explainer core class
│   ├── GCN_explainer_api.py        # Interpretation API service
│   └── combined_api.py             # Combined API (prediction + interpretation)
│
├── 🛠️ Utility Scripts
│   └── xlsx_to_json.py             # Excel to JSON conversion tool
│
├── 📊 Data Files
│   ├── data/                       # Sample data
│   │   ├── node.xlsx              # Node feature data
│   │   ├── adjmatrix.xlsx         # Adjacency matrix
│   │   └── request.json           # API request example
│   ├── datatest/                   # Test data
│   ├── input/                      # Input datasets
│   │   └── 0/                     # Dataset 0
│   └── output/                     # Output results
│       └── 0/                     # Interpretation results
│
├── 🤖 Trained Models
│   └── model/
│       └── energy_merged_EUIGCN9.pth  # Pre-trained model
│
├── 🌍 Environmental Data
│   ├── epw/                        # Weather data files
│   └── grasshopper/                # Grasshopper scripts
│
└── 📋 Configuration Files
    └── env.yml                     # Conda environment configuration
```

---

## 🏛️ Core Architecture Details

### 1. GCN Model Architecture (GCN9.py)

```python
# Model Features:
- Based on GAT (Graph Attention Network)
- Multi-head attention mechanism (4 attention heads)
- Residual connections + layer normalization
- Skip connections to mitigate over-smoothing
- Global max pooling
```

**Network Structure**:
```
Input Layer → GAT Layer 1 (Multi-head Attention) → GAT Layer 2 (Multi-head Attention) → Skip Connection → Global Pooling → Fully Connected Layer → Output
```

**Key Features**:
- **Multi-head Attention**: 4 attention heads for parallel computation
- **Residual Connections**: Mitigates gradient vanishing problem  
- **Layer Normalization**: Stabilizes training process
- **ELU Activation Function**: Better gradient flow

### 2. Graph Data Construction (GraphDataConstruct.py)

**Node Feature Processing**:
```python
# Original Features (16 dimensions)
['Name', 'ConstructionName', 'ZoneName', 'OutsideBoundaryCondiction', 
 'Area', 'SI', 'Subface', 'SubfaceArea', 'SubRes', 'SubSHGC', 'Res', 
 'Thickness', 'ThermalAbsorptance', 'SolarAbsorptance', 'VisiblAbsorptance', 'Direction']

# Features after One-hot Encoding (26 dimensions)
- Numerical Features: Area, SI, SubfaceArea, SubRes, SubSHGC, Res, Thickness, 
            ThermalAbsorptance, SolarAbsorptance, VisiblAbsorptance
- Categorical Features: 
  * ConstructionName → Construction_0/1/2/3 (exterior/interior/ground/roof)
  * OutsideBoundaryCondiction → Boundary_0/1/2 (Outdoors/Surface/Ground)
  * Subface → Subface_0/1/2/3 (NoSubface/Window/Door/Window&Door)
  * Direction → Direction_0/1/2/3/4 (NoDirection/East/South/West/North)
```

**Adjacency Matrix Processing**:
- Convert 2D adjacency matrix to PyG edge_index format
- Filter self-loop connections
- Maintain undirected graph structure

### 3. Explainer System (GCN_explainer.py)

**Interpretation Methods**:
1. **GNNExplainer**: Gradient-based importance analysis
2. **Perturbation Analysis**: Multi-scale feature perturbation testing
3. **Edge Importance**: Analyze connection importance by removing edges

**Importance Calculation Formula**:
```python
# Node Feature Importance
importance = avg_impact × node_mask × original_value

# Edge Importance  
importance = (original_pred - perturbed_pred) × edge_mask
```

---

## 🚀 Usage Guide

### 1. Single Sample Prediction

#### Predict Using Script

```bash
# Edit data files in datatest/ folder, then run:
python predict.py
```

#### Predict Using API

```bash
# Start API service
python predict_api.py

# API will run at http://localhost:5000
```

**API Request Format**:
```json
POST /predict
Content-Type: application/json

{
    "node_data": [
        ["Component Name", "Construction Type", "Zone Name", "Boundary Condition", "Area", "SI", "Subface", "Subface Area", "Subface Resistance", "Subface SHGC", "Resistance", "Thickness", "Thermal Absorptance", "Solar Absorptance", "Visible Absorptance", "Direction"],
        // ... more component data
    ],
    "adj_matrix": [
        [0, 1, 0, 0, ...],
        [1, 0, 1, 0, ...],
        // ... adjacency matrix
    ],
    "energy_data": [  // Optional
        [energy_value1, energy_value2, ...]
    ]
}
```

**API Response Format**:
```json
{
    "prediction": 123.45  // Predicted energy consumption value
}
```

### 2. Model Interpretation

#### Interpret Using Script

```bash
# Run interpretation analysis
python GCN_explainer.py
```

#### Interpret Using API

```bash
# Start interpretation API service
python GCN_explainer_api.py

# Or use combined API (prediction + interpretation)
python combined_api.py
```

**Interpretation API Request Format**:
```json
POST /predict
Content-Type: application/json

{
    "node_data": [...],
    "adj_matrix": [...],
    "explain": true  // Request interpretation results
}
```

**Interpretation API Response Format**:
```json
{
    "prediction": 123.45,
    "explanation": {
        "node_importance": {
            "Node_ID": [0, 1, 2, ...],
            "Area": [0.123, -0.456, ...],
            "SI": [0.789, 0.234, ...],
            // ... feature importance for each feature
        },
        "edge_matrix": [
            [0.0, 0.031, 0.0, ...],
            [0.031, 0.0, -0.024, ...],
            // ... edge importance matrix
        ]
    }
}
```

### 3. Data Format Conversion

```bash
# Convert Excel data to JSON API format
python xlsx_to_json.py
```

---

## 📊 Data Format Details

### Input Data Format

#### 1. Node Feature Data (node.xlsx)

| Column Name | Data Type | Description | Example Value |
|-------------|-----------|-------------|---------------|
| Name | String | Component name | "Room_10_a79cd0dc..Face0" |
| ConstructionName | String | Construction type | "exterior"/"interior"/"ground"/"roof" |
| ZoneName | String | Zone name | "Room_10_a79cd0dc" |
| OutsideBoundaryCondiction | String | Boundary condition | "Outdoors"/"Surface"/"Ground" |
| Area | Float | Area (m²) | 275.8176 |
| SI | Float | SI value | 1.293597 |
| Subface | Integer | Subface type | 0/1/2/3 |
| SubfaceArea | Float | Subface area (m²) | 0.0 |
| SubRes | Float | Subface thermal resistance | 0.0 |
| SubSHGC | Float | Subface solar heat gain coefficient | 0.0 |
| Res | Float | Thermal resistance ((m²·K)/W) | 0.277311 |
| Thickness | Float | Thickness (m) | 0.33 |
| ThermalAbsorptance | Float | Thermal absorptance | 0.57 |
| SolarAbsorptance | Float | Solar absorptance | 0.57 |
| VisiblAbsorptance | Float | Visible light absorptance | 0.57 |
| Direction | Integer | Orientation | 0/1/2/3/4 |

#### 2. Adjacency Matrix (adjmatrix.xlsx)

- **Format**: N×N matrix, where N is the number of components
- **Value Meaning**:
  - 1: Two components are adjacent
  - 0: Two components are not adjacent
- **Properties**: Symmetric matrix, diagonal is 0 (no self-loops)

#### 3. Energy Data (energy_sum.xlsx)

- **Sheet Name**: `eui_end_use`
- **Format**: Table containing various energy consumption data
- **Usage**: As prediction target or validation data

### Output Data Format

#### 1. Node Feature Importance (node_feature_importance.csv)

```csv
Node_ID,Area,SI,SubfaceArea,SubRes,SubSHGC,Res,Thickness,...
0,-1.038,1.911,0.0,0.0,0.0,-4.342,-0.282,...
1,0.748,-1.771,0.0,0.0,0.0,-0.603,-0.357,...
...
```

#### 2. Edge Importance Matrix (edge_importance_matrix.csv)

```csv
0,1,2,3,4,5,6,7,8,9,...
0.0,0.031,0.0,-0.00001,0.0,-0.066,0.0,...
0.031,0.0,-0.00002,0.0,-0.000003,1.044,0.0,...
...
```

---

## 🔧 Advanced Configuration

### Model Parameter Adjustment

You can adjust the following parameters in `GCN9.py`:

```python
class GCN(torch.nn.Module):
    def __init__(self, num_node_features, 
                 hidden_channels=64,    # Hidden layer dimension
                 heads=4,              # Number of attention heads
                 dropout=0.2):         # Dropout ratio
```

### Explainer Parameters

You can adjust parameters in the explainer class:

```python
# GNNExplainer training epochs
self.explainer = Explainer(
    algorithm=GNNExplainer(epochs=200),  # Adjustable epochs
    ...
)

# Perturbation analysis parameters
perturbation_scales = [0.05, 0.1, 0.15, 0.2]  # Perturbation ratios
```

### API Service Configuration

```python
# Port and host configuration
app.run(host='0.0.0.0', port=5000)

# CORS configuration
CORS(app)  # Allow cross-origin requests
```

---

## 🧪 Testing Examples

### 1. Quick Test

```bash
# Use provided test data
cd datatest/
python ../predict.py
```

### 2. API Test

```bash
# Start API service
python predict_api.py

# Test using curl
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d @data/request.json
```

### 3. Interpretation Function Test

```bash
# Start combined API
python combined_api.py

# Test interpretation function
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"node_data": [...], "adj_matrix": [...], "explain": true}'
```

---

## 📈 Performance Optimization

### GPU Acceleration

System automatically detects and uses GPU:

```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
```

### Memory Optimization

- Use batch processing to reduce memory usage
- Release unnecessary tensors promptly
- Use `torch.no_grad()` to disable gradient computation

### Inference Optimization

```python
# Model inference optimization
model.eval()  # Set to evaluation mode
with torch.no_grad():  # Disable gradient computation
    prediction = model(...)
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. CUDA Related Errors

**Problem**: `RuntimeError: CUDA out of memory`

**Solution**:
```python
# Reduce batch size
batch_size = 1  # In predict.py

# Clear GPU cache
torch.cuda.empty_cache()
```

#### 2. Data Format Errors

**Problem**: `ValueError: could not convert string to float`

**Solution**:
- Check Excel file format
- Ensure numeric columns don't contain text
- Verify categorical variable mappings

#### 3. Model Loading Failure

**Problem**: `FileNotFoundError: model/energy_merged_EUIGCN9.pth`

**Solution**:
- Ensure model file exists
- Check file path
- Verify model file is not corrupted

#### 4. API Connection Issues

**Problem**: `Connection refused`

**Solution**:
```bash
# Check port usage
netstat -an | grep 5000

# Change port
app.run(host='0.0.0.0', port=5001)
```

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📚 Technical Details

### Model Training Details

Although this project is primarily for inference, model training used the following configuration:

- **Loss Function**: Mean Squared Error (MSE)
- **Optimizer**: Adam optimizer
- **Learning Rate**: Adaptive learning rate adjustment
- **Regularization**: Dropout + LayerNorm
- **Training Strategy**: Early stopping + learning rate decay

### Graph Neural Network Principles

1. **Graph Representation**: Building components as nodes, spatial adjacency relationships as edges
2. **Message Passing**: Nodes pass information through edges
3. **Attention Mechanism**: Dynamically computes importance weights between nodes
4. **Graph-level Prediction**: Obtains building-level prediction through global pooling

### Interpretability Principles

1. **Gradient Importance**: Computes feature importance based on gradients
2. **Perturbation Analysis**: Observes output changes by perturbing inputs
3. **Ablation Experiments**: Removes specific features or edges to observe impact
4. **Multi-scale Analysis**: Uses different perturbation intensities to ensure stability

---

## 🔄 Version Updates

### v1.0 Current Version Features

- ✅ GAT-based GCN model
- ✅ Complete API service
- ✅ Model interpretability analysis
- ✅ Excel data support
- ✅ GPU acceleration support

### Future Version Plans

- 🔄 Automatic model training functionality
- 🔄 Visualization interface
- 🔄 Batch processing optimization
- 🔄 More interpretability methods
- 🔄 Model performance monitoring

---

## 🤝 Contributing Guidelines

### Development Environment Setup

```bash
# Clone the project
git clone <repository-url>
cd gcn_backend-gpu-

# Setup development environment
conda env create -f env.yml
conda activate gcn_archi

# Install development dependencies
pip install pytest black flake8
```

### Code Style

- Use Black for code formatting
- Follow PEP 8 standards
- Add detailed docstrings
- Write unit tests

### Commit Conventions

```
feat: Add new feature
fix: Fix bug
docs: Update documentation
style: Code formatting adjustments
refactor: Code refactoring
test: Add tests
chore: Build/tool related
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 📞 Contact Information

For questions or suggestions, please contact us through:

- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 Wiki: [Project Wiki](https://github.com/your-repo/wiki)

---

## 📖 References

1. **Graph Attention Networks** - Veličković et al., 2017
2. **GNNExplainer** - Ying et al., 2019  
3. **PyTorch Geometric** - Fey & Lenssen, 2019
4. **Building Energy Modeling** - DOE Commercial Reference Buildings

## 🙏 Acknowledgments

Thanks to the following projects and teams for their support:

- [PyTorch Team](https://pytorch.org/)
- [PyTorch Geometric](https://pytorch-geometric.readthedocs.io/)
- [Flask Community](https://flask.palletsprojects.com/)

---

*This README file provides a comprehensive overview of all aspects of the GCN Building Energy Prediction and Interpretation System. For more information, please refer to the project Wiki or contact the development team.*
