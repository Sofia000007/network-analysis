# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
from tqdm import tqdm
import os
import json
from pathlib import Path
import concurrent.futures
import time
import logging
import threading
from typing import Dict, List, Optional
import argparse
from dotenv import load_dotenv
from openai import OpenAI
import backoff  # 添加 backoff 库用于重试机制

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 加载环境变量（向上查找一级目录找到项目根目录）
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 初始化DeepSeek客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    timeout=30.0  # 增加超时时间
)

# 常量配置
CACHE_VERSION = "v1.2"
CACHE_FILENAME = "org_classification_cache.json"
MAX_RETRIES = 3
INITIAL_WAIT = 1
MAX_WAIT = 10

CLASSIFICATION_PROMPT = """请严格按以下规则分析：
1. 如果名称明显是公司、机构、组织（包含缩写），回答 true
2. 如果名称包含明显个人特征（如人名、称谓），回答 false
3. 如果无法确定，回答 false

名称：{name}
只需回答 true/false："""

# 初始化线程安全锁
cache_lock = threading.Lock()

@backoff.on_exception(
    backoff.expo,
    (Exception),
    max_tries=MAX_RETRIES,
    max_time=30,
    giveup=lambda e: isinstance(e, KeyboardInterrupt)
)
def get_completion(prompt: str) -> str:
    """获取DeepSeek API响应，带指数退避的重试机制"""
    messages = [{"role": "user", "content": prompt}]
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.warning(f"API请求失败: {str(e)}")
        raise


def load_cache(cache_path: Path) -> Dict[str, bool]:
    """加载增强型缓存"""
    cache_data = {}
    if cache_path.exists():
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('version') == CACHE_VERSION:
                    cache_data = data['mapping']
                    logging.info(f"已加载缓存条目：{len(cache_data)}条")
        except Exception as e:
            logging.error(f"缓存加载失败: {e}")
    return cache_data


def save_cache(cache_data: Dict[str, bool], cache_path: Path) -> None:
    """保存增强型缓存"""
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            data = {
                'version': CACHE_VERSION,
                'mapping': cache_data,
                'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            json.dump(data, f, ensure_ascii=False)
        logging.info(f"缓存已保存至：{cache_path}")
    except Exception as e:
        logging.error(f"缓存保存失败: {e}")


def call_deepseek_api(name: str) -> Optional[bool]:
    """调用DeepSeek分类API（带重试机制）"""
    prompt = CLASSIFICATION_PROMPT.format(name=name)

    for attempt in range(3):
        try:
            response = get_completion(prompt).lower()
            if response == 'true':
                return True
            if response == 'false':
                return False
            logging.warning(f"异常API响应：{response}")
        except Exception as e:
            logging.warning(f"分类请求失败（尝试{attempt + 1}/3）: {str(e)}")
            time.sleep(2 ** attempt)
    return None


def split_names(cell_value: str) -> List[str]:
    """拆分并清洗名称"""
    return [n.strip() for n in str(cell_value).split("|") if n.strip()]


def check_organization(names: List[str], cache: Dict[str, bool]) -> bool:
    """判断多个名称中是否存在组织机构"""
    for name in names:
        with cache_lock:
            if name in cache:
                if cache[name]:
                    return True
                continue

        api_result = call_deepseek_api(name)
        if api_result is None:
            continue

        with cache_lock:
            cache[name] = api_result

        if api_result:
            return True
    return False


def process_batch(batch: pd.DataFrame, cache: Dict[str, bool]) -> pd.DataFrame:
    """处理数据批次"""
    results = []
    for _, row in batch.iterrows():
        try:
            raw_names = row['专利权人'] if pd.notna(row['专利权人']) else ''
            names = split_names(raw_names)

            if not names:
                continue

            if check_organization(names, cache):
                results.append(row)
        except Exception as e:
            logging.error(f"处理行数据时出错: {str(e)}")
            continue
    return pd.DataFrame(results)


def remove_personal_applications(input_path: str = None, output_path: str = None) -> str:
    """主处理函数"""
    # 设置默认路径
    if input_path is None:
        input_path = '../data/step1_output/patent_data_cleaned.csv'
    if output_path is None:
        output_path = '../data/step1_output/patent_data_selected_columns.csv'

    # 转换路径为Path对象
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 初始化缓存
    cache_path = output_path.parent / CACHE_FILENAME
    cache = load_cache(cache_path)
    original_cache_size = len(cache)

    try:
        # 读取数据
        logging.info(f"正在读取数据文件：{input_path}")
        df = pd.read_csv(input_path, encoding='utf-8')
        original_count = len(df)

        # 并行处理
        batch_size = 50  # 减小批次大小
        batches = [df[i:i + batch_size] for i in range(0, len(df), batch_size)]
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:  # 减少并发数
            futures = [
                executor.submit(process_batch, batch, cache)
                for batch in batches
            ]

            for future in tqdm(
                    concurrent.futures.as_completed(futures),
                    total=len(futures),
                    desc="处理进度"
            ):
                try:
                    result = future.result()
                    if not result.empty:
                        results.append(result)
                except Exception as e:
                    logging.error(f"处理批次时出错: {str(e)}")
                    continue

        # 合并结果
        final_df = pd.concat(results, ignore_index=True)
        final_count = len(final_df)

        # 保存结果
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logging.info(f"结果已保存至：{output_path}")

        # 保存缓存（仅在变更时保存）
        if len(cache) != original_cache_size:
            save_cache(cache, cache_path)
        else:
            logging.info("无缓存变更，跳过保存")

        # 生成报告
        report = (
            f"处理完成 | 原始数据: {original_count}条 | 保留数据: {final_count}条 | "
            f"过滤率: {(original_count - final_count) / original_count:.1%}"
        )
        return report

    except Exception as e:
        logging.error(f"处理异常: {str(e)}")
        return f"处理失败: {str(e)}"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='专利数据过滤工具')
    parser.add_argument('--input_path', '-i',
                        default='../data/step1_output/patent_data_cleaned.csv',
                        help='输入CSV文件路径')
    parser.add_argument('--output_path', '-o',
                        default='../data/step1_output/patent_data_selected_columns.csv',
                        help='输出CSV文件路径')

    args = parser.parse_args()
    result = remove_personal_applications(args.input_path, args.output_path)
    print("\n最终报告:", result)