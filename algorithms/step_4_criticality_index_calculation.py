# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
from pathlib import Path
from tqdm import tqdm


def calculate_criticality(step2_dir=None, step4_dir=None):
    """计算多网络关键性指数
    
    Args:
        step2_dir (str/Path): step2输出目录路径，默认'../data/step2_output'
        step4_dir (str/Path): step4输出目录路径，默认'../data/step4_output'
    
    Returns:
        str: 处理结果报告
    """
    # 设置默认路径
    step2_dir = Path(step2_dir) if step2_dir else Path('../data/step2_output')
    step4_dir = Path(step4_dir) if step4_dir else Path('../data/step4_output')

    # 输入输出文件路径
    input_db_path = step4_dir / 'structural_hole_coupling_database.csv'

    # 网络配置信息
    network_config = {
        'knowledge_network': {
            'nodes_file': 'knowledge_network_nodes.csv',
            'edge_files': [
                'knowledge-technology_network_edges.csv',
                'knowledge-collaborative_R&D_network_edges.csv'
            ],
            'output_file': 'knowledge_network_criticality_index.csv'
        },
        'technology_network': {
            'nodes_file': 'technology_network_nodes.csv',
            'edge_files': [
                'knowledge-technology_network_edges.csv',
                'technology-collaborative_R&D_network_edges.csv'
            ],
            'output_file': 'technology_network_criticality_index.csv'
        },
        'collaborative_R&D_network': {
            'nodes_file': 'collaborative_R&D_network_nodes.csv',
            'edge_files': [
                'knowledge-collaborative_R&D_network_edges.csv',
                'technology-collaborative_R&D_network_edges.csv'
            ],
            'output_file': 'collaborative_R&D_network_criticality_index.csv'
        }
    }

    try:
        # 确保输出目录存在
        step4_dir.mkdir(parents=True, exist_ok=True)

        # 检查并加载结构洞数据库
        if not input_db_path.exists():
            raise FileNotFoundError(f"结构洞数据库文件不存在：{input_db_path}")
            
        structural_db = pd.read_csv(input_db_path, encoding='utf-8')

        # 检查必要列是否存在
        required_cols = ['节点', 'structural_hole_coupling*weights']
        missing_cols = [col for col in required_cols if col not in structural_db.columns]
        if missing_cols:
            raise ValueError(f"结构洞数据库缺少必要列：{missing_cols}")

        # 处理每个网络类型
        for network_type, config in network_config.items():
            print(f"\n处理{network_type}...")

            # 检查并加载网络节点数据
            nodes_path = step2_dir / config['nodes_file']
            if not nodes_path.exists():
                raise FileNotFoundError(f"节点文件不存在：{nodes_path}")
                
            nodes_df = pd.read_csv(nodes_path, encoding='utf-8')
            if '节点' not in nodes_df.columns:
                raise ValueError(f"{network_type}节点文件缺少'节点'列")

            # 加载相关连边数据
            edge_dfs = []
            for edge_file in config['edge_files']:
                edge_path = step2_dir / edge_file
                if not edge_path.exists():
                    raise FileNotFoundError(f"边文件不存在：{edge_path}")
                    
                edge_df = pd.read_csv(edge_path, encoding='utf-8')
                if not {'节点1', '节点2'}.issubset(edge_df.columns):
                    raise ValueError(f"{edge_file}缺少必要列('节点1'或'节点2')")
                    
                edge_dfs.append(edge_df)

            # 计算关键性指数
            criticality_indices = []
            for _, node_row in tqdm(nodes_df.iterrows(), total=len(nodes_df), 
                                  desc=f"计算{network_type}关键性指数"):
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
            output_path = step4_dir / config['output_file']
            result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"已保存{network_type}结果到：{output_path}")

        # 生成报告
        result_msg = (
            "关键性指数计算完成！\n"
            f"知识网络结果：{network_config['knowledge_network']['output_file']}\n"
            f"技术网络结果：{network_config['technology_network']['output_file']}\n"
            f"合作研发网络结果：{network_config['collaborative_R&D_network']['output_file']}\n"
            f"结果文件已保存至：{step4_dir}"
        )
        print(result_msg)
        return result_msg

    except FileNotFoundError as e:
        error_msg = f"文件错误：{str(e)}"
        print(error_msg)
        return error_msg
    except ValueError as ve:
        error_msg = f"数据验证错误：{str(ve)}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"处理过程中发生错误：{str(e)}"
        print(error_msg)
        return error_msg


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='计算关键性指数')
    parser.add_argument('--step2_dir', type=str, help='step2输出目录路径')
    parser.add_argument('--step4_dir', type=str, help='step4输出目录路径')
    
    args = parser.parse_args()
    calculate_criticality(args.step2_dir, args.step4_dir)