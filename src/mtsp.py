import pandas as pd
filename = 'data.xls'
data = pd.read_excel(filename, index_col='No')
data[data == u'好'] = 1
data[data == u'是'] = 1
data[data == u'高'] = 1
data[data != 1] = -1
#print(data)
x = pd.DataFrame(data.iloc[:, :3].astype(int))
#x = data.iloc[:, :3].values.astype(int) 
print(x)
y = pd.DataFrame(data.iloc[:, 3].astype(int))
print(y)

from sklearn.tree import DecisionTreeClassifier as DTC
dtc = DTC(criterion='entropy') #建立决策树模型，基于信息熵
dtc.fit(x, y)

from sklearn.tree import export_graphviz #可视化决策树
name = 'tree.dot'
with open(name, 'w') as f:
    f = export_graphviz(dtc, feature_names=x.columns, out_file=f)

