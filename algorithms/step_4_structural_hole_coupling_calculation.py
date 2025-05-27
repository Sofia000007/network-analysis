# Copyright © dongbingxue. All rights reserved.
# License: MIT

import os
from pathlib import Path
import pandas as pd
import numpy as np
from numba import jit


def load_network_data(network_type: str, input_dir: Path) -> tuple:
    """加载网络节点和边数据"""
    try:
        # 构建文件路径
        nodes_path = input_dir / f"{network_type}_network_nodes.csv"
        edges_path = input_dir / f"{network_type}_network_edges.csv"

        # 读取节点数据（单列）
        nodes_df = pd.read_csv(nodes_path)
        if "节点" not in nodes_df.columns:
            raise ValueError("节点文件必须包含'节点'列")
        nodes = nodes_df["节点"].astype(str).unique()

        # 读取边数据（两列）
        edges_df = pd.read_csv(edges_path)
        if not {"节点1", "节点2"}.issubset(edges_df.columns):
            raise ValueError("边文件必须包含'节点1'和'节点2'列")
        edges_df = edges_df[["节点1", "节点2"]].rename(
            columns={"节点1": "source", "节点2": "target"}
        ).applymap(str)

        return nodes, edges_df
    except Exception as e:
        raise RuntimeError(f"[{network_type}]数据加载失败: {str(e)}")


def create_adjacency_matrix(nodes: np.ndarray, edges_df: pd.DataFrame) -> tuple:
    """构建邻接矩阵"""
    try:
        node_index = {node: i for i, node in enumerate(nodes)}
        n = len(nodes)
        adj_matrix = np.zeros((n, n), dtype=np.float32)

        for _, row in edges_df.iterrows():
            src, dst = row["source"], row["target"]
            if src in node_index and dst in node_index:
                i, j = node_index[src], node_index[dst]
                adj_matrix[i, j] = 1
                adj_matrix[j, i] = 1  # 无向图
        return node_index, adj_matrix
    except Exception as e:
        raise RuntimeError(f"邻接矩阵构建失败: {str(e)}")


def calculate_probability_matrix(adj_matrix: np.ndarray) -> np.ndarray:
    """计算邻接概率矩阵"""
    try:
        degree = adj_matrix.sum(axis=1)
        prob_matrix = np.divide(
            adj_matrix,
            degree[:, np.newaxis],
            where=degree[:, np.newaxis] != 0,
            out=np.zeros_like(adj_matrix)
        )
        return prob_matrix
    except Exception as e:
        raise RuntimeError(f"概率矩阵计算失败: {str(e)}")


@jit(nopython=True)
def calculate_constraint(prob_matrix: np.ndarray) -> np.ndarray:
    """Numba加速的限制度计算"""
    n = prob_matrix.shape[0]
    constraint = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i != j and prob_matrix[i, j] > 0:
                pij = prob_matrix[i, j]
                indirect = 0.0
                for k in range(n):
                    if k != i and k != j:
                        indirect += prob_matrix[i, k] * prob_matrix[k, j]
                constraint[i, j] = (pij + indirect) ** 2
    return constraint


def calculate_structural_hole(network_type: str, input_dir: Path, output_dir: Path) -> str:
    """主计算函数"""
    try:
        # 加载数据
        nodes, edges_df = load_network_data(network_type, input_dir)

        # 构建邻接矩阵
        node_index, adj_matrix = create_adjacency_matrix(nodes, edges_df)

        # 计算概率矩阵
        prob_matrix = calculate_probability_matrix(adj_matrix)

        # 计算限制度
        constraint_matrix = calculate_constraint(prob_matrix)

        # 计算结构洞耦合值
        stru_values = 1 - constraint_matrix.sum(axis=1)

        # 生成结果DataFrame
        result_df = pd.DataFrame({
            "节点": nodes,
            "structural_hole_coupling": stru_values,
            "网络层": _get_layer_number(network_type)
        })

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 保存结果
        output_path = output_dir / f"{network_type}_network_structural_hole_coupling.csv"
        result_df.to_csv(output_path, index=False)

        return f"[{network_type}]计算完成，结果保存至：{output_path}"

    except Exception as e:
        return f"[{network_type}]计算失败：{str(e)}"


def _get_layer_number(network_type: str) -> int:
    """获取网络层编号"""
    layer_mapping = {
        "knowledge": 1,
        "technology": 2,
        "collaborative_R&D": 3
    }
    return layer_mapping.get(network_type, 0)


def structural_hole_calculation():
    """统一处理所有网络类型"""
    # 定义路径
    base_dir = Path(__file__).parent.parent
    input_dir = base_dir / "data" / "step2_output"
    output_dir = base_dir / "data" / "step4_output"

    # 处理所有网络类型
    network_types = ["knowledge", "technology", "collaborative_R&D"]
    results = []

    for nt in network_types:
        try:
            res = calculate_structural_hole(nt, input_dir, output_dir)
            results.append(res)
            print(res)
        except Exception as e:
            error_msg = f"[{nt}]处理异常：{str(e)}"
            results.append(error_msg)
            print(error_msg)

    return "\n".join(results)


if __name__ == '__main__':
    # 执行计算并打印结果
    result_log = structural_hole_calculation()

    # 将运行结果写入日志文件
    log_dir = Path(__file__).parent.parent / "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_path = log_dir / "step4_calculation.log"

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(result_log)

    print(f"\n完整日志已保存至：{log_path}")