# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import numpy as np
import os


def build_structural_hole_database():
    """构建结构洞耦合数据库"""
    # 定义基础路径
    base_dir = os.path.join('..', 'data')
    step3_dir = os.path.join(base_dir, 'step3_output')
    step4_dir = os.path.join(base_dir, 'step4_output')

    # 输入输出路径配置
    input_files = {
        'weights': os.path.join(step3_dir, 'network_layer_weights.txt'),
        'knowledge': os.path.join(step4_dir, 'knowledge_network_structural_hole_coupling.xlsx'),
        'technology': os.path.join(step4_dir, 'technology_network_structural_hole_coupling.xlsx'),
        'collaborative': os.path.join(step4_dir, 'collaborative_R&D_network_structural_hole_coupling.xlsx')
    }
    output_path = os.path.join(step4_dir, 'structural_hole_coupling_database.xlsx')

    try:
        # 确保输出目录存在
        os.makedirs(step4_dir, exist_ok=True)

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
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"结构洞文件不存在：{file_path}")

            # 读取并标准化列名
            df = pd.read_excel(file_path).rename(columns={
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
        combined_df[output_columns].to_excel(output_path, index=False)
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
    build_structural_hole_database()