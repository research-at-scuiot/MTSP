import gurobipy
import pandas as pd

from cost_matrix import A_graph, B_graph

# %% 1. 数据准备
# 导入文件
A_cost_matrix = pd.read_excel("../table/A 车代价矩阵.xlsx", index_col=0)
B_cost_matrix = pd.read_excel("../table/B 车代价矩阵.xlsx", index_col=0)

# 初始化映射表
cost_matrix = {"A": A_cost_matrix, "B": B_cost_matrix}
graph = {"A": A_graph, "B": B_graph}
alpha = {i: "B" if i in [7, 8, 9, 10, 17, 18, 19, 20] else "A" for i in range(1, 21)}
beta = {i: "D1" if i in range(1, 11) else "D2" for i in range(1, 21)}
w = {"A": 20 / 60, "B": 15 / 60}

I = range(1, 21)
J = [point for point in A_cost_matrix.index if point.startswith("F")]
K = [point for point in A_cost_matrix.index if point.startswith("Z")]

# %% 2. Gurobi 求解
MODEL = gurobipy.Model()

# 创建变量
x = MODEL.addVars(I, J, K, vtype=gurobipy.GRB.BINARY)
t = MODEL.addVars(I)
t_max = MODEL.addVar()

# 更新变量空间
MODEL.update()

# 创建目标函数
MODEL.setObjectiveN(t_max, priority=1, index=0)
MODEL.setObjectiveN(t.sum(), priority=0, index=1)

# 创建约束条件
MODEL.addConstrs(sum(x[i, j, k] for j in J for k in K) == 1 for i in I)
MODEL.addConstrs(sum(x[i, j, k] for i in I for k in K) <= 1 for j in J)
MODEL.addConstrs(sum(x[i, j, k] for i in I for j in J) <= 8 for k in K)
MODEL.addConstrs(t[i] == sum((cost_matrix[alpha[i]].at[beta[i], j] + cost_matrix[alpha[i]].at[j, k]) * x[i, j, k] for j in J for k in K) + w[alpha[i]] for i in I)
MODEL.addConstrs(t_max >= t[i] for i in I)

# 执行最优化
MODEL.optimize()

# 输出结果
print(f"任务完成用时：{round(t_max.x, 2)} h")
print(f"平均用时：{round(t.sum().getValue() / 20, 2)} h")
for i in I:
    for j in J:
        for k in K:
            if x[i, j, k].x:
                path1 = graph[alpha[i]].shortest_paths(beta[i], j, show=False)[0][0][:-1]
                path2 = graph[alpha[i]].shortest_paths(j, k, show=False)[0][0]
                path2[0] = path2[0] + "(作业点)"
                path2[-1] = path2[-1] + "(补水点)"
                points = path1 + path2
                print(f"编号：{alpha[i]}-{i}\t用时：{round(t[i].x, 2)}h\t路线：{' -> '.join(points)}")

