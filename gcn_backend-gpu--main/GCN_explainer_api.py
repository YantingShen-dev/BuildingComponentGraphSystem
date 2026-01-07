import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import torch
import numpy as np
import matplotlib.pyplot as plt
from GCN9 import GCN
from GraphDataConstruct_explain import construct_graph_data
from torch_geometric.explain import GNNExplainer, Explainer
import pandas as pd
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
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
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 直接使用提供的数据
        energy_path = energy_data
        
        # 加载数据和模型
        # -----------------------------------------------------------------------------------
        self.graph_data = construct_graph_data(node_data, adj_matrix, energy_path, 'Heating', 0)
        # -----------------------------------------------------------------------------------
        self.model = GCN(self.graph_data.num_node_features).to(self.device)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        
        # 初始化GNNExplainer
        self.explainer = Explainer(
            model=self.model,
            algorithm=GNNExplainer(epochs=50),
            explanation_type='model',
            edge_mask_type='object',
            node_mask_type='object',
            model_config=dict(
                mode='regression',
                task_level='graph',
                return_type='raw'
            )
        )

    def explain_prediction(self, feature_names=None):
        """使用GNNExplainer解释预测（简化版，只返回总体特征重要性）"""
        # 获取详细的节点和边重要性
        node_importance_df, edge_importance_matrix = self.explain_and_save(feature_names, None, None)
        
        # 计算每个特征的总体重要性
        feature_importance = {}
        for feat_name in feature_names:
            if feat_name != 'Node_ID':  # 跳过Node_ID列
                feature_importance[feat_name] = node_importance_df[feat_name].mean()
        
        # 创建总体特征重要性DataFrame
        importance_df = pd.DataFrame({
            'Feature': feature_importance.keys(),
            'Importance': feature_importance.values()
        })
        importance_df = importance_df.sort_values('Absolute_Importance', ascending=False)
        
        # 获取边的总体重要性
        edge_importance = edge_importance_matrix.flatten()
        top_edges = np.argsort(edge_importance)[-5:][::-1]
        
        return importance_df, edge_importance[top_edges]

    def _get_prediction(self, data):
        """获取单个预测值"""
        self.model.eval()
        with torch.no_grad():
            out = self.model(data.x.to(self.device), 
                            data.edge_index.to(self.device), 
                            torch.zeros(data.x.size(0), dtype=torch.long, device=self.device))
        return out.cpu().numpy().mean()

    def explain_and_save(self, feature_names, dataset_id, output_dir):
        """解释预测并保存详细结果"""
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
        
        return node_importance_df, edge_importance_matrix

@app.route('/predict', methods=['POST'])
def explain():
    """
    API端点，接收JSON格式的预测请求
    
    请求体格式:
    {
        "node_data": [[...], [...], ...],  # 节点特征数据
        "adj_matrix": [[...], [...], ...], # 邻接矩阵
        "energy_data": [[...], [...], ...] # 能量数据（可选）
    }
    """
    BASE_DATA_DIR = r"input"  # 包含所有数据集文件夹的目录
    MODEL_PATH = r"model/energy_merged_EUIGCN9.pth"
    OUTPUT_DIR = r"output"
    
    # 只处理input/0文件夹
    data_dir = os.path.join(BASE_DATA_DIR, "0")
    dataset_output_dir = os.path.join(OUTPUT_DIR, "0")
    os.makedirs(dataset_output_dir, exist_ok=True)

    feature_names = [
        'Area', 'SI', 'SubfaceArea', 'SubRes', 'SubSHGC', 'Res',
        'Thickness', 'ThermalAbsorptance', 'SolarAbsorptance', 'VisiblAbsorptance',
        'exterior', 'interior', 'ground', 'roof',
        'Outdoors', 'Surface', 'Ground',
        'NoSubface', 'Window', 'Door', 'Window&Door',
        'NoDirection', 'East', 'South', 'West', 'North'
    ]
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 检查必要字段
        if not all(key in data for key in ['node_data', 'adj_matrix']):
            return jsonify({'error': 'Missing required fields: node_data and adj_matrix'}), 400
            
        # 获取数据
        node_data = data['node_data']
        adj_matrix = data['adj_matrix']

        _, _, energy_path = read_data_from_dir(data_dir)
        # 创建解释器实例
        explainer = GCNExplainer(MODEL_PATH, node_data, adj_matrix, energy_path)
        
        # 获取解释结果
        node_importance, edge_matrix = explainer.explain_and_save(
            feature_names=feature_names,
            dataset_id="0",
            output_dir=dataset_output_dir
        )
        return jsonify({'node_importance': node_importance.to_dict(), 'edge_matrix': edge_matrix.tolist()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 

    # # 基础路径设置
    # BASE_DATA_DIR = r"input"  # 包含所有数据集文件夹的目录
    # MODEL_PATH = r"model/energy_merged_EUIGCN9.pth"
    # OUTPUT_DIR = r"output"
    
    # # 只处理input/0文件夹
    # data_dir = os.path.join(BASE_DATA_DIR, "0")
    # dataset_output_dir = os.path.join(OUTPUT_DIR, "0")
    # os.makedirs(dataset_output_dir, exist_ok=True)
    
    # print(f"处理数据集 0...")
    
    # # 特征名称定义
    # feature_names = [
    #     'Area', 'SI', 'SubfaceArea', 'SubRes', 'SubSHGC', 'Res',
    #     'Thickness', 'ThermalAbsorptance', 'SolarAbsorptance', 'VisiblAbsorptance',
    #     'exterior', 'interior', 'ground', 'roof',
    #     'Outdoors', 'Surface', 'Ground',
    #     'NoSubface', 'Window', 'Door', 'Window&Door',
    #     'NoDirection', 'East', 'South', 'West', 'North'
    # ]
    
    # try:
    #     # 读取数据
    #     node_data, adj_matrix, energy_path = read_data_from_dir(data_dir)
    #     # 创建解释器实例
    #     explainer = GCNExplainer(MODEL_PATH, node_data, adj_matrix, energy_path)
        
    #     # 获取解释结果
    #     node_importance, edge_matrix = explainer.explain_and_save(
    #         feature_names=feature_names,
    #         dataset_id="0",
    #         output_dir=dataset_output_dir
    #     )

    #     print(node_importance)
    #     print(edge_matrix)
        
    #     # 保存边重要性矩阵
    #     edge_importance_df = pd.DataFrame(edge_matrix)
    #     edge_importance_df.to_csv(
    #         os.path.join(dataset_output_dir, 'edge_importance_matrix.csv'),
    #         index=False
    #     )
        
    #     # 保存节点特征重要性
    #     node_importance.to_csv(
    #         os.path.join(dataset_output_dir, 'node_feature_importance.csv'),
    #         index=False
    #     )
        
    # except Exception as e:
    #     print(f"处理数据集 0 时出错: {str(e)}")

