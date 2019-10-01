import networkx as nx
import igraph
import datetime
import matplotlib.pyplot as plt
import math
import random
import tqdm


fileName = "../Data/daily.l7.t1.c003736.20150102.ams3-nl-DECODED.txt"
mappingFile = "../Data/routeviews-rv2-20150102-1200.pfx2as"

def generatePosition(distance):
    angle = random.uniform(0, 2*math.pi)
    x = distance*math.cos(angle)
    y = distance*math.sin(angle)
    return (x, y)

def positionFromHyperMap():
    position = {}
    with open("/home/ec2-user/NetworkPaths/Tools/DkLab/HyperMap-v1/coordinates_embedding.txt", "r") as f:
        for line in f:
            splitLine = line.split()
            angle = float(splitLine[1])
            radius = float(splitLine[2])
            position[splitLine[0]] = (math.cos(angle*radius), math.sin(angle*radius))
    return position

def createGraph(ipDict):
    
    global sourceNode
    sourceNode = -1

    keyCounter = 0
    nokeyCounter = 0

    G = nx.DiGraph()
    with open(fileName, 'r') as f:
        for line in f:
            splitList = line.split()
            if splitList[0] == 'T' and splitList[12] == 'C':
                sourceIP = splitList[1]
                sourceNode = ipDict[sourceIP]
                destIP = splitList[2]
                path = splitList[13:]
                for i in range(len(path)):
                    path[i] = path[i].split(",")[0]
                pathIP = [sourceIP]+path+[destIP]
                try:
                    pathAS = [ipDict[i] for i in pathIP]
                    keyCounter += 1
                except:
                    nokeyCounter += 1
                for i in range(len(pathAS)-1):
                    source = pathAS[i]
                    dest = pathAS[i+1]
                    if not G.has_edge(source, dest):
                        G.add_edge(source, dest, weight=1)
                    else:
                        G[source][dest]["weight"] = G[source][dest]["weight"]+1

    return G


def ipToBinary(ipAddr):
    ipList = ipAddr.split('.')
    ipListBinary = [format(int(i), '08b') for i in ipList]
    ipBinary = ("").join(ipListBinary)
    return ipBinary


def prefixMatchLength(ipBinary1, ipBinary2):
    for i in range(0, len(ipBinary1)):
        if ipBinary1[:i] != ipBinary2[:i]:
            return i-1


def createIP2AsMapping():

    nodeList = []
    with open(fileName, 'r') as f:
        for line in f:
            splitList = line.split()
            if splitList[0] == 'T' and splitList[12] == 'C':
                sourceIP = splitList[1]
                destIP = splitList[2]
                path = splitList[13:]
                for i in range(len(path)):
                    path[i] = path[i].split(",")[0]
                for i in range(len(path)):
                    path[i] = path[i].split(",")[0]
                    path = [sourceIP]+path+[destIP]
                    for i in range(len(path)):
                        node = path[i]
                        if node not in nodeList:
                            nodeList.append(node)

    fOut = open("ip2AsMappings.txt", "w")
    with open(mappingFile, 'r') as f:
        for line in tqdm.tqdm(f):
            splitList = line.split()
            ip = splitList[0]
            prefixLength = splitList[1]
            asNumber = splitList[2]
            ipBinary = ipToBinary(ip)

            for node in nodeList:
                nodeIPBinary = ipToBinary(node)
                if prefixMatchLength(ipBinary, nodeIPBinary) >= int(prefixLength):
                    fOut.write(node+"\t"+asNumber+"\n")
                    print(node+"\t"+asNumber)

    fOut.close()
#                for node in G.nodes():
#                    nodeIPBinary = ipToBinary(node)
#                    if prefixMatchLength(ipBinary, nodeIPBinary) >= int(prefixLength):
#                        print("MATCH")
#                        if G.has_node(asNumber):
#                            G = nx.contracted_nodes(G, asNumber, node)
#                            print("Merge "+str(len(G.nodes())))
#                        else:
#                            G = nx.relabel_nodes(G, {node: asNumber})
#                            print("Relabel "+str(len(G.nodes())))

def createIP2AsDict():
    ip2AsDict = {}
    with open("ip2AsMappings.txt", "r") as f:
        for line in f:
            splitLine = line.split()
            ip2AsDict[splitLine[0]] = splitLine[1]
    return ip2AsDict

def createShortestPathGraph(G, ipDict):
    G_shortest = G.copy()
    for node in G_shortest.nodes():
        for neighbor in G_shortest.neighbors(node):
            G_shortest[node][neighbor]["weight"] = 1

    with open(fileName, 'r') as f:
        for line in f:
            splitList = line.split()
            if splitList[0] == 'T' and splitList[12] == 'C':
                sourceIP = splitList[1]
                destIP = splitList[2]
                try:
                    sourceAs = ipDict[sourceIP]
                    destAs = ipDict[destIP]
                    shortestPath = nx.shortest_path(G_shortest, sourceAs, destAs, weight=None)
                    for i in range(len(shortestPath)-1):
                        source = shortestPath[i]
                        dest = shortestPath[i+1]
                        G_shortest[source][dest]["weight"] = G_shortest[source][dest]["weight"]+1
                except Exception as e:
                    print("Error:"+str(e))

    return G_shortest

def createDiffGraph(G, G_shortest):
    G_diff = G.copy()
    for node in G.nodes():
        for neighbor in G.neighbors(node):
            G_diff[node][neighbor]["weight"] = abs(G[node][neighbor]["weight"]-G_shortest[node][neighbor]["weight"])
    return G_diff 
    

if __name__=="__main__":
    # createIP2AsMapping();
    ip2AsDict = createIP2AsDict()
    G = createGraph(ip2AsDict)
    nx.write_edgelist(G, "edgelist.txt")

# Plot original
#---------------------------------------------------------
    pos = {}
    for node in G.nodes():
        distance = nx.shortest_path_length(G, sourceNode, node)
        pos[node] = generatePosition(distance)

    edges, weights = zip(*nx.get_edge_attributes(G, 'weight').items())
    zipped = zip(weights, edges)
    zipped.sort()
    edges = [edge for (weight, edge) in zipped]
    weights = [max(0.1, 0.7*math.log(weight)) for (weight, edge) in zipped]

    #nx.draw(G, pos, edgelist = edges, node_color='b', node_size=5, width=weights, edge_color=weights, edge_cmap=plt.cm.autumn, edge_vmin=1)
    #plt.savefig('weightes-paths.png', dpi=1000)

    hyperbolicPosition = positionFromHyperMap()

    nx.draw(G, hyperbolicPosition, edgelist = edges, node_color='b', node_size=5, width=weights, edge_color=weights, edge_cmap=plt.cm.autumn, edge_vmin=1)
    plt.savefig('hyp-weighted-paths.png', dpi=1000)

    print(len(G.nodes()))
    print(len(G.edges()))

# Plot shortest
#--------------------------------------------------
    G_shortest = createShortestPathGraph(G, ip2AsDict)
    print(len(G_shortest.nodes()))
    edges, weights = zip(*nx.get_edge_attributes(G_shortest, 'weight').items())

    edges, weights = zip(*nx.get_edge_attributes(G_shortest, 'weight').items())
    zipped = zip(weights, edges)
    zipped.sort()
    edges = [edge for (weight, edge) in zipped]
    weights = [max(0.1, 0.7*math.log(weight)) for (weight, edge) in zipped]

    hyperbolicPosition = positionFromHyperMap()

    nx.draw(G_shortest, hyperbolicPosition, edgelist = edges, node_color='b', node_size=5, width=weights, edge_color=weights, edge_cmap=plt.cm.autumn, edge_vmin=1)
    plt.savefig('shortest-hyp-weighted-paths.png', dpi=1000)

# Plot difference
#--------------------------------------------------
    G_diff = createDiffGraph(G, G_shortest)
    print(len(G_diff.nodes()))
    edges, weights = zip(*nx.get_edge_attributes(G_diff, 'weight').items())
    print(weights)
    zipped = zip(weights, edges)
    zipped.sort()
    edges = [edge for (weight, edge) in zipped]
    weights = [max(0.1, 0.7*math.log(max(0.001, weight))) for (weight, edge) in zipped]

    hyperbolicPosition = positionFromHyperMap()

    nx.draw(G_diff, hyperbolicPosition, edgelist = edges, node_color='b', node_size=5, width=weights, edge_color=weights, edge_cmap=plt.cm.autumn, edge_vmin=1, with_labels=True, font_size=2)
    plt.savefig('diff-hyp-weighted-paths.png', dpi=1000)
