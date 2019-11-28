import matplotlib.pyplot as plt
import math

xList = []
yList = []

with open("/home/ec2-user/NetworkPaths/Tools/DkLab/HyperMap-v1/coordinates_embedding.txt", "r") as f:
    for line in f:
        splitLine = line.split()
        angle = float(splitLine[1])
        radius = float(splitLine[2])
        x = radius*math.cos(angle)
        y = radius*math.sin(angle)
        xList.append(x)
        yList.append(y)

plt.scatter(xList, yList)
plt.savefig('internet-embedding.png', dpi=1000)

