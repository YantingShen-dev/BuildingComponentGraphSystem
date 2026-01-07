#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查API服务是否运行
"""
import requests
import sys

def check_service(url, service_name):
    """检查服务是否可用"""
    try:
        response = requests.get(f"{url}/health", timeout=2)
        if response.status_code == 200:
            print(f"✅ {service_name} 正在运行: {url}")
            return True
        else:
            print(f"❌ {service_name} 响应异常: {url} (状态码: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {service_name} 无法连接: {url}")
        print(f"   请确保服务正在运行")
        return False
    except requests.exceptions.Timeout:
        print(f"⏱️  {service_name} 连接超时: {url}")
        return False
    except Exception as e:
        print(f"❌ {service_name} 检查失败: {url}")
        print(f"   错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("检查API服务状态")
    print("=" * 50)
    
    # 检查预测API (端口5000)
    predict_ok = check_service("http://localhost:5000", "预测API")
    
    # 检查优化API (端口5001)
    opt_ok = check_service("http://localhost:5001", "优化API")
    
    print("=" * 50)
    
    if predict_ok and opt_ok:
        print("✅ 所有服务运行正常！")
        sys.exit(0)
    else:
        print("❌ 部分服务未运行")
        print("\n启动服务的方法：")
        print("1. 单独启动预测API: python combined_api.py")
        print("2. 单独启动优化API: python optimization_api.py")
        print("3. 同时启动两个服务: python start_apis.py")
        sys.exit(1)

