#!/bin/bash
# 数据中心智能选址与能源优化系统 - 启动脚本 (Linux/Mac)

echo "🚀 启动数据中心智能选址与能源优化系统"
echo "=================================================="

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 配置文件"
    echo "📋 请先运行: cp env.example .env"
    echo "📝 然后编辑 .env 文件，填入您的配置"
    exit 1
fi

# 设置代理（如果需要）
echo "🌐 设置代理..."
source .env
if [ ! -z "$HTTP_PROXY" ]; then
    export HTTP_PROXY=$HTTP_PROXY
    export HTTPS_PROXY=$HTTPS_PROXY
    export http_proxy=$http_proxy
    export https_proxy=$https_proxy
    echo "✅ 代理已设置: $HTTP_PROXY"
fi

# 启动后端服务
echo "🔧 启动后端服务..."
python3 start_system.py &
BACKEND_PID=$!

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 检查后端是否启动成功
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
else
    echo "❌ 后端服务启动失败"
    exit 1
fi

# 启动前端服务
echo "🎨 启动前端服务..."
cd frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 系统启动成功！"
echo "=================================================="
echo "🌐 访问地址:"
echo "   前端界面: http://localhost:3000"
echo "   后端API:  http://localhost:8000"
echo "   API文档:  http://localhost:8000/docs"
echo ""
echo "⏹️  停止服务: 按 Ctrl+C"
echo "=================================================="

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ 服务已停止'; exit 0" INT

# 保持脚本运行
wait
