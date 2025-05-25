# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import networkx as nx
import os


def construct_knowledge_network():
    """构建知识网络"""
    # 定义文件路径
    input_path = os.path.join('..', 'data', 'step1_output', 'patent_data_cleaned.xlsx')
    output_dir = os.path.join('..', 'data', 'step2_output')
    output_path = os.path.join(output_dir, 'knowledge_network.gexf')

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 读取清洗后的数据
        df = pd.read_csv(input_path)
        
        # 创建知识网络图
        G = nx.DiGraph()  # 使用有向图表示引用关系
        
        # 基于专利引用关系构建知识网络
        for _, row in df.iterrows():
            if pd.notna(row['引文专利公开号']) and pd.notna(row['施引专利公开号']):
                G.add_edge(row['引文专利公开号'], row['施引专利公开号'])
        
        # 保存网络
        nx.write_gexf(G, output_path)
        
        result = f"知识网络构建完成，结果已保存至：{output_path}"
        print(result)
        return result
        
    except Exception as e:
        error_msg = f"知识网络构建失败：{str(e)}"
        print(error_msg)
        return error_msg


if __name__ == '__main__':
    construct_knowledge_network()
