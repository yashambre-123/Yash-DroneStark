import cv2
import numpy as np
import sys
import time
from collections import deque
from csv import reader


def peekNode(node):
    _, nodeType = read_from_csv(str(node))

    return nodeType

def read_from_csv(data):
    #data = str(data)
    #print(data)
    # skip first line i.e. read header first and then iterate over each row od csv as a list
    decodedData = ''
    nodeType = ''
    with open('/home/pi/Documents/MobileRobot/Debug/Repo/NodeTable.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        header = next(csv_reader)
        # Check file as empty
        if header != None:
            #print("Header present")
            # Iterate over each row after the header in the csv
            for row in csv_reader:
                # row variable is a list that represents a row in csv
                if data == row[0]:
                    #print(row[0])
                    decodedData = row[1:5] 
                    nodeType = row[5]
            #print(decodedData) 
    return decodedData, nodeType

def decodeQRData(cur_node, next_node, prev_node):
    valid = -1
    decodedData, nodeType = read_from_csv(str(cur_node))
    print("Current QR is: %s" % cur_node)
    if prev_node == cur_node:
        valid = -2
        return -1, nodeType, valid
    nodes = decodedData 
    #print(nodes)
    for i in range(len(nodes)):
        #print(int(nodes[i]))        
        if int(nodes[i]) == prev_node:
            #print(nodes[i])
            inter = deque(nodes)
            inter.rotate(-i)
            inter = list(inter)
            #print(inter)
            valid = 0
            break

    if valid == -1:
        return -1, nodeType, valid

    for j in range(len(inter)):
        if int(inter[j]) == next_node:
            return j, nodeType, valid

    return -1, nodeType, valid

def decodeQR(data, next_node, prev_node):
    #global cur_node, next_node, prev_node
    valid = -1
    #data = data.decode('utf-8')
    cur_node = int(data.split(":")[0])
    print("Current QR is: %s" % cur_node)
    if prev_node == cur_node:
        valid = -2
        return -1, bedType, valid
    nodes = data.split(":")[1]
    #print(nodes)
    nodes = nodes.split(".")
    print(nodes)
    #print(prev_node)
    for i in range(len(nodes)):
        #print(int(nodes[i]))        
        if int(nodes[i]) == prev_node:
            #print(nodes[i])
            inter = deque(nodes)
            inter.rotate(-i)
            inter = list(inter)
            #print(inter)
            valid = 0
            #return inter
            break

    if valid == -1:
        return -1, bedType, valid

    for j in range(len(inter)):
        if int(inter[j]) == next_node:
            return j, bedType, valid

    return -1, bedType, valid


