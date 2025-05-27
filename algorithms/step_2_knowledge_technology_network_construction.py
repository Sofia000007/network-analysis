# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import os

def construct_knowledge_technology_network():
    """构建知识-技术双层网络"""
    # 定义文件路径
    input_path = os.path.join('..', 'data', 'step1_output', 'patent_data_selected_columns.csv')
    output_dir = os.path.join('..', 'data', 'step2_output')
    nodes_path = os.path.join(output_dir, 'knowledge-technology_network_nodes.csv')
    edges_path = os.path.join(output_dir, 'knowledge-technology_network_edges.csv')

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 读取数据（不包含表头）
        df = pd.read_csv(input_path, header=None).iloc[1:]  # 跳过首行表头

        # 数据容器
        nodes = set()
        edges = set()

        # 处理每行数据
        for _, row in df.iterrows():
            # 提取并清洗专利号
            patent_id = str(row[0]).strip()
            if not patent_id:
                continue

            # 添加知识层节点（层标识1）
            nodes.add((patent_id, 1))

            # 处理IPC分类数据
            ipc_codes = []
            for code in str(row[3]).split("|"):  # 第四列为IPC分类
                code = code.strip()[:4]  # 保留前四位
                if code and len(code) >= 4:
                    ipc_codes.append(code)
                    # 添加技术层节点（层标识2）
                    nodes.add((code, 2))

            # 生成连边关系
            for ipc in ipc_codes:
                edges.add((patent_id, ipc))

        # 生成数据框
        nodes_df = pd.DataFrame(
            sorted(nodes, key=lambda x: x[1]),  # 按层排序
            columns=["节点", "网络层"]
        )
        edges_df = pd.DataFrame(
            sorted(edges),
            columns=["节点1", "节点2"]
        )

        # 保存结果
        nodes_df.to_csv(nodes_path, index=False)
        edges_df.to_csv(edges_path, index=False)

        # 统计报告
        report = (
            f"双层网络构建完成\n原始记录数：{len(df)}条\n"
            f"知识节点数：{len([n for n in nodes if n[1]==1])}个\n"
            f"技术节点数：{len([n for n in nodes if n[1]==2])}个\n"
            f"关联边数：{len(edges)}条\n"
            f"节点文件：{nodes_path}\n边文件：{edges_path}"
        )
        print(report)
        return report

    except Exception as e:
        error_msg = f"网络构建失败：{str(e)}"
        print(error_msg)
        return error_msg

if __name__ == '__main__':
    construct_knowledge_technology_network()