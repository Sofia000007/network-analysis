# 网络数据处理与分析项目

这是一个基于 Python 3.11 的网络数据处理与分析项目，使用 uv 进行环境管理。

## 环境要求

- Python 3.11+
- uv (用于包管理)

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 运行 Python 脚本

```bash
uv run python your_script.py
```

### 3. 启动 Jupyter Notebook

```bash
uv run jupyter notebook
```

### 4. 进入虚拟环境

```bash
source .venv/bin/activate
```

## 已安装的主要依赖

### 数据处理与分析
- **pandas**: 数据处理和分析
- **numpy**: 数值计算
- **matplotlib**: 数据可视化
- **seaborn**: 统计数据可视化

### 网络相关
- **networkx**: 网络分析
- **requests**: HTTP 请求
- **beautifulsoup4**: 网页解析
- **scapy**: 网络包分析
- **ipaddress**: IP 地址处理

### 开发工具
- **pytest**: 单元测试
- **black**: 代码格式化
- **flake8**: 代码检查
- **mypy**: 类型检查
- **jupyter**: 交互式开发环境

## 项目结构

```
network/
├── network/           # 主要的 Python 包
│   └── __init__.py
├── data/             # 数据文件
├── util/             # 工具函数
├── pyproject.toml    # 项目配置
├── uv.lock          # 依赖锁定文件
└── README.md        # 项目说明
```

## 使用示例

```python
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# 创建一个简单的网络图
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1)])

# 绘制网络图
nx.draw(G, with_labels=True)
plt.show()
```
