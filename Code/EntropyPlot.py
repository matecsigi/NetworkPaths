import matplotlib.pyplot as plt
import math

xList = [14.5, 21.4, 61.9, 100.067]
yList = [2.008, 4.42, 230, 75.96]
labelList = ["Amsterdam", "Sydney", "San Francisco", "Barcelona"]

plt.plot(xList, yList, labels=labelList, '-o')
plt.yscale('log')
plt.xlabel("Path Inflation (%)")
plt.ylabel("Shortest path and real trace entropy ratio")
plt.fill_between(xList, 0, yList, alpha=0.15)
plt.savefig('path-inflation-entropy.png', dpi=1000)

