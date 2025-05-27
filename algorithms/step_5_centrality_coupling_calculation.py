# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import os


def calculate_centrality_coupling():
    """
    计算中心度耦合指标
    读取step2_output中的各网络节点和边数据
    计算中心度耦合指标并输出到step5_output文件夹
    """
    # 定义基础路径
    base_dir = os.path.join('..', 'data')
    input_dir = os.path.join(base_dir, 'step2_output')
    output_dir = os.path.join(base_dir, 'step5_output')

    # 网络配置
    networks = {
        'knowledge_network': {
            'nodes': 'knowledge_network_nodes.csv',
            'edges': 'knowledge_network_edges.csv',
            'output': 'knowledge_network_centrality_coupling.csv'
        },
        'technology_network': {
            'nodes': 'technology_network_nodes.csv',
            'edges': 'technology_network_edges.csv',
            'output': 'technology_network_centrality_coupling.csv'
        },
        'collaborative_R&D_network': {
            'nodes': 'collaborative_R&D_network_nodes.csv',
            'edges': 'collaborative_R&D_network_edges.csv',
            'output': 'collaborative_R&D_network_centrality_coupling.csv'
        }
    }

    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        results = {}

        for net_name, net_files in networks.items():
            # 构建文件路径
            nodes_path = os.path.join(input_dir, net_files['nodes'])
            edges_path = os.path.join(input_dir, net_files['edges'])
            output_path = os.path.join(output_dir, net_files['output'])

            # 检查文件是否存在
            if not os.path.exists(nodes_path):
                raise FileNotFoundError(f"节点文件不存在: {nodes_path}")
            if not os.path.exists(edges_path):
                raise FileNotFoundError(f"边文件不存在: {edges_path}")

            # 加载数据
            nodes_df = pd.read_csv(nodes_path)
            edges_df = pd.read_csv(edges_path)

            # 检查必要列是否存在
            required_node_cols = ['节点']
            required_edge_cols = ['节点1', '节点2']

            missing_node_cols = [col for col in required_node_cols if col not in nodes_df.columns]
            missing_edge_cols = [col for col in required_edge_cols if col not in edges_df.columns]

            if missing_node_cols:
                raise ValueError(f"{net_name}节点文件缺少必要列: {missing_node_cols}")
            if missing_edge_cols:
                raise ValueError(f"{net_name}边文件缺少必要列: {missing_edge_cols}")

            # 计算度中心性
            centrality_df = nodes_df[['节点']].copy()
            centrality_df['centrality_coupling'] = 0

            # 计算每个节点的连接数（使用'节点1'和'节点2'作为边端点）
            for idx, node in nodes_df['节点'].items():
                count = len(edges_df[
                                (edges_df['节点1'] == node) |
                                (edges_df['节点2'] == node)
                                ])
                centrality_df.at[idx, 'centrality_coupling'] = count

            # 保存结果
            centrality_df.to_csv(output_path, index=False)

            # 记录结果信息
            results[net_name] = {
                'output_file': net_files['output'],
                'node_count': len(centrality_df),
                'max_centrality': int(centrality_df['centrality_coupling'].max()),
                'min_centrality': int(centrality_df['centrality_coupling'].min())
            }

            print(f"已处理{net_name}，节点数: {len(centrality_df)}，最大中心度: {results[net_name]['max_centrality']}")

        # 汇总结果
        result_msg = (
            f"中心度耦合计算完成！\n"
            f"知识网络节点数: {results['knowledge_network']['node_count']}\n"
            f"技术网络节点数: {results['technology_network']['node_count']}\n"
            f"合作研发网络节点数: {results['collaborative_R&D_network']['node_count']}\n"
            f"结果已保存至: {output_dir}"
        )

        print(result_msg)
        return result_msg

    except FileNotFoundError as e:
        error_msg = f"文件错误: {str(e)}"
        print(error_msg)
        return error_msg
    except ValueError as ve:
        error_msg = f"数据验证错误: {str(ve)}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"处理过程中发生错误: {str(e)}"
        print(error_msg)
        return error_msg


if __name__ == '__main__':
    calculate_centrality_coupling()