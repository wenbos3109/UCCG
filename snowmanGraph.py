import matplotlib.pyplot as plt
import networkx as nx
import os
import math
import random

from itertools import combinations
from plotNetwork import plotGraph


def get_size_seq_recur(num_nodes, num_edges, sizes):
    if num_nodes == 0 and num_edges == 0:
        return True
    elif num_nodes == 0 or num_edges == 0 or num_edges < num_nodes - 1:
        return False
    for k in range(sizes[-1]-1, 0, -1):
        sizes.append(k+1)
        if get_size_seq_recur(num_nodes-1, num_edges-k, sizes):
            return True
        sizes.pop()


def get_size_seq(num_nodes, num_edges, largest_size):
    # To form bigger cliques, adjacent two cliques need to share as many edges as possible.
    k = largest_size
    sizes = [k]
    if get_size_seq_recur(num_nodes-k, num_edges-k*(k-1)//2, sizes):
        return sizes
    return []


def build_snowman(num_nodes, num_edges, return_size_seq=False):
    sizes = get_size_seq(num_nodes, num_edges)
    node_set = set(range(num_nodes))
    pre_clique = set()
    cur_clique = set(random.sample(node_set, sizes[0]))
    g = nx.Graph()
    g.add_nodes_from(cur_clique)
    g.add_edges_from(combinations(cur_clique, 2))
    node_set.difference_update(cur_clique)
    for k in sizes[1:]:
        v = random.sample(node_set, 1)[0]
        node_set.remove(v)
        selected_pre_nodes = set(random.sample(cur_clique-pre_clique, k - 1))
        g.add_edges_from([(u, v) for u in selected_pre_nodes])
        pre_clique = cur_clique
        cur_clique = selected_pre_nodes
        cur_clique.add(v)
    return g, sizes if return_size_seq else g


if __name__ == "__main__":
    # In any snowman graph, only the first and second clique can of size greater than 2.
    path = "./snowman sequence"
    # if not os.path.exists(path):
    #     os.mkdir(path)
    # for num_nodes in range(10, 11):
    #     for num_edges in range(num_nodes, num_nodes*(num_nodes-1)//2):
    #         g, sizes = build_snowman(num_nodes, num_edges, return_size_seq=True)
    #         size_seq = ",".join(map(str, sizes))
    #         plotGraph(g)
    #         plt.title("|V|={}, |E|={}, sizes={}".format(num_nodes, num_edges, size_seq))
    #         plt.savefig(os.path.join(path, "{}-{}.jpg".format(num_nodes, num_edges)))
    #         plt.clf()
    #         exit(0)
    #
    for num_nodes in range(6, 11):
        for num_edges in range(num_nodes, num_nodes*(num_nodes-1)//2):
            largest_size = int(math.ceil((math.sqrt(8 * (num_edges - num_nodes) + 17) - 1) / 2)) + 1
            for size in range(largest_size, 1, -1):
                size_seq = get_size_seq(num_nodes, num_edges, size)
                if len(size_seq) == 0:
                    print(num_nodes, num_edges, num_edges - num_nodes, size)
                    break
                # if len(size_seq) > 0:
                #     print(num_nodes, num_edges, num_edges-num_nodes, size_seq)
        print('\n')