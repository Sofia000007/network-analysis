# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
import os
import re


def remove_personal_application():
    """移除个人申请的专利数据"""
    # 定义文件路径
    input_path = os.path.join('..', 'data', 'input', 'original_patent_data.xlsx')
    output_dir = os.path.join('..', 'data', 'step1_output')
    output_path = os.path.join(output_dir, 'patent_data_no_personal.xlsx')

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 读取原始数据
        df = pd.read_excel(input_path)
        
        # 移除个人申请（通常个人申请的专利权人字段包含个人姓名特征）
        # 这里使用简单的规则：如果专利权人字段长度较短且不包含"公司"、"有限"等企业关键词
        enterprise_keywords = ['公司', '有限', '股份', '集团', '企业', '研究院', '大学', '学院', '中心']
        
        def is_enterprise(patent_holder):
            if pd.isna(patent_holder):
                return False
            patent_holder = str(patent_holder)
            # 如果包含企业关键词，认为是企业申请
            for keyword in enterprise_keywords:
                if keyword in patent_holder:
                    return True
            # 如果长度过短（可能是个人姓名），认为是个人申请
            if len(patent_holder) <= 4:
                return False
            return True
        
        # 筛选企业申请的专利
        df_filtered = df[df['专利权人'].apply(is_enterprise)]
        
        # 保存结果
        df_filtered.to_excel(output_path, index=False)
        
        result = f"个人申请移除完成，结果已保存至：{output_path}\n原始数据：{len(df)}条，筛选后：{len(df_filtered)}条"
        print(result)
        return result
        
    except Exception as e:
        error_msg = f"个人申请移除失败：{str(e)}"
        print(error_msg)
        return error_msg


if __name__ == '__main__':
    remove_personal_application()
