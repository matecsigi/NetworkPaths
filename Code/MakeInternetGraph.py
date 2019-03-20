import networkx as nx
import igraph

G = nx.DiGraph()

fileName = 'cycle-aslinks.l7.t1.c006274.20180101.txt'
with open('../Data/'+fileName, 'r') as f:
    for line in f:
        splitList = line.split()
        if splitList[0] == 'D':
            G.add_edge(splitList[1], splitList[2])

print len(G.nodes())

nx.write_gml(G, 'graph-'+fileName[:-4]+".gml")
