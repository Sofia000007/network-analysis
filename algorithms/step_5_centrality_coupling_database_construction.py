# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import numpy as np
from pathlib import Path


def build_centrality_coupling_database(step3_dir=None, step5_dir=None):
    """构建中心度耦合数据库
    
    Args:
        step3_dir (str/Path): step3输出目录路径，默认'../data/step3_output'
        step5_dir (str/Path): step5输出目录路径，默认'../data/step5_output'
    
    Returns:
        str: 处理结果报告
    """
    # 设置默认路径
    step3_dir = Path(step3_dir) if step3_dir else Path('../data/step3_output')
    step5_dir = Path(step5_dir) if step5_dir else Path('../data/step5_output')

    try:
        # 确保输出目录存在
        step5_dir.mkdir(parents=True, exist_ok=True)

        # 1. 加载网络层权重
        weights_path = step3_dir / 'network_layer_weights.txt'
        if not weights_path.exists():
            raise FileNotFoundError(f"网络层权重文件不存在：{weights_path}")
            
        network_layer_weights = np.loadtxt(weights_path)
        print(f"成功加载网络层权重：{network_layer_weights}")

        # 2. 定义网络配置
        networks = {
            'knowledge_network': {
                'layer_id': 1,
                'input_file': 'knowledge_network_centrality_coupling.csv',
                'output_file': 'knowledge_network_centrality_coupling.csv'
            },
            'technology_network': {
                'layer_id': 2,
                'input_file': 'technology_network_centrality_coupling.csv',
                'output_file': 'technology_network_centrality_coupling.csv'
            },
            'collaborative_R&D_network': {
                'layer_id': 3,
                'input_file': 'collaborative_R&D_network_centrality_coupling.csv',
                'output_file': 'collaborative_R&D_network_centrality_coupling.csv'
            }
        }

        # 3. 加载并处理各网络数据
        dfs = []
        for net_name, net_config in networks.items():
            input_path = step5_dir / net_config['input_file']

            # 检查文件是否存在
            if not input_path.exists():
                raise FileNotFoundError(f"{net_name}中心度文件不存在: {input_path}")

            # 读取数据
            df = pd.read_csv(input_path, encoding='utf-8')

            # 检查必要列是否存在
            required_cols = ['节点', 'centrality_coupling']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"{net_name}缺少必要列: {missing_cols}")

            # 添加网络层信息
            df['网络层'] = net_config['layer_id']

            # 添加网络层权重
            df['network_layer_weights'] = network_layer_weights[net_config['layer_id'] - 1]

            # 计算乘积列
            df['centrality_coupling*weights'] = df['centrality_coupling'] * df['network_layer_weights']

            dfs.append(df)
            print(f"已加载 {net_name} 数据：{len(df)} 条记录")

        # 4. 合并数据并保存各网络结果
        for net_name, net_config in networks.items():
            # 筛选当前网络的数据
            net_df = pd.concat(dfs)[pd.concat(dfs)['网络层'] == net_config['layer_id']]

            # 选择输出列
            output_cols = [
                '节点',
                'centrality_coupling',
                '网络层',
                'network_layer_weights',
                'centrality_coupling*weights'
            ]

            # 保存结果
            output_path = step5_dir / net_config['output_file']
            net_df[output_cols].to_csv(output_path, index=False, encoding='utf-8-sig')

        # 5. 保存整合后的数据库
        combined_df = pd.concat(dfs, ignore_index=True)
        database_path = step5_dir / 'centrality_coupling_database.csv'
        combined_df.to_csv(database_path, index=False, encoding='utf-8-sig')

        result_msg = (
            f"中心度耦合数据库构建完成！\n"
            f"知识网络记录数: {len(combined_df[combined_df['网络层'] == 1])}\n"
            f"技术网络记录数: {len(combined_df[combined_df['网络层'] == 2])}\n"
            f"合作研发网络记录数: {len(combined_df[combined_df['网络层'] == 3])}\n"
            f"结果已保存至: {step5_dir}"
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
    
    parser = argparse.ArgumentParser(description='构建中心度耦合数据库')
    parser.add_argument('--step3_dir', type=str, help='step3输出目录路径')
    parser.add_argument('--step5_dir', type=str, help='step5输出目录路径')
    
    args = parser.parse_args()
    build_centrality_coupling_database(args.step3_dir, args.step5_dir)