import networkx as nx
import igraph
import datetime
import matplotlib.pyplot as plt
import math
import random

def generatePosition(distance):
    angle = random.uniform(0, 2*math.pi)
    x = distance*math.cos(angle)
    y = distance*math.sin(angle)
    return (x, y)

fileName = "../Data/daily.l7.t1.c006274.20180101.anc-us.warts-DECODED.txt"

sourceNode = -1

G = nx.DiGraph()
with open(fileName, 'r') as f:
    for line in f:
        splitList = line.split()
        if splitList[0] == 'T':
            sourceIP = splitList[1]
            sourceNode = sourceIP
            destIP = splitList[2]
            path = splitList[13:]
            for i in range(len(path)):
                path[i] = path[i].split(",")[0]
            path = [sourceIP]+path+[destIP]
            for i in range(len(path)-1):
                source = path[i]
                dest = path[i+1]
                if not G.has_edge(source, dest):
                    G.add_edge(source, dest, weight=1)
                else:
                    G[source][dest]["weight"] = G[source][dest]["weight"]+1

# filtering edges
G_filtered = nx.DiGraph()
for edge in G.edges():
    if G[edge[0]][edge[1]]["weight"] > 40:
        G_filtered.add_edge(edge[0], edge[1], weight=G[edge[0]][edge[1]]["weight"])

print(len(G.edges()))
print(len(G_filtered.edges()))

pos = {}

for node in G_filtered.nodes():
    distance = nx.shortest_path_length(G, sourceNode, node)
    pos[node] = generatePosition(distance)

edges, weights = zip(*nx.get_edge_attributes(G_filtered, 'weight').items())

zipped = zip(weights, edges)
zipped.sort()
edges = [edge for (weight, edge) in zipped]
weights = [weight for (weight, edge) in zipped]

nx.draw(G_filtered, pos, edgelist = edges, node_color='b', node_size=2, width=0.5, edge_color=weights, edge_cmap=plt.cm.autumn, edge_vmin=10)
plt.savefig('weightes-paths.png', dpi=1000)

#nx.write_gml(G_filtered, 'edge-filter-8-weighted-network-from-monitor-'+str(datetime.datetime.today().strftime('%Y-%m-%d'))+".gml")
