#!/usr/bin/python3

import numpy as np
import json
from queue import Queue
from queue import LifoQueue
from graph import Graph


def sampleGraph():
    g = Graph('0')
    g.add_edge('0', '11')
    g.add_edge('11', '15')
    g.add_edge('11', '22')
    g.add_edge('11', '12')
    g.add_edge('12', '16')
    g.add_edge('12', '21')
    g.add_edge('12', '13')
    g.add_edge('13', '17')
    g.add_edge('13', '20')
    g.add_edge('13', '14')
    g.add_edge('14', '18')
    g.add_edge('14', '19')

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


def getPath(g, start, end):
    #print(g.graph)
    #start = ['2']
    #end = ['5']
    done = set()
    #path = list()
    q = Queue(maxsize=500)
    m = LifoQueue(maxsize=500)

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
    #json_data_file = "yash_new_qr_map.json"
    json_data_file = "yash_new_qr_map.json"
    worldMap = getWorld(json_data_file, 1)
    #worldMap = sampleGraph()
    getPath(worldMap,'0', '9')
