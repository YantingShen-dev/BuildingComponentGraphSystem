import pandas as pd
import json
import os

def excel_to_json(data_dir='data'):
    """
    将data文件夹中的Excel文件转换为JSON请求格式
    
    参数:
        data_dir: 数据文件夹路径，默认为'data'
        
    返回:
        json_str: JSON格式的字符串
    """
    try:
        # 读取Excel文件
        node_path = os.path.join(data_dir, 'node.xlsx')
        adj_path = os.path.join(data_dir, 'adjmatrix.xlsx')
        energy_path = os.path.join(data_dir, 'energy_sum.xlsx')
        
        # 读取node.xlsx
        node_df = pd.read_excel(node_path, header=None)
        node_data = node_df.values.tolist()
        
        # 读取adjmatrix.xlsx
        adj_df = pd.read_excel(adj_path, header=None)
        adj_matrix = adj_df.values.tolist()
        
        # 尝试读取energy_sum.xlsx（可选）
        energy_data = None
        try:
            energy_df = pd.read_excel(energy_path, sheet_name='eui_end_use', header=None)
            energy_data = energy_df.values.tolist()
        except Exception as e:
            print(f"Note: Could not read energy data: {str(e)}")
        
        # 构建请求数据
        request_data = {
            "node_data": node_data,
            "adj_matrix": adj_matrix
        }
        
        # 如果有energy数据，添加到请求中
        if energy_data is not None:
            request_data["energy_data"] = energy_data
        
        # 转换为JSON字符串，保持缩进格式
        json_str = json.dumps(request_data, indent=4)
        
        # 保存到文件
        output_path = os.path.join(data_dir, 'request.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_str)
            
        print(f"JSON request has been saved to {output_path}")
        return json_str
        
    except Exception as e:
        print(f"Error converting Excel to JSON: {str(e)}")
        return None

if __name__ == "__main__":
    # 使用默认data文件夹
    json_str = excel_to_json("datatest")
    
    if json_str:
        print("\nGenerated JSON request:")
        print(json_str)
