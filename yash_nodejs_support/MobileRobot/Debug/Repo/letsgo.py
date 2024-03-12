#!/usr/bin/env python3

import time, sys, os, signal
import numpy as np
import cv2
import serial, signal, socket
import argparse, json
import Main as m
#from qr_detect_test import decodeQRData
import qr_detect_test as qr
import pathFind as pf
import intf_blynk as b


parser = argparse.ArgumentParser()
parser.add_argument("--world", type=str, default="/home/dronestark/Yash-DroneStark/yash_nodejs_support/MobileRobot/Debug/Repo/newQRmap.json")
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--end", type=int, default=0)
parser.add_argument("--room", type=int, default=1)
parser.add_argument("--mode", type=int, default=0)
parser.add_argument("--data_port", type=int, default=40000)

args = parser.parse_args()

# Global Variable
brake = 0

def setDirection(direction, node_type="J"):
    print("Node type: %s" % node_type)
    print("Setting direction: %s" % direction)

    if node_type == "B":
        m.setOnSpotTurn()
        time.sleep(0.1)
        #m.stepBack()
        #time.sleep(0.1)
    if direction == "L":
        m.leftTurn()
    elif direction == "R":
        m.rightTurn()
    elif direction == "F":
        if node_type != "B":
            m.goForward()
        else:
            pass
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

def endRoutine():
    #setDirection("F")
    #setDirection("F")
    #setDirection("F")
    setDirection("B")

    return

def backOutFromPoint():
    #setDirection("P")
    m.stepBack()
    time.sleep(0.5)
    setDirection("B")

    return

def leavePoint(direction, node_type="J"):
    m.stepBack()
    time.sleep(0.5)
    setDirection(str(direction), str(node_type))

    return

def pullBrake(n):
    for i in range(1,n):
        m.stop_no_line()
        time.sleep(0.05)
    return 1

def quit_game(sig, frame):
    print("Sending stop signal")
    pullBrake()
    sys.exit(0)

def emergencyStop(sig, frame):
    global brake
    brake = 1

def cycleCamera(flag):
    if flag == 1:
        cam.release()
        flag = 0
    if flag == 0:
        cam = cv2.VideoCapture(0)
        flag = 1
    return cam, flag

def Go():
    global brake
    #signal.signal(signal.SIGKILL, quit_game)
    signal.signal(signal.SIGUSR1, emergencyStop)
    end_node = args.end
    home_node = args.start

    cmd = {}
    worldGraph = pf.getWorld(args.world, args.room)     # get world

    sys_states = ["I", "W", "J", "B", "L", "E"]
    
    checkBlue = 0
    noLineCount = 1
    decodeCount = 0
    noQrCount = 0
    noQrFlag = 0
    direction = 0
    node_type = "J"

    direction_resolve = {0:"B", 1:"L", 2:"F", 3:"R"}
    indicators = {"red":"%23CC0000", "green":"%230FF000"}

    current_state = "W" #original one
    # current_state = "L"
    # current_state = "I"
    prev_state = current_state
    set_init = -1       # no goal set
    set_ret = 0         # not return
    cam_flag = 0
    cur_node = 0

    trig = 0
    
    # camera = cv2.VideoCapture(0)
    # _, frame = camera.read()
    # frame = cv2.resize(frame, (240, 180), cv2.INTER_AREA)
    
    # cv2.imshow("my original frame: ", frame)
    # if cv2.waitKey(1) == ord('c'):
    #     print("nothing just to stop the camera")
    
    camera = cv2.VideoCapture(0)
    
    while True:
        # camera = cv2.VideoCapture(0)
        _, frame = camera.read()
        frame = cv2.resize(frame, (240, 180), cv2.INTER_AREA)
    
        cv2.imshow("my original frame: ", frame)
        if cv2.waitKey(1) == ord('c'):
            print("nothing just to stop the camera")
        
        print("BRAKE: ", brake)
        if brake == 1:
            current_state = "E"
        print("my name")
        # elif cam_flag == 1:
        #     _, frame = camera.read()
            # try:
            #     frame = cv2.resize(frame, (240, 180), cv2.INTER_AREA)
            # except:
            #     print("Some error with camera buffer")
            #     continue
        # camera = cv2.VideoCapture(0)
        # _, frame = camera.read()
        # frame = cv2.resize(frame, (240, 180), cv2.INTER_AREA)
            
            #cv2.imshow("frame", frame)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    pass

        if(current_state == "L"):
            print("ds")         
            prev_state = current_state
            checkBlue = m.checkBlueColor(frame)
            print("CHECK BLUE: ", checkBlue)
            print("DECODE COUNT: ", decodeCount)

            if(checkBlue == 1 and decodeCount == 0):
                #m.stop_no_line()
                m.stop_for_blue()
                qr_data = m.findQRcode(frame)
                if(qr_data == ""):
                    #print("bad blue: %d", noQrCount)
                    noQrCount += 1
                    if noQrCount == 25:
                        print("Found bad blue")
                        m.clear_blue()
                        noQrCount = 0
                else:
                    current_state = "J"
                    noQrCount = 0
                checkBlue = 0
                noQrFlag = 0
            else:
                if noQrCount > 0:
                    m.clear_blue()
                    noQrCount = 0
                noLineCount = m.findLine(frame, noLineCount)
                if noLineCount > 12:
                    # b.setLEDColor(indicators["red"])
                    # b.setLED(255)
                    noLineCount = 0
                #elif noLineCount == 0:
                #    b.setLEDColor(indicators["green"])
                #    b.setLED(255)
                #    noLineCount += 1
                checkBlue = 0
                if(decodeCount > 0):
                    decodeCount += 1
                if(decodeCount > 100):
                    decodeCount = 0
            print("CURRENT STATE: ", current_state)

        elif(current_state == "W"):
            
            # camera = cv2.VideoCapture(0)
            # _, frame = camera.read()
            # frame = cv2.resize(frame, (240, 180), cv2.INTER_AREA)
            # cv2.imshow("my original frame: ", frame)
            # if cv2.waitKey(1) == ord('c'):
            #     print("nothing just to stop the camera")

            prev_state = current_state
            trig = 0
            # b.setLED(0)
            # b.setLEDColor(indicators["green"])
            # print("Yash")
            print("\nWAITING FOR USER COMMAND\n")
            # print("Ambre")
            # print("dronestark")
            # print("office")
            # while(trig != 1):
            #     trig = int(b.getTrigger())
            # b.setLED(255)

            # bed = int(b.getEndPoint())
            # mode = int(b.getMode())
            bed = 5
            
            print("SET INIT: ", set_init)
            print("BRAKE: ", brake)
            print("CAM FLAG: ", cam_flag)

            if set_init != -1:
                if direction_resolve[direction] == "F":
                    print("Back out from point")
                    backOutFromPoint()
                else:
                    print("Leave Point")
                    leavePoint(direction_resolve[direction], node_type)
                #start_node = end_node
                start_node = motionPath[-2]     # second last point if node wasn't home node
            else:
                start_node = home_node
                # start_node = 2
                #m.clear_no_line()
            if brake == 1:
                m.clear_no_line()
                brake = 0
            # end_node = start_node
            # if mode == 1:
            #     end_node = bed
            # elif mode == 2:
            #     end_node = 0
            #     set_ret = 1
            
            end_node = bed

            decodeCount = 0
            current_state = "I"
            print("START NODE: ", start_node)
            print("END NODE: ", end_node)
            if start_node == end_node:      # if done check pressed at start, then return to wait state
                current_state = "W"
                        
            # cycle camera
            if cam_flag == 1:
                # camera.release()
                cam_flag = 0
            if cam_flag == 0:
                # camera = cv2.VideoCapture(0)
                cam_flag = 1

        elif(current_state == "J"):
            # b.setLEDColor(indicators["green"])
            # b.setLED(255)
            proxy_cnt = 0
            prev_state = current_state
            print("State J")
            if(decodeCount == 0):
                # temp = prev_node
                qr_data = str(qr_data)
                updated_qr_data = qr_data.replace('b','',1)
                # print("UPDATED QR DATA: ", updated_qr_data)
                cur_node = updated_qr_data[1]
                prev_node = cur_node
                temp = prev_node
                # qr_data = str(qr_data)
                # updated_qr_data = qr_data.replace('b','',1)
                # # print("UPDATED QR DATA: ", updated_qr_data)
                # cur_node = updated_qr_data[1]
                # cur_node = int(qr_data)
                print("CUR NODE MERA: ", cur_node)
                if cur_node == prev_node:
                    prev_node = temp
                    proxy_cnt -= 1
                    next_node = motionPath[proxy_cnt]
                if cur_node == next_node:
                    proxy_cnt += 1
                    if proxy_cnt < len(motionPath):
                        next_node = motionPath[proxy_cnt]
                    else:
                        next_node = cur_node
                direction, node_type, valid = qr.decodeQRData(cur_node, next_node, prev_node)
                if proxy_cnt  == len(motionPath) - 1:     # if next node is end node
                    print("Next Node is End node")
                    node_type = qr.peekNode(motionPath[proxy_cnt])   # get node type of node
                #print(direction, node_type, valid)
                
                if(valid == 0):
                    if(cur_node != end_node):
                        arok = setDirection(direction_resolve[direction], str(node_type))
                        print("AROK: ", arok)
                        if node_type == "B":
                            current_state = "W"
                            pullBrake(100)
                        else:
                            current_state = "L"                        
                    else:
                        if(set_ret == 0):
                            print("Reached destination")
                            #current_state = "P"
                        else:                            
                            endRoutine()
                            print("Reached home")                            
                            set_ret = 0
                            set_init = -1
                        current_state = "W"

                elif valid == -1 or valid == -3 or valid == -2:
                    # If a qr that is not in the path is reached, then set to return home and restart
                    start_node, end_node = cur_node, home_node
                    set_ret = 1
                    setDirection("B")
                    current_state = "I"
                elif valid == -2:
                    # If same QR is read again...
                    print("\n%d QR read again", cur_node)
                    #prev_node = temp                # Don't update the previous node
                    #proxy_cnt -= 1                  
                    #next_node = motionPath[proxy_cnt]   # reset next_node to read node again
                    #valid = 0                       # set valid flag = 0
                    #decodeCount = -1                # no need to wait for 100 counts

            decodeCount += 1
            print("\n############################")
            print("Current node: %s"%cur_node)
            print("Next node: %s"%next_node)
            print("Previous node: %s"%prev_node)
            print("############################\n")

        
        elif(current_state == "B"):
            print("State P")
            #conn.sendall(b'R')          # send ack to blynk stating that the rover has reached the desired bed
            #cmd = getCmd(conn)          # get command from blynk to return home
            if cmd["status"][0] == '2':
                set_ret = 1
                backOutFromPoint()
                start_node, end_node = end_node, start_node     # reverse nodes
                proxy_cnt = 1
                current_state = "I"
            else:
                #conn.sendall(b'R')          # need to send ack to free client
                print("Wrong command")
        

        elif(current_state == "I"):
            prev_state = current_state
            print("MY START NODE IS: ",  start_node)
            print("MY END NODE IS: ", end_node)
            motionPath  = getMotionPath(worldGraph, start_node, end_node)        # get path to follow
            print("OUR MOTION PATH: ", motionPath)
            
            print("*************************************")
            print("INITIALIZATION VALUES")
            print("Start and end node are as follows: %s, %s" % (start_node, end_node))
            #print(start_node, end_node)
            #proxy_cnt = 1
            start_node = int(start_node)
            end_node = int(end_node)
            cur_node = start_node
            prev_node = cur_node
            
            #proxy_cnt = 2
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

        elif(current_state == "E"):
            print("EMERGENCY state")
            print(prev_state)

            pullBrake(20)
            # while int(b.checkEmergency()) == 1:
                # b.setLEDColor(indicators["red"])
                # b.toggleLED()
            m.clear_no_line()
            temp = current_state
            current_state = prev_state
            prev_state = temp
            if camera.isOpened():
                camera.release()
                cam_flag = 0
            if cam_flag == 1:
                camera.release()
                cam_flag = 0
            if cam_flag == 0:
                camera = cv2.VideoCapture(0)
                cam_flag = 1
            brake = 0
            # b.setLEDColor(indicators["green"])
                                       


def lineFunc():
    camera = cv2.VideoCapture(0)
    i = 0
    while True:
        _, frame = camera.read()
        frame = cv2.resize(frame, (240, 180), cv2.INTER_AREA)
        # cv2.imshow()
        a = m.findLine(frame, noLineCount)
        # cv2.imshow("Mobo vision",b)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     pass
        if(i == 10):
            print(i)
            pullBrake(i)
            i = 0
        i += 1

if __name__ == "__main__":
    #getMotionPath(2,5)
    if(args.mode == 0):
        print("Ambre")
        Go()
    elif(args.mode == 2):
        pass
        #sock = getUserPort(args.data_port)
        #conn, addr = sock.accept()
        #while True:
        #    getUserCmd(conn)
    else:
        print("Just following that yellow line")
        noLineCount = 0
        lineFunc()
    
