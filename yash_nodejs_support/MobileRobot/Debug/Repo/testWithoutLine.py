#!/usr/bin/env python3

###################################
# To test algorithm without vehicle
###################################


import time, sys, os
import numpy as np
import cv2
import serial
import argparse
import Main as m
#import qr_detect_test as qr
from qr_detect_test import decodeQR
import pathFind as pf


parser = argparse.ArgumentParser()
parser.add_argument("--world", type=str, default="sampleWorldJson.json")
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--end", type=int, default=3)
parser.add_argument("--room", type=int, default=1)
parser.add_argument("--mode", type=int, default=0)

args = parser.parse_args()

t1 = time.process_time()

def customDelay(t):
    i = 0
    while(i < t):
        i+= 1

    return


def setDirection(direction):
    print("Setting direction: %s" % direction)
    if direction == "L":
        m.leftTurn()
    elif direction == "R":
        m.rightTurn()
    elif direction == "F":
        m.goForward()
    elif direction == "B":
        m.aboutTurn()

    return

def getMotionPath(worldGraph, start_node, end_node):
    motionPath = pf.getPath(worldGraph, str(start_node), str(end_node))
    motionPath = [int(i) for i in motionPath]

    print(motionPath)
    return motionPath

def readInit():
    return 1, -1, 3

def Go():
    #node_list_proxy = [0,1,3]
    #proxy_cnt = 1
    #proxy_map = {0:[1,2], 1:[0,3,4], 2:[0], 3:[1], 4:[1]}

    end_node = args.end
    start_node = args.start

    worldGraph = pf.getWorld(args.world, args.room)     # get world

    sys_states = ["I", "W", "Q", "L", "P"]
    

    checkBlue = 0
    decodeCount = 0

    direction_resolve = {0:"B", 1:"L", 2:"F", 3:"R"}
    current_state = sys_states[0]
    set_init = -1       # no goal set
    set_ret = 0         # not return
    is_moving = 0
    prev_node = -1

    #camera = cv2.VideoCapture(0)

    

    while True:
        #_, frame = camera.read()
        #frame = cv2.resize(frame, (240, 180), cv2.INTER_AREA)
        #cv2.imshow("frame", frame)
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    pass
        #print(prev_node)

        if(current_state == "L"):            
            #checkBlue = m.checkBlueColor(frame)
            #print("decodeCount:")
            #print(decodeCount)
            if(checkBlue == 1 and decodeCount == 0):
                m.stop_no_line()
                #print("blue found")                
                #qr_data = m.findQRcode(frame)
                if(qr_data == ""):
                    pass
                    #print("bad blue")
                else:
                    current_state = "Q"
                #is_moving = 0
                checkBlue = 0
            else:
                #is_moving = m.findLine(frame)
                checkBlue = 0
                if(decodeCount > 0):
                    decodeCount += 1
                if(decodeCount > 100):
                    decodeCount = 0

        elif(current_state == "W"):
            print("Waiting for instruction")

        elif(current_state == "Q"):
            print("State Q")
            #qr_data = m.findQRcode(qr_frame)
            if(decodeCount == 0):
                temp = prev_node
                direction, cur_node = decodeQR(qr_data, next_node, temp)
                #if(cur_node == 0):
                #    prev_node = -1
                #else:
                prev_node = cur_node
                #prev_node = temp
                if(1):
                    if(cur_node != end_node):
                        #arok = setDirection(direction_resolve[direction])
                        #current_state = "L"                        
                    else:
                        if(set_ret == 0):
                            print("Reached destination")
                            current_state = "P"
                        else:
                            current_state = "W"
                            exit(0)
                            #setDirection("F")
                            #setDirection("B")
                            print("Reached home")
                            set_ret = 0

                proxy_cnt += 1
                if(proxy_cnt < len(motionPath)):
                    next_node = motionPath[proxy_cnt]
                else:
                    next_node = cur_node       # set for returning

            #decodeCount += 1
            print("Current node: %s"%cur_node)
            print("Next node: %s"%next_node)
            print("Previous node: %s"%prev_node)
            print(" ")

                            
        elif(current_state == "P"):
            print("State P")
            #pok = deploy_payload()
            set_ret = 1
            setDirection("B")
            start_node, end_node = end_node, start_node     # reverse nodes
            #node_list_proxy = node_list_proxy.reverse()
            #motionPath = motionPath[::-1]
            proxy_cnt = 1
            #current_state = "L"
            current_state = "I"

        elif(current_state == "I"):
            #set_init, start_node, end_node = readInit()
            motionPath = getMotionPath(worldGraph, start_node, end_node)        # get path to follow
            
            print("*************************************")
            print("INITIALIZATION VALUES")
            print("Start and end node are as follows: %s, %s" % (start_node, end_node))
            #print(start_node, end_node)
            #proxy_cnt = 1
            start_node = int(start_node)
            end_node = int(end_node)
            cur_node = start_node
            if set_ret == 1:
                if(len(motionPath) <= 2):
                    motionPath.append(-1)   # hack to not read out of array. 
                proxy_cnt = 2
            else:
                proxy_cnt = 1
            next_node = motionPath[proxy_cnt]
            set_init = 1
            print("Current node: %s"%cur_node)
            print("Next node: %s"%next_node)
            print("Previous node: %s"%prev_node)
            print("*************************************")

            if set_init != -1:
                current_state = "L"
            else:
                current_state = "W"

        global t1
        t2 = time.process_time()

        #print((t2-t1)*1000)
        t1 = t2

def lineFunc():
    camera = cv2.VideoCapture(0)
    while True:
        _, frame = camera.read()
        frame = cv2.resize(frame, (240, 180), cv2.INTER_AREA)
        m.findLine(frame)

if __name__ == "__main__":
    #getMotionPath(2,5)
    
    if(args.mode == 0):
        Go()
    else:
        print("Just following that yellow line")
        lineFunc()
    
