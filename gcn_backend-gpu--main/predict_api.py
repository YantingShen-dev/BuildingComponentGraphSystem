import torch
from GCN9 import GCN
from GraphDataConstruct import construct_graph_data
from torch_geometric.loader import DataLoader
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
# 允许所有来源（生产环境可以限制为特定域名）
CORS(app, 
     resources={
         r"/*": {
             "origins": "*",
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"]
         }
     },
     supports_credentials=True)

# 处理 OPTIONS 预检请求
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        return response
        
def predict_single_sample(model_path, node_data, adj_matrix, energy_data):
    """
    预测单个样本的值
    
    参数:
        model_path: 训练好的模型路径
        node_data: 节点特征数据，二维列表
        adj_matrix: 邻接矩阵，二维列表
        energy_data: 能量数据，二维列表
        
    返回:
        prediction: 预测值
    """
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # 构建单个样本的图数据
    try:
        graph_data = construct_graph_data(node_data, adj_matrix, energy_data, 'EUI', 0)
        print("Successfully constructed graph data")
        print(f"Number of nodes: {graph_data.num_nodes}")
        print(f"Number of node features: {graph_data.num_node_features}")
    except Exception as e:
        print(f"Error constructing graph data: {str(e)}")
        return None

    # 创建模型实例
    model = GCN(graph_data.num_node_features).to(device)

    # 加载训练好的模型参数
    try:
        model.load_state_dict(torch.load(model_path))
        print(f"Successfully loaded model from {model_path}")
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None

    # 创建数据加载器
    loader = DataLoader([graph_data], batch_size=1)

    # 进行预测
    model.eval()
    with torch.no_grad():
        for batch in loader:
            batch = batch.to(device)
            prediction = model(batch.x, batch.edge_index, batch.batch)
            return prediction.item()

@app.route('/predict', methods=['POST'])
def predict():
    """
    API端点，接收JSON格式的预测请求
    
    请求体格式:
    {
        "node_data": [[...], [...], ...],  # 节点特征数据
        "adj_matrix": [[...], [...], ...], # 邻接矩阵
        "energy_data": [[...], [...], ...] # 能量数据（可选）
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 检查必要字段
        if not all(key in data for key in ['node_data', 'adj_matrix']):
            return jsonify({'error': 'Missing required fields: node_data and adj_matrix'}), 400
            
        # 获取数据
        node_data = data['node_data']
        adj_matrix = data['adj_matrix']
        energy_data = data.get('energy_data')  # 使用get方法获取可选参数
        
        # 设置模型路径
        MODEL_PATH = "model/energy_merged_EUIGCN9.pth"
        
        # 进行预测
        prediction = predict_single_sample(MODEL_PATH, node_data, adj_matrix, energy_data)
        
        if prediction is None:
            return jsonify({'error': 'Prediction failed'}), 500
            
        return jsonify({'prediction': prediction})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 