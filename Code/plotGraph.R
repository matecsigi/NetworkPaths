library(igraph)

options(warn=-1)
cmd_args = commandArgs();

infile<-cmd_args[7]
print(infile)

g<-read.graph(infile,format="gml")

#g2 <- as.undirected(g)
#wc <- fastgreedy.community(g2)
#modularity(wc)
#plot(g2, vertex.label=NA, vertex.size=2.5, vertex.color=membership(wc), layout=layout_with_graphopt(g2, niter=100))

#colorVector <- colorRampPalette(c("blue", "yellow"))
#colorFunction <- heat.colors(3)

#E(g)[weight < 10]$color=colorFunction(1)
#E(g)[weight > 10]$color=colorFunction(2)
#E(g)[weight > 20]$color=colorFunction(3)

colorVector <- heat.colors(20)
#plot network
V(g)$color="blue"
V(g)$size=0.2
#E(g)[weight < 10]$color="lightblue"
#E(g)[weight > 10]$color="red"
E(g)$color=colorVector[as.integer(E(g)$weight/20)]
E(g)[weight > 20*19]$color=colorVector[19]
E(g)$width=0.005+0.0005*E(g)$weight

print(min(c(as.integer(E(g)$weight/20), 19)))

pdfFile<-paste(strsplit(infile,"\\.")[[1]][1],"pdf",sep=".")
pdf(pdfFile, width=7.0, height=7.0, paper = "special")

plot(g, vertex.label.family="Helvetica", vertex.label.cex=0.6,vertex.label="", vertex.size=1,edge.arrow.size=0.2, layout=layout_with_graphopt(g, niter=50))

#plot(g, vertex.label.family="Helvetica", vertex.label.cex=0.6,vertex.label="", vertex.size=1,edge.arrow.size=0.2, layout=layout_with_fr(g, niter=10))

#points(0,0) 
dev.off()