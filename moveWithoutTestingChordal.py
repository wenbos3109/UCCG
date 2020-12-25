import matplotlib.pyplot as plt
import networkx as nx
import random

from moveToSnowmanGraph import get_edges_can_be_removed
from networkx.algorithms.approximation.treewidth import treewidth_min_fill_in
from plotNetwork import plotGraph
from uccgGenerator import tree_insertion


def find_edge_to_remove(g):
    _, T = treewidth_min_fill_in(g)
    can_remove = get_edges_can_be_removed(g, T, frozen_edges=set())
    return random.sample(can_remove, 1)[0]


def find_edge_to_add(g):
    _, T = treewidth_min_fill_in(g)
    candidates = set()
    for c1 in T.nodes:
        for c2 in T.neighbors(c1):
            candidates.update([(u, v) for u in c1 for v in c2 if u != v and (u, v) not in g.edges])
    return random.sample(candidates, 1)[0]


def add_remove_using_treeDecomp(g, mixing_time):
    for _ in range(mixing_time):
        u, v = find_edge_to_remove(g)
        g.remove_edge(u, v)
        a, b = find_edge_to_add(g)
        g.add_edge(a, b)

        if not nx.is_chordal(g) or not nx.is_connected(g):
            print('Error: not chordal or disconnected!')
            exit(0)


if __name__ == "__main__":
    # plt.ion()
    num_nodes, num_edges = 10, 18
    g = tree_insertion(num_nodes, num_edges)
    # add_remove_using_treeDecomp(g, mixing_time=5000)
    # G = nx.nx_agraph.to_agraph(g)
    # G.layout(prog='dot')
    # G.draw('file.png')
    plotGraph(g)
    plt.show()


