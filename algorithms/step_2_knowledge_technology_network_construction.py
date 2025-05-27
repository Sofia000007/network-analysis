# Copyright © dongbingxue. All rights reserved.
# License: MIT

import pandas as pd
from pathlib import Path

def construct_knowledge_technology_network(input_path=None, output_dir=None):
    """构建知识-技术双层网络
    
    Args:
        input_path (str/Path): 输入CSV文件路径，默认'../data/step1_output/patent_data_selected_columns.csv'
        output_dir (str/Path): 输出目录路径，默认'../data/step2_output'
    
    Returns:
        str: 处理结果报告
    """
    # 设置默认路径
    input_path = Path(input_path) if input_path else Path('../data/step1_output/patent_data_selected_columns.csv')
    output_dir = Path(output_dir) if output_dir else Path('../data/step2_output')
    
    # 设置输出文件路径
    nodes_path = output_dir / 'knowledge-technology_network_nodes.csv'
    edges_path = output_dir / 'knowledge-technology_network_edges.csv'

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 读取CSV数据
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在：{input_path}")
            
        df = pd.read_csv(input_path, encoding='utf-8')
        original_records = len(df)

        # 初始化数据容器
        nodes = set()
        edges = set()

        # 处理数据
        for _, row in df.iterrows():
            patent_num = str(row['公开（公告）号']).strip()
            ipc_codes = str(row['IPC分类']).split('|')
            ipc_codes = [code.strip() for code in ipc_codes if code.strip()]
            
            # 添加节点和边
            if patent_num and ipc_codes:
                nodes.add(patent_num)
                nodes.update(ipc_codes)
                for ipc in ipc_codes:
                    edge = tuple(sorted([patent_num, ipc]))
                    edges.add(edge)

        # 生成数据框
        nodes_df = pd.DataFrame(sorted(nodes), columns=["节点"])
        edges_df = pd.DataFrame(sorted(edges), columns=["节点1", "节点2"])

        # 保存结果为CSV
        nodes_df.to_csv(nodes_path, index=False, encoding='utf-8-sig')
        edges_df.to_csv(edges_path, index=False, encoding='utf-8-sig')

        # 生成统计报告
        report = (
            f"网络构建完成\n原始专利数：{original_records}条\n"
            f"生成节点数：{len(nodes)}个\n生成边数：{len(edges)}条\n"
            f"节点文件：{nodes_path}\n边文件：{edges_path}"
        )
        print(report)
        return report

    except Exception as e:
        error_msg = f"网络构建失败：{str(e)}"
        print(error_msg)
        return error_msg

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='构建知识-技术双层网络')
    parser.add_argument('--input', type=str, help='输入CSV文件路径')
    parser.add_argument('--output_dir', type=str, help='输出目录路径')
    
    args = parser.parse_args()
    construct_knowledge_technology_network(args.input, args.output_dir)