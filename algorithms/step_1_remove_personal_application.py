# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
from tqdm import tqdm
import re
import os
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator as Translator
from pathlib import Path
import concurrent.futures
from functools import lru_cache
import json
from typing import List, Set, Dict, Union
import time
import logging
from datetime import datetime

def load_cache(cache_dir: Path) -> Dict[str, Set[str]]:
    """加载缓存数据"""
    cache_file = cache_dir / 'company_name_cache.json'
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'company': set(data['company']),
                    'non_company': set(data['non_company'])
                }
        except Exception as e:
            print(f"加载缓存失败: {e}")
    return {'company': set(), 'non_company': set()}

def save_cache(cache_data: Dict[str, Set[str]], cache_dir: Path) -> None:
    """保存缓存数据"""
    cache_file = cache_dir / 'company_name_cache.json'
    cache_dir.mkdir(parents=True, exist_ok=True)
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            cache_data_json = {
                'company': list(cache_data['company']),
                'non_company': list(cache_data['non_company'])
            }
            json.dump(cache_data_json, f, ensure_ascii=False)
    except Exception as e:
        print(f"保存缓存失败: {e}")

@lru_cache(maxsize=1000)
def is_company_name(name: str) -> bool:
    """检查名称是否包含公司相关后缀（使用LRU缓存）"""
    company_suffixes = r'\b(GmbH|Inc\.?|LLC|Corp\.?|Ltd\.?|Pty Ltd|S\.A\.?|PLC|AG|B\.V\.?|S\.L\.?|K\.K\.?|N\.V\.?|S\.A\.S\.?|OÜ|C\.C\.?|Ltda|Kft|S\.r\.o|S\.A\.R\.L\.?|GmbH & Co\. KG|LLP|KG|LP|S\.C\.?|S\.r\.l\.?|SA|SAS|A/S|N.V.|K/S|C.C.)\b'
    return bool(re.search(company_suffixes, name, re.IGNORECASE))

def batch_translate(names: List[str], translator: Translator, batch_size: int = 50) -> dict:
    """批量翻译名称"""
    translations = {}
    for i in range(0, len(names), batch_size):
        batch = names[i:i + batch_size]
        try:
            results = [translator.translate(name, dest='zh-cn') for name in batch]
            translations.update({name: result for name, result in zip(batch, results)})
            time.sleep(1)  # 避免触发API限制
        except Exception as e:
            print(f"翻译批次出错: {e}")
    return translations

def check_company_name_online(name: str, cache: dict) -> bool:
    """检查公司名称（带缓存）"""
    if name in cache['company']:
        return True
    if name in cache['non_company']:
        return False

    try:
        search_url = f"https://www.baidu.com/s?wd={requests.utils.quote(name)}"
        response = requests.get(search_url, timeout=5)
        is_company = False
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            is_company = '公司' in soup.text or '有限公司' in soup.text
        
        if is_company:
            cache['company'].add(name)
        else:
            cache['non_company'].add(name)
        
        return is_company
    except Exception as e:
        print(f"在线搜索错误: {e}")
        return False

def process_batch(batch_data: pd.DataFrame, non_personal_keywords: List[str], 
                 translator: Translator, cache: dict) -> List[pd.Series]:
    """处理数据批次"""
    results = []
    names_to_translate = []
    
    for _, row in batch_data.iterrows():
        name = str(row['专利权人']) if pd.notna(row['专利权人']) else ''
        if not name:
            continue
            
        if any(keyword in name for keyword in non_personal_keywords):
            results.append(row)
        elif is_company_name(name):
            results.append(row)
        else:
            names_to_translate.append(name)
            
    if names_to_translate:
        translations = batch_translate(names_to_translate, translator)
        for name in names_to_translate:
            translated = translations.get(name, '')
            if translated and (any(kw in translated for kw in non_personal_keywords) or 
                             check_company_name_online(name, cache)):
                results.append(batch_data[batch_data['专利权人'] == name].iloc[0])
                
    return results

def remove_personal_applications(input_path: str, output_path: str) -> str:
    """剔除个人专利申请数据
    
    Args:
        input_path: 输入CSV文件路径
        output_path: 输出CSV文件路径
        
    Returns:
        str: 处理结果报告
    """
    # 转换路径为Path对象
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 设置缓存目录
    cache_dir = output_path.parent / 'cache'
    cache_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 加载缓存
        cache = load_cache(cache_dir)
        
        # 读取CSV数据
        print(f"正在读取文件：{input_path}")
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在：{input_path}")
            
        data = pd.read_csv(input_path, encoding='utf-8')
        original_count = len(data)

        # 处理参数配置
        non_personal_keywords = [
            '大学', '学院', '研究院', '研究所', '公司', '会社', '大队',
            '医院', '学校', '所', '中心', '实验室', '厂', '中学',
            '组织', '海关', '院', '部', '企业', '机构', '研究会',
            '委员会', '种植园', '检疫局', '协会', '合作社', '小学',
            '基金', '种植场', '支队', '工作室', '分局', '株',
            '會社', '合伙', '学会'
        ]

        # 初始化翻译器
        translator = Translator()
        
        # 将数据分成小批次处理
        batch_size = 100
        batches = [data[i:i + batch_size] for i in range(0, len(data), batch_size)]
        
        # 使用线程池处理数据
        remaining_data = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(process_batch, batch, non_personal_keywords, translator, cache)
                for batch in batches
            ]
            
            for future in tqdm(concurrent.futures.as_completed(futures), 
                             total=len(futures), desc="处理进度"):
                remaining_data.extend(future.result())

        # 保存结果为CSV
        result_df = pd.DataFrame(remaining_data)
        final_count = len(result_df)
        result_df.to_csv(output_path, index=False, encoding='utf-8')

        # 保存缓存
        save_cache(cache, cache_dir)

        # 生成统计报告
        report = f"数据处理完成\n原始数据量：{original_count}条\n保留数据量：{final_count}条\n删除数据量：{original_count - final_count}条"
        print(report)
        return report

    except Exception as e:
        error_msg = f"数据处理异常：{str(e)}"
        print(error_msg)
        return error_msg

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='剔除个人专利申请数据')
    parser.add_argument('input_path', help='输入CSV文件路径')
    parser.add_argument('output_path', help='输出CSV文件路径')
    
    args = parser.parse_args()
    remove_personal_applications(args.input_path, args.output_path)