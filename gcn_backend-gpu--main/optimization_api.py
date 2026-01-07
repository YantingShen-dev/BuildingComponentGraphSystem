import torch
from GCN9 import GCN
from GraphDataConstruct import construct_graph_data
from torch_geometric.loader import DataLoader
import pandas as pd
import os
from deap import base, creator, tools, algorithms
import random
import numpy as np

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

def read_and_convert_excel(file_path, sheet_name=None):
    
    value_name = ['Con','SCon','SA','SSHGC','Price']
    try:
        df = pd.read_excel(file_path, sheet_name=0)
        if 'ID' in df.columns:
            df['ID'] = df['ID'].astype(int)
        for value in value_name:
            if value in df.columns:
                df[value] = df[value].astype(float)
        return df
    except Exception as e:
        print(f"Error reading and converting Excel file {file_path}: {str(e)}")
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
    # print(f"Using device: {device}")

    # 构建单个样本的图数据
    try:
        graph_data = construct_graph_data(node_data, adj_matrix, energy_data, 'EUI', 0)
        # print("Successfully constructed graph data")
        # print(f"Number of nodes: {graph_data.num_nodes}")
        # print(f"Number of node features: {graph_data.num_node_features}")
    except Exception as e:
        print(f"Error constructing graph data: {str(e)}")
        return

    # 创建模型实例
    model = GCN(graph_data.num_node_features).to(device)

    # 加载训练好的模型参数
    try:
        model.load_state_dict(torch.load(model_path,map_location=device))
        # print(f"Successfully loaded model from {model_path}")
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
            
            # print("\nPrediction Results:")
            # print(f"Predicted value: {prediction.item():.4f}")
            return prediction.item()


def NSGAII_optimization(model_path, node_data, adj_matrix, energy_data, wall_type, population_size, generations, stream_callback=None):

    MATERIAL_PATH = os.path.join('materials')
    door_data = read_and_convert_excel(os.path.join(MATERIAL_PATH, 'door.xlsx'))
    window_data = read_and_convert_excel(os.path.join(MATERIAL_PATH, 'window.xlsx'))
    face_data = read_and_convert_excel(os.path.join(MATERIAL_PATH, 'face.xlsx'))
    heatPreserve_data = read_and_convert_excel(os.path.join(MATERIAL_PATH, 'heatPreserve.xlsx'))
    wall_data = read_and_convert_excel(os.path.join(MATERIAL_PATH, 'wall_select.xlsx'))

    # 1. 定义问题类型
    if not hasattr(creator, "FitnessMin"):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMin)

    # 2. 初始化工具箱
    toolbox = base.Toolbox()

    # 3. 定义参数范围
    DOOR_TYPE_COUNT = len(door_data)
    WINDOW_TYPE_COUNT = len(window_data)
    FACE_TYPE_COUNT = len(face_data)
    HEATPRESERVE_TYPE_COUNT = len(heatPreserve_data)
    THICKNESS_MAX = 0.2
    THICKNESS_MIN = 0.01
    NUM_INDIVIDUALS = len(node_data)

    # 4. 定义混合个体结构
    def create_individual():
        individual = []
        for i in range(NUM_INDIVIDUALS):
            # 每个构件的基本参数：保温层厚度（连续），面层材料id（离散），保温材料id（离散）
            thickness = random.uniform(THICKNESS_MIN, THICKNESS_MAX)  # 保温层厚度
            face_material_id = random.randint(0, FACE_TYPE_COUNT - 1)  # 面层材料id
            heat_preserve_id = random.randint(0, HEATPRESERVE_TYPE_COUNT - 1)  # 保温材料id
            
            individual.extend([thickness, face_material_id, heat_preserve_id])
            
            # 检查node_data中第7个值（索引6），决定是否需要门窗材料
            wall_type = node_data[i][6]  # 第7个值，索引为6
            
            if wall_type == 0:
                # 没有门窗，不添加额外参数
                pass
            elif wall_type == 1:
                # 只有窗户
                window_material_id = random.randint(0, WINDOW_TYPE_COUNT - 1)
                individual.append(window_material_id)
            elif wall_type == 2:
                # 只有门
                door_material_id = random.randint(0, DOOR_TYPE_COUNT - 1)
                individual.append(door_material_id)
            elif wall_type == 3:
                # 既有门又有窗
                window_material_id = random.randint(0, WINDOW_TYPE_COUNT - 1)
                door_material_id = random.randint(0, DOOR_TYPE_COUNT - 1)
                individual.extend([window_material_id, door_material_id])
        
        return individual
    
    # 5. 创建构件索引映射字典
    def create_component_index_map():
        """
        创建构件索引映射字典，用于快速定位每个构件在individual中的位置
        返回: {构件索引: (起始位置, 结束位置)}
        """
        index_map = {}
        current_pos = 0
        
        for i in range(NUM_INDIVIDUALS):
            start_pos = current_pos
            # 基本参数：厚度 + 面层材料ID + 保温材料ID = 3个
            current_pos += 3
            
            # 根据wall_type添加额外参数
            wall_type = node_data[i][6]  # 第7个值，索引为6
            
            if wall_type == 0:
                # 没有门窗，不添加额外参数
                pass
            elif wall_type == 1:
                # 只有窗户，+1个参数
                current_pos += 1
            elif wall_type == 2:
                # 只有门，+1个参数
                current_pos += 1
            elif wall_type == 3:
                # 既有门又有窗，+2个参数
                current_pos += 2
            
            end_pos = current_pos
            index_map[i] = (start_pos, end_pos)
        
        return index_map
    
    # 创建索引映射
    component_index_map = create_component_index_map()

    # 6. 定义评估函数
    def evaluate(individual):

        updated_node_data = [row[:] for row in node_data]

        total_energy = 0
        total_cost = 0

        for i in range(NUM_INDIVIDUALS):
            start_pos, end_pos = component_index_map[i]

            # 获取构件各个材料id
            thickness = individual[start_pos]
            face_material_id = individual[start_pos + 1]
            heat_preserve_id = individual[start_pos + 2]
            if node_data[i][6] == 0: # 没有门窗
                pass
            elif node_data[i][6] == 1: # 只有窗户
                window_material_id = individual[start_pos + 3]
            elif node_data[i][6] == 2: # 只有门
                door_material_id = individual[start_pos + 3]
            elif node_data[i][6] == 3: # 既有门又有窗
                window_material_id = individual[start_pos + 3]
                door_material_id = individual[start_pos + 4]

            # 获取构件各个材料参数
            PreserveThi = individual[start_pos]
            WallThi = node_data[i][11]
            Thi = PreserveThi + WallThi
            SA = face_data.iloc[face_material_id]['SA']
            PreserveCon = heatPreserve_data.iloc[heat_preserve_id]['Con']
            WallCon = wall_data.iloc[wall_type]['Con']
            Con = (PreserveThi + WallThi) * (PreserveThi/PreserveCon + WallThi/WallCon)
            if node_data[i][6] == 0: # 没有门窗
                SCon = 0
                SSHGC = 0
            elif node_data[i][6] == 1: # 只有窗户
                SCon = window_data.iloc[window_material_id]['SCon']
                SSHGC = window_data.iloc[window_material_id]['SSHGC']
            elif node_data[i][6] == 2: # 只有门
                SCon = door_data.iloc[door_material_id]['SCon']
                SSHGC = 0
            elif node_data[i][6] == 3: # 既有门又有窗
                TotalArea = node_data[i][7]
                door_area = 1.8
                window_area = TotalArea - door_area
                if window_area <= 0:
                    window_area = 0
                window_SCon = window_data.iloc[window_material_id]['SCon']
                window_SSHGC = window_data.iloc[window_material_id]['SSHGC']
                door_SCon = door_data.iloc[door_material_id]['SCon']
                door_SSHGC = 0
                SCon = (window_SCon * window_area + door_SCon * door_area) / TotalArea
                SSHGC = (window_SSHGC * window_area + door_SSHGC * door_area) / TotalArea

            # 更新构件各个参数
            updated_node_data[i][10] = Con
            updated_node_data[i][11] = Thi
            updated_node_data[i][13] = SA
            updated_node_data[i][8] = SCon
            updated_node_data[i][9] = SSHGC

            # 计算成本
            area = node_data[i][4]

            wall_price = wall_data.iloc[wall_type]['Price']
            preserve_price = heatPreserve_data.iloc[heat_preserve_id]['Price']
            face_price = face_data.iloc[face_material_id]['Price']

            wall_cost = wall_price * area * WallThi
            preserve_cost = preserve_price * area * PreserveThi
            face_cost = face_price * area

            if node_data[i][6] == 0: # 没有门窗
                window_cost = 0
                door_cost = 0
            elif node_data[i][6] == 1: # 只有窗户
                window_price = window_data.iloc[window_material_id]['Price']
                window_area = node_data[i][7]
                window_cost = window_price * window_area
                door_cost = 0
            elif node_data[i][6] == 2: # 只有门
                door_price = door_data.iloc[door_material_id]['Price']
                door_area = node_data[i][7]
                door_cost = door_price * door_area
                window_cost = 0
            elif node_data[i][6] == 3: # 既有门又有窗
                window_price = window_data.iloc[window_material_id]['Price']
                door_price = door_data.iloc[door_material_id]['Price']
                subface_area = node_data[i][7]
                door_area = 1.8
                window_area = subface_area - door_area
                if window_area <= 0:
                    window_area = 0
                window_cost = window_price * window_area
                door_cost = door_price * door_area

            node_cost = wall_cost + preserve_cost + face_cost + window_cost + door_cost
            total_cost += node_cost
    
        total_energy = predict_single_sample(model_path, updated_node_data, adj_matrix, energy_data)
        return total_energy, total_cost
            
    def cx_mixed(ind1, ind2):
        """
        混合变量的交叉算子
        处理连续变量（厚度）和离散变量（材料ID）的交叉
        """
        # 遍历每个构件
        for i in range(NUM_INDIVIDUALS):
            start_pos, end_pos = component_index_map[i]
            
            # 以一定概率交叉这个构件
            if random.random() < 0.5:
                # 交叉厚度（连续变量）- 使用算术交叉
                if random.random() < 0.7:  # 70%概率进行厚度交叉
                    alpha = random.random()
                    temp1 = alpha * ind1[start_pos] + (1-alpha) * ind2[start_pos]
                    temp2 = alpha * ind2[start_pos] + (1-alpha) * ind1[start_pos]
                    # 确保在合理范围内
                    ind1[start_pos] = max(THICKNESS_MIN, min(THICKNESS_MAX, temp1))
                    ind2[start_pos] = max(THICKNESS_MIN, min(THICKNESS_MAX, temp2))
                
                # 交叉面层材料ID（离散变量）- 直接交换
                if random.random() < 0.5:
                    ind1[start_pos + 1], ind2[start_pos + 1] = ind2[start_pos + 1], ind1[start_pos + 1]
                
                # 交叉保温材料ID（离散变量）- 直接交换
                if random.random() < 0.5:
                    ind1[start_pos + 2], ind2[start_pos + 2] = ind2[start_pos + 2], ind1[start_pos + 2]
                
                # 交叉门窗材料ID（如果存在）
                wall_type = node_data[i][6]
                if wall_type == 1:  # 只有窗户
                    if random.random() < 0.5:
                        ind1[start_pos + 3], ind2[start_pos + 3] = ind2[start_pos + 3], ind1[start_pos + 3]
                elif wall_type == 2:  # 只有门
                    if random.random() < 0.5:
                        ind1[start_pos + 3], ind2[start_pos + 3] = ind2[start_pos + 3], ind1[start_pos + 3]
                elif wall_type == 3:  # 既有门又有窗
                    # 交叉窗材料ID
                    if random.random() < 0.5:
                        ind1[start_pos + 3], ind2[start_pos + 3] = ind2[start_pos + 3], ind1[start_pos + 3]
                    # 交叉门材料ID
                    if random.random() < 0.5:
                        ind1[start_pos + 4], ind2[start_pos + 4] = ind2[start_pos + 4], ind1[start_pos + 4]
        
        return ind1, ind2

    
    def mut_mixed(individual, indpb):
        """
        混合变量的变异算子
        处理连续变量（厚度）和离散变量（材料ID）的变异
        
        参数:
            individual: 个体
            indpb: 变异概率
        """
        # 遍历每个构件
        for i in range(NUM_INDIVIDUALS):
            start_pos, end_pos = component_index_map[i]
            
            # 变异厚度（连续变量）- 高斯变异
            if random.random() < indpb:
                # 使用高斯变异，标准差为范围的10%
                sigma = (THICKNESS_MAX - THICKNESS_MIN) * 0.1
                individual[start_pos] += random.gauss(0, sigma)
                # 确保在合理范围内
                individual[start_pos] = max(THICKNESS_MIN, min(THICKNESS_MAX, individual[start_pos]))
            
            # 变异面层材料ID（离散变量）- 随机选择新值
            if random.random() < indpb:
                individual[start_pos + 1] = random.randint(0, FACE_TYPE_COUNT - 1)
            
            # 变异保温材料ID（离散变量）- 随机选择新值
            if random.random() < indpb:
                individual[start_pos + 2] = random.randint(0, HEATPRESERVE_TYPE_COUNT - 1)
            
            # 变异门窗材料ID（如果存在）
            wall_type = node_data[i][6]
            if wall_type == 1:  # 只有窗户
                if random.random() < indpb:
                    individual[start_pos + 3] = random.randint(0, WINDOW_TYPE_COUNT - 1)
            elif wall_type == 2:  # 只有门
                if random.random() < indpb:
                    individual[start_pos + 3] = random.randint(0, DOOR_TYPE_COUNT - 1)
            elif wall_type == 3:  # 既有门又有窗
                # 变异窗材料ID
                if random.random() < indpb:
                    individual[start_pos + 3] = random.randint(0, WINDOW_TYPE_COUNT - 1)
                # 变异门材料ID
                if random.random() < indpb:
                    individual[start_pos + 4] = random.randint(0, DOOR_TYPE_COUNT - 1)
        
        return individual,
    
    # 7. 注册遗传算子
    toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", cx_mixed)
    toolbox.register("mutate", mut_mixed, indpb=0.2)
    toolbox.register("select", tools.selNSGA2)
    
    # 添加流式回调到toolbox
    toolbox.stream_callback = stream_callback
    
    # 8. 运行NSGA-II算法
    def run_optimization():
        # 参数设置
        POPULATION_SIZE = population_size
        GENERATIONS = generations
        CXPB = 0.7  # 交叉概率
        MUTPB = 0.2  # 变异概率
        
        print(f"开始NSGA-II优化...")
        print(f"种群大小: {POPULATION_SIZE}")
        print(f"进化代数: {GENERATIONS}")
        print(f"交叉概率: {CXPB}")
        print(f"变异概率: {MUTPB}")
        
        # 创建初始种群
        population = toolbox.population(n=POPULATION_SIZE)
        
        # 评估初始种群
        print("评估初始种群...")
        fitnesses = list(map(toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit
        
        # 统计初始种群
        fits = [ind.fitness.values for ind in population]
        energy_values = [fit[0] for fit in fits]
        cost_values = [fit[1] for fit in fits]
        print(f"初始种群 - 能耗范围: [{min(energy_values):.2f}, {max(energy_values):.2f}]")
        print(f"初始种群 - 成本范围: [{min(cost_values):.2f}, {max(cost_values):.2f}]")
        
        # 运行进化算法（手动循环以支持流式输出）
        print("开始进化过程...")
        
        # 如果有流式回调函数，输出初始代
        if hasattr(toolbox, 'stream_callback') and toolbox.stream_callback:
            initial_pareto = tools.sortNondominated(population, POPULATION_SIZE, first_front_only=True)[0]
            stream_data = {
                'generation': 0,
                'pareto_solutions': [{'energy': ind.fitness.values[0], 'cost': ind.fitness.values[1]} for ind in initial_pareto]
            }
            toolbox.stream_callback(stream_data)
        
        # 手动进化循环
        for gen in range(GENERATIONS):
            # 生成子代
            offspring = algorithms.varOr(population, toolbox, POPULATION_SIZE, CXPB, MUTPB)
            
            # 评估子代
            fitnesses = list(map(toolbox.evaluate, offspring))
            for ind, fit in zip(offspring, fitnesses):
                ind.fitness.values = fit
            
            # 选择下一代
            population = toolbox.select(population + offspring, POPULATION_SIZE)
            
            # 流式输出当前代的帕累托前沿
            if hasattr(toolbox, 'stream_callback') and toolbox.stream_callback:
                current_pareto = tools.sortNondominated(population, POPULATION_SIZE, first_front_only=True)[0]
                stream_data = {
                    'generation': gen + 1,
                    'pareto_solutions': [{'energy': ind.fitness.values[0], 'cost': ind.fitness.values[1]} for ind in current_pareto]
                }
                toolbox.stream_callback(stream_data)
        
        # 获取帕累托前沿
        pareto_front = tools.sortNondominated(population, POPULATION_SIZE, first_front_only=True)[0]
        
        return pareto_front
    

    def decode_individual(individual):
        """
        解码个体为JSON格式的节点数据
        
        参数:
            individual: 优化后的个体
            
        返回:
            list: 包含每个节点JSON数据的列表
        """
        result = []
        
        for i in range(NUM_INDIVIDUALS):
            start_pos, end_pos = component_index_map[i]
            
            # 获取优化后的参数
            thickness = individual[start_pos]  # 保温层厚度
            face_material_id = int(individual[start_pos + 1])  # 面层材料ID
            heat_preserve_id = int(individual[start_pos + 2])  # 保温材料ID
            
            # 获取门窗材料ID（如果存在）
            window_material_id = None
            door_material_id = None
            
            if node_data[i][6] == 1:  # 只有窗户
                window_material_id = int(individual[start_pos + 3])
            elif node_data[i][6] == 2:  # 只有门
                door_material_id = int(individual[start_pos + 3])
            elif node_data[i][6] == 3:  # 既有门又有窗
                window_material_id = int(individual[start_pos + 3])
                door_material_id = int(individual[start_pos + 4])
            
            # 计算SCon
            if node_data[i][6] == 0:  # 没有门窗
                SCon = 0
            elif node_data[i][6] == 1:  # 只有窗户
                SCon = window_data.iloc[window_material_id]['SCon']
            elif node_data[i][6] == 2:  # 只有门
                SCon = door_data.iloc[door_material_id]['SCon']
            elif node_data[i][6] == 3:  # 既有门又有窗
                TotalArea = node_data[i][7]
                door_area = 1.8
                window_area = TotalArea - door_area
                if window_area <= 0:
                    window_area = 0
                window_SCon = window_data.iloc[window_material_id]['SCon']
                door_SCon = door_data.iloc[door_material_id]['SCon']
                SCon = (window_SCon * window_area + door_SCon * door_area) / TotalArea
            
            # 计算SSHGC
            if node_data[i][6] == 0 or node_data[i][6] == 2:  # 没有门窗或只有门
                SSHGC = 0
            elif node_data[i][6] == 1:  # 只有窗户
                SSHGC = window_data.iloc[window_material_id]['SSHGC']
            elif node_data[i][6] == 3:  # 既有门又有窗
                TotalArea = node_data[i][7]
                door_area = 1.8
                window_area = TotalArea - door_area
                if window_area <= 0:
                    window_area = 0
                window_SSHGC = window_data.iloc[window_material_id]['SSHGC']
                door_SSHGC = 0  # 门的SSHGC为0
                SSHGC = (window_SSHGC * window_area + door_SSHGC * door_area) / TotalArea
            
            # 计算Con（总导热系数）
            PreserveThi = thickness
            WallThi = node_data[i][11]
            PreserveCon = heatPreserve_data.iloc[heat_preserve_id]['Con']
            WallCon = wall_data.iloc[wall_type]['Con']
            Con = (PreserveThi + WallThi) / (PreserveThi/PreserveCon + WallThi/WallCon)
            
            # 计算Thi（总厚度）
            Thi = round(PreserveThi + WallThi, 2)
            
            # 获取材料名称
            wall_material_name = wall_data.iloc[wall_type]['Material']
            preserve_material_name = heatPreserve_data.iloc[heat_preserve_id]['Material']
            face_material_name = face_data.iloc[face_material_id]['Material']

            wall_materian_en_name = wall_data.iloc[wall_type]['MaterialEN']
            preserve_material_en_name = heatPreserve_data.iloc[heat_preserve_id]['MaterialEN']
            face_material_en_name = face_data.iloc[face_material_id]['MaterialEN']
            
            door_material_name = None
            window_glass_name = None
            window_frame_name = None
            
            if door_material_id is not None:
                door_material_name = door_data.iloc[door_material_id]['Material']
                door_material_en_name = door_data.iloc[door_material_id]['MaterialEN']
            
            if window_material_id is not None:
                window_glass_name = window_data.iloc[window_material_id]['glassType']
                window_frame_name = window_data.iloc[window_material_id]['frameType']
                window_glass_en_name = window_data.iloc[window_material_id]['glassTypeEN']
                window_frame_en_name = window_data.iloc[window_material_id]['frameTypeEN']
            
            # 构建JSON数据
            node_json = {
                "Type": node_data[i][1],
                "Out": node_data[i][3],
                "Area": node_data[i][4],
                "SI": node_data[i][5],
                "SType": node_data[i][6],
                "SArea": node_data[i][7],
                "SCon": SCon,
                "SSHGC": SSHGC,
                "Con": Con,
                "Thi": Thi,
                "WThi": node_data[i][11],
                "PThi": round(thickness, 2),
                "TA": node_data[i][12],  # 原数据第12个
                "SA": face_data.iloc[face_material_id]['SA'],
                "VA": node_data[i][14],  # 原数据第14个
                "Dir": node_data[i][15],  # 原数据第15个
                "WMat": wall_material_name,
                "WMatEN": wall_materian_en_name,
                "PMat": preserve_material_name,
                "PMatEN": preserve_material_en_name,
                "FMat": face_material_name,
                "FMatEN": face_material_en_name,
                "DMat": door_material_name if door_material_name else "None",
                "DMatEN": door_material_en_name if door_material_name else "None",
                "WGMat": window_glass_name if window_glass_name else "None",
                "WGMatEN": window_glass_en_name if window_glass_name else "None",
                "WFMat": window_frame_name if window_frame_name else "None",
                "WFMatEN": window_frame_en_name if window_frame_name else "None"
            }
            
            result.append(node_json)
        
        return result
    
    # 运行优化
    best_solutions = run_optimization()
    
    # 解码所有帕累托最优解，并添加能耗和总价信息
    decoded_solutions = []
    for solution in best_solutions:
        decoded_solution = decode_individual(solution)
        
        # 添加方案的能耗和总价信息
        energy, cost = solution.fitness.values
        solution_info = {
            'energy': energy,
            'cost': cost,
            'nodes': decoded_solution
        }
        decoded_solutions.append(solution_info)
    
    return decoded_solutions

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import threading

app = Flask(__name__)
CORS(app)


@app.route('/optimize', methods=['POST'])
def optimize():
    """
    API端点，接收JSON格式的优化请求
    
    请求体格式:
    {
        "node_data": [[...], [...], ...],     # 节点特征数据
        "adj_matrix": [[...], [...], ...],    # 邻接矩阵
        "wall_type": 0,                       # 墙体材料类型ID
        "population_size": 50,                # 种群大小（可选，默认50）
        "generations": 10,                    # 进化代数（可选，默认10）
        "energy_data": null                   # 能量数据（可选）
        "stream": false                       # 是否启用流式输出（可选）
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 检查必要字段
        if not all(key in data for key in ['node_data', 'adj_matrix', 'wall_type']):
            return jsonify({'error': 'Missing required fields: node_data, adj_matrix, and wall_type'}), 400
            
        # 获取数据
        node_data = data['node_data']
        adj_matrix = data['adj_matrix']
        wall_type = data['wall_type']
        population_size = data.get('population_size', 50)  # 默认50
        generations = data.get('generations', 10)          # 默认10
        energy_data = data.get('energy_data')              # 可选参数
        stream_mode = data.get('stream', False)            # 是否启用流式输出
        
        # 验证参数范围
        if population_size < 10 or population_size > 200:
            return jsonify({'error': 'population_size must be between 10 and 200'}), 400
            
        if generations < 5 or generations > 100:
            return jsonify({'error': 'generations must be between 5 and 100'}), 400
        
        # 设置模型路径
        MODEL_PATH = "model/energy_merged_EUIGCN9.pth"
        
        # 如果启用流式输出
        if stream_mode:
            def generate_stream():
                """生成器函数，用于流式输出"""
                try:
                    # 发送开始信号
                    yield f"data: {json.dumps({'status': 'starting', 'message': '开始优化...'})}\n\n"
                    
                    # 存储流式数据
                    stream_buffer = []
                    
                    def collect_stream_data(stream_data):
                        stream_buffer.append(stream_data)
                        # 立即发送流式数据
                        return f"data: {json.dumps(stream_data)}\n\n"
                    
                    # 运行优化
                    decoded_solutions = NSGAII_optimization(
                        model_path=MODEL_PATH,
                        node_data=node_data,
                        adj_matrix=adj_matrix,
                        energy_data=energy_data,
                        wall_type=wall_type,
                        population_size=population_size,
                        generations=generations,
                        stream_callback=collect_stream_data
                    )
                    
                    # 发送流式数据
                    for stream_data in stream_buffer:
                        yield f"data: {json.dumps(stream_data)}\n\n"
                    
                    # 发送最终结果
                    final_result = {
                        'status': 'completed',
                        'pareto_solutions': decoded_solutions,
                        'summary': {
                            'total_solutions': len(decoded_solutions),
                            'population_size': population_size,
                            'generations': generations,
                            'wall_type': wall_type
                        }
                    }
                    
                    # 添加统计信息
                    if decoded_solutions:
                        energies = [sol['energy'] for sol in decoded_solutions]
                        costs = [sol['cost'] for sol in decoded_solutions]
                        
                        final_result['summary']['energy_range'] = {
                            'min': min(energies),
                            'max': max(energies),
                            'avg': sum(energies) / len(energies)
                        }
                        final_result['summary']['cost_range'] = {
                            'min': min(costs),
                            'max': max(costs),
                            'avg': sum(costs) / len(costs)
                        }
                    
                    yield f"data: {json.dumps(final_result)}\n\n"
                    
                except Exception as e:
                    error_data = {'status': 'error', 'error': str(e)}
                    yield f"data: {json.dumps(error_data)}\n\n"
            
            return Response(generate_stream(), 
                          mimetype='text/event-stream',
                          headers={
                              'Cache-Control': 'no-cache',
                              'Connection': 'keep-alive',
                              'Access-Control-Allow-Origin': '*'
                          })
        
        # 非流式模式（原有逻辑）
        else:
            # 运行优化
            decoded_solutions = NSGAII_optimization(
                model_path=MODEL_PATH,
                node_data=node_data,
                adj_matrix=adj_matrix,
                energy_data=energy_data,
                wall_type=wall_type,
                population_size=population_size,
                generations=generations
            )
            
            # 构建响应
            result = {
                'success': True,
                'pareto_solutions': decoded_solutions,
                'summary': {
                    'total_solutions': len(decoded_solutions),
                    'population_size': population_size,
                    'generations': generations,
                    'wall_type': wall_type
                }
            }
            
            # 添加能耗和成本范围统计
            if decoded_solutions:
                energies = [sol['energy'] for sol in decoded_solutions]
                costs = [sol['cost'] for sol in decoded_solutions]
                
                result['summary']['energy_range'] = {
                    'min': min(energies),
                    'max': max(energies),
                    'avg': sum(energies) / len(energies)
                }
                result['summary']['cost_range'] = {
                    'min': min(costs),
                    'max': max(costs),
                    'avg': sum(costs) / len(costs)
                }
            
            return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """健康检查端点"""
    return jsonify({'status': 'healthy', 'service': 'NSGA-II Optimization API'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
    

