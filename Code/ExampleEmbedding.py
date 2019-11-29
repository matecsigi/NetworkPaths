import networkx as nx
import math
import matplotlib.pyplot as plt

def positionFromHyperMap():
    position = {}
    with open("coordinates_embedding.txt", "r") as f:
        for line in f:
            splitLine = line.split()
            angle = float(splitLine[1])
            radius = float(splitLine[2])
            x = radius*math.cos(angle)
            y = radius*math.sin(angle)
            position[int(splitLine[0])] = (x, y)
    return position

G = nx.barabasi_albert_graph(100, 2, seed= 210)

nx.write_edgelist(G, "example-edgelist.txt")

hyperbolicPosition = positionFromHyperMap()
colors = [x%10 for x in range((len(G.edges())))]
#nx.draw(G, pos, node_color='#A0CBE2', edge_color=colors,
#        width=4, edge_cmap=plt.cm.Blues, with_labels=False)

#print(colors)

#print(G.edges())

plt.figure()
nx.draw(G, hyperbolicPosition,  node_color='b', node_size=15, edge_color=colors, edge_cmap=plt.cm.Blues, width=1, alpha=0.5)
plt.savefig('example-embedding.png', dpi=1000)
