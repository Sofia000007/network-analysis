# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
from pathlib import Path


def calculate_centrality_coupling(input_dir=None, output_dir=None):
    """计算中心度耦合指标
    
    Args:
        input_dir (str/Path): 输入目录路径，默认'../data/step2_output'
        output_dir (str/Path): 输出目录路径，默认'../data/step5_output'
    
    Returns:
        str: 处理结果报告
    """
    # 设置默认路径
    input_dir = Path(input_dir) if input_dir else Path('../data/step2_output')
    output_dir = Path(output_dir) if output_dir else Path('../data/step5_output')

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
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        for net_name, net_files in networks.items():
            # 构建文件路径
            nodes_path = input_dir / net_files['nodes']
            edges_path = input_dir / net_files['edges']
            output_path = output_dir / net_files['output']

            # 检查文件是否存在
            if not nodes_path.exists():
                raise FileNotFoundError(f"节点文件不存在: {nodes_path}")
            if not edges_path.exists():
                raise FileNotFoundError(f"边文件不存在: {edges_path}")

            # 加载数据
            nodes_df = pd.read_csv(nodes_path, encoding='utf-8')
            edges_df = pd.read_csv(edges_path, encoding='utf-8')

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
            centrality_df.to_csv(output_path, index=False, encoding='utf-8-sig')

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
    import argparse
    
    parser = argparse.ArgumentParser(description='计算中心度耦合指标')
    parser.add_argument('--input_dir', type=str, help='输入目录路径')
    parser.add_argument('--output_dir', type=str, help='输出目录路径')
    
    args = parser.parse_args()
    calculate_centrality_coupling(args.input_dir, args.output_dir)