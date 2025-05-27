# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import numpy as np
from pathlib import Path


def calculate_index_weights(input_dir=None, output_dir=None):
    """计算关键性和核心性指标权重
    
    Args:
        input_dir (str/Path): 输入目录路径，默认'../data/step6_output'
        output_dir (str/Path): 输出目录路径，默认'../data/step6_output'
    
    Returns:
        str: 处理结果报告
    """
    # 设置默认路径
    input_dir = Path(input_dir) if input_dir else Path('../data/step6_output')
    output_dir = Path(output_dir) if output_dir else Path('../data/step6_output')

    # 输入输出文件路径
    input_file = input_dir / 'criticality_and_centrality_database.csv'
    output_file = output_dir / 'index_weights.txt'

    try:
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. 加载数据
        if not input_file.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_file}")

        df = pd.read_csv(input_file, encoding='utf-8')

        # 检查必要列是否存在
        required_cols = ['关键性', '核心性']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"输入文件缺少必要列: {missing_cols}")

        # 2. 数据标准化 (极差法)
        normalized_data = (df[required_cols] - df[required_cols].min()) / (
                    df[required_cols].max() - df[required_cols].min())

        # 3. 计算CRITIC权重
        # 计算指标变异性（标准差）
        std_dev = normalized_data.std()

        # 计算冲突性（相关系数）
        corr_matrix = normalized_data.corr().abs()
        conflict = 1 - corr_matrix.sum(axis=1)

        # 计算信息量
        information = std_dev * conflict

        # 计算权重
        weights = information / information.sum()

        # 4. 准备输出结果
        weights_dict = {
            'criticality_weight': round(weights['关键性'], 4),
            'centrality_weight': round(weights['核心性'], 4)
        }

        # 5. 保存权重结果
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"criticality_weight: {weights_dict['criticality_weight']:.4f}\n")
            f.write(f"centrality_weight: {weights_dict['centrality_weight']:.4f}\n")

        # 6. 打印结果信息
        result_msg = (
            f"指标权重计算完成！\n"
            f"关键性权重: {weights_dict['criticality_weight']:.4f}\n"
            f"核心性权重: {weights_dict['centrality_weight']:.4f}\n"
            f"权重总和: {weights_dict['criticality_weight'] + weights_dict['centrality_weight']:.4f}\n"
            f"结果已保存至: {output_file}"
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
    
    parser = argparse.ArgumentParser(description='计算关键性和核心性指标权重')
    parser.add_argument('--input_dir', type=str, help='输入目录路径')
    parser.add_argument('--output_dir', type=str, help='输出目录路径')
    
    args = parser.parse_args()
    calculate_index_weights(args.input_dir, args.output_dir)