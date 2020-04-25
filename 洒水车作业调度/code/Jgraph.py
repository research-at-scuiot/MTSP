import igraph
import pandas as pd


class Jgraph(object):

    def __init__(self, nodes, edges, directed=False):
        self.g = igraph.Graph(directed=directed)

        for node in nodes:
            self.g.add_vertex(node['name'], weight=node.get('value'))
        for edge in edges:
            self.g.add_edge(edge['source'], edge['target'], weight=edge.get('value'))

        self.N = len(self.g.vs)
        self.edge_weights = None if None in self.g.es['weight'] else self.g.es['weight']

    def Series(self, keys, values, name):
        series = pd.Series(dict(zip(keys, values)))
        series.name = name
        return series

    def page_rank(self):
        return self.Series(self.g.vs['name'], self.g.pagerank(), "PageRank算法")

    def degree_centrality(self, mode="all"):
        name = "自由度中心性" if mode == "all" else "(入)自由度中心性" if mode == "in" else "(出)自由度中心性"
        return self.Series(self.g.vs['name'], [degree / (self.N - 1) for degree in self.g.degree(mode=mode)], name)

    def closeness_centrality(self, mode="all"):
        name = "紧密度中心性" if mode == "all" else "(入)紧密度中心性" if mode == "in" else  "(出)紧密度中心性"
        return self.Series(self.g.vs['name'], self.g.closeness(weights=self.edge_weights, mode=mode), name)

    def betweenness_centrality(self):
        return self.Series(self.g.vs['name'], [2 * betweenness / ((self.N - 1) * (self.N - 2)) for betweenness in
                                               self.g.betweenness(weights=self.edge_weights)], "介数中心性")

    def eigenvalue_centrality(self):
        return self.Series(self.g.vs['name'], self.g.eigenvector_centrality(weights=self.edge_weights), "特征值中心性")

    def shortest_paths(self, source, target, mode="single", show=True):
        if mode is "multi":
            search_shortest_paths = []
            for single_source in source:
                for single_target in target:
                    search_shortest_paths.append(self.__search_shortest_paths(single_source, single_target, show))
            return search_shortest_paths
        else:
            return self.__search_shortest_paths(source, target, show)

    def __search_shortest_paths(self, single_source, single_target, show):
        try:
            shortest_paths_ids = self.g.get_all_shortest_paths(single_source, single_target, weights=self.edge_weights)
            shortest_paths_names = [[self.g.vs[id]['name'] for id in shortest_paths_id] for shortest_paths_id in
                                    shortest_paths_ids]
            if self.edge_weights:
                shortest_paths_lengths = [sum(self.g.es[self.g.get_eids(path=shortest_paths_ids[i])]['weight']) for i in
                                          range(len(shortest_paths_ids))]
            else:
                shortest_paths_lengths = [len(shortest_paths_ids[i]) - 1 for i in range(len(shortest_paths_ids))]

            if show:
                for (d, shortest_path_name) in enumerate(shortest_paths_names):
                    print(f"Path {d + 1} ({shortest_paths_lengths[d]}): {' -> '.join(shortest_path_name)}")
            return list(zip(shortest_paths_names, shortest_paths_lengths))
        except IndexError:
            return [[], float("inf")]

    def consine_similarity(self):
        return pd.DataFrame(self.g.similarity_dice(), index=self.g.vs["name"], columns=self.g.vs["name"])

    def jaccard_similarity(self):
        return pd.DataFrame(self.g.similarity_jaccard(), index=self.g.vs["name"], columns=self.g.vs["name"])