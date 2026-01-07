import subprocess
import threading
import time

def start_combined_api():
    """启动combined_api.py"""
    subprocess.run(['python', 'combined_api.py'])

def start_optimization_api():
    """启动optimization_api.py"""
    subprocess.run(['python', 'optimization_api.py'])

if __name__ == "__main__":
    print("启动GCN建筑优化API服务...")
    
    # 创建线程启动两个API
    thread1 = threading.Thread(target=start_combined_api)
    thread2 = threading.Thread(target=start_optimization_api)
    
    # 启动线程
    thread1.start()
    time.sleep(2)  # 延迟2秒启动第二个API
    thread2.start()
    
    print("✅ Combined API: http://localhost:5000")
    print("✅ Optimization API: http://localhost:5001")
    print("按Ctrl+C停止服务")
    
    # 等待线程结束
    thread1.join()
    thread2.join()
