import torch
import numpy as np
import pandas as pd
import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

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

# 存储正在处理的请求
processing_requests = {}
processing_lock = threading.Lock()

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
    def __init__(self, model_path, node_data, adj_matrix, energy_data, explainer_epochs=50):
        """
        初始化GCN解释器
        
        参数:
            model_path: 模型路径
            node_data: 节点数据
            adj_matrix: 邻接矩阵
            energy_data: 能量数据路径
            explainer_epochs: GNNExplainer的训练轮数，默认50（减少以提高速度）
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
        print(f"[EXPLAIN] 注意: GNNExplainer 正在训练中，请耐心等待...")
        explainer_start = time.time()
        heartbeat_interval = 10.0  # 每10秒输出一次心跳
        
        # 使用线程来输出心跳（因为GNNExplainer是阻塞的）
        import threading
        import sys
        
        heartbeat_stop = threading.Event()
        
        def heartbeat():
            """定期输出心跳日志"""
            while not heartbeat_stop.is_set():
                if heartbeat_stop.wait(heartbeat_interval):
                    break  # 如果事件被设置，退出循环
                elapsed = time.time() - explainer_start
                print(f"[EXPLAIN] GNNExplainer 仍在运行中... (已耗时: {elapsed:.1f} 秒)")
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
            print(f"[EXPLAIN] GNNExplainer 完成！耗时: {explainer_time:.2f} 秒 ({explainer_time/60:.2f} 分钟)")
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
        
        # 创建节点特征重要性DataFrame
        node_feature_importance = []
        node_start_time = time.time()
        total_node_feature_ops = num_nodes * num_features
        
        for node_idx in range(num_nodes):
            progress_interval = max(1, num_nodes // 10) if num_nodes > 0 else 1
            if (node_idx + 1) % progress_interval == 0 or node_idx == 0:
                elapsed = time.time() - node_start_time
                progress = (node_idx + 1) / num_nodes * 100 if num_nodes > 0 else 0
                print(f"[EXPLAIN] 节点特征处理进度: {node_idx + 1}/{num_nodes} ({progress:.1f}%), 已耗时: {elapsed:.2f} 秒")
            
            node_importance = {}
            node_importance['Node_ID'] = node_idx
            
            for feat_idx, feat_name in enumerate(feature_names):
                # 计算特征的原始值
                original_value = data.x[node_idx, feat_idx].item()
                
                # 简化扰动分析（减少计算量）
                # 只使用一个中等大小的扰动，而不是多个
                perturbation_scale = 0.1  # 只使用一个扰动比例
                
                # 正向扰动
                perturbed_data = data.clone()
                epsilon = perturbation_scale * abs(original_value) if original_value != 0 else perturbation_scale
                perturbed_data.x[node_idx, feat_idx] += epsilon
                pos_prediction = self._get_prediction(perturbed_data)
                pos_impact = (pos_prediction - original_prediction) / epsilon if epsilon != 0 else 0
                
                # 负向扰动
                perturbed_data = data.clone()
                perturbed_data.x[node_idx, feat_idx] -= epsilon
                neg_prediction = self._get_prediction(perturbed_data)
                neg_impact = (original_prediction - neg_prediction) / epsilon if epsilon != 0 else 0
                
                # 取平均影响
                avg_impact = (pos_impact + neg_impact) / 2
                importance = avg_impact * node_mask[node_idx][0] * original_value
                
                node_importance[feat_name] = importance
            
            node_feature_importance.append(node_importance)
        
        node_time = time.time() - node_start_time
        print(f"[EXPLAIN] 节点特征重要性处理完成，耗时: {node_time:.2f} 秒")
        
        # 转换为DataFrame
        print(f"[EXPLAIN] 步骤5: 转换为 DataFrame...")
        node_importance_df = pd.DataFrame(node_feature_importance)
        print(f"[EXPLAIN] 节点重要性 DataFrame 形状: {node_importance_df.shape}")
        
        # 处理边的重要性
        print(f"[EXPLAIN] 步骤6: 处理边的重要性...")
        edge_mask = explanation.edge_mask.cpu().detach().numpy()
        edge_importance_matrix = np.zeros((num_nodes, num_nodes))
        
        # 将边的重要性转换为邻接矩阵格式
        edge_index = data.edge_index.cpu().numpy()
        edge_start_time = time.time()
        
        for i, (src, dst) in enumerate(edge_index.T):
            progress_interval = max(1, num_edges // 10) if num_edges > 0 else 1
            if (i + 1) % progress_interval == 0 or i == 0:
                elapsed = time.time() - edge_start_time
                progress = (i + 1) / num_edges * 100 if num_edges > 0 else 0
                print(f"[EXPLAIN] 边重要性处理进度: {i + 1}/{num_edges} ({progress:.1f}%), 已耗时: {elapsed:.2f} 秒")
            
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
        
        edge_time = time.time() - edge_start_time
        print(f"[EXPLAIN] 边重要性处理完成，耗时: {edge_time:.2f} 秒")
        
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
        
        # 检查是否是 explain 请求，如果是则检查是否已有相同请求在处理
        need_explain = data.get('explain', False)
        if need_explain:
            request_hash = get_request_hash(data)
            with processing_lock:
                if request_hash in processing_requests:
                    existing_start_time = processing_requests[request_hash]
                    elapsed = time.time() - existing_start_time
                    print(f"[PREDICT] 检测到重复的 explain 请求 (hash: {request_hash[:8]}...), 已有请求正在处理中 (已运行: {elapsed:.1f} 秒)")
                    return jsonify({
                        'error': '相同的解释请求正在处理中，请勿重复提交',
                        'request_hash': request_hash[:8],
                        'processing_time': elapsed
                    }), 429  # 429 Too Many Requests
                else:
                    processing_requests[request_hash] = time.time()
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
                
                # 从请求中获取explainer_epochs，如果没有则使用默认值50
                explainer_epochs = data.get('explainer_epochs', 50)
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
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"Error in explanation: {str(e)}")
                print(f"Traceback: {error_trace}")
                # 如果解释失败，仍然返回预测结果，但添加解释错误信息
                result['explanation_error'] = str(e)
        
            return jsonify(result)
        finally:
            # 清理请求记录
            if request_id and need_explain:
                with processing_lock:
                    if request_id in processing_requests:
                        elapsed = time.time() - processing_requests[request_id]
                        del processing_requests[request_id]
                        print(f"[PREDICT] 完成 explain 请求 (hash: {request_id[:8]}...), 总耗时: {elapsed:.2f} 秒")
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in predict endpoint: {str(e)}")
        print(f"Traceback: {error_trace}")
        
        # 清理请求记录（即使出错也要清理）
        if request_id and need_explain:
            with processing_lock:
                if request_id in processing_requests:
                    del processing_requests[request_id]
                    print(f"[PREDICT] 清理失败的 explain 请求 (hash: {request_id[:8]}...)")
        
        # 在生产环境中，只返回错误信息，不返回完整的 traceback
        return jsonify({'error': str(e)}), 500

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