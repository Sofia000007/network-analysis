# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
from pathlib import Path


def calculate_critical_centrality_index(input_dir=None, output_dir=None):
    """计算关键-核心性指数
    
    Args:
        input_dir (str/Path): 输入目录路径，默认'../data/step6_output'
        output_dir (str/Path): 输出目录路径，默认'../data/step7_output'
    
    Returns:
        str: 处理结果报告
    """
    # 设置默认路径
    input_dir = Path(input_dir) if input_dir else Path('../data/step6_output')
    output_dir = Path(output_dir) if output_dir else Path('../data/step7_output')

    # 输入输出文件路径
    db_file = input_dir / 'criticality_and_centrality_database.csv'
    weights_file = input_dir / 'index_weights.txt'
    output_file = output_dir / 'criticality-centrality_index.csv'

    try:
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. 加载数据库文件
        if not db_file.exists():
            raise FileNotFoundError(f"数据库文件不存在: {db_file}")

        df = pd.read_csv(db_file, encoding='utf-8')

        # 检查必要列是否存在
        required_cols = ['节点', '网络层', '关键性', '核心性']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"数据库文件缺少必要列: {missing_cols}")

        # 2. 加载权重文件
        if not weights_file.exists():
            raise FileNotFoundError(f"权重文件不存在: {weights_file}")

        weights = {}
        with open(weights_file, 'r', encoding='utf-8') as f:
            for line in f:
                if ':' in line:
                    key, value = line.strip().split(': ')
                    weights[key] = float(value)

        # 检查权重是否完整
        if 'criticality_weight' not in weights or 'centrality_weight' not in weights:
            raise ValueError("权重文件缺少必要权重值")

        # 3. 计算关键-核心性指数
        df['关键性权重'] = weights['criticality_weight']
        df['核心性权重'] = weights['centrality_weight']
        df['关键核心性'] = (df['关键性'] * df['关键性权重']) + (df['核心性'] * df['核心性权重'])

        # 4. 选择输出列
        output_cols = ['节点', '网络层', '关键性', '关键性权重', '核心性', '核心性权重', '关键核心性']
        output_df = df[output_cols]

        # 5. 保存结果
        output_df.to_csv(output_file, index=False, encoding='utf-8-sig')

        # 6. 统计信息
        stats = {
            '总节点数': len(output_df),
            '最大关键核心性': output_df['关键核心性'].max(),
            '最小关键核心性': output_df['关键核心性'].min(),
            '平均关键核心性': output_df['关键核心性'].mean(),
            '知识网络节点数': len(output_df[output_df['网络层'] == 1]),
            '技术网络节点数': len(output_df[output_df['网络层'] == 2]),
            '合作研发网络节点数': len(output_df[output_df['网络层'] == 3])
        }

        # 7. 结果消息
        result_msg = (
            f"关键-核心性指数计算完成！\n"
            f"结果已保存至: {output_file}\n"
            f"总节点数: {stats['总节点数']}\n"
            f"最大关键核心性: {stats['最大关键核心性']:.4f}\n"
            f"最小关键核心性: {stats['最小关键核心性']:.4f}\n"
            f"平均关键核心性: {stats['平均关键核心性']:.4f}\n"
            f"知识网络节点数: {stats['知识网络节点数']}\n"
            f"技术网络节点数: {stats['技术网络节点数']}\n"
            f"合作研发网络节点数: {stats['合作研发网络节点数']}"
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
    
    parser = argparse.ArgumentParser(description='计算关键-核心性指数')
    parser.add_argument('--input_dir', type=str, help='输入目录路径')
    parser.add_argument('--output_dir', type=str, help='输出目录路径')
    
    args = parser.parse_args()
    calculate_critical_centrality_index(args.input_dir, args.output_dir)