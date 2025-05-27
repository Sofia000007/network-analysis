"""
网络分析流程执行器
此模块提供了一个统一的接口来执行完整的网络分析流程。
"""

import time
from datetime import datetime
from pathlib import Path
import pandas as pd

# 导入所有步骤函数
from step_1_clean_patent_data import clean_patent_data
from step_1_remove_personal_application import remove_personal_applications
from step_2_knowledge_network_construction import construct_knowledge_network
from step_2_technology_network_construction import construct_technology_network
from step_2_collaborative_RD_network_construction import construct_collaborative_RD_network
from step_2_knowledge_technology_network_construction import construct_knowledge_technology_network
from step_2_technology_collaborative_RD_network_construction import construct_technology_collaborative_RD_network
from step_2_knowledge_collaborative_RD_network_construction import construct_knowledge_collaborative_RD_network
from step_3_network_layer_weights import calculate_network_weights
from step_4_structural_hole_coupling_calculation import calculate_structural_hole
from step_4_structural_hole_coupling_database_construction import build_structural_hole_database
from step_4_criticality_index_calculation import calculate_criticality
from step_5_centrality_coupling_calculation import calculate_centrality_coupling
from step_5_centrality_coupling_database_construction import build_centrality_coupling_database
from step_5_centrality_index_calculation import calculate_centrality_index
from step_6_criticality_and_centrality_database_construction import build_criticality_centrality_database


def run_full_pipeline(project_root=None):
    """
    执行完整的网络分析流程
    
    Args:
        project_root (Path, optional): 项目根目录。如果未指定，使用当前工作目录。
    
    Returns:
        dict: 包含每个步骤执行结果的字典
    """
    # 设置路径
    PROJECT_ROOT = Path(project_root) if project_root else Path.cwd()
    DATA_ROOT = PROJECT_ROOT / 'data'
    
    # 确保所有必要的目录存在
    for step in range(1, 8):
        (DATA_ROOT / f'step{step}_output').mkdir(parents=True, exist_ok=True)
    
    # 定义步骤配置
    steps = [
        {
            "name": "1.1 数据清洗",
            "func": clean_patent_data,
            "params": {
                "input_path": str(DATA_ROOT / 'input' / 'original_patent_data.csv'),
                "output_path": str(DATA_ROOT / 'step1_output' / 'patent_data_cleaned.csv')
            }
        },
        {
            "name": "1.2 去除个人申请",
            "func": remove_personal_applications,
            "params": {
                "input_path": str(DATA_ROOT / 'step1_output' / 'patent_data_cleaned.csv'),
                "output_path": str(DATA_ROOT / 'step1_output' / 'patent_data_selected_columns.csv')
            }
        },
        {
            "name": "2.1 知识网络构建",
            "func": construct_knowledge_network,
            "params": {
                "input_path": str(DATA_ROOT / 'step1_output' / 'patent_data_selected_columns.csv'),
                "output_dir": str(DATA_ROOT / 'step2_output')
            }
        },
        {
            "name": "2.2 技术网络构建",
            "func": construct_technology_network,
            "params": {
                "input_path": str(DATA_ROOT / 'step1_output' / 'patent_data_selected_columns.csv'),
                "output_dir": str(DATA_ROOT / 'step2_output')
            }
        },
        {
            "name": "2.3 协作研发网络构建",
            "func": construct_collaborative_RD_network,
            "params": {
                "input_path": str(DATA_ROOT / 'step1_output' / 'patent_data_selected_columns.csv'),
                "output_dir": str(DATA_ROOT / 'step2_output')
            }
        },
        {
            "name": "2.4 知识-技术耦合网络",
            "func": construct_knowledge_technology_network,
            "params": {
                "input_path": str(DATA_ROOT / 'step1_output' / 'patent_data_selected_columns.csv'),
                "output_dir": str(DATA_ROOT / 'step2_output')
            }
        },
        {
            "name": "2.5 技术-协作耦合网络",
            "func": construct_technology_collaborative_RD_network,
            "params": {
                "input_path": str(DATA_ROOT / 'step1_output' / 'patent_data_selected_columns.csv'),
                "output_dir": str(DATA_ROOT / 'step2_output')
            }
        },
        {
            "name": "2.6 知识-协作耦合网络",
            "func": construct_knowledge_collaborative_RD_network,
            "params": {
                "input_path": str(DATA_ROOT / 'step1_output' / 'patent_data_selected_columns.csv'),
                "output_dir": str(DATA_ROOT / 'step2_output')
            }
        },
        {
            "name": "3.1 网络权重计算",
            "func": calculate_network_weights,
            "params": {
                "input_dir": str(DATA_ROOT / 'step2_output'),
                "output_dir": str(DATA_ROOT / 'step3_output')
            }
        },
        {
            "name": "4.1 结构洞耦合计算",
            "func": calculate_structural_hole,
            "params": {
                "input_dir": str(DATA_ROOT / 'step2_output'),
                "output_dir": str(DATA_ROOT / 'step4_output')
            },
            "multi_run": [
                {"network_type": "knowledge"},
                {"network_type": "technology"},
                {"network_type": "collaborative_R&D"}
            ]
        },
        {
            "name": "4.2 结构洞数据库构建",
            "func": build_structural_hole_database,
            "params": {
                "step3_dir": str(DATA_ROOT / 'step3_output'),
                "step4_dir": str(DATA_ROOT / 'step4_output')
            }
        },
        {
            "name": "4.3 关键性指数计算",
            "func": calculate_criticality,
            "params": {
                "step2_dir": str(DATA_ROOT / 'step2_output'),
                "step4_dir": str(DATA_ROOT / 'step4_output')
            }
        },
        {
            "name": "5.1 中心性耦合计算",
            "func": calculate_centrality_coupling,
            "params": {
                "input_dir": str(DATA_ROOT / 'step2_output'),
                "output_dir": str(DATA_ROOT / 'step5_output')
            }
        },
        {
            "name": "5.2 中心性数据库构建",
            "func": build_centrality_coupling_database,
            "params": {
                "step3_dir": str(DATA_ROOT / 'step3_output'),
                "step5_dir": str(DATA_ROOT / 'step5_output')
            }
        },
        {
            "name": "5.3 中心性指数计算",
            "func": calculate_centrality_index,
            "params": {
                "step2_dir": str(DATA_ROOT / 'step2_output'),
                "step5_dir": str(DATA_ROOT / 'step5_output')
            }
        },
        {
            "name": "6.1 综合数据库构建",
            "func": build_criticality_centrality_database,
            "params": {
                "step4_dir": str(DATA_ROOT / 'step4_output'),
                "step5_dir": str(DATA_ROOT / 'step5_output'),
                "output_dir": str(DATA_ROOT / 'step6_output')
            }
        }
    ]
    
    results = {}
    start_time = time.time()
    
    print(f"\n开始执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"项目根目录: {PROJECT_ROOT}")
    print("\n" + "="*80 + "\n")
    
    for step in steps:
        step_start = time.time()
        print(f"\n=== 执行步骤: {step['name']} ===")
        
        try:
            # 验证输入文件/目录是否存在
            for param_name, param_value in step['params'].items():
                if 'dir' not in param_name and Path(param_value).suffix:  # 如果是文件路径
                    input_path = Path(param_value)
                    if 'input' in param_name and not input_path.exists():
                        raise FileNotFoundError(f"输入文件不存在: {input_path}")
                elif 'dir' in param_name:  # 如果是目录路径
                    Path(param_value).mkdir(parents=True, exist_ok=True)
            
            # 执行函数
            if 'multi_run' in step:
                # 需要多次运行的步骤（如结构洞计算）
                for run_params in step['multi_run']:
                    params = {**step['params'], **run_params}
                    result = step['func'](**params)
                    print(f"✓ {step['name']} ({run_params}) 执行成功")
            else:
                # 普通步骤
                result = step['func'](**step['params'])
            
            # 验证输出
            if isinstance(result, str):
                print(f"结果: {result}")
            
            results[step['name']] = {
                "status": "成功",
                "time": time.time() - step_start,
                "result": result
            }
            
        except Exception as e:
            error_msg = f"执行失败: {str(e)}"
            print(f"✗ {error_msg}")
            results[step['name']] = {
                "status": "失败",
                "time": time.time() - step_start,
                "error": error_msg
            }
            
            # 询问是否继续执行
            if input("\n是否继续执行后续步骤？(y/n): ").lower() != 'y':
                break
        
        print(f"耗时: {time.time() - step_start:.2f}秒")
        print("-" * 80)
    
    # 打印执行汇总
    total_time = time.time() - start_time
    success_count = sum(1 for r in results.values() if r['status'] == '成功')
    
    print("\n=== 执行结果汇总 ===")
    print(f"总耗时: {total_time:.2f}秒")
    print(f"成功步骤: {success_count}/{len(steps)}")
    print("\n各步骤详情:")
    
    for step_name, result in results.items():
        status_symbol = "✓" if result['status'] == '成功' else "✗"
        print(f"{status_symbol} {step_name}: {result['status']} ({result['time']:.2f}秒)")
        if result['status'] == '失败':
            print(f"   错误信息: {result['error']}")
    
    return results


if __name__ == '__main__':
    # 如果直接运行此文件，执行完整流程
    pipeline_results = run_full_pipeline() 