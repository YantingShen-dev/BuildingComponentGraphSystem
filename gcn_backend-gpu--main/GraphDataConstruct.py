import pandas as pd
import numpy as np
import torch
from torch_geometric.data import Data
import os
from torch_geometric.loader import DataLoader
import pickle

def construct_graph_data(node_data, adj_matrix, energy_data, y_type='EUI', index=0):
    """
    构建图数据结构
    
    参数:
        node_data: 节点特征数据，二维列表
        adj_matrix: 邻接矩阵，二维列表
        energy_data: 能量数据，二维列表
        y_type: 目标类型，默认为'EUI'
        index: 索引值，默认为0
        
    返回:
        graph_data: PyG的Data对象
    """
    # 定义列名
    name = ["Name", "ConstructionName", "ZoneName", "OutsideBoundaryCondiction", 
            "Area", "SI", "Subface", "SubfaceArea", "SubRes", "SubSHGC", "Res", 
            "Thickness", "ThermalAbsorptance", "SolarAbsorptance", "VisiblAbsorptance", "Direction"]

    #################################### 处理node特征 ####################################
    # 将二维列表转换为DataFrame
    df = pd.DataFrame(node_data)
    # 只保留前16列数据
    if df.shape[1] > len(name):
        df = df.iloc[:, :len(name)]
    
    # 设置列名
    df.columns = name
    
    # 添加ID列
    df.insert(0, 'ID', range(len(df)))
    
    # 添加EnergyFlow列（设为0，因为这是预测时不需要的）
    df['EnergyFlow'] = 0
    
    # 独热编码处理
    construction_mapping = {'exterior': 0, 'interior': 1, 'ground': 2, 'roof': 3}
    df['ConstructionName'] = df['ConstructionName'].map(construction_mapping)
    construction_onehot = pd.get_dummies(df['ConstructionName'], prefix='Construction')
    # 确保所有类别都存在
    for i in range(len(construction_mapping)):
        col_name = f'Construction_{i}'
        if col_name not in construction_onehot.columns:
            construction_onehot[col_name] = 0
    construction_onehot = construction_onehot[sorted(construction_onehot.columns)]  # 排序列名
    
    boundary_mapping = {'Outdoors': 0, 'Surface': 1, 'Ground': 2}
    df['OutsideBoundaryCondiction'] = df['OutsideBoundaryCondiction'].map(boundary_mapping)
    boundary_onehot = pd.get_dummies(df['OutsideBoundaryCondiction'], prefix='Boundary')
    # 确保所有类别都存在
    for i in range(len(boundary_mapping)):
        col_name = f'Boundary_{i}'
        if col_name not in boundary_onehot.columns:
            boundary_onehot[col_name] = 0
    boundary_onehot = boundary_onehot[sorted(boundary_onehot.columns)]
    
    subface_mapping = {0:0, 1:1, 2:2, 3:3}
    df['Subface'] = df['Subface'].map(subface_mapping)
    subface_onehot = pd.get_dummies(df['Subface'], prefix='Subface')
    # 确保所有类别都存在
    for i in range(len(subface_mapping)):
        col_name = f'Subface_{i}'
        if col_name not in subface_onehot.columns:
            subface_onehot[col_name] = 0
    subface_onehot = subface_onehot[sorted(subface_onehot.columns)]

    direction_mapping = {0:0, 1:1, 2:2, 3:3, 4:4}
    df['Direction'] = df['Direction'].map(direction_mapping)
    direction_onehot = pd.get_dummies(df['Direction'], prefix='Direction')
    # 确保所有类别都存在
    for i in range(len(direction_mapping)):
        col_name = f'Direction_{i}'
        if col_name not in direction_onehot.columns:
            direction_onehot[col_name] = 0
    direction_onehot = direction_onehot[sorted(direction_onehot.columns)]
    
    # 删除原始列并合并独热编码列
    df = df.drop(['Name', 'ZoneName', 'ConstructionName', 'OutsideBoundaryCondiction', 'Subface', 'Direction'], axis=1)
    df = pd.concat([df, construction_onehot, boundary_onehot, subface_onehot, direction_onehot], axis=1)

    # 重排列列顺序
    cols = df.columns.tolist()
    cols = ['ID'] + [col for col in cols if col != 'ID']
    df = df[cols]
    
    # 删除EnergyFlow列
    x_lable = df['EnergyFlow']
    df = df.drop(["EnergyFlow"], axis=1)

    # 转换为float类型
    df_numeric = df.drop(['ID'], axis=1)
    df_numeric = df_numeric.astype(float)
    x = torch.tensor(df_numeric.values, dtype=torch.float)

    #################################### 处理邻接矩阵 ####################################
    adj_matrix = np.array(adj_matrix)
    edge_index = convert_adj_to_edge_index(adj_matrix)

    #################################### 处理总图特征 ####################################
    if energy_data is not None:
        graph_features = pd.DataFrame(energy_data)
        if y_type == 'EUI':
            graph_features[y_type] = graph_features.sum(axis=1)
        else:
            graph_features[y_type] = graph_features.iloc[0, index]
        y = torch.tensor([graph_features[y_type].values], dtype=torch.float)
    else:
        y = torch.tensor([[0.0]], dtype=torch.float)  # 设置y为0

    #################################### 构建PyG的Data ####################################
    graph_data = Data(x=x, edge_index=edge_index, y=y)
    
    return graph_data

def convert_adj_to_edge_index(adj_matrix):
    """转换邻接矩阵为edge_index格式"""
    edges = np.where(adj_matrix == 1)
    mask = edges[0] != edges[1]
    edge_index = torch.tensor([edges[0][mask], edges[1][mask]], dtype=torch.long)
    return edge_index

def process_all_data(base_dir='data', y_type='EUI', index=0):
    """
    处理数据文件夹
    
    返回:
        tuple: (graph_data_list, failed_cases)
    """
    graph_data_list = []
    failed_cases = []
    
    try:
        graph_data = construct_graph_data(base_dir, y_type, index)
        graph_data_list.append(graph_data)
        print(f"Successfully processed {base_dir}")
    except Exception as e:
        print(f"Error processing {base_dir}: {str(e)}")
        print(f"Failed to process {base_dir}. Check if all required files are present.")
        failed_cases.append(base_dir)
    
    return graph_data_list, failed_cases

def process_pkl_data(file_path):
    """
    处理.pkl文件中的图数据
    """
    print(f"Loading data from {file_path}")
    with open(file_path, 'rb') as f:
        data_list = pickle.load(f)
    
    # 获取第一个图的数据进行详细打印
    first_graph = data_list[0]
    print("\nFeature Information:")
    print(f"Number of nodes: {first_graph.num_nodes}")
    print(f"Number of edges: {first_graph.num_edges}")
    print(f"Feature dimension: {first_graph.x.shape}")
    print(f"Feature matrix shape: {first_graph.x.shape} (nodes × features)")
    
    # 打印特征的统计信息
    feature_stats = {
        'min': first_graph.x.min(dim=0)[0],
        'max': first_graph.x.max(dim=0)[0],
        'mean': first_graph.x.mean(dim=0),
        'std': first_graph.x.std(dim=0)
    }
    
    return data_list

# 使用示例
if __name__ == "__main__":
    # 处理所有数据
    graph_data_list, failed_cases = process_all_data('data')
    print(f"Loaded {len(graph_data_list)} graphs in total")
    
    # 如果成功加载了图数据
    if len(graph_data_list) > 0:
        graph_data = graph_data_list[0]  # 获取第一个（也是唯一的）图数据
        
        # 打印数据集信息
        print(f"\nDataset Info:")
        print(f"Number of nodes: {graph_data.num_nodes}")
        print(f"Number of node features: {graph_data.num_node_features}")
        print(f"Number of edges: {graph_data.num_edges}")
        
        # 打印第一个节点的特征
        first_node_features = graph_data.x[0]
        print(f"\nFirst node features: {first_node_features}")