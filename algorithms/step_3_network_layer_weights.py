# Copyright © dongbingxue. All rights reserved.
# License: MIT

import numpy as np
import pandas as pd
import networkx as nx
from pathlib import Path

def calculate_network_weights(input_dir=None, output_dir=None):
    """计算多层网络权重
    
    Args:
        input_dir (str/Path): 输入目录路径，默认'../data/step2_output'
        output_dir (str/Path): 输出目录路径，默认'../data/step3_output'
    
    Returns:
        str: 处理结果报告
    """
    # 设置默认路径
    input_dir = Path(input_dir) if input_dir else Path('../data/step2_output')
    output_dir = Path(output_dir) if output_dir else Path('../data/step3_output')
    
    # 设置输出文件路径
    output_path = output_dir / 'network_layer_weights.txt'

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 配置参数
        config = {
            "max_iter": 1000,
            "tol": 1e-6,
            "alpha": 0.85,
            "layer_order": ["knowledge", "technology", "collaborative_R&D"]
        }

        # 加载单层网络
        def load_network(network_type):
            G = nx.Graph()
            nodes_path = input_dir / f"{network_type}_network_nodes.csv"
            edges_path = input_dir / f"{network_type}_network_edges.csv"
            
            if not nodes_path.exists() or not edges_path.exists():
                raise FileNotFoundError(f"网络文件不存在：{nodes_path} 或 {edges_path}")
                
            nodes = pd.read_csv(nodes_path, encoding='utf-8')
            edges = pd.read_csv(edges_path, encoding='utf-8')
            G.add_nodes_from(nodes['节点'].astype(str))
            G.add_edges_from(edges[['节点1', '节点2']].astype(str).values.tolist())
            return G

        # 加载层间耦合网络
        def load_coupling(coupling_type):
            G = nx.Graph()
            edges_path = input_dir / f"{coupling_type}_network_edges.csv"
            
            if not edges_path.exists():
                raise FileNotFoundError(f"耦合网络文件不存在：{edges_path}")
                
            edges = pd.read_csv(edges_path, encoding='utf-8')
            G.add_edges_from(edges[['节点1', '节点2']].astype(str).values.tolist())
            return G

        # 初始化网络
        knowledge_net = load_network("knowledge")
        technology_net = load_network("technology")
        collaborative_RD_net = load_network("collaborative_R&D")

        # 加载耦合网络
        kt_coupling = load_coupling("knowledge-technology")
        tc_coupling = load_coupling("technology-collaborative_R&D")
        kc_coupling = load_coupling("knowledge-collaborative_R&D")

        # 初始化权重矩阵
        Y = np.ones(3) / 3
        X = {
            "knowledge": np.ones(knowledge_net.number_of_nodes()) / knowledge_net.number_of_nodes(),
            "technology": np.ones(technology_net.number_of_nodes()) / technology_net.number_of_nodes(),
            "collaborative_R&D": np.ones(collaborative_RD_net.number_of_nodes()) / collaborative_RD_net.number_of_nodes()
        }

        # 迭代计算
        for _ in range(config["max_iter"]):
            X_new = {
                "knowledge": np.array(list(nx.pagerank(knowledge_net, alpha=config["alpha"]).values())),
                "technology": np.array(list(nx.pagerank(technology_net, alpha=config["alpha"]).values())),
                "collaborative_R&D": np.array(list(nx.pagerank(collaborative_RD_net, alpha=config["alpha"]).values()))
            }

            # 应用耦合效应
            def apply_coupling(src_net, dst_net, coupling, src_layer, dst_layer):
                src_nodes = list(src_net.nodes)
                dst_nodes = list(dst_net.nodes)
                for src, dst in coupling.edges():
                    if src in src_nodes and dst in dst_nodes:
                        src_idx = src_nodes.index(src)
                        dst_idx = dst_nodes.index(dst)
                        X_new[dst_layer][dst_idx] += X_new[src_layer][src_idx] * Y[config["layer_order"].index(src_layer)]

            apply_coupling(knowledge_net, technology_net, kt_coupling, "knowledge", "technology")
            apply_coupling(technology_net, collaborative_RD_net, tc_coupling, "technology", "collaborative_R&D")
            apply_coupling(collaborative_RD_net, knowledge_net, kc_coupling, "collaborative_R&D", "knowledge")

            # 更新全局权重
            Y_new = np.array([
                X_new["knowledge"].sum(),
                X_new["technology"].sum(),
                X_new["collaborative_R&D"].sum()
            ])
            Y_new /= Y_new.sum()

            if np.linalg.norm(Y_new - Y) < config["tol"]:
                break
            Y = Y_new.copy()

        # 保存结果
        np.savetxt(output_path, Y, fmt="%.6f")

        # 生成报告
        report = (
            "网络权重计算完成\n"
            f"知识层权重: {Y[0]:.4f}\n"
            f"技术层权重: {Y[1]:.4f}\n"
            f"合作研发层权重: {Y[2]:.4f}\n"
            f"权重文件已保存至: {output_path}"
        )
        print(report)
        return report

    except Exception as e:
        error_msg = f"权重计算失败: {str(e)}"
        print(error_msg)
        return error_msg

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='计算多层网络权重')
    parser.add_argument('--input_dir', type=str, help='输入目录路径')
    parser.add_argument('--output_dir', type=str, help='输出目录路径')
    
    args = parser.parse_args()
    calculate_network_weights(args.input_dir, args.output_dir)