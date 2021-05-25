import networkx as nx
import matplotlib.pyplot as plt

B = nx.Graph()
left_nodes = {'1': 'label1', '2': 'label2', '3': 'label3'}
right_nodes = {'A': 'labelA', 'B': 'labelB', 'C': 'labelC'}
nodes = {**left_nodes, **right_nodes}
edges = {
    ('1', "A"): '1A', 
    ('1', "B"): '1B', 
    ('1', "C"): '1C', 
    ('2', "A"): '2A', 
    ('2', "B"): '2B',
    ('2', "C"): '2C',  
    ('3', "A"): '3A',
    ('3', "B"): '3B',  
    ('3', "C"): '3C'
}
B.add_nodes_from(list(left_nodes.keys()))
B.add_nodes_from(list(right_nodes.keys()))
B.add_edges_from(list(edges.keys()))

X = set(left_nodes.keys())
Y = set(right_nodes.keys())

pos = dict()
pos.update( (n, (1, i)) for i, n in enumerate(X) )
pos.update( (n, (2, i)) for i, n in enumerate(Y) )

nx.draw_networkx_nodes(B, pos, node_size=[len(nodes[i]) ** 2 * 60 for i in pos])
nx.draw_networkx_edges(B, pos)
nx.draw_networkx_labels(B, pos, labels=nodes)
nx.draw_networkx_edge_labels(B, pos, edge_labels=edges, label_pos=0.3)
plt.show()
