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
    # 检查是否在 Railway 环境
    # Railway 总是会设置 PORT 环境变量，且通常是随机端口（不是 5000/5001）
    port_env = os.environ.get('PORT')
    
    # Railway 检测：如果 PORT 存在且不是常见的本地开发端口，就认为是 Railway
    # 本地开发时通常使用 5000 或 5001，或者不设置 PORT
    # 为了更可靠，如果 PORT 存在且不是 5000/5001，就认为是 Railway
    is_railway = port_env is not None and str(port_env) not in ['5000', '5001']
    
    # 添加调试信息
    print(f"DEBUG: PORT={port_env}, is_railway={is_railway}")
    print(f"DEBUG: 环境变量检查 - RAILWAY_ENV={os.environ.get('RAILWAY_ENVIRONMENT')}, RAILWAY_PROJECT={os.environ.get('RAILWAY_PROJECT_ID')}")
    
    if is_railway:
        # Railway 环境：只启动主服务（预测服务）
        # Railway 需要主进程直接监听端口，不能使用子进程
        print("=" * 60)
        print("检测到 Railway 环境")
        print("启动预测服务 (Combined API)...")
        print("=" * 60)
        
        # 直接运行 combined_api，而不是使用子进程
        # 这样可以确保主进程监听端口，Railway 可以正确路由流量
        port = int(os.environ.get('PORT', 5000))
        print(f"✅ 预测服务启动在端口: {port}")
        print("=" * 60)
        print("注意：优化服务需要创建独立的 Railway 服务")
        print("=" * 60 + "\n")
        
        # 导入 combined_api 并获取 app 对象
        import combined_api
        
        # 在 Railway 上使用 gunicorn 作为生产服务器
        # gunicorn 更适合生产环境，支持更长的请求超时
        try:
            import gunicorn.app.base
            
            class StandaloneApplication(gunicorn.app.base.BaseApplication):
                def __init__(self, app, options=None):
                    self.options = options or {}
                    self.application = app
                    super().__init__()
                
                def load_config(self):
                    for key, value in self.options.items():
                        self.cfg.set(key.lower(), value)
                
                def load(self):
                    return self.application
            
            # 配置 gunicorn
            options = {
                'bind': f'0.0.0.0:{port}',
                'workers': 1,  # Railway 资源有限，使用单 worker
                'worker_class': 'sync',
                'timeout': 600,  # 10分钟超时，确保 explain 过程有足够时间完成
                'graceful_timeout': 30,  # 优雅关闭超时
                'keepalive': 5,
                'accesslog': '-',  # 输出到 stdout
                'errorlog': '-',  # 输出到 stderr
                'worker_tmp_dir': '/dev/shm',  # 使用内存文件系统提高性能（如果可用）
            }
            
            print("使用 Gunicorn 生产服务器启动...")
            StandaloneApplication(combined_api.app, options).run()
        except ImportError:
            # 如果没有 gunicorn，回退到 Flask 开发服务器
            print("警告: 未安装 gunicorn，使用 Flask 开发服务器（不推荐生产环境）")
            combined_api.app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    else:
        # 本地环境：启动两个服务
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
