# Google Earth Engine 认证设置指南

## 📋 概述

本项目使用 Google Earth Engine (GEE) 获取卫星图像和地理数据。要使用此功能，您需要设置 GEE 认证。

## 🔑 获取 GEE 认证

### 方法1：使用个人 Google 账户（推荐用于开发）

1. **访问 GEE 网站**
   - 打开 https://earthengine.google.com/
   - 使用您的 Google 账户登录

2. **注册 GEE 账户**
   - 点击 "Sign up for Earth Engine"
   - 填写注册表单
   - 等待审核通过（通常需要1-2天）

3. **获取项目ID**
   - 在 GEE 控制台中创建新项目
   - 记录项目ID（如：`your-project-name`）

### 方法2：使用服务账号（推荐用于生产）

1. **创建 Google Cloud 项目**
   - 访问 https://console.cloud.google.com/
   - 创建新项目或选择现有项目

2. **启用 Earth Engine API**
   - 在 Google Cloud Console 中
   - 转到 "APIs & Services" > "Library"
   - 搜索 "Earth Engine API" 并启用

3. **创建服务账号**
   - 转到 "IAM & Admin" > "Service Accounts"
   - 点击 "Create Service Account"
   - 填写服务账号信息

4. **生成密钥文件**
   - 在服务账号列表中，点击刚创建的服务账号
   - 转到 "Keys" 标签
   - 点击 "Add Key" > "Create new key"
   - 选择 "JSON" 格式
   - 下载密钥文件

5. **将密钥文件添加到项目**
   - 将下载的 JSON 文件重命名为 `gee_service_account_key.json`
   - 将文件放在项目根目录

## ⚙️ 配置项目

### 1. 复制环境配置文件
```bash
cp env.example .env
```

### 2. 编辑 .env 文件
```env
# GEE 配置
GEE_PROJECT_ID=your_gee_project_id
GEE_SERVICE_ACCOUNT_KEY_PATH=./gee_service_account_key.json
```

### 3. 设置环境变量（可选）
```bash
# Windows
set GEE_PROJECT_ID=your_gee_project_id
set GOOGLE_APPLICATION_CREDENTIALS=./gee_service_account_key.json

# Linux/Mac
export GEE_PROJECT_ID=your_gee_project_id
export GOOGLE_APPLICATION_CREDENTIALS=./gee_service_account_key.json
```

## 🧪 测试 GEE 连接

运行以下命令测试 GEE 连接：

```bash
python setup_gee_auth.py
```

如果看到 "GEE 认证成功" 消息，说明配置正确。

## ❗ 注意事项

1. **不要将密钥文件提交到 Git**
   - 确保 `gee_service_account_key.json` 在 `.gitignore` 中
   - 使用 `env.example` 作为模板

2. **权限管理**
   - 服务账号需要 Earth Engine 用户权限
   - 联系 GEE 团队添加服务账号权限

3. **配额限制**
   - GEE 有使用配额限制
   - 超出限制可能导致请求失败

## 🔧 故障排除

### 常见错误

1. **认证失败**
   ```
   Error: The caller does not have permission
   ```
   - 检查服务账号是否有 GEE 权限
   - 确认项目ID正确

2. **API 未启用**
   ```
   Error: Earth Engine API has not been used
   ```
   - 在 Google Cloud Console 中启用 Earth Engine API

3. **配额超限**
   ```
   Error: Quota exceeded
   ```
   - 等待配额重置或申请增加配额

### 获取帮助

- [GEE 官方文档](https://developers.google.com/earth-engine)
- [GEE 社区论坛](https://groups.google.com/forum/#!forum/google-earth-engine-developers)
- [项目 Issues](https://github.com/your-repo/issues)

## 📝 更新日志

- 2025-10-12: 初始版本
- 添加了个人账户和服务账号两种认证方式
- 提供了详细的配置步骤和故障排除指南
