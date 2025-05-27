# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import os

def construct_knowledge_collaborative_network():
    """构建知识-合作研发双层网络"""
    # 定义文件路径
    input_path = os.path.join('..', 'data', 'step1_output', 'patent_data_selected_columns.xlsx')
    output_dir = os.path.join('..', 'data', 'step2_output')
    nodes_path = os.path.join(output_dir, 'knowledge-collaborative_R&D_network_nodes.xlsx')
    edges_path = os.path.join(output_dir, 'knowledge-collaborative_R&D_network_edges.xlsx')

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
            # 提取并清洗专利号
            patent_id = str(row['公开（公告）号']).strip()
            if not patent_id or patent_id == 'nan':
                continue

            # 添加知识层节点（层标识1）
            nodes.add((patent_id, 1))

            # 处理专利权人数据
            patentees = []
            for p in str(row['专利权人']).split("|"):
                p_clean = p.strip()
                if p_clean:
                    patentees.append(p_clean)
                    # 添加合作层节点（层标识3）
                    nodes.add((p_clean, 3))

            # 生成连边关系
            for patentee in patentees:
                edges.add((patent_id, patentee))

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
        knowledge_nodes = len([n for n in nodes if n[1]==1])
        collaborative_nodes = len([n for n in nodes if n[1]==3])
        report = (
            f"双层网络构建完成\n原始专利数：{original_count}条\n"
            f"知识节点数：{knowledge_nodes}个\n"
            f"合作机构数：{collaborative_nodes}个\n"
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
    construct_knowledge_collaborative_network()