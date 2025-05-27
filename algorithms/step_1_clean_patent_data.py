# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import os


def clean_patent_data(input_path=None, output_path=None):
    """清洗专利数据
    Args:
        input_path (str): 输入文件路径，默认'../data/input/original_patent_data.xlsx'
        output_path (str): 输出文件路径，默认'../data/step1_output/patent_data_cleaned.xlsx'
    Returns:
        str: 处理结果描述
    """
    # 设置默认路径
    if input_path is None:
        input_path = os.path.join('..', 'data', 'input', 'original_patent_data.xlsx')
    if output_path is None:
        output_path = os.path.join('..', 'data', 'step1_output', 'patent_data_cleaned.xlsx')

    # 创建输出目录
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 读取原始数据
        df = pd.read_excel(input_path)
        original_count = len(df)

        # 选择指定列并调整顺序
        required_columns = ["公开（公告）号", "引文专利公开号", "施引专利公开号", "IPC分类", "专利权人"]
        df = df[required_columns]

        # 将各列内容转换为大写
        for col in required_columns:
            df[col] = df[col].astype(str).str.upper()

        # 删除IPC分类空值行
        df.dropna(subset=['IPC分类'], inplace=True)
        after_dropna_count = len(df)

        # 删除公开号重复值
        df.drop_duplicates(subset=['公开（公告）号'], keep='first', inplace=True)
        final_count = len(df)

        # 保存清洗后的数据
        df.to_csv(output_path, index=False)

        result = f"""数据清洗完成，清洗结果已保存至：{output_path}
原始数据：{original_count}条
删除IPC分类空值后：{after_dropna_count}条
删除重复值后：{final_count}条"""
        print(result)
        return result

    except Exception as e:
        error_msg = f"数据清洗失败：{str(e)}"
        print(error_msg)
        return error_msg


if __name__ == '__main__':
    # 使用示例（可自定义路径）
    clean_patent_data(
        input_path='../data/input/original_patent_data.xlsx',
        output_path='../data/step1_output/patent_data_cleaned.xlsx'
    )