import matplotlib.pyplot as plt
import networkx as nx
# import pulp

from collections import Iterable
from networkx.drawing.nx_agraph import graphviz_layout

node_size = 100
alpha = 0.3
font_size = 12

in_current = 'in_current'
label = 'label'
INIT = 'INIT'
FINAL = 'FINAL'
COMMON = 'COMMON'
NOTIN = 'NOTIN'

def plotGraphIS(g, figsize=None, pos=None, labels=None):
    if not figsize:
        plt.figure()
    else:
        plt.figure(figsize=figsize)
    plt.axis('off')
    pos = pos if pos else nx.kamada_kawai_layout(g)
    nx.draw_networkx_edges(g, pos)
    nx.draw_networkx_nodes(g, pos, nodelist=[u for u in g.nodes if g.nodes[u][in_current]], node_size=node_size, node_color='r', alpha=0.5)
    nx.draw_networkx_nodes(g, pos, nodelist=[u for u in g.nodes if not g.nodes[u][in_current]], node_size=node_size, node_color='k', alpha=0.3)
    nx.draw_networkx_labels(g, pos)

    
def plotSymmetricDiff(g, figsize=None, pos=None, labels=None):
    if not figsize:
        figsize = (6, 6)
    plt.figure(figsize=figsize)
    plt.axis('off')
    pos = pos if pos else nx.kamada_kawai_layout(g)
    highlight_edges = [(u, v) for (u, v) in g.edges if {g.nodes[u][label],g.nodes[v][label]} == {INIT, FINAL}]
    nx.draw_networkx_edges(g, pos, edgelist = highlight_edges, width=1.5)
    nx.draw_networkx_edges(g, pos, [e for e in g.edges if e not in highlight_edges], width=0.5, style='dashed')
    alpha = 0.5
    nx.draw_networkx_nodes(g, pos, nodelist=[u for u in g if g.nodes[u][label]==INIT],
                           node_size=node_size, node_color='b')
    nx.draw_networkx_nodes(g, pos, nodelist=[u for u in g if g.nodes[u][label]==FINAL], 
                           node_size=node_size, node_color='r')
    nx.draw_networkx_nodes(g, pos, nodelist=[u for u in g if g.nodes[u][label]==COMMON], 
                           node_size=node_size, node_color='g')
    nx.draw_networkx_nodes(g, pos, nodelist=[u for u in g if g.nodes[u][label]==NOTIN], 
                           node_size=node_size, node_color='y', alpha=alpha)
    nx.draw_networkx_labels(g, pos)
    
    
def plotGraphColoring(g, pos=None):
    plt.axis('off')
    pos = pos if pos else nx.kamada_kawai_layout(g)
    nx.draw_networkx_edges(g, pos)
    nx.draw_networkx_nodes(g, pos, node_size=node_size, node_color=[g.nodes[u]['v_color'] for u in g])
    nx.draw_networkx_labels(g, pos)

def plotGraph(g, pos=None, labels=None, color='r', node_list=None):
    plt.axis('off')
    if not pos:
        pos = nx.kamada_kawai_layout(g)
        # pos = graphviz_layout(g, prog='twopi', args='')
    if not labels:
        labels = dict()
        for node in g.nodes:
            if not isinstance(node, Iterable):
                labels[node] = str(node)
            else:
                labels[node] = ','.join(map(str, list(node)))
    nx.draw_networkx_edges(g, pos, width=2)
    node_size = 300
    color = 'white'
    font_size = 13
    alpha=1
    width = 2
    if not node_list:
        nx.draw_networkx_nodes(g, pos, linewidths=width, node_size=node_size, alpha=alpha, node_color=color, edgecolors='k')
    else:
        nx.draw_networkx_nodes(g, pos, linewidths=width, node_size=node_size, alpha=alpha, node_color=color, edgecolors='k', nodelist=node_list)
    nx.draw_networkx_labels(g, pos, labels, font_size=font_size)


def plotCoupling(g1, g2, g1_children, g2_children, dists, joint_prob, e_dist, layout_func=nx.kamada_kawai_layout, pos=None, plotfunc=plotGraph):
    l1, l2 = len(g1_children), len(g2_children)
    for i in range(l1):
        for j in range(l2):
            if joint_prob[i][j].varValue > 1e-5:
                fig = plt.figure()
                plt.cla()
                my_title = fig.suptitle(f"g2 move: {g2.move}\nExpected dist: {e_dist:.4f}\n\
                g1: {g1_children[i].move}; g2: {g2_children[j].move}\ncurrent dist: {dists[i][j]}", fontsize=14, y=-0.01)
                plt.subplot(2, 2, 1)
                plotfunc(g1, pos=pos)

                plt.subplot(2, 2, 2)
                plotfunc(g2, pos=pos)

                ax1 = plt.subplot(2, 2, 3)
                plotfunc(g1_children[i], pos=pos)
                plt.title(f'prob: {g1_children[i].prob:.3f}, joint prob: {joint_prob[i][j].varValue:.3f}')

                plt.subplot(2, 2, 4)
                plotfunc(g2_children[j], pos=pos)
                plt.title(f'prob: {g2_children[j].prob:.3f}')

#                 plt.savefig(f"{i}st_{j}_nd.png",dpi=fig.dpi, bbox_inches='tight', bbox_extra_artists=[my_title])

if __name__ == "__main__":
    g = nx.complete_graph(5)
    plotGraph(g)
    plt.show()