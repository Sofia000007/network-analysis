# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import numpy as np
from pathlib import Path


def build_structural_hole_database(step3_dir=None, step4_dir=None):
    """构建结构洞耦合数据库
    
    Args:
        step3_dir (str/Path): step3输出目录路径，默认'../data/step3_output'
        step4_dir (str/Path): step4输出目录路径，默认'../data/step4_output'
    
    Returns:
        str: 处理结果报告
    """
    # 设置默认路径
    step3_dir = Path(step3_dir) if step3_dir else Path('../data/step3_output')
    step4_dir = Path(step4_dir) if step4_dir else Path('../data/step4_output')

    # 输入输出路径配置
    input_files = {
        'weights': step3_dir / 'network_layer_weights.txt',
        'knowledge': step4_dir / 'knowledge_network_structural_hole_coupling.csv',
        'technology': step4_dir / 'technology_network_structural_hole_coupling.csv',
        'collaborative': step4_dir / 'collaborative_R&D_network_structural_hole_coupling.csv'
    }
    output_path = step4_dir / 'structural_hole_coupling_database.csv'

    try:
        # 确保输出目录存在
        step4_dir.mkdir(parents=True, exist_ok=True)

        # 检查输入文件是否存在
        for name, path in input_files.items():
            if not path.exists():
                raise FileNotFoundError(f"输入文件不存在：{path}")

        # 加载网络层权重
        layer_weights = np.loadtxt(input_files['weights'])
        print(f"成功加载网络层权重：{layer_weights}")

        # 定义网络元数据
        networks = [
            ('knowledge', 1, '知识网络'),
            ('technology', 2, '技术网络'),
            ('collaborative', 3, '合作研发网络')
        ]

        # 加载并处理各网络数据
        dfs = []
        for net_key, layer_id, net_name in networks:
            file_path = input_files[net_key]

            # 读取并标准化列名
            df = pd.read_csv(file_path, encoding='utf-8').rename(columns={
                'node': '节点',
                'structural_hole_coupling': 'structural_hole_coupling',
                'structural_hole': 'structural_hole_coupling'  # 兼容旧版列名
            })

            # 列名校验
            required_columns = ['节点', 'structural_hole_coupling']
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                raise ValueError(f"文件 {net_name} 缺少必要列：{missing_cols}")

            # 添加网络层信息
            df['网络层'] = layer_id
            df['network_layer_weights'] = layer_weights[layer_id - 1]
            df['structural_hole_coupling*weights'] = df['structural_hole_coupling'] * df['network_layer_weights']

            dfs.append(df)
            print(f"已加载 {net_name} 数据：{len(df)} 条记录")

        # 合并数据集
        combined_df = pd.concat(dfs, ignore_index=True)

        # 规范输出列顺序
        output_columns = [
            '节点',
            'structural_hole_coupling',
            '网络层',
            'network_layer_weights',
            'structural_hole_coupling*weights'
        ]

        # 保存结果
        combined_df[output_columns].to_csv(output_path, index=False, encoding='utf-8-sig')
        result = f"数据库构建成功！总记录数：{len(combined_df)}，保存路径：{output_path}"
        print(result)
        return result

    except FileNotFoundError as e:
        error_msg = f"文件不存在错误：{str(e)}"
        print(error_msg)
        return error_msg
    except ValueError as ve:
        error_msg = f"数据校验失败：{str(ve)}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"处理过程中发生未预期错误：{str(e)}"
        print(error_msg)
        return error_msg


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='构建结构洞耦合数据库')
    parser.add_argument('--step3_dir', type=str, help='step3输出目录路径')
    parser.add_argument('--step4_dir', type=str, help='step4输出目录路径')
    
    args = parser.parse_args()
    build_structural_hole_database(args.step3_dir, args.step4_dir)