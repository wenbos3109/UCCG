import networkx as nx
import matplotlib.pyplot as plt
import math
import random
import os

from itertools import combinations
from plotNetwork import plotGraph
from moveToSnowmanGraph import find_valid_clique_pairs, get_frozen_edges, get_edges_can_be_removed
from networkx.algorithms.approximation.treewidth import treewidth_min_fill_in
from uccgGenerator import tree_insertion


path = './treeSeq'
if not os.path.exists(path):
    os.mkdir(path)


def generate_clique(g, vertices):
    g.add_nodes_from(vertices)
    g.add_edges_from(combinations(vertices, 2))


def generate_two_intersected_cliques(m, n, k):
    # m, n are sizes of the two cliques and k is the size of intersection.
    num_vertices = m + n - k
    c1 = nx.Graph()
    c2 = nx.Graph()
    vertices = {i for i in range(num_vertices)}
    common = set(random.sample(vertices, k))
    first = set(random.sample(vertices-common, m-k))
    second = vertices - common - first
    generate_clique(c1, first.union(common))
    generate_clique(c2, second.union(common))

    g = nx.Graph()
    g.add_edges_from(c1.edges)
    g.add_edges_from(c2.edges)
    return g


def plotGraphAndTree(g, T):
    plt.figure()
    plt.subplot(1, 2, 1)
    plotGraph(g)
    plt.subplot(1, 2, 2)
    plotGraph(T)
    print(",".join(map(str, list(T.nodes))))


def keep_merging_adjacent_cliques(g):
    _, T = treewidth_min_fill_in(g)
    valid_clique_pairs = find_valid_clique_pairs(T)
    c1, c2 = random.sample(valid_clique_pairs, 1)[0]
    frozen_edges = get_frozen_edges(c1, c2)
    can_remove = set(get_edges_can_be_removed(g, T, frozen_edges))

    i = 1
    while len(can_remove) > 0:
        can_add = [(u, v) for u in c1-c2 for v in c2-c1]
        u, v = random.sample(can_add, 1)[0]
        x, y = random.sample(can_remove, 1)[0]

        plt.figure(1)
        plt.subplot(1, 2, 1)
        plotGraph(g)
        plt.subplot(1, 2, 2)
        plotGraph(T)

        g.remove_edge(x, y)
        _, T = treewidth_min_fill_in(g)

        plt.figure(2)
        plt.subplot(1, 2, 1)
        plotGraph(g)
        plt.subplot(1, 2, 2)
        plotGraph(T)
        plt.title('remove {}-{}'.format(x, y))

        g.add_edge(u, v)
        _, T = treewidth_min_fill_in(g)

        plt.figure(3)
        plt.subplot(1, 2, 1)
        plotGraph(g)
        plt.subplot(1, 2, 2)
        plotGraph(T)
        plt.title('add {}-{}'.format(u, v))

        img = os.path.join(path, "{}.jpg".format(i))
        plt.savefig(img)

        union = c1.union(c2)
        c1, c2 = max(find_valid_clique_pairs(T),
                     key=lambda pair: (len(pair[0].intersection(union)),
                     (len(pair[1].intersection(union)))))
        frozen_edges = get_frozen_edges(c1, c2)
        can_remove = get_edges_can_be_removed(g, T, frozen_edges)
        if not nx.is_chordal(g):
            print('Error when merging')
            exit(0)
        i += 1
        plt.show()
        plt.clf()


if __name__ == "__main__":
    m, n, k = 10, 10, 3
    #
    g = generate_two_intersected_cliques(m, n, k)
    _, T = treewidth_min_fill_in(g)
    plt.figure()
    plotGraph(T)
    plt.show()
    # for u in g.nodes:
    #     for v in g.nodes:
    #         if u != v and (u, v) not in g.edges:
    #             g.add_edge(u, v)
    #             if not nx.is_chordal(g):
    #                 print('Error')
    #                 plotGraph(g)
    #                 plt.show()
    #             g.remove_edge(u, v)
    # print(nx.is_chordal(g))
    # plt.figure()
    # plotGraph(g)
    # plt.figure()
    # plotGraph(T)
    # plt.show()
    # g = tree_insertion(num_nodes=10, num_edges=15)
    # keep_merging_adjacent_cliques(g)
    # plotGraph(g)
    # plt.show()
    # g = nx.Graph()
    # g.add_edges_from([(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4), (1, 6), (3, 6), (3, 5), (4, 5), (5,6)])
    # plotGraph(g)
    # plt.show()
    # print(nx.is_chordal(g))

