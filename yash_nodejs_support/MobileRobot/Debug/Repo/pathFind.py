#!/usr/bin/python3

import numpy as np
import json
from queue import Queue
from queue import LifoQueue
from graph import Graph


def sampleGraph():
    g = Graph('0')
    g.add_edge('0', '1')
    g.add_edge('0', '2')
    g.add_edge('1', '3')
    g.add_edge('1', '4')
    g.add_edge('3', '5')

    return g


def getWorld(data_file, room_no):
    f = open(data_file)
    json_data = json.load(f)

    data = json_data["World"][str(room_no)]

    home = data[0].split(":")[1]
    g = Graph(home)

    #print("data[1:] -> %s" % data[1:])
    for i in data[1:]:
        nodes = i.split(":")
        base_node = nodes[0]
        node_str = nodes[1].split(",")
        #print("base_node -> %s" % base_node)
        #print("node_str -> %s" % node_str)
        
        for j in node_str:
            #print(j)
            g.add_edge(base_node, j)

    print (g.graph)
    return g


def getPath(g, start='2', end='5'):
    #print(g.graph)
    #start = ['2']
    #end = ['5']
    done = set()
    #path = list()
    q = Queue(maxsize=100)
    m = LifoQueue(maxsize=100)

    q.put(start)
    while not q.empty():
        i = q.get()
        m.put(i)
        #path.append(i)
        if i == end:
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
        #if k == g.graph[f][0]:
        if k in set(g.graph[f]):
            finalPath.append(k)
            f = k
    print(finalPath[::-1])
    return finalPath[::-1]



if __name__ == "__main__":
    #json_data_file = "sampleWorldJson.json"
    json_data_file = "newQRmap.json"
    worldMap = getWorld(json_data_file, 1)
    #worldMap = sampleGraph()
    getPath(worldMap,'0', '9')
