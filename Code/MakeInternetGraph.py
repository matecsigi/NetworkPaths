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
