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
print(len(G.edges()))

nx.write_gml(G, 'weighted-path-'+str(datetime.datetime.today().strftime('%Y-%m-%d'))+".gml")
