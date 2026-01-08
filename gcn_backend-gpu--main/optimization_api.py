import torch
from GCN9 import GCN
from GraphDataConstruct import construct_graph_data
from torch_geometric.loader import DataLoader
import pandas as pd
import os
from deap import base, creator, tools, algorithms
import random
import numpy as np
from flask import Flask, request, jsonify, Response, make_response
from flask_cors import CORS
import json

# ==========================================
# 1. Flask 设置
# ==========================================

app = Flask(__name__)

# 虽然手动处理了，保留这个配置作为双重保险
CORS(app, resources={r"/*": {"origins": "*"}})

# ==========================================
# 2. 核心算法函数 (保持不变)
# ==========================================

def read_excel_to_list(file_path, sheet_name=None):
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
    device = torch.device('cpu')
    try:
        graph_data = construct_graph_data(node_data, adj_matrix, energy_data, 'EUI', 0)
    except Exception as e:
        print(f"Error constructing graph data: {str(e)}")
        return

    model = GCN(graph_data.num_node_features).to(device)
    try:
        model.load_state_dict(torch.load(model_path, map_location=device))
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return

    loader = DataLoader([graph_data], batch_size=1)
    model.eval()
    with torch.no_grad():
        for batch in loader:
            batch = batch.to(device)
            prediction = model(batch.x, batch.edge_index, batch.batch)
            return prediction.item()

def NSGAII_optimization(model_path, node_data, adj_matrix, energy_data, wall_type, population_size, generations, stream_callback=None):
    MATERIAL_PATH = os.path.join('materials')
    door_data = read_and_convert_excel(os.path.join(MATERIAL_PATH, 'door.xlsx'))
    window_data = read_and_convert_excel(os.path.join(MATERIAL_PATH, 'window.xlsx'))
    face_data = read_and_convert_excel(os.path.join(MATERIAL_PATH, 'face.xlsx'))
    heatPreserve_data = read_and_convert_excel(os.path.join(MATERIAL_PATH, 'heatPreserve.xlsx'))
    wall_data = read_and_convert_excel(os.path.join(MATERIAL_PATH, 'wall_select.xlsx'))

    if not hasattr(creator, "FitnessMin"):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()

    DOOR_TYPE_COUNT = len(door_data)
    WINDOW_TYPE_COUNT = len(window_data)
    FACE_TYPE_COUNT = len(face_data)
    HEATPRESERVE_TYPE_COUNT = len(heatPreserve_data)
    THICKNESS_MAX = 0.2
    THICKNESS_MIN = 0.01
    NUM_INDIVIDUALS = len(node_data)

    def create_individual():
        individual = []
        for i in range(NUM_INDIVIDUALS):
            thickness = random.uniform(THICKNESS_MIN, THICKNESS_MAX)
            face_material_id = random.randint(0, FACE_TYPE_COUNT - 1)
            heat_preserve_id = random.randint(0, HEATPRESERVE_TYPE_COUNT - 1)
            individual.extend([thickness, face_material_id, heat_preserve_id])
            
            wall_type_node = node_data[i][6]
            if wall_type_node == 1:
                individual.append(random.randint(0, WINDOW_TYPE_COUNT - 1))
            elif wall_type_node == 2:
                individual.append(random.randint(0, DOOR_TYPE_COUNT - 1))
            elif wall_type_node == 3:
                individual.extend([random.randint(0, WINDOW_TYPE_COUNT - 1), random.randint(0, DOOR_TYPE_COUNT - 1)])
        return individual
    
    def create_component_index_map():
        index_map = {}
        current_pos = 0
        for i in range(NUM_INDIVIDUALS):
            start_pos = current_pos
            current_pos += 3
            wall_type_node = node_data[i][6]
            if wall_type_node == 1: current_pos += 1
            elif wall_type_node == 2: current_pos += 1
            elif wall_type_node == 3: current_pos += 2
            end_pos = current_pos
            index_map[i] = (start_pos, end_pos)
        return index_map
    
    component_index_map = create_component_index_map()

    def evaluate(individual):
        updated_node_data = [row[:] for row in node_data]
        total_cost = 0

        for i in range(NUM_INDIVIDUALS):
            start_pos, end_pos = component_index_map[i]
            thickness = individual[start_pos]
            face_material_id = individual[start_pos + 1]
            heat_preserve_id = individual[start_pos + 2]
            
            window_material_id = None
            door_material_id = None

            if node_data[i][6] == 1:
                window_material_id = individual[start_pos + 3]
            elif node_data[i][6] == 2:
                door_material_id = individual[start_pos + 3]
            elif node_data[i][6] == 3:
                window_material_id = individual[start_pos + 3]
                door_material_id = individual[start_pos + 4]

            PreserveThi = individual[start_pos]
            WallThi = node_data[i][11]
            SA = face_data.iloc[face_material_id]['SA']
            PreserveCon = heatPreserve_data.iloc[heat_preserve_id]['Con']
            WallCon = wall_data.iloc[wall_type]['Con']
            Con = (PreserveThi + WallThi) * (PreserveThi/PreserveCon + WallThi/WallCon)
            
            SCon, SSHGC = 0, 0
            if node_data[i][6] == 1:
                SCon = window_data.iloc[window_material_id]['SCon']
                SSHGC = window_data.iloc[window_material_id]['SSHGC']
            elif node_data[i][6] == 2:
                SCon = door_data.iloc[door_material_id]['SCon']
            elif node_data[i][6] == 3:
                TotalArea = node_data[i][7]
                door_area = 1.8
                window_area = max(0, TotalArea - door_area)
                window_SCon = window_data.iloc[window_material_id]['SCon']
                window_SSHGC = window_data.iloc[window_material_id]['SSHGC']
                door_SCon = door_data.iloc[door_material_id]['SCon']
                SCon = (window_SCon * window_area + door_SCon * door_area) / TotalArea
                SSHGC = (window_SSHGC * window_area) / TotalArea

            updated_node_data[i][10] = Con
            updated_node_data[i][11] = PreserveThi + WallThi
            updated_node_data[i][13] = SA
            updated_node_data[i][8] = SCon
            updated_node_data[i][9] = SSHGC

            area = node_data[i][4]
            wall_price = wall_data.iloc[wall_type]['Price']
            preserve_price = heatPreserve_data.iloc[heat_preserve_id]['Price']
            face_price = face_data.iloc[face_material_id]['Price']

            wall_cost = wall_price * area * WallThi
            preserve_cost = preserve_price * area * PreserveThi
            face_cost = face_price * area
            
            window_cost, door_cost = 0, 0
            if node_data[i][6] == 1:
                window_price = window_data.iloc[window_material_id]['Price']
                window_cost = window_price * node_data[i][7]
            elif node_data[i][6] == 2:
                door_price = door_data.iloc[door_material_id]['Price']
                door_cost = door_price * node_data[i][7]
            elif node_data[i][6] == 3:
                window_price = window_data.iloc[window_material_id]['Price']
                door_price = door_data.iloc[door_material_id]['Price']
                door_area = 1.8
                window_area = max(0, node_data[i][7] - door_area)
                window_cost = window_price * window_area
                door_cost = door_price * door_area

            total_cost += (wall_cost + preserve_cost + face_cost + window_cost + door_cost)
    
        total_energy = predict_single_sample(model_path, updated_node_data, adj_matrix, energy_data)
        return total_energy, total_cost
            
    def cx_mixed(ind1, ind2):
        for i in range(NUM_INDIVIDUALS):
            start_pos, end_pos = component_index_map[i]
            if random.random() < 0.5:
                if random.random() < 0.7:
                    alpha = random.random()
                    temp1 = alpha * ind1[start_pos] + (1-alpha) * ind2[start_pos]
                    temp2 = alpha * ind2[start_pos] + (1-alpha) * ind1[start_pos]
                    ind1[start_pos] = max(THICKNESS_MIN, min(THICKNESS_MAX, temp1))
                    ind2[start_pos] = max(THICKNESS_MIN, min(THICKNESS_MAX, temp2))
                if random.random() < 0.5:
                    ind1[start_pos + 1], ind2[start_pos + 1] = ind2[start_pos + 1], ind1[start_pos + 1]
                if random.random() < 0.5:
                    ind1[start_pos + 2], ind2[start_pos + 2] = ind2[start_pos + 2], ind1[start_pos + 2]
                
                wall_type_node = node_data[i][6]
                if wall_type_node in [1, 2]:
                    if random.random() < 0.5:
                        ind1[start_pos + 3], ind2[start_pos + 3] = ind2[start_pos + 3], ind1[start_pos + 3]
                elif wall_type_node == 3:
                    if random.random() < 0.5:
                        ind1[start_pos + 3], ind2[start_pos + 3] = ind2[start_pos + 3], ind1[start_pos + 3]
                    if random.random() < 0.5:
                        ind1[start_pos + 4], ind2[start_pos + 4] = ind2[start_pos + 4], ind1[start_pos + 4]
        return ind1, ind2

    def mut_mixed(individual, indpb):
        for i in range(NUM_INDIVIDUALS):
            start_pos, end_pos = component_index_map[i]
            if random.random() < indpb:
                sigma = (THICKNESS_MAX - THICKNESS_MIN) * 0.1
                individual[start_pos] += random.gauss(0, sigma)
                individual[start_pos] = max(THICKNESS_MIN, min(THICKNESS_MAX, individual[start_pos]))
            if random.random() < indpb:
                individual[start_pos + 1] = random.randint(0, FACE_TYPE_COUNT - 1)
            if random.random() < indpb:
                individual[start_pos + 2] = random.randint(0, HEATPRESERVE_TYPE_COUNT - 1)
            
            wall_type_node = node_data[i][6]
            if wall_type_node == 1:
                if random.random() < indpb: individual[start_pos + 3] = random.randint(0, WINDOW_TYPE_COUNT - 1)
            elif wall_type_node == 2:
                if random.random() < indpb: individual[start_pos + 3] = random.randint(0, DOOR_TYPE_COUNT - 1)
            elif wall_type_node == 3:
                if random.random() < indpb: individual[start_pos + 3] = random.randint(0, WINDOW_TYPE_COUNT - 1)
                if random.random() < indpb: individual[start_pos + 4] = random.randint(0, DOOR_TYPE_COUNT - 1)
        return individual,
    
    toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", cx_mixed)
    toolbox.register("mutate", mut_mixed, indpb=0.2)
    toolbox.register("select", tools.selNSGA2)
    toolbox.stream_callback = stream_callback
    
    def run_optimization():
        POPULATION_SIZE = population_size
        GENERATIONS = generations
        CXPB, MUTPB = 0.7, 0.2
        
        population = toolbox.population(n=POPULATION_SIZE)
        fitnesses = list(map(toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit
        
        if hasattr(toolbox, 'stream_callback') and toolbox.stream_callback:
            initial_pareto = tools.sortNondominated(population, POPULATION_SIZE, first_front_only=True)[0]
            stream_data = {
                'generation': 0,
                'pareto_solutions': [{'energy': ind.fitness.values[0], 'cost': ind.fitness.values[1]} for ind in initial_pareto]
            }
            toolbox.stream_callback(stream_data)
        
        for gen in range(GENERATIONS):
            offspring = algorithms.varOr(population, toolbox, POPULATION_SIZE, CXPB, MUTPB)
            fitnesses = list(map(toolbox.evaluate, offspring))
            for ind, fit in zip(offspring, fitnesses):
                ind.fitness.values = fit
            
            population = toolbox.select(population + offspring, POPULATION_SIZE)
            
            if hasattr(toolbox, 'stream_callback') and toolbox.stream_callback:
                current_pareto = tools.sortNondominated(population, POPULATION_SIZE, first_front_only=True)[0]
                stream_data = {
                    'generation': gen + 1,
                    'pareto_solutions': [{'energy': ind.fitness.values[0], 'cost': ind.fitness.values[1]} for ind in current_pareto]
                }
                toolbox.stream_callback(stream_data)
        
        return tools.sortNondominated(population, POPULATION_SIZE, first_front_only=True)[0]
    

    def decode_individual(individual):
        result = []
        for i in range(NUM_INDIVIDUALS):
            start_pos, end_pos = component_index_map[i]
            thickness = individual[start_pos]
            face_material_id = int(individual[start_pos + 1])
            heat_preserve_id = int(individual[start_pos + 2])
            
            window_material_id, door_material_id = None, None
            
            if node_data[i][6] == 1: window_material_id = int(individual[start_pos + 3])
            elif node_data[i][6] == 2: door_material_id = int(individual[start_pos + 3])
            elif node_data[i][6] == 3:
                window_material_id = int(individual[start_pos + 3])
                door_material_id = int(individual[start_pos + 4])
            
            SCon, SSHGC = 0, 0
            if node_data[i][6] == 1:
                SCon = window_data.iloc[window_material_id]['SCon']
                SSHGC = window_data.iloc[window_material_id]['SSHGC']
            elif node_data[i][6] == 2:
                SCon = door_data.iloc[door_material_id]['SCon']
            elif node_data[i][6] == 3:
                TotalArea = node_data[i][7]
                door_area = 1.8
                window_area = max(0, TotalArea - door_area)
                window_SCon = window_data.iloc[window_material_id]['SCon']
                window_SSHGC = window_data.iloc[window_material_id]['SSHGC']
                door_SCon = door_data.iloc[door_material_id]['SCon']
                SCon = (window_SCon * window_area + door_SCon * door_area) / TotalArea
                SSHGC = (window_SSHGC * window_area) / TotalArea
            
            PreserveThi = thickness
            WallThi = node_data[i][11]
            PreserveCon = heatPreserve_data.iloc[heat_preserve_id]['Con']
            WallCon = wall_data.iloc[wall_type]['Con']
            Con = (PreserveThi + WallThi) / (PreserveThi/PreserveCon + WallThi/WallCon)
            Thi = round(PreserveThi + WallThi, 2)
            
            wall_material_name = wall_data.iloc[wall_type]['Material']
            preserve_material_name = heatPreserve_data.iloc[heat_preserve_id]['Material']
            face_material_name = face_data.iloc[face_material_id]['Material']
            wall_materian_en_name = wall_data.iloc[wall_type]['MaterialEN']
            preserve_material_en_name = heatPreserve_data.iloc[heat_preserve_id]['MaterialEN']
            face_material_en_name = face_data.iloc[face_material_id]['MaterialEN']
            
            door_material_name, door_material_en_name = None, None
            if door_material_id is not None:
                door_material_name = door_data.iloc[door_material_id]['Material']
                door_material_en_name = door_data.iloc[door_material_id]['MaterialEN']
            
            window_glass_name, window_frame_name = None, None
            window_glass_en_name, window_frame_en_name = None, None
            if window_material_id is not None:
                window_glass_name = window_data.iloc[window_material_id]['glassType']
                window_frame_name = window_data.iloc[window_material_id]['frameType']
                window_glass_en_name = window_data.iloc[window_material_id]['glassTypeEN']
                window_frame_en_name = window_data.iloc[window_material_id]['frameTypeEN']
            
            node_json = {
                "Type": node_data[i][1], "Out": node_data[i][3], "Area": node_data[i][4],
                "SI": node_data[i][5], "SType": node_data[i][6], "SArea": node_data[i][7],
                "SCon": SCon, "SSHGC": SSHGC, "Con": Con, "Thi": Thi,
                "WThi": node_data[i][11], "PThi": round(thickness, 2), "TA": node_data[i][12],
                "SA": face_data.iloc[face_material_id]['SA'], "VA": node_data[i][14], "Dir": node_data[i][15],
                "WMat": wall_material_name, "WMatEN": wall_materian_en_name,
                "PMat": preserve_material_name, "PMatEN": preserve_material_en_name,
                "FMat": face_material_name, "FMatEN": face_material_en_name,
                "DMat": door_material_name if door_material_name else "None",
                "DMatEN": door_material_en_name if door_material_name else "None",
                "WGMat": window_glass_name if window_glass_name else "None",
                "WGMatEN": window_glass_en_name if window_glass_name else "None",
                "WFMat": window_frame_name if window_frame_name else "None",
                "WFMatEN": window_frame_en_name if window_frame_name else "None"
            }
            result.append(node_json)
        return result
    
    best_solutions = run_optimization()
    decoded_solutions = []
    for solution in best_solutions:
        decoded_solution = decode_individual(solution)
        energy, cost = solution.fitness.values
        solution_info = {'energy': energy, 'cost': cost, 'nodes': decoded_solution}
        decoded_solutions.append(solution_info)
    
    return decoded_solutions

# ==========================================
# 3. API 路由 (关键修复)
# ==========================================

# 重点：显式在 methods 中添加 'OPTIONS'，强制 Flask 处理预检请求
@app.route('/optimize', methods=['POST', 'OPTIONS'])
def optimize():
    # 1. 显式处理 OPTIONS 请求，直接返回 200 和跨域头
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
        return response

    # 2. 处理 POST 业务逻辑
    try:
        data = request.get_json()
        if not all(key in data for key in ['node_data', 'adj_matrix', 'wall_type']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
        node_data = data['node_data']
        adj_matrix = data['adj_matrix']
        wall_type = data['wall_type']
        population_size = data.get('population_size', 50)
        generations = data.get('generations', 10)
        energy_data = data.get('energy_data')
        stream_mode = data.get('stream', False)
        
        if population_size < 10 or population_size > 200:
            return jsonify({'success': False, 'error': 'population_size must be 10-200'}), 400
        if generations < 5 or generations > 100:
            return jsonify({'success': False, 'error': 'generations must be 5-100'}), 400
        
        MODEL_PATH = "model/energy_merged_EUIGCN9.pth"
        
        if stream_mode:
            def generate_stream():
                try:
                    yield f"data: {json.dumps({'status': 'starting', 'message': '开始优化...'})}\n\n"
                    stream_buffer = []
                    
                    def collect_stream_data(stream_data):
                        stream_buffer.append(stream_data)
                        return f"data: {json.dumps(stream_data)}\n\n"
                    
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
                    
                    for stream_data in stream_buffer:
                        yield f"data: {json.dumps(stream_data)}\n\n"
                    
                    final_result = {
                        'status': 'completed',
                        'pareto_solutions': decoded_solutions,
                        'summary': {
                            'total_solutions': len(decoded_solutions),
                            'population_size': population_size,
                            'generations': generations
                        }
                    }
                    if decoded_solutions:
                        energies = [sol['energy'] for sol in decoded_solutions]
                        costs = [sol['cost'] for sol in decoded_solutions]
                        final_result['summary']['energy_range'] = {'min': min(energies), 'max': max(energies)}
                        final_result['summary']['cost_range'] = {'min': min(costs), 'max': max(costs)}
                    
                    yield f"data: {json.dumps(final_result)}\n\n"
                    
                except Exception as e:
                    error_data = {'status': 'error', 'error': str(e)}
                    yield f"data: {json.dumps(error_data)}\n\n"
            
            # 流式响应的 CORS 头
            return Response(generate_stream(), 
                          mimetype='text/event-stream',
                          headers={
                              'Cache-Control': 'no-cache',
                              'Connection': 'keep-alive',
                              'Access-Control-Allow-Origin': '*',
                              'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                              'X-Accel-Buffering': 'no'
                          })
        
        else:
            decoded_solutions = NSGAII_optimization(
                model_path=MODEL_PATH,
                node_data=node_data,
                adj_matrix=adj_matrix,
                energy_data=energy_data,
                wall_type=wall_type,
                population_size=population_size,
                generations=generations
            )
            result = {'success': True, 'pareto_solutions': decoded_solutions}
            if decoded_solutions:
                energies = [sol['energy'] for sol in decoded_solutions]
                costs = [sol['cost'] for sol in decoded_solutions]
                result['summary'] = {
                    'energy_range': {'min': min(energies), 'max': max(energies)},
                    'cost_range': {'min': min(costs), 'max': max(costs)}
                }
            return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'NSGA-II Optimization API'})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)