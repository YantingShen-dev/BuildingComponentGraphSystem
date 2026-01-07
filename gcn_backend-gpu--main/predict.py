import torch
from GCN9 import GCN
from GraphDataConstruct import construct_graph_data
from torch_geometric.loader import DataLoader
import pandas as pd
import os

def read_excel_to_list(file_path, sheet_name=None):
    """
    读取Excel文件并返回二维列表
    
    参数:
        file_path: Excel文件路径
        sheet_name: 工作表名称，默认为None（读取第一个工作表）
        
    返回:
        data_list: 二维列表形式的数据
    """
    try:
        if sheet_name is not None:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        else:
            df = pd.read_excel(file_path, header=None)
        return df.values.tolist()
    except Exception as e:
        print(f"Error reading Excel file {file_path}: {str(e)}")
        return None

def predict_single_sample(model_path, node_data, adj_matrix, energy_data):
    """
    预测单个样本的值
    
    参数:
        model_path: 训练好的模型路径
        node_data: 节点特征数据，二维列表
        adj_matrix: 邻接矩阵，二维列表
        energy_data: 能量数据，二维列表
    """
    # 设置设备
    device = torch.device('cpu')
    print(f"Using device: {device}")

    # 构建单个样本的图数据
    try:
        graph_data = construct_graph_data(node_data, adj_matrix, energy_data, 'EUI', 0)
        print("Successfully constructed graph data")
        print(f"Number of nodes: {graph_data.num_nodes}")
        print(f"Number of node features: {graph_data.num_node_features}")
    except Exception as e:
        print(f"Error constructing graph data: {str(e)}")
        return

    # 创建模型实例
    model = GCN(graph_data.num_node_features).to(device)

    # 加载训练好的模型参数
    try:
        model.load_state_dict(torch.load(model_path,map_location=device))
        print(f"Successfully loaded model from {model_path}")
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return

    # 创建数据加载器
    loader = DataLoader([graph_data], batch_size=1)

    # 进行预测
    model.eval()
    with torch.no_grad():
        for batch in loader:
            batch = batch.to(device)
            prediction = model(batch.x, batch.edge_index, batch.batch)
            
            print("\nPrediction Results:")
            print(f"Predicted value: {prediction.item():.4f}")

if __name__ == "__main__":
    # 设置路径
    MODEL_PATH = "model/energy_merged_EUIGCN9.pth"  # 训练好的模型路径
    DATA_DIR = os.path.join("input", "0")  # 新样本数据所在的目录

    # 读取Excel文件
    try:
        node_data = read_excel_to_list(os.path.join(DATA_DIR, 'node.xlsx'))
        adj_matrix = read_excel_to_list(os.path.join(DATA_DIR, 'adjmatrix.xlsx'))
        energy_data = read_excel_to_list(os.path.join(DATA_DIR, 'energy_sum.xlsx'), sheet_name='eui_end_use')
        energy_data = None
        if node_data is None or adj_matrix is None:
            print("Error: Failed to read required Excel files")
        else:
            # 进行预测
            predict_single_sample(MODEL_PATH, node_data, adj_matrix, energy_data)
    except Exception as e:
        print(f"Error reading data files: {str(e)}") 