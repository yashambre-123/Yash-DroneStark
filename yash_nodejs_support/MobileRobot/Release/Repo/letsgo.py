#!/usr/bin/env python3

import time, sys, os
import numpy as np
import cv2
import serial, signal, socket
import argparse, json
import Main as m
#import qr_detect_test as qr
from qr_detect_test import decodeQR
import pathFind as pf


parser = argparse.ArgumentParser()
parser.add_argument("--world", type=str, default="/home/pi/Documents/MobileRobot/Release/Repo/tenBedHospital.json")
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--end", type=int, default=3)
parser.add_argument("--room", type=int, default=1)
parser.add_argument("--mode", type=int, default=0)
parser.add_argument("--data_port", type=int, default=40000)

args = parser.parse_args()

t1 = time.process_time()

def getUserPort(port_no):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((socket.gethostname(), port_no))
    sock.listen(5)

    print("opened port")

    return sock

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
    elif direction == "P":
        m.stepBack()

    return

def getMotionPath(worldGraph, start_node, end_node):
    motionPath = pf.getPath(worldGraph, str(start_node), str(end_node))
    motionPath = [int(i) for i in motionPath]

    print(motionPath)
    return motionPath

def readInit():
    return 1, -1, 3

#def quit_handler(sig, frame):

def getUserCmd(conn):
    cmd_recv = 0
    if cmd_recv == 0:
        print("Waiting for cmd")
        cmd_data = conn.recv(1024)

        cmd = json.loads(cmd_data.decode('utf-8'))

        print(cmd)
        time.sleep(5)
        conn.sendall(b'R')

        #if cmd_data["state"] == "Go to Bed":
        #    end_node = cmd_data["Bed"]
        #    cmd_recv = 1

def getCmd(conn):
    cmd_recv = 0
    if cmd_recv == 0:
        print("Waiting for cmd")
        cmd_data = conn.recv(1024)

        cmd = json.loads(cmd_data.decode('utf-8'))

        print(cmd)
        return cmd
        #time.sleep(5)
        #conn.sendall(b'R')

        #if cmd_data["state"] == "Go to Bed":
        #    end_node = cmd_data["Bed"]
        #    cmd_recv = 1


def Go():
    #end_node = args.end
    #sock = get_user_port(args.data_port)
    sock = getUserPort(args.data_port)
    conn, addr = sock.accept()
    start_node = args.start

    cmd_recv = 0
    cmd = {}
    worldGraph = pf.getWorld(args.world, args.room)     # get world

    sys_states = ["I", "W", "Q", "L", "P", "D"]
    

    checkBlue = 0
    decodeCount = 0
    noQrCount = 0

    direction_resolve = {0:"B", 1:"L", 2:"F", 3:"R"}
    current_state = "W"
    set_init = -1       # no goal set
    set_ret = 0         # not return
    cam_flag = 0
    #signal.signal(signal.SIGINT, quit_handler)
    
    while True:
        if cam_flag == 1:
            _, frame = camera.read()
            #i = 0
            #for i in range(5):
            #    camera.grab()
            #    i += 1
            #frame = camera.retrieve()
            frame = cv2.resize(frame, (240, 180), cv2.INTER_AREA)
            #cv2.imshow("frame", frame)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    pass

        if(current_state == "L"):            
            checkBlue = m.checkBlueColor(frame)
            #if noQrCount == 50:
            #    #setDirection("F")
            #    print("Only blue seen, no QR\n")
            #    noQrCount = 0
            #    if noQrCount != 0:
            #        checkBlue = 0       # if only blue seen without QR for 75 counts, find yellow again
            #    noQrCount -= 1

            if(checkBlue == 1 and decodeCount == 0):
                m.stop_no_line()
                #print("blue found")                
                qr_data = m.findQRcode(frame)
                if(qr_data == ""):
                    pass
                    #print("bad blue")
                    #noQrCount += 1
                else:
                    current_state = "Q"
                checkBlue = 0
            else:
                is_moving = m.findLine(frame)
                checkBlue = 0
                if(decodeCount > 0):
                    decodeCount += 1
                if(decodeCount > 100):
                    decodeCount = 0

        elif(current_state == "W"):
            if cam_flag == 0:
                camera = cv2.VideoCapture(0)
                cam_flag = 1
            if set_ret == 1:
                start_node = end_node
                conn.sendall(b'R')          # send ack to blynk stating that the rover has reached the home location
                set_ret = 0
            #else:
            prev_node = -2

            cmd = getCmd(conn)              # get command from blynk for bed number
            if cmd["status"][0] == '1':
                end_node = cmd["Bed"][0]
                #print(end_node)
                decodeCount = 0             # need to reset decodeCount
                current_state = "I"
                reached_home = 0
            else:
                conn.sendall(b'R')          # need to send ack to free client
                current_state = "W"

        elif(current_state == "Q"):
            print("State Q")
            #noQrCount = 0
            if(decodeCount == 0):
                temp = prev_node
                direction, cur_node, valid = decodeQR(qr_data, next_node, temp)
                prev_node = cur_node
                if(valid == 0):
                    if(cur_node != end_node):
                        arok = setDirection(direction_resolve[direction])
                        current_state = "L"                        
                    else:
                        if(set_ret == 0):
                            print("Reached destination")
                            current_state = "P"
                        else:
                            current_state = "W"
                            setDirection("F")
                            setDirection("F")
                            setDirection("F")
                            setDirection("B")
                            print("Reached home")
                            reached_home = 0
                            #set_ret = 0                

                    proxy_cnt += 1
                    if(proxy_cnt < len(motionPath)):
                        next_node = motionPath[proxy_cnt]
                    else:
                        next_node = cur_node       # set for returning
                elif valid == -1 or valid == -2:
                    # If a qr that is not in the path is reached, then set to return home and restart
                    start_node, end_node = cur_node, start_node
                    set_ret = 1
                    setDirection("B")
                    current_state = "I"
                #elif valid == -2:
                #    # If same QR is read again...
                #    prev_node = temp                # Don't update the previous node

            decodeCount += 1
            print("Current node: %s"%cur_node)
            print("Next node: %s"%next_node)
            print("Previous node: %s"%prev_node)
            print(" ")

                            
        elif(current_state == "P"):
            print("State P")
            #pok = deploy_payload()
            conn.sendall(b'R')          # send ack to blynk stating that the rover has reached the desired bed
            cmd = getCmd(conn)          # get command from blynk to return home
            if cmd["status"][0] == '2':
                set_ret = 1
                setDirection("P")
                time.sleep(0.5)
                setDirection("B")
                start_node, end_node = end_node, start_node     # reverse nodes
                proxy_cnt = 1
                current_state = "I"
            else:
                conn.sendall(b'R')          # need to send ack to free client
                print("Wrong command")

        elif(current_state == "I"):
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
                    motionPath.append(-2)   # hack to not read out of array. 
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
                current_state = "D"

        elif(current_state == "D"):
            print("Dead state")

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
    elif(args.mode == 2):
        sock = getUserPort(args.data_port)
        conn, addr = sock.accept()
        while True:
            getUserCmd(conn)
    else:
        print("Just following that yellow line")
        lineFunc()
    
