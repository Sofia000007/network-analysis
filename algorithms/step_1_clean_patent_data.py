# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
from pathlib import Path


def clean_patent_data(input_path=None, output_path=None):
    """清洗专利数据

    Args:
        input_path (str/Path): CSV输入文件路径，默认'./data/input/original_patent_data.csv'
        output_path (str/Path): CSV输出路径，默认'./data/step1_output/patent_data_cleaned.csv'
    """
    input_path = Path(input_path) if input_path else Path('../data/input/original_patent_data.csv')
    output_path = Path(output_path) if output_path else Path('../data/step1_output/patent_data_cleaned.csv')

    # 确保输入文件存在
    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    # 创建输出目录
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # 读取CSV文件
        df = pd.read_csv(input_path)
        original_count = len(df)

        # 处理数据
        required_columns = ["公开（公告）号", "引文专利公开号", "施引专利公开号", "IPC分类", "专利权人"]
        df = df[required_columns]

        for col in required_columns:
            df[col] = df[col].astype(str).str.upper()

        df.dropna(subset=['IPC分类'], inplace=True)
        df.drop_duplicates(subset=['公开（公告）号'], keep='first', inplace=True)

        # 保存为CSV
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"清洗完成，保存到: {output_path}")
        return f"原始: {original_count}条 | 结果: {len(df)}条"
    except Exception as e:
        raise RuntimeError(f"清洗失败: {str(e)}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str)
    parser.add_argument('--output', type=str)
    args = parser.parse_args()
    clean_patent_data(args.input, args.output)