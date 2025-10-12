# 🚀 数据中心智能选址与能源优化系统

基于Google Earth Engine (GEE)和AI技术的智能数据中心选址与能源资源评估系统，集成卫星遥感数据、多模态AI分析和多准则决策分析。

## ✨ 主要功能

- 🌍 **卫星图像分析** - 基于GEE的高分辨率卫星图像获取与AI分析
- ⚡ **能源资源评估** - 太阳能、风能、水能等可再生能源潜力AI评估
- 🏭 **余热利用分析** - 数据中心余热回收利用潜力分析
- 🌿 **地理环境分析** - 海拔、河流、森林、气候等地理要素分析
- 🔋 **供电方案分析** - 多种供电方案的技术经济性AI分析
- 💾 **储能布局分析** - 储能系统布局优化AI分析
- 🎯 **智能决策分析** - 基于PROMETHEE-MCGP的多准则决策分析
- 🤖 **多模态AI分析** - 集成图像、文本、数据的综合AI分析
- 📊 **可视化地图** - 基于Leaflet的交互式地图展示

## 🛠️ 技术栈

### 后端
- **FastAPI 0.104.1** - 高性能Web框架
- **Google Earth Engine** - 卫星遥感数据处理
- **Python 3.8+** - 核心开发语言
- **Pydantic 2.5.0** - 数据验证
- **Uvicorn** - ASGI服务器
- **OpenCV** - 图像处理
- **scikit-learn** - 机器学习
- **NumPy & Pandas** - 数据处理

### 前端
- **React 18** - 用户界面框架
- **TypeScript** - 类型安全的JavaScript
- **Ant Design 5.27.4** - UI组件库
- **Leaflet** - 地图组件
- **Recharts** - 数据可视化

## 📋 系统要求

- **Python 3.8+** (推荐3.9+)
- **Node.js 16+** (推荐18+)
- **Google Earth Engine账号** (必需)
- **8GB+ RAM** (推荐)
- **稳定的网络连接** (访问GEE服务)
- **支持Windows/Linux/Mac** (WSL也可用)

## 🚀 快速开始

### 方法一：一键启动（推荐）

**直接双击 `start.bat` 即可！**

这个批处理文件会自动：
- 设置代理（如果需要）
- 构建前端
- 启动后端服务
- 显示访问地址

### 方法二：完整配置流程

#### 1️⃣ 安装依赖
```cmd
# Windows用户 - 双击运行
install_all.bat

# Linux/Mac用户
chmod +x install_all.sh
./install_all.sh

# 或手动安装
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
```

#### 2️⃣ 配置环境变量
```cmd
# 复制环境配置文件
cp env.example .env

# 编辑 .env 文件，填入您的配置：
# - OPENAI_API_KEY: 您的OpenAI API密钥
# - GEE_PROJECT_ID: 您的GEE项目ID
# - 代理设置（如需要）
```

#### 3️⃣ 配置GEE认证（必需）
```cmd
python setup_gee_auth.py
```
**重要**：系统必须使用Google Earth Engine数据！
详细步骤请参考 [GEE_SETUP_GUIDE.md](GEE_SETUP_GUIDE.md)

#### 4️⃣ 启动系统
```cmd
# 方法1：直接双击
start.bat

# 方法2：Python启动
python start_system.py
```

### 🌐 访问地址
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 📖 详细文档

- [GEE认证指南](docs/GEE认证指南.md) - 配置Google Earth Engine
- [API文档](docs/API文档.md) - 后端API接口说明
- [使用指南](docs/使用指南.md) - 系统使用说明
- [GEE真实数据配置指南](GEE真实数据配置指南.md) - 真实数据配置

## 🔧 配置说明

### GEE认证配置
系统必须配置Google Earth Engine认证才能正常运行：

1. 注册Google Earth Engine账号
2. 创建Google Cloud项目
3. 启用Earth Engine API
4. 运行认证脚本

详细步骤请参考 [GEE认证指南](docs/GEE认证指南.md)

### 环境变量
创建 `.env` 文件（可选）：
```env
GEE_PROJECT_ID=your-project-id
DEBUG=False
```

## 📊 系统架构

```
├── backend/                    # 后端服务
│   ├── main.py                # FastAPI主应用
│   └── services/              # 业务服务层
│       ├── satellite_service.py           # 卫星图像服务
│       ├── image_analysis.py              # 图像分析服务
│       ├── energy_assessment.py           # 能源资源评估
│       ├── energy_ai_analysis.py          # 能源AI分析
│       ├── power_supply_analysis.py       # 供电方案分析
│       ├── power_supply_ai_analysis.py    # 供电AI分析
│       ├── energy_storage_analysis.py     # 储能布局分析
│       ├── energy_storage_ai_analysis.py  # 储能AI分析
│       ├── decision_analysis.py           # 决策分析
│       ├── decision_ai_analysis.py        # 决策AI分析
│       ├── promethee_mcgp_analysis.py     # PROMETHEE决策
│       ├── multimodal_analysis.py         # 多模态分析
│       └── multimodal_analysis_new.py     # 新版多模态分析
├── frontend/                  # 前端应用
│   ├── src/                  # React源码
│   │   ├── App.tsx           # 主应用
│   │   ├── App_simple.tsx    # 简化版应用
│   │   ├── App_advanced.tsx  # 高级版应用
│   │   └── components/       # 组件
│   │       ├── MapComponent.tsx      # 地图组件
│   │       ├── EnergyAssessment.tsx  # 能源评估
│   │       ├── DecisionAnalysis.tsx  # 决策分析
│   │       └── AnalysisResults.tsx   # 分析结果
│   └── build/                # 构建输出
├── docs/                     # 文档
├── notebooks/                # Jupyter示例
└── 启动脚本/                  # 各种启动脚本
    ├── start.bat            # 一键启动
    ├── install_all.bat      # 一键安装
    └── setup_gee_auth.py    # GEE认证
```

## 🌟 核心特性

### 🌍 卫星图像分析
- 基于Landsat 8/9和Sentinel-2数据
- 自动云量过滤和图像质量优化
- 多数据源备选方案
- 20公里覆盖半径
- AI图像识别和分析

### ⚡ 能源资源评估
- 太阳能辐射量AI计算
- 风能资源AI评估
- 水能潜力分析
- 可再生能源覆盖率计算
- 多模态数据融合分析

### 🔋 供电与储能分析
- 多种供电方案技术经济性分析
- 储能系统布局优化
- AI驱动的成本效益分析
- 可再生能源集成方案

### 🎯 智能决策分析
- PROMETHEE多准则决策方法
- AI增强的决策支持
- 经济因素分析
- 自然因素分析
- 综合评分排序

### 🤖 AI功能
- 多模态AI分析（图像+文本+数据）
- 智能图像识别
- 自动化决策支持
- 预测性分析

## 🚨 故障排除

### 常见问题

1. **GEE认证失败**
   ```cmd
   python setup_gee_auth.py
   ```

2. **依赖安装失败**
   ```cmd
   install_all.bat
   ```

3. **网络连接问题**
   - 检查代理设置
   - 确保能访问Google服务

4. **端口占用**
   - 后端：8000端口
   - 前端：3000端口

### 系统检查
```cmd
# 检查后端状态
python check_backend_status.py

# 检查网络连接
python check_network.py
```

## 📝 更新日志

### v1.0.0 (当前版本)
- ✅ 集成Google Earth Engine
- ✅ 多模态AI分析
- ✅ 交互式地图界面
- ✅ 完整的API文档
- ✅ 一键启动脚本

## 🤝 贡献

欢迎提交Issue和Pull Request！