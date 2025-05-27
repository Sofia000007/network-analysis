# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
from pathlib import Path


def build_criticality_centrality_database(step4_dir=None, step5_dir=None, output_dir=None):
    """构建关键性-核心性数据库
    
    Args:
        step4_dir (str/Path): step4输出目录路径，默认'../data/step4_output'
        step5_dir (str/Path): step5输出目录路径，默认'../data/step5_output'
        output_dir (str/Path): 输出目录路径，默认'../data/step6_output'
    
    Returns:
        str: 处理结果报告
    """
    # 设置默认路径
    step4_dir = Path(step4_dir) if step4_dir else Path('../data/step4_output')
    step5_dir = Path(step5_dir) if step5_dir else Path('../data/step5_output')
    output_dir = Path(output_dir) if output_dir else Path('../data/step6_output')

    # 网络配置
    networks = {
        'knowledge_network': {
            'layer': 1,
            'criticality_file': 'knowledge_network_criticality_index.csv',
            'centrality_file': 'knowledge_network_centrality_index.csv'
        },
        'technology_network': {
            'layer': 2,
            'criticality_file': 'technology_network_criticality_index.csv',
            'centrality_file': 'technology_network_centrality_index.csv'
        },
        'collaborative_R&D_network': {
            'layer': 3,
            'criticality_file': 'collaborative_R&D_network_criticality_index.csv',
            'centrality_file': 'collaborative_R&D_network_centrality_index.csv'
        }
    }

    try:
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 合并所有网络数据
        combined_df = pd.DataFrame()

        for net_name, net_config in networks.items():
            print(f"正在处理{net_name}...")

            # 从step4加载关键性数据
            crit_path = step4_dir / net_config['criticality_file']
            if not crit_path.exists():
                raise FileNotFoundError(f"关键性文件不存在：{crit_path}")
                
            crit_df = pd.read_csv(crit_path, encoding='utf-8')

            # 检查必要列
            if '节点' not in crit_df.columns or 'criticality_index' not in crit_df.columns:
                raise ValueError(f"{net_name}关键性文件缺少必要列('节点'或'criticality_index')")

            # 从step5加载核心性数据
            cent_path = step5_dir / net_config['centrality_file']
            if not cent_path.exists():
                raise FileNotFoundError(f"核心性文件不存在：{cent_path}")
                
            cent_df = pd.read_csv(cent_path, encoding='utf-8')

            # 检查必要列
            if '节点' not in cent_df.columns or 'centrality_index' not in cent_df.columns:
                raise ValueError(f"{net_name}核心性文件缺少必要列('节点'或'centrality_index')")

            # 合并关键性和核心性数据
            merged_df = pd.merge(
                crit_df[['节点', 'criticality_index']],
                cent_df[['节点', 'centrality_index']],
                on='节点',
                how='outer'
            )

            # 添加网络层信息
            merged_df['网络层'] = net_config['layer']

            # 添加到总表
            combined_df = pd.concat([combined_df, merged_df], ignore_index=True)

            print(f"已合并{net_name}数据，节点数: {len(merged_df)}")

        # 检查合并后的数据
        if combined_df.empty:
            raise ValueError("合并后的数据为空，请检查输入文件")

        # 重命名列以符合规范
        final_df = combined_df.rename(columns={
            'criticality_index': '关键性',
            'centrality_index': '核心性'
        })

        # 选择输出列顺序
        output_cols = ['节点', '网络层', '关键性', '核心性']
        final_df = final_df[output_cols]

        # 保存结果
        output_path = output_dir / 'criticality_and_centrality_database.csv'
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')

        # 统计信息
        stats = {
            '总节点数': len(final_df),
            '知识网络节点数': len(final_df[final_df['网络层'] == 1]),
            '技术网络节点数': len(final_df[final_df['网络层'] == 2]),
            '合作研发网络节点数': len(final_df[final_df['网络层'] == 3]),
            '平均关键性': final_df['关键性'].mean(),
            '平均核心性': final_df['核心性'].mean()
        }

        # 结果消息
        result_msg = (
            f"关键性-核心性数据库构建完成！\n"
            f"结果已保存至: {output_path}\n"
            f"总节点数: {stats['总节点数']}\n"
            f"知识网络节点数: {stats['知识网络节点数']}\n"
            f"技术网络节点数: {stats['技术网络节点数']}\n"
            f"合作研发网络节点数: {stats['合作研发网络节点数']}\n"
            f"平均关键性: {stats['平均关键性']:.4f}\n"
            f"平均核心性: {stats['平均核心性']:.4f}"
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
    
    parser = argparse.ArgumentParser(description='构建关键性-核心性数据库')
    parser.add_argument('--step4_dir', type=str, help='step4输出目录路径')
    parser.add_argument('--step5_dir', type=str, help='step5输出目录路径')
    parser.add_argument('--output_dir', type=str, help='输出目录路径')
    
    args = parser.parse_args()
    build_criticality_centrality_database(args.step4_dir, args.step5_dir, args.output_dir)