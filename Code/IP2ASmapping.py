import networkx as nx
import igraph
import datetime
import matplotlib.pyplot as plt
import math
import random
import tqdm

sourcePath = "/home/ec2-user/NetworkPaths/Data/TraceData/ams3-nl-2015/"
fileName = sourcePath+"daily.l7.t1.c003736.20150102.ams3-nl-DECODED.txt"

mappingFile = "../Data/routeviews-rv2-20150102-1200.pfx2as"

def generatePosition(distance):
    angle = random.uniform(0, 2*math.pi)
    x = distance*math.cos(angle)
    y = distance*math.sin(angle)
    return (x, y)

def positionFromHyperMap():
    position = {}
    with open(sourcePath+"coordinates_embedding.txt", "r") as f:
        for line in f:
            splitLine = line.split()
            angle = float(splitLine[1])
            radius = float(splitLine[2])
            x = radius*math.cos(angle)
            y = radius*math.sin(angle)
            position[splitLine[0]] = (x, y)
    return position

def createGraph(ipDict):
    
    global sourceNode
    sourceNode = -1

    graphPathCounter = 0

    G = nx.DiGraph()
    with open(fileName, 'r') as f:
        for line in f:
            splitList = line.split()
            if splitList[0] == 'T' and splitList[12] == 'C':
                sourceIP = splitList[1]
                try:
                    sourceNode = ipDict[sourceIP]
                except Exception as e:
                    # print(str(e))
                    continue
                destIP = splitList[2]
                path = splitList[13:]
                for i in range(len(path)):
                    path[i] = path[i].split(",")[0]
                pathIP = [sourceIP]+path+[destIP]
                try:
                    pathAS = [ipDict[i] for i in pathIP]
                    graphPathCounter += 1
                    for i in range(len(pathAS)-1):
                        source = pathAS[i]
                        dest = pathAS[i+1]
                        if not G.has_edge(source, dest):
                            G.add_edge(source, dest, weight=1)
                        else:
                            G[source][dest]["weight"] = G[source][dest]["weight"]+1
                except:
                    pass
    print("Graph Path Counter: "+str(graphPathCounter))

    for node in G.nodes():
        try:
            G.remove_edge(node, node)
        except:
            pass

    print("Original graph (nodes/edges): "+str(len(G.nodes()))+"/"+str(len(G.edges())))

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

    fOut = open(sourcePath+"ip2AsMappings.txt", "w")
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
    with open(sourcePath+"ip2AsMappings.txt", "r") as f:
        for line in f:
            splitLine = line.split()
            ip2AsDict[splitLine[0]] = splitLine[1]
    return ip2AsDict

def createShortestPathGraph(G, ipDict):
    G_shortest = G.copy()
    for node in G.nodes():
        for neighbor in G.neighbors(node):
            G_shortest[node][neighbor]["weight"] = 0


    asEdgeAddedCounter = 0
    G_AS = nx.read_gml("as-graph-2019-10-08.gml")
    for node in G_shortest.nodes():
        if G_AS.has_node(node):
            for neighbor in G_AS.neighbors(node):
                if G_shortest.has_node(neighbor) and not G_shortest.has_edge(node, neighbor):
                    asEdgeAddedCounter += 1
                    G_shortest.add_edge(node, neighbor, weight=0)
    print("New edges added: "+str(asEdgeAddedCounter))
    print("Total edges: "+str(len(G_shortest.edges()))+" -- "+str(len(G.edges())))

    shortestPathCounter = 0

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
                    shortestPathCounter += 1
                except Exception as e:
                    # print("Error:"+str(e))
                    pass

    print("Shortest path counter: "+str(shortestPathCounter))

    for node in G_shortest.nodes():
        try:
            G_shortest.remove_edge(node, node)
        except:
            pass

    for node in G.nodes():
        for neighbor in G.neighbors(node):
            if G_shortest[node][neighbor]["weight"] == 0:
                G_shortest.remove_edge(node, neighbor)

    print("Shortest graph (nodes/edges): "+str(len(G_shortest.nodes()))+"/"+str(len(G_shortest.edges())))

    return G_shortest

def createDiffGraphs(G, G_shortest):
    G_diff_orig_bigger = G.copy()
    for node in G.nodes():
        for neighbor in G.neighbors(node):
            if G_shortest.has_edge(node, neighbor):
                G_diff_orig_bigger[node][neighbor]["weight"] = max(G[node][neighbor]["weight"]-G_shortest[node][neighbor]["weight"], 0)
            else:
                G_diff_orig_bigger[node][neighbor]["weight"] = G[node][neighbor]["weight"]

    G_diff_shortest_bigger = G_shortest.copy()
    for node in G_shortest.nodes():
        for neighbor in G_shortest.neighbors(node):
            if G.has_edge(node, neighbor):
                G_diff_shortest_bigger[node][neighbor]["weight"] = max(G_shortest[node][neighbor]["weight"]-G[node][neighbor]["weight"], 0)
            else:
                G_diff_shortest_bigger[node][neighbor]["weight"] = G_shortest[node][neighbor]["weight"]

    return G_diff_orig_bigger, G_diff_shortest_bigger 

def calculateEntropyOld(Gr):
    entropy = 0
    for node in Gr.nodes():
        neighborProbList = []
        for neighbor in Gr.neighbors(node):
            if Gr[node][neighbor]["weight"] != 0:
                neighborProbList.append(Gr[node][neighbor]["weight"])
        neighborProbList = normalizeList(neighborProbList)
        print(neighborProbList)
        nodeEntropy = -sum([p*math.log(p, 2) for p in neighborProbList])
        print(nodeEntropy)
        entropy += nodeEntropy

    entropy = float(entropy)/len(Gr.nodes())
    return entropy
    

def calculateEntropyReal(ipDict):
    nodeTable = {}

    with open(fileName, 'r') as f:
        for line in f:
            splitList = line.split()
            if splitList[0] == 'T' and splitList[12] == 'C':
                sourceIP = splitList[1]
                destIP = splitList[2]
                path = splitList[13:]
                for i in range(len(path)):
                    path[i] = path[i].split(",")[0]
                pathIP = [sourceIP]+path+[destIP]
                try:
                    pathAS = [ipDict[i] for i in pathIP]
                    for k in range(len(pathAS)-1):
                        source = pathAS[k]
                        nextAs = pathAS[k+1]
                        # print(str(source + "->"+str(nextAs)))
                        for j in range(k+1, len(pathAS)-1):
                            dest = pathAS[j]
                            # print(str(source + "->"+str(nextAs)+"->"+str(dest)))
                            if not source in nodeTable:
                                nodeTable[source] = {}
                            nodeTable[source][dest] = nextAs
                except Exception as e:
                    # print("Exception: "+str(e))
                    pass

    print(len(nodeTable.keys()))

    valueCounter = 0
    for nodeKey in nodeTable.keys():
        valueCounter += len(nodeTable[nodeKey].keys())
    print("Node table percentage: "+str(100*float(valueCounter)/(len(nodeTable.keys())*len(nodeTable.keys())))+"%")

    # print(nodeTable)

    entropy = 0
    for source, nextHopDict in nodeTable.iteritems():
        nodeOccurrenceList = []
        for key, value in nextHopDict.iteritems():
            nodeOccurrenceList.append(value)
        # print(nodeOccurrenceList)
        nodeProbList = [nodeOccurrenceList.count(x) for x in set(nodeOccurrenceList)]
        # print(nodeProbList)
        nodeProbList = normalizeList(nodeProbList)
        # print(nodeProbList)
        nodeEntropy = -sum([p*math.log(p, 2) for p in nodeProbList])
        # print(nodeEntropy)
        entropy += nodeEntropy
    entropy = float(entropy)/len(nodeTable.keys())
    return entropy


def calculateEntropyShortest(ipDict, Gr_shortest):
    nodeTable = {}

    with open(fileName, 'r') as f:
        for line in f:
            splitList = line.split()
            if splitList[0] == 'T' and splitList[12] == 'C':
                sourceIP = splitList[1]
                destIP = splitList[2]
                path = splitList[13:]
                for i in range(len(path)):
                    path[i] = path[i].split(",")[0]
                pathIP = [sourceIP]+path+[destIP]
                try:
                    pathAS = [ipDict[i] for i in pathIP]
                    for k in range(len(pathAS)-1):
                        source = pathAS[k]
                        for j in range(k+1, len(pathAS)-1):
                            dest = pathAS[j]
                            shortest_path = nx.shortest_path(Gr_shortest, source, dest, weight=None)
                            if not len(shortest_path) > 1:
                                nextAs = shortest_path[0]
                            else:
                                nextAs = shortest_path[1]
                            # print(str(source)+"->"+str(dest)+" :: "+str(nextAs))
                            # print(shortest_path)
                            if not source in nodeTable:
                                nodeTable[source] = {}
                            nodeTable[source][dest] = nextAs
                except Exception as e:
                    # print("Exception: "+str(e))
                    pass

    print(len(nodeTable.keys()))
    valueCounter = 0
    for nodeKey in nodeTable.keys():
        valueCounter += len(nodeTable[nodeKey].keys())
    print("Node table percentage: "+str(100*float(valueCounter)/(len(nodeTable.keys())*len(nodeTable.keys())))+"%")

    # print(nodeTable)

    entropy = 0
    for source, nextHopDict in nodeTable.iteritems():
        nodeOccurrenceList = []
        for key, value in nextHopDict.iteritems():
            nodeOccurrenceList.append(value)
        # print(nodeOccurrenceList)
        nodeProbList = [nodeOccurrenceList.count(x) for x in set(nodeOccurrenceList)]
        # print(nodeProbList)
        nodeProbList = normalizeList(nodeProbList)
        # print(nodeProbList)
        nodeEntropy = -sum([p*math.log(p, 2) for p in nodeProbList])
        # print(nodeEntropy)
        entropy += nodeEntropy
    entropy = float(entropy)/len(nodeTable.keys())
    return entropy


def normalizeList(listNotNormed):
    # print(listNotNormed)
    sum = 0
    for element in listNotNormed:
        sum += element
    listNormed = []
    for element in listNotNormed:
        listNormed.append(float(element)/sum)
    return listNormed

def edgeWeightAnalysis(Gr):
    sourceList = []
    targetList = []
    weightList = []
    for edge in Gr.edges():
        sourceList.append(edge[0])
        targetList.append(edge[1])
        weightList.append(Gr[edge[0]][edge[1]]["weight"])
    sortedEdges = [[x,y,z] for z,x,y in sorted(zip(weightList,sourceList,targetList),reverse=True)]
    for i in range(10):
        print(sortedEdges[i])


if __name__=="__main__":
    #createIP2AsMapping();
    ip2AsDict = createIP2AsDict()
    G = createGraph(ip2AsDict)
    nx.write_edgelist(G, sourcePath+"edgelist.txt")

    print("Real entropy: "+str(calculateEntropyReal(ip2AsDict)))

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

    weights = [max(0.05, 0.4*math.log(weight)) for (weight, edge) in zipped]

    #nx.draw(G, pos, edgelist = edges, node_color='b', node_size=5, width=weights, edge_color=weights, edge_cmap=plt.cm.autumn, edge_vmin=1)
    #plt.savefig('weightes-paths.png', dpi=1000)

    hyperbolicPosition = positionFromHyperMap()

    plt.figure()
    nx.draw(G, hyperbolicPosition, edgelist = edges, node_color='b', node_size=5, width=weights, edge_color=weights, edge_cmap=plt.cm.autumn, edge_vmin=1)
    plt.savefig(sourcePath+'hyp-weighted-paths.png', dpi=1000)

    nx.write_gml(G, sourcePath+'original-graph-'+str(datetime.datetime.today().strftime('%Y-%m-%d'))+".gml")


# Plot shortest
#--------------------------------------------------
    G_shortest = createShortestPathGraph(G, ip2AsDict)
    print("Shortest entropy: "+str(calculateEntropyShortest(ip2AsDict, G_shortest)))

    edges, weights = zip(*nx.get_edge_attributes(G_shortest, 'weight').items())
    zipped = zip(weights, edges)
    zipped.sort()
    edges = [edge for (weight, edge) in zipped]

    weights = [max(0.05, 0.4*math.log(max(weight, 0.01))) for (weight, edge) in zipped]

    d = dict(G_shortest.degree)

    hyperbolicPosition = positionFromHyperMap()

    plt.figure()
#    nx.draw(G_shortest, hyperbolicPosition, edgelist = edges, nodelist=d.keys(), node_color='b', node_size=[v * 0.75 for v in d.values()], width=weights, edge_color=weights, edge_cmap=plt.cm.autumn, edge_vmin=1)
    nx.draw(G_shortest, hyperbolicPosition, edgelist = edges, nodelist=d.keys(), node_color='b', node_size=5, width=weights, edge_color=weights, edge_cmap=plt.cm.autumn, edge_vmin=1)

    plt.savefig(sourcePath+'shortest-hyp-weighted-paths.png', dpi=1000)

    nx.write_gml(G_shortest, sourcePath+'shortest-path-graph-'+str(datetime.datetime.today().strftime('%Y-%m-%d'))+".gml")


# Plot differences
#--------------------------------------------------
    G_diff_orig_bigger, G_diff_shortest_bigger = createDiffGraphs(G, G_shortest)

    print("Orig bigger edges: ")
    edgeWeightAnalysis(G_diff_orig_bigger)

    print("Shortest bigger edges: ")
    edgeWeightAnalysis(G_diff_shortest_bigger)

    edges, weights = zip(*nx.get_edge_attributes(G_diff_orig_bigger, 'weight').items())
    zipped = zip(weights, edges)
    zipped.sort()
    edges = [edge for (weight, edge) in zipped]

    weights = [max(0.01, 0.4*math.log(max(0.001, weight))) for (weight, edge) in zipped]

    hyperbolicPosition = positionFromHyperMap()

    plt.figure()
    nx.draw(G_diff_orig_bigger, hyperbolicPosition, edgelist = edges, node_color='b', node_size=5, width=weights, edge_color=weights, edge_cmap=plt.cm.autumn, edge_vmin=1, with_labels=True, font_size=2)
    plt.savefig(sourcePath+'diff-orig-bigger-hyp-weighted-paths.png', dpi=1000)

#----------------------------

    edges, weights = zip(*nx.get_edge_attributes(G_diff_shortest_bigger, 'weight').items())
    zipped = zip(weights, edges)
    zipped.sort()
    edges = [edge for (weight, edge) in zipped]

    weights = [max(0.01, 0.4*math.log(max(0.001, weight))) for (weight, edge) in zipped]

    hyperbolicPosition = positionFromHyperMap()

    plt.figure()
    nx.draw(G_diff_shortest_bigger, hyperbolicPosition, edgelist = edges, node_color='b', node_size=5, width=weights, edge_color=weights, edge_cmap=plt.cm.autumn, edge_vmin=1, with_labels=True, font_size=2)
    plt.savefig(sourcePath+'diff-shortest-bigger-hyp-weighted-paths.png', dpi=1000)
