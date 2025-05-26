# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import os
from itertools import product


def construct_tech_collaborative_network():
    """构建技术-合作研发双层网络"""
    # 定义文件路径
    input_path = os.path.join('..', 'data', 'step1_output', 'patent_data_selected_columns.xlsx')
    output_dir = os.path.join('..', 'data', 'step2_output')
    nodes_path = os.path.join(output_dir, 'technology-collaborative_R&D_network_nodes.xlsx')
    edges_path = os.path.join(output_dir, 'technology-collaborative_R&D_network_edges.xlsx')

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 读取数据
        df = pd.read_excel(input_path)
        original_count = len(df)

        # 初始化数据容器
        nodes = set()
        edges = set()

        # 处理每行数据
        for _, row in df.iterrows():
            # 处理技术层数据（IPC分类）
            ipc_codes = [code.strip()[:4] for code in str(row['IPC分类']).split("|") if code.strip()[:4]]

            # 处理合作层数据（专利权人）
            patentees = [p.strip() for p in str(row['专利权人']).split("|") if p.strip()]

            # 添加技术层节点（层标识2）
            nodes.update([(ipc, 2) for ipc in ipc_codes if len(ipc) >= 4])

            # 添加合作层节点（层标识3）
            nodes.update([(patentee, 3) for patentee in patentees if patentee])

            # 生成跨层全连接边
            if ipc_codes and patentees:
                for ipc, patentee in product(ipc_codes, patentees):
                    edges.add((ipc, patentee))

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
        nodes_df.to_excel(nodes_path, index=False)
        edges_df.to_excel(edges_path, index=False)

        # 统计报告
        tech_nodes = len([n for n in nodes if n[1] == 2])
        collab_nodes = len([n for n in nodes if n[1] == 3])
        report = (
            f"双层网络构建完成\n原始专利数：{original_count}条\n"
            f"技术节点数：{tech_nodes}个（IPC前4位）\n"
            f"合作机构数：{collab_nodes}个\n"
            f"跨层关联边数：{len(edges)}条\n"
            f"节点文件：{nodes_path}\n边文件：{edges_path}"
        )
        print(report)
        return report

    except Exception as e:
        error_msg = f"网络构建失败：{str(e)}"
        print(error_msg)
        return error_msg


if __name__ == '__main__':
    construct_tech_collaborative_network()