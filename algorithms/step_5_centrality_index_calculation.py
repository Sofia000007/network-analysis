# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
from pathlib import Path


def calculate_centrality_index(step2_dir=None, step5_dir=None):
    """计算中心度指数
    
    Args:
        step2_dir (str/Path): step2输出目录路径，默认'../data/step2_output'
        step5_dir (str/Path): step5输出目录路径，默认'../data/step5_output'
    
    Returns:
        str: 处理结果报告
    """
    # 设置默认路径
    step2_dir = Path(step2_dir) if step2_dir else Path('../data/step2_output')
    step5_dir = Path(step5_dir) if step5_dir else Path('../data/step5_output')

    # 网络配置
    networks = {
        'knowledge_network': {
            'nodes_file': 'knowledge_network_nodes.csv',
            'edge_files': [
                'knowledge-technology_network_edges.csv',
                'knowledge-collaborative_R&D_network_edges.csv'
            ],
            'output_file': 'knowledge_network_centrality_index.csv'
        },
        'technology_network': {
            'nodes_file': 'technology_network_nodes.csv',
            'edge_files': [
                'knowledge-technology_network_edges.csv',
                'technology-collaborative_R&D_network_edges.csv'
            ],
            'output_file': 'technology_network_centrality_index.csv'
        },
        'collaborative_R&D_network': {
            'nodes_file': 'collaborative_R&D_network_nodes.csv',
            'edge_files': [
                'knowledge-collaborative_R&D_network_edges.csv',
                'technology-collaborative_R&D_network_edges.csv'
            ],
            'output_file': 'collaborative_R&D_network_centrality_index.csv'
        }
    }

    try:
        # 确保输出目录存在
        step5_dir.mkdir(parents=True, exist_ok=True)

        # 加载中心度数据库
        centrality_db_path = step5_dir / 'centrality_coupling_database.csv'
        if not centrality_db_path.exists():
            raise FileNotFoundError(f"中心度数据库文件不存在：{centrality_db_path}")
            
        centrality_db = pd.read_csv(centrality_db_path, encoding='utf-8')

        # 检查必要列是否存在
        required_db_cols = ['节点', 'centrality_coupling*weights']
        missing_db_cols = [col for col in required_db_cols if col not in centrality_db.columns]
        if missing_db_cols:
            raise ValueError(f"中心度数据库缺少必要列: {missing_db_cols}")

        # 处理每个网络
        for net_name, net_config in networks.items():
            print(f"\n正在处理{net_name}...")

            # 加载节点数据
            nodes_path = step2_dir / net_config['nodes_file']
            if not nodes_path.exists():
                raise FileNotFoundError(f"节点文件不存在：{nodes_path}")
                
            nodes_df = pd.read_csv(nodes_path, encoding='utf-8')

            # 检查节点列是否存在
            if '节点' not in nodes_df.columns:
                raise ValueError(f"{net_name}节点文件缺少'节点'列")

            # 加载边数据
            edge_dfs = []
            for edge_file in net_config['edge_files']:
                edge_path = step2_dir / edge_file
                if not edge_path.exists():
                    raise FileNotFoundError(f"边文件不存在：{edge_path}")
                    
                edge_df = pd.read_csv(edge_path, encoding='utf-8')

                # 检查边列是否存在
                if not all(col in edge_df.columns for col in ['节点1', '节点2']):
                    raise ValueError(f"{edge_file}缺少必要列('节点1'或'节点2')")

                edge_dfs.append(edge_df)

            # 计算每个节点的中心度指数
            centrality_indices = []
            for _, node_row in nodes_df.iterrows():
                node = node_row['节点']

                # 获取节点自身的中心度值
                node_value = centrality_db.loc[
                    centrality_db['节点'] == node,
                    'centrality_coupling*weights'
                ].sum()

                # 获取关联节点
                related_nodes = set()
                for edge_df in edge_dfs:
                    # 找到与当前节点相连的所有边
                    mask = (edge_df['节点1'] == node) | (edge_df['节点2'] == node)
                    connected_edges = edge_df[mask]

                    # 提取所有关联节点
                    related_nodes.update(connected_edges['节点1'].tolist())
                    related_nodes.update(connected_edges['节点2'].tolist())

                # 排除自身并去重
                related_nodes.discard(node)

                # 计算关联节点的中心度总和
                related_value = centrality_db[
                    centrality_db['节点'].isin(related_nodes)
                ]['centrality_coupling*weights'].sum()

                # 计算中心度指数
                centrality_index = node_value + (related_value if not pd.isna(related_value) else 0)
                centrality_indices.append(centrality_index)

            # 创建结果DataFrame
            result_df = pd.DataFrame({
                '节点': nodes_df['节点'],
                'centrality_index': centrality_indices
            })

            # 保存结果
            output_path = step5_dir / net_config['output_file']
            result_df.to_csv(output_path, index=False, encoding='utf-8-sig')

            # 打印统计信息
            print(f"已保存{net_name}中心度指数到: {output_path}")
            print(f"节点数: {len(result_df)}")
            print(f"最小中心度指数: {result_df['centrality_index'].min():.4f}")
            print(f"最大中心度指数: {result_df['centrality_index'].max():.4f}")
            print(f"平均中心度指数: {result_df['centrality_index'].mean():.4f}")

        # 返回成功消息
        result_msg = (
            f"中心度指数计算完成！\n"
            f"结果已保存至: {step5_dir}\n"
            f"包含知识网络、技术网络和合作研发网络的中心度指数文件"
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
    
    parser = argparse.ArgumentParser(description='计算中心度指数')
    parser.add_argument('--step2_dir', type=str, help='step2输出目录路径')
    parser.add_argument('--step5_dir', type=str, help='step5输出目录路径')
    
    args = parser.parse_args()
    calculate_centrality_index(args.step2_dir, args.step5_dir)