# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import os


def clean_patent_data():
    # 定义文件路径
    input_path = os.path.join('..', 'data', 'input', 'original patent data.xlsx')
    output_dir = os.path.join('..', 'data', 'step1_output')
    output_path = os.path.join(output_dir, 'patent_data_cleaned.xlsx')

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 读取原始数据
    df = pd.read_excel(input_path)

    # 选择指定列并调整顺序
    required_columns = ["公开（公告）号", "引文专利公开号", "施引专利公开号", "IPC分类", "专利权人"]
    df = df[required_columns]

    # 将各列内容转换为大写
    for col in required_columns:
        df[col] = df[col].astype(str).str.upper()

    # 删除IPC分类空值行
    df.dropna(subset=['IPC分类'], inplace=True)

    # 删除公开号重复值
    df.drop_duplicates(subset=['公开（公告）号'], keep='first', inplace=True)

    # 保存清洗后的数据
    df.to_excel(output_path, index=False)
    print(f"数据清洗完成，清洗结果已保存至：{output_path}")


if __name__ == '__main__':
    clean_patent_data()