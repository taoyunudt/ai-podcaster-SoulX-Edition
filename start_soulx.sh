#!/bin/bash

# SoulX Podcast 启动脚本
# 同时启动 SoulX-Podcast API 和 ai-podcaster API

echo "=================================================="
echo "🎙️ SoulX Podcast 启动脚本"
echo "=================================================="
echo ""

# 检查必要的目录
if [ ! -d "~/projects/SoulX-Podcast" ]; then
    echo "❌ 错误: SoulX-Podcast 目录不存在"
    exit 1
fi

if [ ! -d "~/projects/ai-podcaster" ]; then
    echo "❌ 错误: ai-podcaster 目录不存在"
    exit 1
fi

# 检查端口是否被占用
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

if check_port 8000; then
    echo "⚠️  警告: 端口 8000 已被占用"
    echo "   可能已有服务在运行"
    read -p "   是否继续启动? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# 启动 SoulX-Podcast API
echo ""
echo "📦 启动 SoulX-Podcast API..."
echo "   端口: 8000"
echo "   模型: SoulX-Podcast-1.7B"
echo ""

cd ~/projects/SoulX-Podcast
source venv/bin/activate

# 后台启动 SoulX-Podcast
python run_api.py --model pretrained_models/SoulX-Podcast-1.7B --port 8000 > ~/projects/SoulX-Podcast/logs/api.log 2>&1 &
SOULX_PID=$!

echo "✅ SoulX-Podcast API 已启动 (PID: $SOULX_PID)"
echo "   日志: ~/projects/SoulX-Podcast/logs/api.log"
echo ""

# 等待 SoulX-Podcast 启动
echo "⏳ 等待 SoulX-Podcast API 启动..."
sleep 10

# 检查 SoulX-Podcast 是否成功启动
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ SoulX-Podcast API 启动成功！"
else
    echo "❌ SoulX-Podcast API 启动失败"
    echo "   请检查日志: tail -f ~/projects/SoulX-Podcast/logs/api.log"
    exit 1
fi

echo ""
echo "=================================================="
echo "🚀 服务已启动完成！"
echo "=================================================="
echo ""
echo "📱 访问地址："
echo "   • SoulX Edition:  http://localhost:8001/soulx"
echo "   • 标准版:        http://localhost:8001"
echo "   • SoulX API:     http://localhost:8000/health"
echo "   • SoulX Docs:    http://localhost:8000/docs"
echo ""
echo "📋 快捷命令："
echo "   • 查看日志:     tail -f ~/projects/SoulX-Podcast/logs/api.log"
echo "   • 停止服务:     kill $SOULX_PID"
echo "   • 健康检查:     curl http://localhost:8000/health"
echo ""
echo "=================================================="
echo ""

# 保存 PID 到文件
echo $SOULX_PID > /tmp/soulx_api.pid
echo "PID 已保存到: /tmp/soulx_api.pid"

echo "💡 提示: 按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
wait
