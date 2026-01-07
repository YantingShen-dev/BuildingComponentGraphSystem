import subprocess
import sys
import os
import signal
import time

# 存储子进程对象
processes = []

def signal_handler(sig, frame):
    """处理Ctrl+C信号，优雅地关闭所有子进程"""
    print("\n\n正在关闭服务...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        except Exception as e:
            print(f"关闭进程时出错: {e}")
    print("所有服务已关闭")
    sys.exit(0)

def start_combined_api():
    """启动combined_api.py"""
    try:
        # 在 Railway 上，使用环境变量 PORT（如果存在）
        # 否则使用默认端口 5000
        env = os.environ.copy()
        if 'PORT' not in env:
            env['PORT'] = '5000'
        
        # 使用Popen而不是run，因为run是阻塞的
        process = subprocess.Popen(
            [sys.executable, 'combined_api.py'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        processes.append(process)
        port = env.get('PORT', '5000')
        print(f"✅ Combined API 进程已启动 (PID: {process.pid}, Port: {port})")
        return process
    except Exception as e:
        print(f"❌ 启动 Combined API 失败: {e}")
        return None

def start_optimization_api():
    """启动optimization_api.py"""
    try:
        # 在 Railway 上，如果 PORT 已被使用，optimization_api 使用内部端口
        # 否则使用默认端口 5001
        env = os.environ.copy()
        # 如果 PORT 环境变量存在（Railway 提供），optimization_api 使用 5001
        # 否则也使用 5001
        if 'PORT' in env:
            # Railway 环境：主服务使用 PORT，优化服务使用内部端口
            # 注意：在 Railway 上，只有主服务（使用 PORT）可以被外部访问
            # 如果需要外部访问优化服务，需要创建独立的服务
            env['PORT'] = '5001'
        else:
            env['PORT'] = '5001'
        
        # 使用Popen而不是run，因为run是阻塞的
        process = subprocess.Popen(
            [sys.executable, 'optimization_api.py'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        processes.append(process)
        port = env.get('PORT', '5001')
        print(f"✅ Optimization API 进程已启动 (PID: {process.pid}, Port: {port})")
        return process
    except Exception as e:
        print(f"❌ 启动 Optimization API 失败: {e}")
        return None

def monitor_processes():
    """监控进程状态"""
    while True:
        for i, process in enumerate(processes):
            if process.poll() is not None:
                # 进程已结束
                stdout, stderr = process.communicate()
                service_name = "Combined API" if i == 0 else "Optimization API"
                print(f"\n⚠️  {service_name} 进程意外退出 (退出码: {process.returncode})")
                if stderr:
                    print(f"错误信息: {stderr}")
                # 可以选择重启服务
                # processes[i] = start_combined_api() if i == 0 else start_optimization_api()
        time.sleep(5)  # 每5秒检查一次

if __name__ == "__main__":
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("启动GCN建筑优化API服务...")
    print("=" * 60)
    
    # 启动两个API服务
    combined_process = start_combined_api()
    time.sleep(2)  # 延迟2秒启动第二个API
    opt_process = start_optimization_api()
    
    if combined_process and opt_process:
        print("\n" + "=" * 60)
        # 获取实际使用的端口
        combined_port = os.environ.get('PORT', '5000')
        opt_port = '5001'  # 优化服务始终使用 5001
        
        print(f"✅ Combined API: http://localhost:{combined_port}")
        print(f"✅ Optimization API: http://localhost:{opt_port}")
        
        # 检查是否在 Railway 环境
        if 'RAILWAY_ENVIRONMENT' in os.environ or 'RAILWAY_PROJECT_ID' in os.environ:
            print("\n⚠️  检测到 Railway 环境")
            print("   注意：Railway 一个服务只能暴露一个端口")
            print("   如果需要在外部访问优化服务，请创建独立的 Railway 服务")
            print(f"   当前主服务端口: {combined_port}")
            print(f"   优化服务端口: {opt_port} (仅内部可访问)")
        
        print("=" * 60)
        print("服务正在运行中...")
        print("按 Ctrl+C 停止所有服务")
        print("=" * 60 + "\n")
        
        # 启动监控线程（可选）
        import threading
        monitor_thread = threading.Thread(target=monitor_processes, daemon=True)
        monitor_thread.start()
        
        # 等待所有进程
        try:
            combined_process.wait()
            opt_process.wait()
        except KeyboardInterrupt:
            signal_handler(None, None)
    else:
        print("\n❌ 服务启动失败，请检查错误信息")
        signal_handler(None, None)
