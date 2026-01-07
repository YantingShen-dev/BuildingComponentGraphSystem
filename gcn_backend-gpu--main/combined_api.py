import torch
import numpy as np
import pandas as pd
import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

from GCN9 import GCN
from GraphDataConstruct import construct_graph_data
from GraphDataConstruct_explain import construct_graph_data as construct_graph_data_explain
from torch_geometric.explain import GNNExplainer, Explainer
from torch_geometric.loader import DataLoader

app = Flask(__name__)

# 配置 CORS - 允许所有来源（flask-cors 会自动处理所有 CORS 头）
CORS(app, 
     origins="*",
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=False,
     expose_headers=None,
     max_age=None)

# 请求去重机制：防止重复的 explain 请求
import threading
from collections import defaultdict
from hashlib import md5
import json

# 存储正在处理的请求和最近完成的请求（用于去重）
processing_requests = {}
completed_requests = {}  # 存储最近完成的请求，避免短时间内重复处理
processing_lock = threading.Lock()
COMPLETED_REQUEST_RETENTION = 300  # 完成的请求保留5分钟，避免重复处理

def get_request_hash(data):
    """生成请求的唯一哈希值"""
    # 只使用关键数据生成哈希，忽略时间戳等变化的数据
    key_data = {
        'node_data': data.get('node_data'),
        'adj_matrix': data.get('adj_matrix'),
        'explain': data.get('explain', False)
    }
    key_str = json.dumps(key_data, sort_keys=True)
    return md5(key_str.encode()).hexdigest()

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
    def __init__(self, model_path, node_data, adj_matrix, energy_data, explainer_epochs=5):
        """
        初始化GCN解释器
        
        参数:
            model_path: 模型路径
            node_data: 节点数据
            adj_matrix: 邻接矩阵
            energy_data: 能量数据路径
            explainer_epochs: GNNExplainer的训练轮数，默认5（减少以提高速度）
        """
        self.device = torch.device('cpu')
        self.explainer_epochs = explainer_epochs
        
        # 直接使用提供的数据
        energy_path = energy_data
        
        # 加载数据和模型
        print(f"[GCNExplainer.__init__] 开始构建图数据...")
        graph_data_start = time.time()
        self.graph_data = construct_graph_data_explain(node_data, adj_matrix, energy_path, 'Heating', 0)
        graph_data_time = time.time() - graph_data_start
        print(f"[GCNExplainer.__init__] 图数据构建完成，耗时: {graph_data_time:.2f} 秒")
        print(f"[GCNExplainer.__init__] 图数据: {self.graph_data.num_nodes} 节点, {self.graph_data.num_edges} 边, {self.graph_data.num_node_features} 特征")
        
        print(f"[GCNExplainer.__init__] 创建模型实例...")
        self.model = GCN(self.graph_data.num_node_features).to(self.device)
        
        print(f"[GCNExplainer.__init__] 加载模型权重: {model_path}")
        model_load_start = time.time()
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'), weights_only=False))
        model_load_time = time.time() - model_load_start
        print(f"[GCNExplainer.__init__] 模型权重加载完成，耗时: {model_load_time:.2f} 秒")
        
        self.model.eval()
        print(f"[GCNExplainer.__init__] 模型设置为评估模式")
        
        # 初始化GNNExplainer（使用可配置的epochs）
        print(f"[GCNExplainer.__init__] 初始化 GNNExplainer (epochs={self.explainer_epochs})...")
        explainer_init_start = time.time()
        self.explainer = Explainer(
            model=self.model,
            algorithm=GNNExplainer(epochs=self.explainer_epochs),
            explanation_type='model',
            edge_mask_type='object',
            node_mask_type='object',
            model_config=dict(
                mode='regression',
                task_level='graph',
                return_type='raw'
            )
        )
        explainer_init_time = time.time() - explainer_init_start
        print(f"[GCNExplainer.__init__] GNNExplainer 初始化完成，耗时: {explainer_init_time:.2f} 秒")
        print(f"[GCNExplainer.__init__] 解释器准备就绪")

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
        start_time = time.time()
        print(f"[EXPLAIN] 开始解释过程，时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 获取数据
        print(f"[EXPLAIN] 步骤1: 准备图数据...")
        data = self.graph_data.to(self.device)
        num_nodes = data.x.size(0)
        num_edges = data.edge_index.size(1)
        num_features = len(feature_names)
        print(f"[EXPLAIN] 图数据信息: {num_nodes} 个节点, {num_edges} 条边, {num_features} 个特征")
        
        print(f"[EXPLAIN] 步骤2: 计算原始预测值...")
        original_prediction = self._get_prediction(data)
        print(f"[EXPLAIN] 原始预测值: {original_prediction:.6f}")
        
        # 获取解释
        print(f"[EXPLAIN] 步骤3: 调用 GNNExplainer (epochs={self.explainer_epochs}, 这可能需要较长时间)...")
        print(f"[EXPLAIN] ========================================")
        print(f"[EXPLAIN] GNNExplainer 工作原理说明:")
        print(f"[EXPLAIN] - GNNExplainer 通过优化节点掩码和边掩码来解释模型预测")
        print(f"[EXPLAIN] - 每个 epoch 会:")
        print(f"[EXPLAIN]   1. 前向传播: 使用当前掩码计算预测")
        print(f"[EXPLAIN]   2. 计算损失: 比较掩码后的预测与原始预测")
        print(f"[EXPLAIN]   3. 反向传播: 更新掩码参数以最小化损失")
        print(f"[EXPLAIN] - 训练 {self.explainer_epochs} 个 epochs 以找到最佳解释掩码")
        print(f"[EXPLAIN] - 计算复杂度: O(epochs × (nodes + edges) × features)")
        print(f"[EXPLAIN]   估算: {self.explainer_epochs} × ({num_nodes} + {num_edges}) × {num_features} ≈ {self.explainer_epochs * (num_nodes + num_edges) * num_features} 次操作")
        print(f"[EXPLAIN] ========================================")
        print(f"[EXPLAIN] 开始训练，请耐心等待...")
        explainer_start = time.time()
        heartbeat_interval = 10.0  # 每10秒输出一次心跳
        
        # 使用线程来输出心跳（因为GNNExplainer是阻塞的）
        import threading
        import sys
        import os
        
        # 尝试导入 psutil 用于系统资源监控
        try:
            import psutil
            HAS_PSUTIL = True
        except ImportError:
            HAS_PSUTIL = False
            print(f"[EXPLAIN] 警告: psutil 未安装，将无法显示系统资源信息")
        
        heartbeat_stop = threading.Event()
        heartbeat_count = 0
        
        def heartbeat():
            """定期输出心跳日志，包含系统资源信息"""
            nonlocal heartbeat_count
            while not heartbeat_stop.is_set():
                if heartbeat_stop.wait(heartbeat_interval):
                    break  # 如果事件被设置，退出循环
                heartbeat_count += 1
                elapsed = time.time() - explainer_start
                
                # 估算剩余时间和当前epoch进度
                remaining_str = ""
                estimated_epoch = 1
                if heartbeat_count > 0:
                    # 基于已用时间估算总时间（假设线性关系）
                    avg_time_per_heartbeat = elapsed / heartbeat_count
                    # 粗略估算：每个epoch大约需要相同时间
                    # 假设每10秒完成约1个epoch（这个估算可能不准确，但可以给用户一个参考）
                    estimated_epoch_time = 10.0  # 假设每个epoch需要10秒
                    estimated_total = estimated_epoch_time * self.explainer_epochs
                    remaining = max(0, estimated_total - elapsed)
                    remaining_str = f", 估算剩余: {remaining:.1f} 秒"
                    
                    # 估算当前epoch进度
                    estimated_epoch = min(self.explainer_epochs, int(elapsed / estimated_epoch_time) + 1)
                
                print(f"[EXPLAIN] GNNExplainer 训练中... (已耗时: {elapsed:.1f} 秒{remaining_str})")
                print(f"[EXPLAIN]   当前阶段: 优化节点和边掩码 (估算 epoch {estimated_epoch}/{self.explainer_epochs})")
                
                # 获取系统资源信息（如果可用）
                if HAS_PSUTIL:
                    try:
                        process = psutil.Process(os.getpid())
                        cpu_percent = process.cpu_percent(interval=0.1)
                        memory_info = process.memory_info()
                        memory_mb = memory_info.rss / 1024 / 1024
                        print(f"[EXPLAIN]   系统资源: CPU={cpu_percent:.1f}%, 内存={memory_mb:.1f}MB")
                    except Exception as e:
                        pass  # 忽略资源获取错误
                
                sys.stdout.flush()  # 强制刷新输出
        
        heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
        heartbeat_thread.start()
        
        try:
            explanation = self.explainer(
                x=data.x,
                edge_index=data.edge_index,
                batch=torch.zeros(data.x.size(0), dtype=torch.long, device=self.device)
            )
            heartbeat_stop.set()  # 停止心跳
            explainer_time = time.time() - explainer_start
            print(f"[EXPLAIN] ========================================")
            print(f"[EXPLAIN] GNNExplainer 训练完成！")
            print(f"[EXPLAIN] 总耗时: {explainer_time:.2f} 秒 ({explainer_time/60:.2f} 分钟)")
            print(f"[EXPLAIN] 平均每个 epoch 耗时: {explainer_time/self.explainer_epochs:.2f} 秒")
            
            # 获取解释结果的基本信息
            try:
                node_mask_sum = explanation.node_mask.sum().item()
                edge_mask_sum = explanation.edge_mask.sum().item()
                node_mask_mean = explanation.node_mask.mean().item()
                edge_mask_mean = explanation.edge_mask.mean().item()
                print(f"[EXPLAIN] 解释结果统计:")
                print(f"[EXPLAIN]   - 节点掩码: 总和={node_mask_sum:.4f}, 均值={node_mask_mean:.4f}")
                print(f"[EXPLAIN]   - 边掩码: 总和={edge_mask_sum:.4f}, 均值={edge_mask_mean:.4f}")
            except Exception as e:
                print(f"[EXPLAIN] 无法获取解释结果统计: {str(e)}")
            
            print(f"[EXPLAIN] ========================================")
        except Exception as e:
            heartbeat_stop.set()  # 停止心跳
            import traceback
            error_trace = traceback.format_exc()
            explainer_time = time.time() - explainer_start
            print(f"[EXPLAIN] GNNExplainer 失败 (已耗时: {explainer_time:.2f} 秒): {str(e)}")
            print(f"[EXPLAIN] Traceback: {error_trace}")
            raise
        
        # 获取节点数量
        print(f"[EXPLAIN] 步骤4: 处理节点特征重要性...")
        node_mask = explanation.node_mask.cpu().detach().numpy()
        print(f"[EXPLAIN] 节点掩码形状: {node_mask.shape}")
        
        # 创建节点特征重要性DataFrame（优化版本：直接使用掩码值，减少计算）
        print(f"[EXPLAIN] 使用快速模式计算节点特征重要性（基于掩码值，无需扰动计算）...")
        node_feature_importance = []
        node_start_time = time.time()
        
        # 获取节点掩码值（用于加权）
        node_mask_values = node_mask.flatten() if len(node_mask.shape) > 1 else node_mask
        
        for node_idx in range(num_nodes):
            progress_interval = max(1, num_nodes // 10) if num_nodes > 0 else 1
            if (node_idx + 1) % progress_interval == 0 or node_idx == 0:
                elapsed = time.time() - node_start_time
                progress = (node_idx + 1) / num_nodes * 100 if num_nodes > 0 else 0
                print(f"[EXPLAIN] 节点特征处理进度: {node_idx + 1}/{num_nodes} ({progress:.1f}%), 已耗时: {elapsed:.2f} 秒")
            
            node_importance = {}
            node_importance['Node_ID'] = node_idx
            
            # 获取该节点的掩码值
            node_mask_value = node_mask_values[node_idx] if node_idx < len(node_mask_values) else 1.0
            
            for feat_idx, feat_name in enumerate(feature_names):
                # 计算特征的原始值
                original_value = data.x[node_idx, feat_idx].item()
                
                # 快速模式：直接使用掩码值和特征值的乘积作为重要性
                # 这比扰动方法快得多，同时仍然能反映特征的重要性
                importance = node_mask_value * original_value
                
                node_importance[feat_name] = importance
            
            node_feature_importance.append(node_importance)
        
        node_time = time.time() - node_start_time
        print(f"[EXPLAIN] 节点特征重要性处理完成，耗时: {node_time:.2f} 秒")
        
        # 转换为DataFrame
        print(f"[EXPLAIN] 步骤5: 转换为 DataFrame...")
        node_importance_df = pd.DataFrame(node_feature_importance)
        print(f"[EXPLAIN] 节点重要性 DataFrame 形状: {node_importance_df.shape}")
        
        # 处理边的重要性（优化版本：直接使用掩码值，无需删除边重新计算）
        print(f"[EXPLAIN] 步骤6: 处理边的重要性（快速模式：直接使用掩码值）...")
        edge_mask = explanation.edge_mask.cpu().detach().numpy()
        edge_importance_matrix = np.zeros((num_nodes, num_nodes))
        
        # 将边的重要性转换为邻接矩阵格式
        edge_index = data.edge_index.cpu().numpy()
        edge_start_time = time.time()
        
        # 快速模式：直接使用边掩码值，乘以原始预测值作为重要性
        # 这比删除每条边重新计算快得多
        for i, (src, dst) in enumerate(edge_index.T):
            if i < len(edge_mask):
                # 直接使用掩码值作为重要性（可以乘以原始预测值作为缩放因子）
                importance = edge_mask[i] * abs(original_prediction)
                
                # 保存到邻接矩阵（保持对称性）
                edge_importance_matrix[src][dst] = importance
                edge_importance_matrix[dst][src] = importance
        
        edge_time = time.time() - edge_start_time
        print(f"[EXPLAIN] 边重要性处理完成，处理了 {num_edges} 条边，耗时: {edge_time:.2f} 秒")
        
        total_time = time.time() - start_time
        print(f"[EXPLAIN] 解释过程全部完成！总耗时: {total_time:.2f} 秒")
        print(f"[EXPLAIN] 时间分解: Explainer={explainer_time:.2f}s, 节点特征={node_time:.2f}s, 边={edge_time:.2f}s")
        
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
        print(f"Successfully constructed graph data: {graph_data.num_nodes} nodes, {graph_data.num_node_features} features")
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error constructing graph data: {str(e)}")
        print(f"Traceback: {error_trace}")
        return None, str(e)

    # 创建模型实例
    model = GCN(graph_data.num_node_features).to(device)

    # 加载训练好的模型参数
    try:
        if not os.path.exists(model_path):
            error_msg = f"Model file not found: {model_path}"
            print(error_msg)
            return None, error_msg
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        print(f"Successfully loaded model from {model_path}")
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error loading model: {str(e)}")
        print(f"Traceback: {error_trace}")
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
    request_id = None
    need_explain = False
    try:
        # 获取请求数据
        data = request.get_json()
        
        if data is None:
            print("Error: Request body is empty or not valid JSON")
            return jsonify({'error': 'Request body is empty or not valid JSON'}), 400
        
        # 检查是否是 explain 请求，如果是则检查是否已有相同请求在处理或最近完成
        need_explain = data.get('explain', False)
        if need_explain:
            request_hash = get_request_hash(data)
            current_time = time.time()
            
            with processing_lock:
                # 清理过期的已完成请求记录
                expired_hashes = [h for h, t in completed_requests.items() 
                                 if current_time - t > COMPLETED_REQUEST_RETENTION]
                for h in expired_hashes:
                    del completed_requests[h]
                
                # 检查是否正在处理
                if request_hash in processing_requests:
                    existing_start_time = processing_requests[request_hash]
                    elapsed = current_time - existing_start_time
                    print(f"[PREDICT] 检测到重复的 explain 请求 (hash: {request_hash[:8]}...), 已有请求正在处理中 (已运行: {elapsed:.1f} 秒)")
                    return jsonify({
                        'error': '相同的解释请求正在处理中，请勿重复提交',
                        'request_hash': request_hash[:8],
                        'processing_time': elapsed,
                        'status': 'processing'
                    }), 429  # 429 Too Many Requests
                
                # 检查是否最近完成（5分钟内）
                elif request_hash in completed_requests:
                    completed_time = completed_requests[request_hash]
                    elapsed_since_completion = current_time - completed_time
                    print(f"[PREDICT] 检测到重复的 explain 请求 (hash: {request_hash[:8]}...), 该请求在 {elapsed_since_completion:.1f} 秒前已完成")
                    return jsonify({
                        'error': '相同的解释请求在最近已完成，请勿重复提交',
                        'request_hash': request_hash[:8],
                        'completed_time': elapsed_since_completion,
                        'status': 'recently_completed',
                        'message': f'该请求在 {int(elapsed_since_completion)} 秒前已完成，请等待至少 {COMPLETED_REQUEST_RETENTION} 秒后重试'
                    }), 429  # 429 Too Many Requests
                
                # 新请求，开始处理
                else:
                    processing_requests[request_hash] = current_time
                    request_id = request_hash
                    print(f"[PREDICT] 开始处理新的 explain 请求 (hash: {request_id[:8]}...)")
        
        # 检查必要字段
        if not all(key in data for key in ['node_data', 'adj_matrix']):
            print(f"Error: Missing required fields. Received keys: {list(data.keys()) if data else 'None'}")
            return jsonify({'error': 'Missing required fields: node_data and adj_matrix'}), 400
        
        # 验证数据格式
        if not isinstance(data['node_data'], list) or not isinstance(data['adj_matrix'], list):
            print(f"Error: Invalid data types. node_data type: {type(data['node_data'])}, adj_matrix type: {type(data['adj_matrix'])}")
            return jsonify({'error': 'node_data and adj_matrix must be lists'}), 400
        
        print(f"Received predict request: {len(data['node_data'])} nodes, {len(data['adj_matrix'])}x{len(data['adj_matrix'][0]) if data['adj_matrix'] else 0} adj matrix")
            
        # 获取数据
        node_data = data['node_data']
        adj_matrix = data['adj_matrix']
        energy_data = data.get('energy_data')  # 使用get方法获取可选参数
        # need_explain 已在上面定义，这里不需要重复定义
        
        # 设置模型路径
        MODEL_PATH = "model/energy_merged_EUIGCN9.pth"
        
        # 保存 energy_path 用于解释器（解释器需要文件路径）
        energy_path_for_explainer = None
        
        # 如果需要能源数据但未提供
        if energy_data is None:
            # 使用默认数据文件夹中的能源数据
            try:
                data_dir = os.path.join("input", "0")
                _, _, energy_path = read_data_from_dir(data_dir)
                # 保存路径用于解释器
                energy_path_for_explainer = energy_path
                # 读取文件内容用于预测（construct_graph_data 需要列表）
                if os.path.exists(energy_path):
                    energy_data = pd.read_excel(energy_path, header=None).values.tolist()
                else:
                    print(f"Warning: Energy file not found at {energy_path}")
                    energy_data = None
            except Exception as e:
                print(f"Warning: Could not load default energy data: {str(e)}")
                energy_data = None
                # 即使读取失败，也尝试使用默认路径
                try:
                    data_dir = os.path.join("input", "0")
                    energy_path_for_explainer = os.path.join(data_dir, 'energy_sum.xlsx')
                except:
                    pass
        
        # 进行预测
        prediction, error = predict_single_sample(MODEL_PATH, node_data, adj_matrix, energy_data)
        
        if prediction is None:
            return jsonify({'error': f'Prediction failed: {error}'}), 500
        
        result = {'prediction': prediction}
        
        # 如果需要解释（默认禁用，因为计算量太大可能导致超时）
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
                
                # 确定用于解释器的 energy_path
                # 如果 energy_path_for_explainer 未设置，尝试使用默认路径
                if energy_path_for_explainer is None:
                    try:
                        data_dir = os.path.join("input", "0")
                        energy_path_for_explainer = os.path.join(data_dir, 'energy_sum.xlsx')
                        if not os.path.exists(energy_path_for_explainer):
                            raise FileNotFoundError(f"Energy file not found: {energy_path_for_explainer}")
                    except Exception as e:
                        print(f"Warning: Could not determine energy path for explainer: {str(e)}")
                        raise Exception(f"Cannot create explainer: energy file path not available. {str(e)}")
                
                print(f"[PREDICT] 创建解释器，energy_path: {energy_path_for_explainer}")
                print(f"[PREDICT] 节点数据: {len(node_data)} 行, 邻接矩阵: {len(adj_matrix)}x{len(adj_matrix[0]) if adj_matrix else 0}")
                
                # 从请求中获取explainer_epochs，如果没有则使用默认值5（优化速度）
                explainer_epochs = data.get('explainer_epochs', 5)
                print(f"[PREDICT] 使用 GNNExplainer epochs: {explainer_epochs}")
                
                # 创建解释器实例（需要文件路径，不是列表）
                explainer_start = time.time()
                try:
                    explainer = GCNExplainer(MODEL_PATH, node_data, adj_matrix, energy_path_for_explainer, explainer_epochs=explainer_epochs)
                    explainer_init_time = time.time() - explainer_start
                    print(f"[PREDICT] 解释器创建成功，耗时: {explainer_init_time:.2f} 秒")
                except Exception as e:
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"[PREDICT] 解释器创建失败: {str(e)}")
                    print(f"[PREDICT] Traceback: {error_trace}")
                    raise
                
                # 获取解释结果
                print("[PREDICT] 开始解释过程...")
                explain_start = time.time()
                try:
                    node_importance, edge_matrix, _ = explainer.explain_and_save(feature_names=feature_names)
                    explain_time = time.time() - explain_start
                    print(f"[PREDICT] 解释完成，耗时: {explain_time:.2f} 秒")
                except Exception as e:
                    import traceback
                    error_trace = traceback.format_exc()
                    explain_time = time.time() - explain_start
                    print(f"[PREDICT] 解释过程失败，已耗时: {explain_time:.2f} 秒")
                    print(f"[PREDICT] 错误: {str(e)}")
                    print(f"[PREDICT] Traceback: {error_trace}")
                    raise
                
                # 添加到结果中
                result['explanation'] = {
                    'node_importance': node_importance.to_dict(),
                    'edge_matrix': edge_matrix.tolist()
                }
                print(f"[PREDICT] 解释结果已添加到响应中")
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"Error in explanation: {str(e)}")
                print(f"Traceback: {error_trace}")
                # 如果解释失败，仍然返回预测结果，但添加解释错误信息
                result['explanation_error'] = str(e)
        
        # 返回结果（无论是否需要解释）
        try:
            # 估算响应大小
            result_str = json.dumps(result)
            result_size_kb = len(result_str.encode('utf-8')) / 1024
            print(f"[PREDICT] 准备返回响应，数据大小: {result_size_kb:.2f} KB")
            print(f"[PREDICT] 响应包含: prediction={('prediction' in result)}, explanation={('explanation' in result)}")
        except Exception as e:
            print(f"[PREDICT] 无法估算响应大小: {str(e)}")
        
        response = jsonify(result)
        print(f"[PREDICT] 响应已创建，准备发送给客户端...")
        return response
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in predict endpoint: {str(e)}")
        print(f"Traceback: {error_trace}")
        
        # 在生产环境中，只返回错误信息，不返回完整的 traceback
        return jsonify({'error': str(e)}), 500
    finally:
        # 清理请求记录（无论成功还是失败都要清理）
        if request_id and need_explain:
            with processing_lock:
                if request_id in processing_requests:
                    elapsed = time.time() - processing_requests[request_id]
                    del processing_requests[request_id]
                    # 将完成的请求添加到已完成列表，保留一段时间避免重复处理
                    completed_requests[request_id] = time.time()
                    print(f"[PREDICT] 完成 explain 请求 (hash: {request_id[:8]}...), 总耗时: {elapsed:.2f} 秒")
                    print(f"[PREDICT] 请求记录已移至已完成列表，将保留 {COMPLETED_REQUEST_RETENTION} 秒以避免重复处理")

@app.route('/optimize', methods=['OPTIONS', 'POST'])
def proxy_optimize():
    """
    代理优化请求到优化服务
    如果设置了 OPTIMIZATION_API_URL 环境变量，则转发到该服务
    否则返回错误提示
    """
    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With, Accept, Origin")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        return response
    
    # 获取优化服务的 URL（从环境变量或使用默认值）
    optimization_url = os.environ.get('OPTIMIZATION_API_URL', 'http://localhost:5001')
    
    if optimization_url == 'http://localhost:5001':
        # 如果使用默认值，说明没有配置优化服务 URL
        return jsonify({
            'success': False,
            'error': '优化服务未配置。请设置 OPTIMIZATION_API_URL 环境变量，或在 Vercel 中配置 VITE_API_URL_OPT 指向优化服务。'
        }), 503
    
    try:
        # 获取原始请求数据
        data = request.get_json()
        
        # 转发请求到优化服务
        opt_service_url = f"{optimization_url}/optimize"
        print(f"[PROXY] 转发优化请求到: {opt_service_url}")
        
        response = requests.post(
            opt_service_url,
            json=data,
            timeout=600,  # 10分钟超时
            headers={
                'Content-Type': 'application/json',
                'Origin': request.headers.get('Origin', '*')
            }
        )
        
        # 返回优化服务的响应
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'error': f'无法连接到优化服务: {optimization_url}。请确保优化服务正在运行。'
        }), 503
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': '优化请求超时。优化过程可能需要较长时间。'
        }), 504
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[PROXY] 代理优化请求失败: {str(e)}")
        print(f"[PROXY] Traceback: {error_trace}")
        return jsonify({
            'success': False,
            'error': f'代理请求失败: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """健康检查端点"""
    try:
        # 检查模型文件是否存在
        MODEL_PATH = "model/energy_merged_EUIGCN9.pth"
        model_exists = os.path.exists(MODEL_PATH)
        
        # 检查输入数据目录
        input_dir = os.path.join("input", "0")
        input_exists = os.path.exists(input_dir)
        
        return jsonify({
            'status': 'healthy',
            'model_exists': model_exists,
            'model_path': MODEL_PATH,
            'input_dir_exists': input_exists,
            'input_dir': input_dir
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port) 