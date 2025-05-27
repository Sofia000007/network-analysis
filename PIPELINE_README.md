# 网络数据处理与分析完整流程

本项目提供了两种方式来执行完整的网络数据处理与分析流程：

1. **Jupyter Notebook** (`network_analysis_pipeline.ipynb`) - 交互式执行
2. **Python 脚本** (`run_pipeline.py`) - 命令行批量执行

## 📋 流程概述

整个分析流程包含以下步骤：

### 第一步：数据预处理
- **1.1 数据清洗** - 清洗原始专利数据，标准化格式
- **1.2 去除个人申请** - 过滤掉个人专利申请，保留机构申请

### 第二步：网络构建
- **2.1 知识网络构建** - 基于专利引用关系构建知识网络
- **2.2 技术网络构建** - 基于IPC分类构建技术网络
- **2.3 协作研发网络构建** - 基于专利权人构建协作网络
- **2.4-2.6 跨层耦合网络** - 构建知识-技术、技术-协作、知识-协作耦合网络

### 第三步：网络权重计算
- **3.1 网络层权重计算** - 使用PageRank算法计算多层网络权重

### 第四步：结构洞分析
- **4.1 结构洞耦合计算** - 计算网络中的结构洞指标
- **4.2 结构洞数据库构建** - 整合结构洞数据
- **4.3 关键性指数计算** - 基于结构洞计算节点关键性

### 第五步：中心性分析
- **5.1 中心性耦合计算** - 计算多层网络中心性指标
- **5.2 中心性数据库构建** - 整合中心性数据
- **5.3 中心性指数计算** - 基于中心性计算节点重要性

### 第六步：综合分析
- **6.1 综合数据库构建** - 整合关键性和中心性指标，生成最终分析结果

## 🚀 快速开始

### 准备工作

1. **确保环境已配置**：
   ```bash
   # 使用 uv 安装依赖
   uv sync
   
   # 或使用 pip 安装
   pip install -r requirements.txt
   ```

2. **准备数据文件**：
   - 将原始专利数据文件命名为 `original_patent_data.xlsx`
   - 放置在 `./data/input/` 目录下
   - 确保数据包含以下列：`公开（公告）号`、`引文专利公开号`、`施引专利公开号`、`IPC分类`、`专利权人`

### 方式一：使用 Jupyter Notebook（推荐）

1. **启动 Jupyter**：
   ```bash
   # 使用项目提供的启动脚本
   ./start_jupyter.sh
   
   # 或直接启动
   jupyter notebook
   ```

2. **打开 notebook**：
   - 在浏览器中打开 `network_analysis_pipeline.ipynb`

3. **执行流程**：
   - 按顺序执行每个代码块
   - 可以查看每步的详细输出和结果
   - 支持单独执行某个步骤进行调试

### 方式二：使用命令行脚本

1. **执行完整流程**：
   ```bash
   python run_pipeline.py
   ```

2. **从特定步骤开始**：
   ```bash
   # 从步骤3（网络权重计算）开始
   python run_pipeline.py --step 3
   ```

3. **跳过错误继续执行**：
   ```bash
   # 遇到错误时跳过，继续执行后续步骤
   python run_pipeline.py --skip-errors
   ```

4. **查看帮助**：
   ```bash
   python run_pipeline.py --help
   ```

## 📁 输出文件结构

执行完成后，将在 `./data/` 目录下生成以下文件结构：

```
data/
├── input/
│   └── original_patent_data.xlsx          # 原始数据（用户提供）
├── step1_output/
│   ├── patent_data_cleaned.xlsx           # 清洗后的数据
│   └── patent_data_selected_columns.xlsx  # 去除个人申请后的数据
├── step2_output/
│   ├── knowledge_network_nodes.xlsx       # 知识网络节点
│   ├── knowledge_network_edges.xlsx       # 知识网络边
│   ├── technology_network_nodes.xlsx      # 技术网络节点
│   ├── technology_network_edges.xlsx      # 技术网络边
│   ├── collaborative_R&D_network_nodes.xlsx    # 协作网络节点
│   ├── collaborative_R&D_network_edges.xlsx    # 协作网络边
│   ├── knowledge-technology_network_*.xlsx     # 知识-技术耦合网络
│   ├── technology-collaborative_R&D_network_*.xlsx  # 技术-协作耦合网络
│   └── knowledge-collaborative_R&D_network_*.xlsx   # 知识-协作耦合网络
├── step3_output/
│   └── network_layer_weights.txt          # 网络层权重
├── step4_output/
│   ├── *_structural_hole_coupling.xlsx    # 各网络结构洞耦合
│   ├── structural_hole_coupling_database.xlsx  # 结构洞数据库
│   └── *_criticality_index.xlsx          # 各网络关键性指数
├── step5_output/
│   ├── *_centrality_coupling.xlsx        # 各网络中心性耦合
│   ├── centrality_coupling_database.xlsx # 中心性数据库
│   └── *_centrality_index.xlsx          # 各网络中心性指数
└── step6_output/
    └── criticality_and_centrality_database.xlsx  # 最终综合数据库
```

## 🔧 高级用法

### 单独执行某个步骤

在 Jupyter Notebook 中，可以单独执行任何步骤：

```python
# 例如：只执行知识网络构建
result = construct_knowledge_network()
print(result)
```

### 自定义参数

某些步骤支持参数自定义，可以修改相应的配置：

```python
# 在 step_3_network_layer_weights.py 中
config = {
    "max_iter": 1000,    # 最大迭代次数
    "tol": 1e-6,         # 收敛容差
    "alpha": 0.85,       # PageRank 阻尼系数
}
```

### 错误处理

如果某个步骤执行失败：

1. **检查输入文件**：确保前置步骤已正确执行
2. **查看错误信息**：根据错误提示检查数据格式
3. **单独调试**：在 notebook 中单独执行失败的步骤
4. **跳过错误**：使用 `--skip-errors` 参数继续执行

## 📊 结果分析

### 关键输出文件

1. **最终综合数据库** (`step6_output/criticality_and_centrality_database.xlsx`)
   - 包含所有节点的关键性和中心性指标
   - 可用于后续的网络分析和可视化

2. **网络层权重** (`step3_output/network_layer_weights.txt`)
   - 知识层、技术层、协作层的相对重要性权重

3. **各网络指数文件** (`step4_output/` 和 `step5_output/`)
   - 各个网络的关键性和中心性指数
   - 可用于识别重要节点和关键路径

### 数据可视化

生成的网络数据可以使用以下工具进行可视化：

- **NetworkX** - Python 网络分析库
- **Gephi** - 专业网络可视化软件
- **Cytoscape** - 生物网络分析工具
- **D3.js** - Web 端交互式可视化

## ⚠️ 注意事项

1. **数据质量**：确保原始数据质量良好，包含必要的列和有效数据
2. **计算资源**：大规模数据可能需要较长处理时间和较多内存
3. **依赖关系**：各步骤之间存在依赖关系，建议按顺序执行
4. **文件路径**：确保相对路径正确，脚本从项目根目录执行
5. **编码问题**：确保数据文件使用正确的字符编码（推荐 UTF-8）

## 🐛 常见问题

### Q: 执行时提示模块导入失败
A: 确保已正确安装所有依赖包，并且 `util` 目录在 Python 路径中

### Q: 数据文件读取失败
A: 检查文件路径和格式，确保 Excel 文件可以正常打开

### Q: 内存不足错误
A: 对于大规模数据，可以考虑分批处理或增加系统内存

### Q: 某个步骤执行时间过长
A: 这是正常现象，特别是去除个人申请和网络构建步骤

## 📞 技术支持

如果遇到问题，请：

1. 查看详细的错误信息
2. 检查数据格式和文件路径
3. 参考本文档的故障排除部分
4. 在 GitHub 上提交 Issue（如果适用）

## 📄 许可证

本项目采用 MIT 许可证，详见 `LICENSE` 文件。 