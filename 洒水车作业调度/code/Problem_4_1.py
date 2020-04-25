import gurobipy
import pandas as pd

# %% 1. 数据准备
# 导入文件
cost_matrix = pd.read_excel("../table/距离矩阵.xlsx", index_col=0)
link_matrix_1 = pd.read_excel("../table/边邻接矩阵1.xlsx", index_col=0)
link_matrix_2 = pd.read_excel("../table/边邻接矩阵2.xlsx", index_col=0)
point_location = pd.read_excel("../table/相关的要素名称及位置坐标数据.xls", index_col="要素编号")

# 初始化映射表

Z = [point for point in cost_matrix.index if point.startswith(("J", "Z"))]
J = [point for point in cost_matrix.index if point.startswith("F")]

# %% 2. Gurobi 求解
MODEL = gurobipy.Model()

# 创建变量
y = MODEL.addVars(Z, vtype=gurobipy.GRB.BINARY)
b = MODEL.addVars(Z, J, vtype=gurobipy.GRB.BINARY)
gamma = MODEL.addVars(Z)

# 更新变量空间
MODEL.update()

# 创建目标函数
MODEL.setObjective(gamma.sum(), gurobipy.GRB.MINIMIZE)

# 创建约束条件
MODEL.addConstrs(b[z, j] <= y[z] for z in Z for j in J)
MODEL.addConstrs(sum(b[z, j] for j in J) <= 8 for z in Z)
MODEL.addConstrs(sum(b[z, j] for z in Z) == 1 for j in J)
MODEL.addConstr(sum(y[z] for z in Z) == 8)
MODEL.addConstrs(y[z] == 1 for z in [point for point in cost_matrix.index if point.startswith("Z")])
MODEL.addConstrs(gamma[z] == sum(b[z, j] * cost_matrix.at[z, j] for j in J) for z in Z)

# 执行最优化
MODEL.Params.LogToConsole = False
MODEL.optimize()

# 输出结果
clusters = {z: [j for j in J if b[z, j].x] for z in Z if y[z].x}

if __name__ == '__main__':
    from cost_matrix import graph
    import pygraphviz as pgv
    from PIL import Image

    G = pgv.AGraph(directed=False, concentrate=True)
    colors = dict(zip(clusters.keys(), ["#60acfc", "#32d3eb", "#5bc49f", "#feb64d", "#ff7c7c", "#9287e7", "#999999", "#F781FF"]))
    colors.update({end: colors[start] for start, ends in clusters.items() for end in ends})

    # 添加节点
    for point in point_location.index:
        color = colors[point] if point in colors.keys() else "#5bc49f32" if point.startswith("D") else "#0000ff" if point.startswith("F") else "#ff000032"
        fontname = "bold" if point in clusters.keys() else "normal"
        shape = "circle" if point in clusters.keys() else "none"
        width = height = 0.4 if point in clusters.keys() else 0.3

        G.add_node(point, shape=shape, color=color, fontcolor=color, fixedsize=True, width=width, height=height, fontname=fontname,
                   pos=f"{0.06 * point_location.at[point, 'X坐标（单位：km）']},{0.06 * (point_location.at[point, 'Y坐标（单位：km）'])}!")

    # 添加边
    for start in point_location.index:
        for end in point_location.index:
            # 支道
            if link_matrix_1.at[start, end] ^ link_matrix_2.at[start, end]:
                G.add_edge(start, end, color="#00000019")

            # 主道
            if link_matrix_2.at[start, end]:
                G.add_edge(start, end, color="#ff000019", penwidth=2)

    # 加粗显示聚类簇
    for start, ends in clusters.items():
        for paths in graph.shortest_paths([start], ends, "multi", False):
            G.add_edges_from(list(zip(paths[0][0], paths[0][0][1:])), color=colors[start], penwidth=3)

    # 导出图形
    G.layout()
    G.draw("../image/聚类结果.png")

    im = Image.open('../image/聚类结果.png')
    im.show()

# 'Z01': ['F24', 'F25', 'F44', 'F45', 'F46', 'F47', 'F49', 'F50']
# 'Z02': ['F26', 'F29', 'F30', 'F48', 'F51', 'F52', 'F53', 'F56']
# 'Z03': ['F54', 'F55', 'F57', 'F58', 'F59', 'F60']
# 'Z04': ['F31', 'F32', 'F33', 'F34', 'F35', 'F37', 'F38', 'F39']
# 'Z05': ['F20', 'F23', 'F40', 'F41', 'F42', 'F43']
# 'Z06': ['F07', 'F08', 'F09', 'F10', 'F11', 'F12', 'F13', 'F36']
# 'J21': ['F01', 'F02', 'F03', 'F04', 'F05', 'F06', 'F27', 'F28']
# 'J27': ['F14', 'F15', 'F16', 'F17', 'F18', 'F19', 'F21', 'F22']
