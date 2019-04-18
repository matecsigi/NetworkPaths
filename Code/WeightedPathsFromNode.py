import networkx as nx
import igraph
import datetime

fileName = "../Data/daily.l7.t1.c006274.20180101.anc-us.warts-DECODED.txt"

G = nx.DiGraph()
with open(fileName, 'r') as f:
    for line in f:
        splitList = line.split()
        if splitList[0] == 'T':
            sourceIP = splitList[1]
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
    if G[edge[0]][edge[1]]["weight"] > 8:
        G_filtered.add_edge(edge[0], edge[1], weight=G[edge[0]][edge[1]]["weight"])

print(len(G.edges()))
print(len(G_filtered.edges()))

nx.write_gml(G_filtered, 'edge-filter-8-weighted-network-from-monitor-'+str(datetime.datetime.today().strftime('%Y-%m-%d'))+".gml")
