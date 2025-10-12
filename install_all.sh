#!/bin/bash
# 数据中心智能选址与能源优化系统 - 一键安装脚本 (Linux/Mac)

echo "🚀 数据中心智能选址与能源优化系统 - 安装脚本"
echo "=================================================="

# 检查Python版本
echo "🔍 检查Python版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python3 未安装，请先安装Python 3.8+"
    exit 1
fi

# 检查Node.js版本
echo "🔍 检查Node.js版本..."
node --version
if [ $? -ne 0 ]; then
    echo "❌ Node.js 未安装，请先安装Node.js 16+"
    exit 1
fi

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Python依赖安装失败"
    exit 1
fi

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "❌ 前端依赖安装失败"
    exit 1
fi

# 构建前端
echo "🔨 构建前端..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ 前端构建失败"
    exit 1
fi

cd ..

# 复制环境配置文件
echo "📋 设置环境配置..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "✅ 已创建 .env 配置文件"
    echo "⚠️  请编辑 .env 文件，填入您的API密钥和配置"
else
    echo "✅ .env 配置文件已存在"
fi

echo ""
echo "🎉 安装完成！"
echo "=================================================="
echo "📋 下一步："
echo "1. 编辑 .env 文件，填入您的配置"
echo "2. 运行 python setup_gee_auth.py 设置GEE认证"
echo "3. 运行 ./start.sh 启动系统"
echo "=================================================="