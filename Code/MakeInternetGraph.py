import networkx as nx
import igraph
import glob
import datetime

def graphFromFile(fileName):
    G = nx.DiGraph()
    with open(fileName, 'r') as f:
        for line in f:
            splitList = line.split()
            if splitList[0] == 'D':
                G.add_edge(splitList[1], splitList[2])
    return G

folderName = '../Data/AsLinks/'
files = glob.glob(str(folderName)+'*.txt')

G = nx.DiGraph()

for f in files:
    fileGraph = graphFromFile(f)
    G.add_edges_from(fileGraph.edges())
    print(len(G.nodes))

nx.write_gml(G, 'as-graph-'+str(datetime.datetime.today().strftime('%Y-%m-%d'))+".gml")

# Basic graph merging
# fileName1 = 'cycle-aslinks.l7.t1.c006274.20180101.txt'
# fileName2 = 'cycle-aslinks.l7.t1.c006277.20180102.txt'
# G1 = graphFromFile(fileName1)
# G2 = graphFromFile(fileName2)
# G = G1.copy()
# G.add_edges_from(G2.edges())
