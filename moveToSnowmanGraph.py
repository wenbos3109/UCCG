import matplotlib.pyplot as plt
import networkx as nx
import random

from itertools import combinations
from networkx.algorithms.approximation.treewidth import treewidth_min_fill_in
from plotNetwork import plotGraph
from uccgGenerator import tree_insertion
from snowmanGraph import build_snowman


def get_edges_can_be_removed(g, T, frozen_edges=set()):
    # An edge can be removed if it is only in one clique.
    e_to_clique = dict()
    valid_edges = g.edges-frozen_edges
    for u, v in valid_edges:
        e_to_clique[(u, v)] = [c for c in T.nodes if u in c and v in c and len(c) > 2]
    return filter(lambda x: len(e_to_clique[x]) == 1, valid_edges)


def find_valid_clique_pairs(T):
    # A pair of cliques is valid if they are adjacent in the clique tree but one is not the subset of the other.
    return [(c1, c2) for c1 in T.nodes for c2 in T.neighbors(c1) if not c1.issubset(c2) and not c2.issubset(c1)]


def get_edges_can_be_added(valid_clique_pairs):
    can_add = set()
    for c1, c2 in valid_clique_pairs:
        can_add.update([(x, y) for x in c1 - c2 for y in c2 - c1])
    return can_add


def get_edges_in_clique(clique):
    return set(combinations(sorted(clique), 2))


def get_frozen_edges(c1, c2):
    # c1, c2 is a valid pair that we want it to grow larger, so we will freeze all edges inside them, an edge
    # is frozen means it cannot be removed.
    return get_edges_in_clique(c1).union(get_edges_in_clique(c2)) - get_edges_in_clique(c1.intersection(c2))


def get_largest_two_cliques(T):
    # Find the largest two cliques, notice that there are at most 2 cliques of size greater than 2.
    cliques = sorted(list(T.nodes), key=lambda c: (len(c), sorted(c)))
    # Two largest cliques have the same size, use the one with smaller lexicographical as the root
    if len(cliques[-2]) == len(cliques[-1]):
        largest, second_largest = cliques[-2], cliques[-1]
    else:
        largest = cliques[-1]
        second_largest = max(T.neighbors(largest), key=lambda c: len(c))
    return largest, second_largest


def keep_merging_adjacent_cliques(g, input_clique_pair=None):
    _, T = treewidth_min_fill_in(g)
    if not input_clique_pair:
        valid_clique_pairs = find_valid_clique_pairs(T)
        c1, c2 = random.sample(valid_clique_pairs, 1)[0]
    else:
        # This pair need to be guaranteed adjacent in T.
        c1, c2 = input_clique_pair
    frozen_edges = get_frozen_edges(c1, c2)
    can_remove = set(get_edges_can_be_removed(g, T, frozen_edges))
    # While there are edges outside frozen edge set that can be removed (split other cliques and make
    # c1, c2 larger)
    while len(can_remove) > 0:
        can_add = [(u, v) for u in c1-c2 for v in c2-c1]
        u, v = random.sample(can_add, 1)[0]
        x, y = random.sample(can_remove, 1)[0]
        g.add_edge(u, v)
        g.remove_edge(x, y)
        _, T = treewidth_min_fill_in(g)
        union = c1.union(c2)
        # After the transition, the new c1, c2 is pair that has the largest intersection with the old pair.
        c1, c2 = max(find_valid_clique_pairs(T),
                     key=lambda pair: (len(pair[0].intersection(union)),
                     (len(pair[1].intersection(union)))))
        # freeze edges in c1, c2.
        frozen_edges = get_frozen_edges(c1, c2)
        can_remove = get_edges_can_be_removed(g, T, frozen_edges)
        if not nx.is_chordal(g):
            print('Error when merging')
            exit(0)


def stretch(g):
    # Stretch the clique tree to a clique path, the source is the largest clique, then the second
    # largest, and so on.
    _, T = treewidth_min_fill_in(g)
    largest, second_largest = get_largest_two_cliques(T)
    if len(T) == 2:
        return
    if len(second_largest) > 2:
        root, tail = second_largest, list(second_largest-largest)[0]
    else:
        root, tail = largest, random.sample(largest, 1)[0]
    num_involve_cliques = {u: 0 for u in g.nodes}
    for clique in T.nodes:
        num_involve_cliques.update({u: num_involve_cliques[u] + 1 for u in clique})
    edges_cliques_size_2 = [c for c in T.nodes if len(c) == 2]
    edges_to_assign = set(filter(lambda e: tail not in e, edges_cliques_size_2))
    while len(edges_to_assign) > 0:
        x, y = random.sample(edges_to_assign, 1)[0]
        if num_involve_cliques[x] > 1 and num_involve_cliques[y] > 1:
            continue
        edges_to_assign.remove(frozenset([x, y]))
        g.remove_edge(x, y)
        x, y = (x, y) if num_involve_cliques[x] == 1 else (y, x)
        g.add_edge(x, tail)
        num_involve_cliques[x] -= 1
        num_involve_cliques[y] -= 1
        if not nx.is_chordal(g):
            print('Error when stretching')
            exit(0)
    edges_to_assign = [(u, tail) for u in g.nodes if u not in root and (u, tail) in g.edges]
    edges_to_assign.sort()
    tail, _ = edges_to_assign[0]
    for u, v in edges_to_assign[1:]:
        g.remove_edge(u, v)
        g.add_edge(u, tail)
        tail = u


def valid_neighbor(root, child):
    return max(root) < list(child - root)[0]


def calibrate_the_largest_two_cliques(g, root, child):
    u_child = list(child-root)[0]
    root_max = max(root)
    # If the adjacent two largest cliques have the same size, for example two k5 share a k4.
    if len(root) == len(child):
        u_root = list(root - child)[0]
        if u_root != root_max:
            g.remove_edge(u_root, root_max)
            g.add_edge(u_root, u_child)
        return
    num_edges = len(root)-len(child)
    # While the max vertex is not the unique vertex in the child, loop.
    while root_max != u_child:
        # If max vertex is not shared by root and child, we can easily kick it out by removing its
        # incident edges and adding edges incident to u_child.
        u = root_max if root_max not in child else random.sample(root-child, 1)[0]
        subclique = root.difference([u])
        for _ in range(num_edges):
            v = random.sample(list(g.neighbors(u)), 1)[0]
            g.remove_edge(u, v)
            can_add = filter(lambda w: (u_child, w) not in g.edges, subclique)
            w = random.sample(can_add, 1)[0]
            g.add_edge(u_child, w)
            if not nx.is_chordal(g):
                print('Moving out root_max fails, not chordal!')
                exit(0)
        # When second and third cliques are both of size two, there might be a problem.
        _, T = treewidth_min_fill_in(g)
        root, child = get_largest_two_cliques(T)
        u_child = list(child-root)[0]


def move_to_smallest(g):
    # Need to stretch the graph first to make sure the largest two cliques are at the beginning.
    stretch(g)
    _, T = treewidth_min_fill_in(g)
    largest, second_largest = get_largest_two_cliques(T)
    if len(T) == 2:
        if not valid_neighbor(largest, second_largest):
            calibrate_the_largest_two_cliques(g, largest, second_largest)
        return
    # First three largest cliques
    first, second, third = list(nx.dfs_preorder_nodes(T, largest))[:3]
    while not valid_neighbor(first, second) or not valid_neighbor(second, third):
        u = list(third-second)[0]
        v = list(second-first)[0]
        if not valid_neighbor(first, second):
            sub_first_two = nx.Graph(g.subgraph(first.union(second)))
            sub_from_third = nx.Graph(g.subgraph(g.nodes-first.union(second)))
            calibrate_the_largest_two_cliques(sub_first_two, first, second)
            g = nx.Graph(sub_first_two)
            g.add_edges_from(sub_from_third.edges)
            w = random.sample(sub_first_two.nodes, 1)[0]
            g.add_edge(u, w)
        else:
            # If the second and third cliques are invalid, just reconnect all edges (cliques of size 2) to
            # the largest clique, then stretch the graph.
            g.remove_edge(u, v)
            w = random.sample(first-second, 1)[0]
            g.add_edge(u, w)
            for _ in range(len(second)-len(third)):
                y = random.sample(set(g.neighbors(v)), 1)[0]
                g.remove_edge(v, y)
                z = random.sample(first-set(g.neighbors(u)), 1)[0]
                g.add_edge(u, z)
        if not nx.is_chordal(g):
            print('Final is not chordal')
            exit(0)
        stretch(g)
        _, T = treewidth_min_fill_in(g)
        largest, second_largest = get_largest_two_cliques(T)
        first, second, third = list(nx.dfs_preorder_nodes(T, largest))[:3]

    if not valid_neighbor(first, second) or not valid_neighbor(second, third):
        print('Fatal error inside!')
        exit(0)
    # g has been re-allocated, the original reference to g has been lost.
    return g


def test():
    for num_nodes in range(10, 11):
        for num_edges in range(num_nodes*3, num_nodes*(num_nodes-1)//2):
            _, sizes = build_snowman(num_nodes, num_edges, return_size_seq=True)
            for i in range(30):
                g = tree_insertion(num_nodes, num_edges)
                plt.subplot(1, 2, 1)
                plotGraph(g)
                keep_merging_adjacent_cliques(g)
                g = move_to_smallest(g)
                _ , T = treewidth_min_fill_in(g)
                cliques = sorted(list(T.nodes), key=lambda x: len(x), reverse=True)
                clique_size = map(len, cliques)
                if clique_size != sizes:
                    print('Fatal error outside!')
                    plotGraph(g)
                    exit(0)
                plt.subplot(1, 2, 2)
                plotGraph(g)
                plt.show()
                plt.clf()
            print("{} nodes {} edges succeed.".format(num_nodes, num_edges))


if __name__ == "__main__":
    # test()
    g = tree_insertion(num_nodes=6, num_edges=8)
    keep_merging_adjacent_cliques(g)
    # g = move_to_smallest(g)
    plotGraph(g)
    plt.show()



