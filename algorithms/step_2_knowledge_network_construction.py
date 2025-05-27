# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import re
import os

def construct_knowledge_network():
    """构建知识网络"""
    # 定义文件路径
    input_path = os.path.join('..', 'data', 'step1_output', 'patent_data_selected_columns.csv')
    output_dir = os.path.join('..', 'data', 'step2_output')
    nodes_path = os.path.join(output_dir, 'knowledge_network_nodes.csv')
    edges_path = os.path.join(output_dir, 'knowledge_network_edges.csv')

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 读取数据
        df = pd.read_csv(input_path)
        original_records = len(df)

        # 定义文本清洗函数
        def clean_text(text):
            if pd.isna(text):
                return ""
            cleaned = re.sub(r"\(.*?\)|（.*?）", "", str(text)).strip()
            return cleaned if cleaned else ""

        # 初始化数据容器
        nodes = set()
        edges = set()

        # 处理数据
        for _, row in df.iterrows():
            patent_num = clean_text(row['公开（公告）号'])
            citations = [x.strip() for x in clean_text(row['引文专利公开号']).split("|") if x.strip()]
            citing = [x.strip() for x in clean_text(row['施引专利公开号']).split("|") if x.strip()]

            # 添加节点和边
            nodes.add(patent_num)
            for target in citations + citing:
                if target:
                    nodes.add(target)
                    edge = tuple(sorted([patent_num, target]))
                    edges.add(edge)

        # 生成数据框
        nodes_df = pd.DataFrame(sorted(nodes), columns=["节点"])
        edges_df = pd.DataFrame(sorted(edges), columns=["节点1", "节点2"])

        # 保存结果
        nodes_df.to_csv(nodes_path, index=False)
        edges_df.to_csv(edges_path, index=False)

        # 生成统计报告
        report = (
            f"网络构建完成\n原始专利数：{original_records}条\n"
            f"生成节点数：{len(nodes)}个\n生成边数：{len(edges)}条\n"
            f"节点文件：{nodes_path}\n边文件：{edges_path}"
        )
        print(report)
        return report

    except Exception as e:
        error_msg = f"网络构建失败：{str(e)}"
        print(error_msg)
        return error_msg

if __name__ == '__main__':
    construct_knowledge_network()