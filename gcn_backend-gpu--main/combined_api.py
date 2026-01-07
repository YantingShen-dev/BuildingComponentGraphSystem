import torch
import numpy as np
import pandas as pd
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from GCN9 import GCN
from GraphDataConstruct import construct_graph_data
from GraphDataConstruct_explain import construct_graph_data as construct_graph_data_explain
from torch_geometric.explain import GNNExplainer, Explainer
from torch_geometric.loader import DataLoader

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

def read_data_from_dir(data_dir):
    """
    从目录中读取node.xlsx, adjmatrix.xlsx和energy_sum.xlsx文件
    
    参数:
        data_dir: 数据文件夹路径
        
    返回:
        tuple: (node_data, adj_matrix, energy_path)
    """
    # 读取node.xlsx
    node_path = os.path.join(data_dir, 'node.xlsx')
    node_data = pd.read_excel(node_path, header=None).values.tolist()
    
    # 读取adjmatrix.xlsx
    adj_path = os.path.join(data_dir, 'adjmatrix.xlsx')
    adj_matrix = pd.read_excel(adj_path, header=None).values.tolist()
    
    # 获取energy_sum.xlsx的路径
    energy_path = os.path.join(data_dir, 'energy_sum.xlsx')
    
    return node_data, adj_matrix, energy_path

class GCNExplainer:
    def __init__(self, model_path, node_data, adj_matrix, energy_data):
        self.device = torch.device('cpu')
        
        # 直接使用提供的数据
        energy_path = energy_data
        
        # 加载数据和模型
        self.graph_data = construct_graph_data_explain(node_data, adj_matrix, energy_path, 'Heating', 0)
        self.model = GCN(self.graph_data.num_node_features).to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        self.model.eval()
        
        # 初始化GNNExplainer
        self.explainer = Explainer(
            model=self.model,
            algorithm=GNNExplainer(epochs=200),
            explanation_type='model',
            edge_mask_type='object',
            node_mask_type='object',
            model_config=dict(
                mode='regression',
                task_level='graph',
                return_type='raw'
            )
        )

    def _get_prediction(self, data):
        """获取单个预测值"""
        self.model.eval()
        with torch.no_grad():
            out = self.model(data.x.to(self.device), 
                            data.edge_index.to(self.device), 
                            torch.zeros(data.x.size(0), dtype=torch.long, device=self.device))
        return out.cpu().numpy().mean()

    def explain_and_save(self, feature_names):
        """解释预测并返回结果"""
        # 获取数据
        data = self.graph_data.to(self.device)
        original_prediction = self._get_prediction(data)
        
        # 获取解释
        explanation = self.explainer(
            x=data.x,
            edge_index=data.edge_index,
            batch=torch.zeros(data.x.size(0), dtype=torch.long, device=self.device)
        )
        
        # 获取节点数量
        num_nodes = data.x.size(0)
        
        # 创建节点特征重要性DataFrame
        node_feature_importance = []
        node_mask = explanation.node_mask.cpu().detach().numpy()
        
        for node_idx in range(num_nodes):
            node_importance = {}
            node_importance['Node_ID'] = node_idx
            
            for feat_idx, feat_name in enumerate(feature_names):
                # 计算特征的原始值
                original_value = data.x[node_idx, feat_idx].item()
                
                # 多次不同大小的扰动
                perturbation_scales = [0.05, 0.1, 0.15, 0.2]  # 不同的扰动比例
                importance_list = []
                
                for scale in perturbation_scales:
                    # 正向扰动
                    perturbed_data = data.clone()
                    epsilon = scale * abs(original_value) if original_value != 0 else scale
                    perturbed_data.x[node_idx, feat_idx] += epsilon
                    pos_prediction = self._get_prediction(perturbed_data)
                    pos_impact = (pos_prediction - original_prediction) / epsilon
                    
                    # 负向扰动
                    perturbed_data = data.clone()
                    perturbed_data.x[node_idx, feat_idx] -= epsilon
                    neg_prediction = self._get_prediction(perturbed_data)
                    neg_impact = (original_prediction - neg_prediction) / epsilon
                    
                    # 取平均影响
                    avg_impact = (pos_impact + neg_impact) / 2
                    importance = avg_impact * node_mask[node_idx][0] * original_value
                    importance_list.append(importance)
                
                # 取所有扰动结果的平均值
                node_importance[feat_name] = np.mean(importance_list)
            
            node_feature_importance.append(node_importance)
        
        # 转换为DataFrame
        node_importance_df = pd.DataFrame(node_feature_importance)
        
        # 处理边的重要性
        edge_mask = explanation.edge_mask.cpu().detach().numpy()
        edge_importance_matrix = np.zeros((num_nodes, num_nodes))
        
        # 将边的重要性转换为邻接矩阵格式
        edge_index = data.edge_index.cpu().numpy()
        for i, (src, dst) in enumerate(edge_index.T):
            # 复制原始数据
            perturbed_data = data.clone()
            
            # 删除这条边（通过创建新的edge_index）
            mask = torch.ones(data.edge_index.size(1), dtype=torch.bool)
            mask[i] = False
            perturbed_data.edge_index = data.edge_index[:, mask]
            
            # 获取删除边后的预测
            perturbed_prediction = self._get_prediction(perturbed_data)
            
            # 计算影响
            importance = (original_prediction - perturbed_prediction) * edge_mask[i]
            
            # 保存到邻接矩阵（保持对称性）
            edge_importance_matrix[src][dst] = importance
            edge_importance_matrix[dst][src] = importance
        
        return node_importance_df, edge_importance_matrix, original_prediction

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
    device = torch.device('cpu')
    
    # 构建单个样本的图数据
    try:
        graph_data = construct_graph_data(node_data, adj_matrix, energy_data, 'EUI', 0)
    except Exception as e:
        print(f"Error constructing graph data: {str(e)}")
        return None, str(e)

    # 创建模型实例
    model = GCN(graph_data.num_node_features).to(device)

    # 加载训练好的模型参数
    try:
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None, str(e)

    # 创建数据加载器
    loader = DataLoader([graph_data], batch_size=1)

    # 进行预测
    model.eval()
    with torch.no_grad():
        for batch in loader:
            batch = batch.to(device)
            prediction = model(batch.x, batch.edge_index, batch.batch)
            return prediction.item(), None

@app.route('/predict', methods=['POST'])
def predict():
    """
    API端点，接收JSON格式的预测请求
    
    请求体格式:
    {
        "node_data": [[...], [...], ...],  # 节点特征数据
        "adj_matrix": [[...], [...], ...], # 邻接矩阵
        "energy_data": [[...], [...], ...], # 能量数据（可选）
        "explain": true/false  # 是否需要解释（可选，默认为true）
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
        need_explain = data.get('explain', True)  # 默认不需要解释
        
        # 设置模型路径
        MODEL_PATH = "model/energy_merged_EUIGCN9.pth"
        
        # 如果需要能源数据但未提供
        if energy_data is None:
            # 使用默认数据文件夹中的能源数据
            data_dir = os.path.join("input", "0")
            _, _, energy_path = read_data_from_dir(data_dir)
            energy_data = energy_path
        
        # 进行预测
        prediction, error = predict_single_sample(MODEL_PATH, node_data, adj_matrix, energy_data=None)
        
        if prediction is None:
            return jsonify({'error': f'Prediction failed: {error}'}), 500
        
        result = {'prediction': prediction}
        
        # 如果需要解释
        if need_explain:
            try:
                # 特征名称定义
                feature_names = [
                    'Area', 'SI', 'SubfaceArea', 'SubRes', 'SubSHGC', 'Res',
                    'Thickness', 'ThermalAbsorptance', 'SolarAbsorptance', 'VisiblAbsorptance',
                    'exterior', 'interior', 'ground', 'roof',
                    'Outdoors', 'Surface', 'Ground',
                    'NoSubface', 'Window', 'Door', 'Window&Door',
                    'NoDirection', 'East', 'South', 'West', 'North'
                ]
                
                # 创建解释器实例
                explainer = GCNExplainer(MODEL_PATH, node_data, adj_matrix, energy_data)
                
                # 获取解释结果
                node_importance, edge_matrix, _ = explainer.explain_and_save(feature_names=feature_names)
                
                # 添加到结果中
                result['explanation'] = {
                    'node_importance': node_importance.to_dict(),
                    'edge_matrix': edge_matrix.tolist()
                }
            except Exception as e:
                # 如果解释失败，仍然返回预测结果，但添加解释错误信息
                result['explanation_error'] = str(e)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 