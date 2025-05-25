#!/bin/bash

# 网络数据处理与分析项目 - Jupyter Notebook 启动脚本

echo "🚀 启动网络分析 Jupyter Notebook..."

# 检查是否在项目根目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安装，请先安装 uv"
    exit 1
fi

# 同步依赖（如果需要）
echo "📦 检查依赖..."
uv sync

# 启动 Jupyter Notebook
echo "🌐 启动 Jupyter Notebook 服务器..."
echo "📝 Notebook 文件: network_analysis.ipynb"
echo "🔗 访问地址: http://localhost:8888"
echo "⏹️  停止服务: Ctrl+C"
echo ""

uv run jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser 