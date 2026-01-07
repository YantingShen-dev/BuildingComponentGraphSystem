# Railway 部署指南

## 部署方式

Railway 一个服务只能暴露一个端口。要同时运行两个 API 服务，有两种方式：

### 方式1：单个服务（推荐用于开发/测试）

使用 `start_apis.py` 在一个服务中启动两个 API：

1. **创建 Railway 服务**
   - 在 Railway 中创建新项目
   - 连接到你的 GitHub 仓库
   - 选择 `gcn_backend-gpu--main` 目录作为根目录

2. **配置启动命令**
   - Railway 会自动读取 `Procfile` 或 `railway.json`
   - 确保启动命令是：`python start_apis.py`

3. **端口配置**
   - Combined API (预测服务) 会使用 Railway 提供的 `PORT` 环境变量
   - Optimization API (优化服务) 会使用内部端口 5001
   - **注意**：只有 Combined API 可以被外部访问

4. **环境变量**
   - Railway 会自动设置 `PORT` 环境变量
   - 无需手动配置

### 方式2：两个独立服务（推荐用于生产环境）

创建两个独立的 Railway 服务，每个服务运行一个 API：

#### 服务1：预测服务 (Combined API)

1. **创建第一个服务**
   - 服务名称：`gcn-predict-api`
   - 根目录：`gcn_backend-gpu--main`
   - 启动命令：`python combined_api.py`

2. **创建 Procfile**（如果使用方式1，已存在）
   ```
   web: python combined_api.py
   ```

3. **获取服务 URL**
   - Railway 会提供一个公共 URL，例如：`https://your-predict-api.railway.app`

#### 服务2：优化服务 (Optimization API)

1. **创建第二个服务**
   - 服务名称：`gcn-optimization-api`
   - 根目录：`gcn_backend-gpu--main`
   - 启动命令：`python optimization_api.py`

2. **创建独立的 Procfile**
   ```
   web: python optimization_api.py
   ```

3. **获取服务 URL**
   - Railway 会提供一个公共 URL，例如：`https://your-optimization-api.railway.app`

## 前端配置

部署后端后，需要更新前端的 API URL：

1. **方式1（单个服务）**
   ```env
   VITE_API_URL=https://your-service.railway.app
   VITE_API_URL_OPT=https://your-service.railway.app  # 注意：优化服务不可访问
   ```
   ⚠️ **限制**：优化服务无法从外部访问

2. **方式2（两个服务）**
   ```env
   VITE_API_URL=https://your-predict-api.railway.app
   VITE_API_URL_OPT=https://your-optimization-api.railway.app
   ```

## 检查服务状态

部署后，可以使用健康检查端点验证服务：

```bash
# 检查预测服务
curl https://your-predict-api.railway.app/health

# 检查优化服务（如果使用方式2）
curl https://your-optimization-api.railway.app/health
```

## 常见问题

### Q: 为什么优化服务无法访问？

A: 如果使用方式1（单个服务），Railway 只暴露一个端口。优化服务运行在内部端口 5001，无法从外部访问。建议使用方式2创建两个独立服务。

### Q: 如何查看服务日志？

A: 在 Railway 控制台的 "Deployments" 标签页可以查看实时日志。

### Q: 服务启动失败怎么办？

A: 
1. 检查 `requirements.txt` 是否包含所有依赖
2. 检查模型文件是否存在：`model/energy_merged_EUIGCN9.pth`
3. 检查材料文件是否存在：`materials/` 目录
4. 查看 Railway 日志获取详细错误信息

## 推荐配置

**生产环境推荐使用方式2（两个独立服务）**，因为：
- 每个服务可以独立扩展
- 更好的资源隔离
- 两个服务都可以从外部访问
- 更灵活的部署策略

