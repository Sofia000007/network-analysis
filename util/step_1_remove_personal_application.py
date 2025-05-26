# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
from tqdm import tqdm
import re
import os
import requests
from bs4 import BeautifulSoup
from googletrans import Translator


def remove_personal_applications():
    """剔除个人专利申请数据"""
    # 定义文件路径
    input_path = os.path.join('..', 'data', 'step1_output', 'patent_data_cleaned.xlsx')
    output_dir = os.path.join('..', 'data', 'step1_output')
    output_path = os.path.join(output_dir, 'patent_data_selected_columns.xlsx')

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 读取数据
        data = pd.read_excel(input_path)
        original_count = len(data)

        # 定义辅助函数
        def is_company_name(name):
            company_suffixes = r'\b(GmbH|Inc\.?|LLC|Corp\.?|Ltd\.?|Pty Ltd|S\.A\.?|PLC|AG|B\.V\.?|S\.L\.?|K\.K\.?|N\.V\.?|S\.A\.S\.?|OÜ|C\.C\.?|Ltda|Kft|S\.r\.o|S\.A\.R\.L\.?|GmbH & Co\. KG|LLP|KG|LP|S\.C\.?|S\.r\.l\.?|SA|SAS|A/S|N.V.|K/S|C.C.)\b'
            return bool(re.search(company_suffixes, name, re.IGNORECASE))

        def check_company_name_online(name):
            search_url = f"https://www.baidu.com/s?wd={requests.utils.quote(name)}"
            try:
                response = requests.get(search_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    return '公司' in soup.text or '有限公司' in soup.text
            except Exception as e:
                print(f"在线搜索错误: {e}")
            return False

        # 处理参数配置
        non_personal_keywords = [
            '大学', '学院', '研究院', '研究所', '公司', '会社', '大队',
            '医院', '学校', '所', '中心', '实验室', '厂', '中学',
            '组织', '海关', '院', '部', '企业', '机构', '研究会',
            '委员会', '种植园', '检疫局', '协会', '合作社', '小学',
            '基金', '种植场', '支队', '工作室', '分局', '株',
            '會社', '合伙', '学会'
        ]

        # 数据处理容器
        remaining_data = []
        translator = Translator()

        # 进度条处理
        print("开始处理专利权人数据...")
        for index, row in tqdm(data.iterrows(), total=data.shape[0], desc="处理进度"):
            name = row['专利权人']
            if pd.isna(name):
                continue

            name = str(name)
            if any(keyword in name for keyword in non_personal_keywords):
                remaining_data.append(row)
            elif is_company_name(name):
                remaining_data.append(row)
            else:
                try:
                    translated = translator.translate(name, dest='zh-cn').text
                    if any(kw in translated for kw in non_personal_keywords) or check_company_name_online(translated):
                        remaining_data.append(row)
                except:
                    if check_company_name_online(name):
                        remaining_data.append(row)

        # 生成结果数据
        result_df = pd.DataFrame(remaining_data)
        final_count = len(result_df)

        # 保存结果
        result_df.to_excel(output_path, index=False)

        # 生成统计报告
        report = f"数据处理完成，有效数据已保存至：{output_path}\n原始数据量：{original_count}条\n保留数据量：{final_count}条"
        print(report)
        return report

    except Exception as e:
        error_msg = f"数据处理异常：{str(e)}"
        print(error_msg)
        return error_msg


if __name__ == '__main__':
    remove_personal_applications()