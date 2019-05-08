import networkx as nx

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

nrOfPaths = 0
sumPathLength = 0
sumShortestPathLength = 0

with open(fileName, 'r') as f:
    for line in f:
        splitList = line.split()
        if splitList[0] == 'T':
            nrOfPaths = nrOfPaths+1
            sourceIP = splitList[1]
            sourceNode = sourceIP
            destIP = splitList[2]
            path = splitList[13:]
            for i in range(len(path)):
                path[i] = path[i].split(",")[0]
            path = [sourceIP]+path+[destIP]
            sumPathLength = sumPathLength+len(path)
            shortestPathLength = nx.shortest_path_length(G, source=sourceIP, target=destIP, weight=None)
            sumShortestPathLength = sumShortestPathLength+shortestPathLength


print("Number of paths: "+str(nrOfPaths))

avgPathLength = sumPathLength/float(nrOfPaths)
avgShortestPathLength = sumShortestPathLength/float(nrOfPaths)

print("Average path length: "+str(avgPathLength))
print("Average shortest path length: "+str(avgShortestPathLength))
