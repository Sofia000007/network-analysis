# %% [markdown]
# # 基于多层耦合创新网络的关键核心技术识别
# 
# 本脚本实现了基于多层耦合创新网络的关键核心技术识别的完整流程。

# %% [code]
# 导入基础依赖
import pandas as pd
import numpy as np
from pathlib import Path

# 设置数据路径
DATA_DIR = Path("data")
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"

# 确保输出目录存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ## 1. 原始数据清洗
# 
# - 将所有英文字母转化为小写字母
# - 只保留关键列数据
# - 删除无效数据和重复值
# - 删除个人申请专利

# %% [code]
from algorithms.step_1_clean_patent_data import clean_patent_data
from algorithms.step_1_remove_personal_application import remove_personal_applications

print("🚀 开始数据清洗...")
clean_patent_data()
remove_personal_applications()
print("✅ 数据清洗完成！")

# %% [markdown]
# ## 2. 多层耦合创新网络构建
# 
# 构建三个网络层：
# - 知识网络
# - 技术网络
# - 合作研发网络
# 
# 构建三个层间网络：
# - 知识-技术网络
# - 知识-合作研发网络
# - 技术-合作研发网络

# %% [code]
# 导入网络构建函数
from algorithms.step_2_knowledge_network_construction import construct_knowledge_network
from algorithms.step_2_technology_network_construction import construct_technology_network
from algorithms.step_2_collaborative_R&D_network_construction import construct_collaborative_network
from algorithms.step_2_knowledge_technology_network_construction import construct_knowledge_technology_network
from algorithms.step_2_knowledge_collaborative_R&D_network_construction import construct_knowledge_collaborative_network
from algorithms.step_2_technology_collaborative_R&D_network_construction import construct_technology_collaborative_network

print("🚀 开始构建多层耦合创新网络...")

# 构建三个网络层
construct_knowledge_network()
construct_technology_network()
construct_collaborative_network()

# 构建三个层间网络
construct_knowledge_technology_network()
construct_knowledge_collaborative_network()
construct_technology_collaborative_network()

print("✅ 多层耦合创新网络构建完成！")

# %% [markdown]
# ## 3. 网络层权重计算
# 
# 使用多pagerank中心性算法计算网络层权重

# %% [code]
from algorithms.step_3_network_layer_weights import calculate_network_layer_weights

print("🚀 开始计算网络层权重...")
calculate_network_layer_weights()
print("✅ 网络层权重计算完成！")

# %% [markdown]
# ## 4. 节点关键性计算
# 
# 计算节点在多层耦合创新网络中的结构洞

# %% [code]
from algorithms.step_4_criticality_index_calculation import calculate_criticality_index
from algorithms.step_4_structural_hole_coupling_calculation import calculate_structural_hole_coupling
from algorithms.step_4_structural_hole_coupling_database_construction import construct_structural_hole_database

print("🚀 开始计算节点关键性...")

# 计算结构洞耦合
calculate_structural_hole_coupling()

# 构建结构洞耦合数据库
construct_structural_hole_database()

# 计算关键性指标
calculate_criticality_index()

print("✅ 节点关键性计算完成！")

# %% [markdown]
# ## 5. 节点核心性计算
# 
# 计算节点在多层耦合创新网络中的中心度

# %% [code]
from algorithms.step_5_centrality_index_calculation import calculate_centrality_index
from algorithms.step_5_centrality_coupling_calculation import calculate_centrality_coupling
from algorithms.step_5_centrality_coupling_database_construction import construct_centrality_database

print("🚀 开始计算节点核心性...")

# 计算中心性耦合
calculate_centrality_coupling()

# 构建中心性耦合数据库
construct_centrality_database()

# 计算核心性指标
calculate_centrality_index()

print("✅ 节点核心性计算完成！")

# %% [markdown]
# ## 6. 指标权重计算
# 
# 构建关键性和核心性数据库，计算指标权重

# %% [code]
from algorithms.step_6_index_weights import calculate_index_weights
from algorithms.step_6_criticality_and_centrality_database_construction import construct_criticality_centrality_database

print("🚀 开始计算指标权重...")

# 构建关键性和核心性数据库
construct_criticality_centrality_database()

# 计算指标权重
calculate_index_weights()

print("✅ 指标权重计算完成！")

# %% [markdown]
# ## 7. 节点关键核心性计算
# 
# 读取关键性和核心性数据库、指标权重，计算节点关键核心性

# %% [code]
from algorithms.step_7_criticality_centrality_index_calculation import calculate_criticality_centrality_index

print("🚀 开始计算节点关键核心性...")
calculate_criticality_centrality_index()
print("✅ 节点关键核心性计算完成！")

# %% [markdown]
# ## 总结
# 
# 本脚本实现了完整的网络分析流程：
# 
# 1. **原始数据清洗**: 清理专利数据，删除个人申请专利
# 2. **多层耦合创新网络构建**: 构建三个网络层和三个层间网络
# 3. **网络层权重计算**: 使用多pagerank中心性算法计算网络层权重
# 4. **节点关键性计算**: 计算结构洞耦合和关键性指标
# 5. **节点核心性计算**: 计算中心性耦合和核心性指标
# 6. **指标权重计算**: 构建关键性和核心性数据库，计算指标权重
# 7. **节点关键核心性计算**: 最终计算节点的关键核心性
# 
# 每个步骤都有相应的函数实现，可以根据需要单独运行或按顺序执行完整流程。 