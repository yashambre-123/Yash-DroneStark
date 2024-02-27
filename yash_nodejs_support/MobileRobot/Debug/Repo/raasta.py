#!/usr/bin/python3

import numpy as np
from queue import Queue
from queue import LifoQueue
from graph import Graph

#graph = {'s':['a'], 'a':['b', 'd', 's'], 'b':['c', 'f', 'a'], 'd':['e', 'a'], 'e':['f','d'], 'c':['b'], 'f':['e', 'b'] }

"""
g = Graph('S')

g.add_edge('S', 'A')
g.add_edge('A', 'B')
g.add_edge('A', '1')
g.add_edge('A', '2')
g.add_edge('B', 'C')
g.add_edge('B', '3')
g.add_edge('B', '4')
g.add_edge('C', 'D')
g.add_edge('C', '5')
g.add_edge('C', '6')
g.add_edge('D', '7')
g.add_edge('D', '8')
g.add_edge('6', 'F')
g.add_edge('8', 'E')
g.add_edge('E', 'F')
g.add_edge('E', '9')
g.add_edge('F', '10')
"""

g = Graph('0')
g.add_edge('0', '1')
g.add_edge('0', '2')
g.add_edge('1', '3')
g.add_edge('1', '4')
g.add_edge('3', '5')



print(g.graph)


start = ['0']
end = ['3']
done = set()
path = list()
q = Queue(maxsize=100)
m = LifoQueue(maxsize=100)

q.put(start[0])
while not q.empty():
    i = q.get()
    m.put(i)
    path.append(i)
    if i == end[0]:
        break
    #print(i)
    nodes = g.graph[i]
    for n in nodes:
        if n not in done:
            #print(n),
            q.put(n)
    done.add(i)

#print (path)

finalPath = list()

#f = m.get()
#while f != start[0]:
#    finalPath.append(f)
#    f = g.graph[f][0]


f = m.get()
finalPath.append(f)
while not m.empty():
    k = m.get()
    #print(f, g.graph[f], k)
    if k == g.graph[f][0]:
        finalPath.append(k)
        f = k
print(finalPath)
