# Copyright © dongbingxue. All rights reserved.
# License: MIT

import os
import pandas as pd
from tqdm import tqdm


def calculate_criticality():
    """计算多网络关键性指数"""
    # 定义文件路径
    input_db_path = os.path.join('..', 'data', 'step4_output', 'structural_hole_coupling_database.xlsx')
    input_network_dir = os.path.join('..', 'data', 'step2_output')
    output_dir = os.path.join('..', 'data', 'step4_output')

    # 网络配置信息
    network_config = {
        'knowledge_network': {
            'nodes_file': 'knowledge_network_nodes.xlsx',
            'edge_files': [
                'knowledge-technology_network_edges.xlsx',
                'knowledge-collaborative_R&D_network_edges.xlsx'
            ],
            'output_file': 'knowledge_network_criticality_index.xlsx'
        },
        'technology_network': {
            'nodes_file': 'technology_network_nodes.xlsx',
            'edge_files': [
                'knowledge-technology_network_edges.xlsx',
                'technology-collaborative_R&D_network_edges.xlsx'
            ],
            'output_file': 'technology_network_criticality_index.xlsx'
        },
        'collaborative_R&D_network': {
            'nodes_file': 'collaborative_R&D_network_nodes.xlsx',
            'edge_files': [
                'knowledge-collaborative_R&D_network_edges.xlsx',
                'technology-collaborative_R&D_network_edges.xlsx'
            ],
            'output_file': 'collaborative_R&D_network_criticality_index.xlsx'
        }
    }

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 加载结构洞数据库
        structural_db = pd.read_excel(input_db_path)

        # 处理每个网络类型
        for network_type, config in network_config.items():
            # 加载网络节点数据
            nodes_path = os.path.join(input_network_dir, config['nodes_file'])
            nodes_df = pd.read_excel(nodes_path)

            # 加载相关连边数据
            edge_dfs = []
            for edge_file in config['edge_files']:
                edge_path = os.path.join(input_network_dir, edge_file)
                edge_dfs.append(pd.read_excel(edge_path))

            # 计算关键性指数
            criticality_indices = []
            for _, node_row in tqdm(nodes_df.iterrows(), total=len(nodes_df), desc=f"处理{network_type}"):
                node = node_row['节点']

                # 获取节点核心值
                node_value = structural_db.loc[
                    structural_db['节点'] == node,
                    'structural_hole_coupling*weights'
                ].sum()

                # 获取关联节点
                related_nodes = set()
                for edge_df in edge_dfs:
                    mask = (edge_df['节点1'] == node) | (edge_df['节点2'] == node)
                    related_nodes.update(edge_df[mask]['节点1'].tolist())
                    related_nodes.update(edge_df[mask]['节点2'].tolist())
                related_nodes.discard(node)  # 排除自身

                # 计算关联值
                related_value = structural_db[
                    structural_db['节点'].isin(related_nodes)
                ]['structural_hole_coupling*weights'].sum()

                criticality_indices.append(node_value + related_value)

            # 生成结果文件
            result_df = pd.DataFrame({
                '节点': nodes_df['节点'],
                'criticality_index': criticality_indices
            })

            # 保存结果
            output_path = os.path.join(output_dir, config['output_file'])
            result_df.to_excel(output_path, index=False)

        # 生成报告
        report = (
            "关键性指数计算完成\n"
            f"知识网络结果: {network_config['knowledge_network']['output_file']}\n"
            f"技术网络结果: {network_config['technology_network']['output_file']}\n"
            f"合作研发网络结果: {network_config['collaborative_R&D_network']['output_file']}\n"
            f"结果文件已保存至: {output_dir}"
        )
        print(report)
        return report

    except Exception as e:
        error_msg = f"计算失败: {str(e)}"
        print(error_msg)
        return error_msg


if __name__ == '__main__':
    calculate_criticality()