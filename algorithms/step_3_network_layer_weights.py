# Copyright © dongbingxue. All rights reserved.
# License: MIT

import os
import numpy as np
import pandas as pd
import networkx as nx

def calculate_network_weights():
    """计算多层网络权重"""
    # 定义文件路径
    input_dir = os.path.join('..', 'data', 'step2_output')
    output_dir = os.path.join('..', 'data', 'step3_output')
    output_path = os.path.join(output_dir, 'network_layer_weights.txt')

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

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
            nodes = pd.read_excel(os.path.join(input_dir, f"{network_type}_network_nodes.xlsx"))
            edges = pd.read_excel(os.path.join(input_dir, f"{network_type}_network_edges.xlsx"))
            G.add_nodes_from(nodes['节点'].astype(str))
            G.add_edges_from(edges[['节点1', '节点2']].astype(str).values.tolist())
            return G

        # 加载层间耦合网络
        def load_coupling(coupling_type):
            G = nx.Graph()
            edges = pd.read_excel(os.path.join(input_dir, f"{coupling_type}_network_edges.xlsx"))
            G.add_edges_from(edges[['节点1', '节点2']].astype(str).values.tolist())
            return G

        # 初始化网络
        knowledge_net = load_network("knowledge")
        technology_net = load_network("technology")
        collaborative_RD_net = load_network("collaborative_R&D")  # 修改网络名称

        # 加载耦合网络（更新耦合网络名称）
        kt_coupling = load_coupling("knowledge-technology")
        tc_coupling = load_coupling("technology-collaborative_R&D")  # 修改耦合网络名称
        kc_coupling = load_coupling("knowledge-collaborative_R&D")   # 修改耦合网络名称

        # 初始化权重矩阵（更新层名称）
        Y = np.ones(3) / 3
        X = {
            "knowledge": np.ones(knowledge_net.number_of_nodes()) / knowledge_net.number_of_nodes(),
            "technology": np.ones(technology_net.number_of_nodes()) / technology_net.number_of_nodes(),
            "collaborative_R&D": np.ones(collaborative_RD_net.number_of_nodes()) / collaborative_RD_net.number_of_nodes()
        }

        # 迭代计算（更新层名称引用）
        for _ in range(config["max_iter"]):
            X_new = {
                "knowledge": np.array(list(nx.pagerank(knowledge_net, alpha=config["alpha"]).values())),
                "technology": np.array(list(nx.pagerank(technology_net, alpha=config["alpha"]).values())),
                "collaborative_R&D": np.array(list(nx.pagerank(collaborative_RD_net, alpha=config["alpha"]).values()))
            }

            # 应用耦合效应（更新层参数）
            def apply_coupling(src_net, dst_net, coupling, src_layer, dst_layer):
                src_nodes = list(src_net.nodes)
                dst_nodes = list(dst_net.nodes)
                for src, dst in coupling.edges():
                    if src in src_nodes and dst in dst_nodes:
                        src_idx = src_nodes.index(src)
                        dst_idx = dst_nodes.index(dst)
                        X_new[dst_layer][dst_idx] += X_new[src_layer][src_idx] * Y[config["layer_order"].index(src_layer)]

            apply_coupling(knowledge_net, technology_net, kt_coupling, "knowledge", "technology")
            apply_coupling(technology_net, collaborative_RD_net, tc_coupling, "technology", "collaborative_R&D")  # 修改参数
            apply_coupling(collaborative_RD_net, knowledge_net, kc_coupling, "collaborative_R&D", "knowledge")     # 修改参数

            # 更新全局权重
            Y_new = np.array([
                X_new["knowledge"].sum(),
                X_new["technology"].sum(),
                X_new["collaborative_R&D"].sum()  # 更新层名称
            ])
            Y_new /= Y_new.sum()

            if np.linalg.norm(Y_new - Y) < config["tol"]:
                break
            Y = Y_new.copy()

        # 保存结果
        np.savetxt(output_path, Y, fmt="%.6f")

        # 生成报告（更新输出名称）
        report = (
            "网络权重计算完成\n"
            f"知识层权重: {Y[0]:.4f}\n"
            f"技术层权重: {Y[1]:.4f}\n"
            f"合作研发层权重: {Y[2]:.4f}\n"  # 修改层名称
            f"权重文件已保存至: {output_path}"
        )
        print(report)
        return report

    except Exception as e:
        error_msg = f"权重计算失败: {str(e)}"
        print(error_msg)
        return error_msg

if __name__ == '__main__':
    calculate_network_weights()