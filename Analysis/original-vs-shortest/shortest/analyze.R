library(igraph)

options(warn=-1)
cmd_args = commandArgs();

infile<-cmd_args[7]
print(infile)

g<-read.graph(infile,format="gml")

#in degree distribution
pdfFile<-paste(strsplit(infile, "\\.")[[1]][1], "in_deg.pdf", sep="_")
pdf(pdfFile, width=7.0, height=7.0, paper = "special")
dd<-degree.distribution(g, cumulative=TRUE, mode="in")
max_degree<-max(degree(g,mode="in"))
plot(0:max_degree, dd, xlab="Degree", ylab="Frequency", log="xy", main="The cumulative in degree distribution in a log-log scale")
coef<-coef(lm (log10(dd) ~ log10(1:(max_degree+1))))
pl_est<- -coef[2]
lines(((1:(max_degree+1))^(-2)) * 10^(coef[1]))
dev.off()

#out degree distribution
pdfFile<-paste(strsplit(infile,"\\.")[[1]][1],"out_deg.pdf",sep="_")
pdf(pdfFile, width=7.0, height=7.0, paper = "special")
dd<-degree.distribution(g, cumulative=TRUE, mode="out")
max_degree<-max(degree(g, mode="out"))
plot(0:max_degree, dd, xlab="Degree", ylab="Frequency", log="xy", main="The cumulative out degree distribution in a log-log scale")
coef<-coef(lm (log10(dd) ~ log10(1:(max_degree+1))))
pl_est<- -coef[2]
lines(0.29245*(1:(max_degree+1))^(-1.5))
dev.off()

#total degree distribution
pdfFile<-paste(strsplit(infile,"\\.")[[1]][1],"total_deg.pdf",sep="_")
pdf(pdfFile, width=7.0, height=7.0, paper = "special")
dd<-degree.distribution(g, cumulative=TRUE, mode="total")
max_degree<-max(degree(g, mode="total"))
plot(0:max_degree,dd,xlab="Degree",ylab="Frequency", log="xy",main="The cumulative out degree distribution in a log-log scale")
coef<-coef(lm (log10(dd) ~ log10(1:(max_degree+1))))
pl_est<- -coef[2]
lines(((1:(max_degree+1))^(-2)) * 10^(coef[1]))
dev.off()

#basic measures
avg_degree_in <- mean(degree(g,mode="in"))
avg_degree_out <- mean(degree(g,mode="out"))

txtFile<-paste(strsplit(infile,"\\.")[[1]][1],"txt",sep=".")
cat("", file=txtFile, append=FALSE)
#avgdist<-average.path.length(g, directed=FALSE, unconnected=TRUE)
avgdist<-average.path.length(g, directed=TRUE, unconnected=FALSE)
#diam<-diameter(g, directed=FALSE, unconnected=TRUE)
diam<-diameter(g, directed=TRUE, unconnected=FALSE)
max_cluster<-max(clusters(g)$csize)
t<-mean(transitivity(g,type="local")[which(degree(g)>1)])
cat("vcount", vcount(g), "\necount", ecount(g), "\navgdeg\t", (ecount(g)*2)/vcount(g), "\navgdeg_in\t", avg_degree_in, "\navgdeg_out\t", avg_degree_out, "\navgdist\t", avgdist, "\ndiameter\t", diam, "\nmax_cluster_size\t", max_cluster, "\nmax_degree\t", max_degree,"\nclustering\t", t,"\n", file=txtFile, append=TRUE)

#g2 <- as.undirected(g)
#wc <- fastgreedy.community(g2)
#modularity(wc)
#plot(g2, vertex.label=NA, vertex.size=2.5, vertex.color=membership(wc), layout=layout_with_graphopt(g2, niter=10000))

#plot network
#V(g)$color="blue"
#V(g)$size=1
#E(g)$color="lightblue"
#E(g)$width=0.5

#pdfFile<-paste(strsplit(infile,"\\.")[[1]][1],"pdf",sep=".")
#pdf(pdfFile, width=7.0, height=7.0, paper = "special")
#plot(g, vertex.label.family="Helvetica", vertex.label.cex=0.6,vertex.label="", vertex.size=1,edge.arrow.size=0.2)
#points(0,0) 
#dev.off()
