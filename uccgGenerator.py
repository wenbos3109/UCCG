import networkx as nx
import random
import dwave_networkx as dnx

from operator import and_
from functools import reduce
from itertools import combinations

class Graph(nx.Graph):
    def __eq__(self, other):
#         this is not true
#         return sorted(self.edges) == sorted(other.edges)
        return self.edges == other.edges
    
    def __neighborSeq__(self):
        return tuple([len(self.edges(v)) for v in sorted(self.nodes)])

    def __hash__(self):
        return hash(self.__neighborSeq__())
    
class DiGraph(nx.DiGraph):
    def __eq__(self, other):
#         this is not true
#         return sorted(self.edges) == sorted(other.edges)
        return self.edges == other.edges
    
    def __neighborSeq__(self):
        return tuple([len(self.edges(v)) for v in sorted(self.nodes)])

    def __hash__(self):
        return hash(self.__neighborSeq__())
    

def tree_insertion(num_nodes, num_edges, return_tree=False):
    tree = nx.random_tree(num_nodes)
    chordal = Graph(tree)
    while len(chordal.edges) < num_edges:
        u, v = random.sample(chordal.nodes, 2)
        chordal.add_edge(u, v)
        while not nx.is_chordal(chordal):
            chordal.remove_edge(u, v)
            u, v = random.sample(chordal.nodes, 2)
            chordal.add_edge(u, v)
    if not return_tree:
        return chordal
    return tree, chordal


def markov_add_remove(g, num_steps):
    # The input should be a UCCG.
    all_edges = set(combinations(g.nodes, 2))
    for _ in range(num_steps):
        u, v = random.sample(g.edges, 1)[0]
        a, b = random.sample(all_edges-g.edges, 1)[0]
        g.remove_edge(u, v)
        g.add_edge(a, b)
        while not nx.is_connected(g) or not nx.is_chordal(g):
            g.add_edge(u, v)
            g.remove_edge(a, b)
            u, v = random.sample(g.edges, 1)[0]
            a, b = random.sample(all_edges - g.edges, 1)[0]
            g.remove_edge(u, v)
            g.add_edge(a, b)


def markov_add_remove_simplicial_vertex(g, num_steps):
    for _ in range(num_steps):
        simplicial_vertices = filter(lambda v: dnx.is_simplicial(g, v), g.nodes)
        v = random.choice(g.nodes)
        # remove an edge
        c = set(g.neighbors(v))
        common_neighbors = reduce(and_, [set(g.neighbors(u)) for u in c])
        common_neighbors = filter(lambda u: u != v, common_neighbors)
        u = random.choice(common_neighbors)
        g.add_edge(u, v)


def markov_add_or_remove(g, num_steps):
    all_edges = set(combinations(g.nodes, 2))
    for _ in range(num_steps):
        flag = random.randint(0, 1)
        if flag == 0:
            u, v = random.sample(g.edges, 1)[0]
            g.remove_edge(u, v)
            while not nx.is_connected(g) or not nx.is_chordal(g):
                g.add_edge(u, v)
                u, v = random.sample(g.edges, 1)[0]
                g.remove_edge(u, v)
        else:
            u, v = random.sample(all_edges - g.edges, 1)[0]
            g.add_edge(u, v)
            while not nx.is_connected(g) or not nx.is_chordal(g):
                g.remove_edge(u, v)
                u, v = random.sample(all_edges - g.edges, 1)[0]
                g.add_edge(u, v)

