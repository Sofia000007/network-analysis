# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import networkx as nx
import os


def construct_technology_network():
    """构建技术网络"""
    # 定义文件路径
    input_path = os.path.join('..', 'data', 'step1_output', 'patent_data_cleaned.xlsx')
    output_dir = os.path.join('..', 'data', 'step2_output')
    output_path = os.path.join(output_dir, 'technology_network.gexf')

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 读取清洗后的数据
        df = pd.read_csv(input_path)
        
        # 创建技术网络图
        G = nx.Graph()
        
        # 基于IPC分类构建技术网络
        # 这里是一个简化的示例，实际实现需要根据具体需求调整
        ipc_classes = df['IPC分类'].dropna().unique()
        
        for ipc in ipc_classes:
            G.add_node(ipc)
        
        # 保存网络
        nx.write_gexf(G, output_path)
        
        result = f"技术网络构建完成，结果已保存至：{output_path}"
        print(result)
        return result
        
    except Exception as e:
        error_msg = f"技术网络构建失败：{str(e)}"
        print(error_msg)
        return error_msg


if __name__ == '__main__':
    construct_technology_network()
