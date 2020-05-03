import pandas as pd

from Jgraph import Jgraph

# %% 1.导入数据
link_matrix_1 = pd.read_excel('../table/边邻接矩阵1.xlsx', index_col=0)  # 全网络图数据
link_matrix_2 = pd.read_excel('../table/边邻接矩阵2.xlsx', index_col=0)  # 主干道网络图数据
point_location = pd.read_excel('../table/相关的要素名称及位置坐标数据.xls', index_col='要素编号')
point_name = point_location.index

# %% 2. 距离矩阵
distance = pd.DataFrame(0.0, index=point_name, columns=point_name)

for start in point_name:
    for end in point_name:
        x1, y1 = point_location.at[start, 'X坐标（单位：km）'], point_location.at[start, 'Y坐标（单位：km）']
        x2, y2 = point_location.at[end, 'X坐标（单位：km）'], point_location.at[end, 'Y坐标（单位：km）']
        distance.at[start, end] = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** (1 / 2)

A_matrix_1 = distance / 60  # A 车主干道时间
A_matrix_2 = distance / 45  # A 车支干道时间

B_matrix_1 = distance / 50  # B 车主干道时间
B_matrix_2 = distance / 30  # B 车支干道时间


# %% 3.最短路径矩阵
def shortest_matrix(matrix_1, matrix_2):
    nodes = [{"name": i} for i in matrix_1.index]
    links = []

    for start_index, start in enumerate(point_name):
        for end in point_name[start_index + 1:]:
            if link_matrix_1.at[start, end] ^ link_matrix_2.at[start, end]:
                links.append({"source": start, "target": end, "value": matrix_1.at[start, end]})

            if link_matrix_2.at[start, end]:
                links.append({"source": start, "target": end, "value": matrix_2.at[start, end]})

    # 生成 Jgraph 图，调用最短路径算法
    graph = Jgraph(nodes, links)
    paths = graph.shortest_paths(point_name, point_name, 'multi', False)

    cost_matrix = pd.DataFrame(index=point_name, columns=point_name)
    for road in paths:
        start, end, dis = road[0][0][0], road[0][0][-1], road[0][1]
        cost_matrix.at[start, end] = dis
    return graph, cost_matrix

A_graph, A_cost_matrix = shortest_matrix(A_matrix_1, A_matrix_2)
B_graph, B_cost_matrix = shortest_matrix(B_matrix_1, B_matrix_2)
graph, cost_matrix = shortest_matrix(distance, distance)

if __name__ == '__main__':
    A_cost_matrix.to_excel("../table/A 车代价矩阵.xlsx")
    B_cost_matrix.to_excel("../table/B 车代价矩阵.xlsx")
    cost_matrix.to_excel("../table/距离矩阵.xlsx")
