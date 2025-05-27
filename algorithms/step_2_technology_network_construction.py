# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import os

def construct_technology_network():
    """构建技术网络"""
    # 定义文件路径
    input_path = os.path.join('..', 'data', 'step1_output', 'patent_data_selected_columns.xlsx')
    output_dir = os.path.join('..', 'data', 'step2_output')
    nodes_path = os.path.join(output_dir, 'technology_network_nodes.xlsx')
    edges_path = os.path.join(output_dir, 'technology_network_edges.xlsx')

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 读取数据
        df = pd.read_excel(input_path)
        original_count = len(df)

        # 初始化数据容器
        nodes = set()
        edges = set()

        # 处理IPC分类数据
        for _, row in df.iterrows():
            ipc_codes = []
            for code in str(row['IPC分类']).split("|"):
                code = code.strip()[:4]  # 取前四位并去除空格
                if code and len(code) >= 4:  # 有效IPC分类校验
                    ipc_codes.append(code)
                    nodes.add(code)

            # 生成无向边
            if len(ipc_codes) >= 2:
                for i in range(len(ipc_codes)):
                    for j in range(i+1, len(ipc_codes)):
                        edge = tuple(sorted([ipc_codes[i], ipc_codes[j]]))
                        edges.add(edge)

        # 生成数据框
        nodes_df = pd.DataFrame(sorted(nodes), columns=["节点"])
        edges_df = pd.DataFrame(sorted(edges), columns=["节点1", "节点2"])

        # 保存结果
        nodes_df.to_excel(nodes_path, index=False)
        edges_df.to_excel(edges_path, index=False)

        # 生成统计报告
        report = (
            f"技术网络构建完成\n原始专利数：{original_count}条\n"
            f"生成IPC节点数：{len(nodes)}个\n生成技术关联边数：{len(edges)}条\n"
            f"节点文件：{nodes_path}\n边文件：{edges_path}"
        )
        print(report)
        return report

    except Exception as e:
        error_msg = f"网络构建失败：{str(e)}"
        print(error_msg)
        return error_msg

if __name__ == '__main__':
    construct_technology_network()