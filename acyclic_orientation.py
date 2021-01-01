
import networkx as nx
from uccgGenerator import tree_insertion
import random
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.algorithms.dag import *
from networkx.algorithms.tree.decomposition import junction_tree
from networkx.algorithms.chordal import chordal_graph_cliques


#%%


label = 'I'
I_edge = 'I_edge'
F_edge = 'F_edge'
common_edge = 'common_edge'
in_current = 'in_current'

connectionstyle = 'arc3, rad=0.1'
node_size = 300
color = 'white'
font_size = 13
alpha=1
width = 2


#%%

def succeed(IF):
    for e in IF.edges:
        if IF.edges[e][label] == I_edge and IF.edges[e][in_current]:
            return False
        if IF.edges[e][label] == F_edge and not IF.edges[e][in_current]:
            return False
    return True


def resample(g, cycles):
    edges_to_resample = set()
    for a, b, c in cycles:
        edges_to_resample.update([(a, b), (b, c), (c, a)])
    for x, y in edges_to_resample:
        flag = random.randint(0, 1)
        if flag == 0:
            continue
        g.remove_edge(x, y)
        g.add_edge(y, x)

#%%

def gen_random_acyclic_orientation(g):
    dg = nx.DiGraph()
    for u, v in g.edges:
        coin = random.randint(0, 1)
        if coin == 0:
            dg.add_edge(u, v)
        else:
            dg.add_edge(v, u)
    while not is_directed_acyclic_graph(dg):
        cycles = [c for c in nx.simple_cycles(dg) if len(c)==3]
        resample(dg, cycles)
    return dg


def current_graph(IF):
    current_edges = [e for e in IF.edges if IF.edges[e][in_current]]
    dg = nx.DiGraph()
    dg.add_edges_from(current_edges)
    return dg


def get_IF(I, F):
    common_edges = list(set(I.edges).intersection(F.edges))
    diff_edges = list(set(I.edges).symmetric_difference(F.edges))
    IF = nx.DiGraph()

    IF.add_edges_from(common_edges+diff_edges)
    for e in set(I.edges) - set(F.edges):
        IF.edges[e][label] = I_edge
        IF.edges[e][in_current] = True
    for e in set(F.edges) - set(I.edges):
        IF.edges[e][label] = F_edge
        IF.edges[e][in_current] = False
    for e in common_edges:
        IF.edges[e][label] = common_edge
        IF.edges[e][in_current] = True
    return IF


def plot_IF(IF, pos):
    color = {I_edge: 'b', F_edge: 'r', common_edge: 'k'}
    width = {True: 1.5, False: 1}
    get_color = lambda e: color[IF.edges[e][label]]
    get_width = lambda e: width[IF.edges[e][in_current]]

    nx.draw_networkx_nodes(IF, pos,
                           node_size=node_size,
                           node_color='white',
                           edgecolors='k')
    nx.draw_networkx_labels(IF, pos)
    edge_lists = [[e for e in IF.edges if IF.edges[e][in_current]],
                  [e for e in IF.edges if not IF.edges[e][in_current]]]
    alphas = [1, 0.5]
    styles = ['solid', 'dashed']
    for i in range(2):
        nx.draw_networkx_edges(IF, pos,
                           edgelist=edge_lists[i],
                           edge_color=list(map(get_color, edge_lists[i])),
                           alpha=alphas[i],
                           style=styles[i],
                           width=list(map(get_width, edge_lists[i])),
                           connectionstyle=connectionstyle)


def plot_complement(IF, pos):
    common_edges = [e for e in IF.edges if IF.edges[e][label] == common_edge]
    complement_edges = [e for e in IF.edges if IF.edges[e][label] != common_edge and not IF.edges[e][in_current]]
    nx.draw_networkx_edges(IF, pos, common_edges,
                           edge_color='k',
                           width=1,
                           alpha=1,
                           connectionstyle=connectionstyle)
    nx.draw_networkx_edges(IF, pos, [e for e in complement_edges if IF.edges[e][label] == I_edge],
                           edge_color='b',
                           width=1,
                           style='dashed',
                           connectionstyle=connectionstyle)
    nx.draw_networkx_edges(IF, pos, [e for e in complement_edges if IF.edges[e][label] == F_edge],
                           edge_color='r',
                           width=1,
                           style='dashed',
                           connectionstyle=connectionstyle)
    nx.draw_networkx_nodes(IF, pos,
                           linewidths=width,
                           node_size=node_size,
                           node_color=color,
                           edgecolors='k')
    nx.draw_networkx_labels(IF, pos)


def plot_rt(g, pos, cycles=None):
    plt.axis('off')
    nx.draw_networkx_edges(g, pos, width=2)
    node_size = 1000
    color = 'white'
    font_size = 13
    alpha = 1
    width = 2
    if not cycles:
        nx.draw_networkx_nodes(g, pos, linewidths=width, node_size=node_size, alpha=alpha, node_color=color,
                               edgecolors='k', node_shape='s')
    else:
        node_contain_cycles = [u for u in g for c in cycles if c.issubset(u)]
        nx.draw_networkx_nodes(g, pos, nodelist=node_contain_cycles, linewidths=width, node_size=node_size, alpha=alpha,
                               node_color=color, edgecolors='r', node_shape='s')
        nx.draw_networkx_nodes(g, pos, nodelist=g.nodes - set(node_contain_cycles), linewidths=width,
                               node_size=node_size, alpha=alpha, node_color=color, edgecolors='k', node_shape='s')

    labels = {u: ','.join(map(str, list(u))) for u in g}
    nx.draw_networkx_labels(g, pos, labels, font_size=font_size)