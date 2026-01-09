# Graph Attention Network for Building Energy Prediction and Optimization

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Vue 3](https://img.shields.io/badge/Vue-3-4FC08D?logo=vue.js)](https://vuejs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-1.13+-EE4C2C?logo=pytorch)](https://pytorch.org/)

An intelligent web application for **component-based building energy prediction and optimization** using Graph Attention Networks (GAT). This system provides interactive 3D modeling, real-time energy consumption prediction, interpretability analysis, and multi-objective optimization for building design.

📄 **Research Paper**: [Building Energy Modeling with Graph Attention Networks: A Component-Level Interpretable Approach](https://www.sciencedirect.com/science/article/abs/pii/S0378778825013143)  
💻 **Web App**: [click here](https://bcgs.vercel.app/)  

## 🌟 Features

### 🏗️ Interactive 3D Building Modeling
- **Intuitive 3D Interface**: Create and manipulate building models using Three.js
- **Real-time Manipulation**: Drag, resize, and position building components with visual feedback
- **Smart Snapping**: Automatic alignment of components for precise modeling
- **Model Validation**: Connectivity and intersection checks to ensure valid building geometry

### 🧠 AI-Powered Energy Prediction
- **Graph Neural Network Model**: Enhanced GAT (Graph Attention Network) for accurate energy prediction
- **Component-Level Analysis**: Treats building components (walls, doors, windows) as graph nodes
- **Spatial Relationship Learning**: Captures thermal relationships through graph edges
- **Real-time Prediction**: Instant energy consumption estimates during design

### 🔍 Model Interpretability
- **Feature Importance Analysis**: Understand which component features impact energy consumption
- **Connection Importance**: Analyze how spatial relationships affect energy performance
- **GNNExplainer Integration**: Provides detailed explanations for each prediction
- **Visual Heatmaps**: Color-coded importance visualization

### 🎯 Multi-Objective Optimization
- **NSGA-II Algorithm**: Pareto-optimal solutions for energy-cost trade-offs
- **Material Selection**: Optimize building materials, thickness, and configurations
- **Pareto Front Visualization**: Interactive exploration of optimization solutions
- **Design Recommendations**: Automated suggestions for energy-efficient design

## 📊 Research Highlights

This work demonstrates:
- **13% accuracy improvement** over end-to-end models under Changsha, China climate conditions
- **Knowledge embedding method** representing 3D models and thermal relationships
- **Component-level interpretability** revealing that geometric features and connections have greater impact than material performance alone
- **Practical validation** through real-world design and retrofit cases

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vue 3)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 3D Model │  │ Analysis │  │Prediction│  │Optimize  │   │
│  │  Builder │  │  View    │  │  View    │  │  View    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │ REST API
┌───────────────────────┴─────────────────────────────────────┐
│                   Backend (Python Flask)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Prediction   │  │ Explainability│  │ Optimization │     │
│  │   API        │  │     API      │  │     API      │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
┌─────────┴──────────────────┴──────────────────┴─────────────┐
│              Deep Learning Model (PyTorch)                   │
│  ┌──────────────────────────────────────────────────┐       │
│  │        Enhanced GAT (Graph Attention Network)     │       │
│  │  • Multi-head Attention                           │       │
│  │  • Residual Connections                           │       │
│  │  • Graph-level Regression                         │       │
│  └──────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 16+ and npm/yarn
- **Python** 3.9+
- **CUDA** 11.6+ (optional, for GPU acceleration)

### Frontend Setup

```bash
# Navigate to frontend directory
cd gcn_frontend_app-main

# Install dependencies
npm install
# or
yarn install

# Start development server
npm run dev
# or
yarn dev
```

Frontend will be available at `http://localhost:5173`

### Backend Setup

```bash
# Navigate to backend directory
cd gcn_backend-gpu--main

# Create conda environment (recommended)
conda env create -f env.yml
conda activate gcn_archi

# Or install dependencies manually
pip install torch torch-geometric flask flask-cors pandas numpy openpyxl

# Start API server
python combined_api.py
```

Backend API will be available at `http://localhost:5000`

### Full Stack Development

```bash
# Terminal 1: Start backend
cd gcn_backend-gpu--main
python combined_api.py

# Terminal 2: Start frontend
cd gcn_frontend_app-main
npm run dev
```

## 📁 Project Structure

```
.
├── gcn_frontend_app-main/          # Frontend application (Vue 3)
│   ├── src/
│   │   ├── views/                  # Page components
│   │   │   ├── HomeView.vue       # 3D modeling interface
│   │   │   ├── SecondView.vue     # Model analysis
│   │   │   ├── ThirdView.vue      # Prediction & interpretability
│   │   │   └── OptView.vue        # Optimization interface
│   │   ├── components/             # Reusable components
│   │   └── utils/                  # Utility functions
│   └── package.json
│
├── gcn_backend-gpu--main/          # Backend API (Python)
│   ├── GCN9.py                     # Enhanced GAT model
│   ├── GraphDataConstruct.py       # Graph data builder
│   ├── combined_api.py             # Main prediction API
│   ├── optimization_api.py         # Optimization API
│   ├── model/                      # Trained model weights
│   │   └── energy_merged_EUIGCN9.pth
│   └── materials/                  # Material database
│
└── README.md
```

## 🔧 Configuration

### Frontend API Configuration

Update API endpoints in:
- `src/views/SecondView.vue`
- `src/views/ThirdView.vue`
- `src/views/OptView.vue`

Or configure proxy in `vite.config.ts`:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true,
  }
}
```

### Backend Model Path

Ensure model file exists at:
```
gcn_backend-gpu--main/model/energy_merged_EUIGCN9.pth
```

## 📚 API Documentation

### Prediction API

**Endpoint**: `POST /predict`

**Request Body**:
```json
{
  "node_data": [[...]],      // Component features (16 dimensions per component)
  "adj_matrix": [[...]],     // Adjacency matrix (N×N)
  "energy_data": null,       // Optional: energy reference data
  "explain": true            // Optional: include interpretability analysis
}
```

**Response**:
```json
{
  "prediction": 123.45,
  "explanation": {
    "node_importance": {...},
    "edge_matrix": [[...]]
  }
}
```

### Optimization API

**Endpoint**: `POST /optimize`

**Request Body**:
```json
{
  "node_data": [[...]],
  "adj_matrix": [[...]],
  "wall_type": 0,
  "population_size": 50,
  "generations": 10,
  "stream": false
}
```

**Response**:
```json
{
  "success": true,
  "pareto_solutions": [
    {
      "energy": 120.5,
      "cost": 15000.0,
      "nodes": [...]
    }
  ]
}
```

## 🌐 Deployment

### Vercel Deployment (Frontend)

1. **Prepare for deployment**:
```bash
cd gcn_frontend_app-main
npm run build
```

2. **Deploy to Vercel**:
   - Install Vercel CLI: `npm i -g vercel`
   - Run: `vercel`
   - Follow the prompts

3. **Environment Variables** (if using):
   - Add backend API URL in Vercel dashboard

### Backend Deployment

For backend API, consider:
- **Railway**: Easy Python deployment
- **Render**: Free tier available
- **Heroku**: Traditional option
- **AWS/Google Cloud**: For production scale

## 🧪 Usage Example

1. **Build 3D Model**: Use interactive interface to create building geometry
2. **Analyze Components**: View component features and relationships
3. **Predict Energy**: Get instant energy consumption estimates
4. **Understand Results**: Explore feature importance and connections
5. **Optimize Design**: Find Pareto-optimal material configurations

## 📊 Data Format

### Node Features (16 dimensions)
- Name, ConstructionType, ZoneName, BoundaryCondition
- Area, SI (Shape Index), Subface type/area
- Thermal properties (Resistance, Thickness, Absorptance)
- Direction (Orientation)

### Adjacency Matrix
- N×N binary matrix
- 1 indicates physical connection between components
- Symmetric (undirected graph)

## 🤝 Citation

If you use this work in your research, please cite:

```bibtex
@article{your2025building,
  title={Building Energy Modeling with Graph Attention Networks: A Component-Level Interpretable Approach},
  author={Your Name and Collaborators},
  journal={Energy and Buildings},
  year={2025},
  doi={10.1016/j.enbuild.2025.xxx}
}
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **PyTorch Geometric** for GNN framework
- **Three.js** for 3D visualization
- **Vue.js** for frontend framework
- **DEAP** for evolutionary algorithms

## 📧 Contact

For questions or collaborations, please refer to the research paper contact information.

---

**Note**: This is a research prototype. For production use, additional testing, security measures, and performance optimization are recommended.

