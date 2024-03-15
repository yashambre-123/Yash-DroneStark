import sys
import os, signal
import numpy as np
#import pdb
import serial, struct
import cv2
import time
#import RPi.GPIO as GPIO
import pyzbar.pyzbar as pyzbar
from Image import *
from Utils import *
import qr_detect_test as qr
import yash_path_find as pf
import argparse
import time
from csv import reader
# import sys

# end_node = sys.argv[1]

parser = argparse.ArgumentParser()
parser.add_argument("--world", type=str, default="/home/dronestark/Yash-DroneStark/yash_nodejs_support/MobileRobot/Debug/Repo/yash_new_qr_map.json")
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--end", type=int, default=0)
parser.add_argument("--room", type=int, default=1)
parser.add_argument("--mode", type=int, default=0)
parser.add_argument("--data_port", type=int, default=40000)

args = parser.parse_args()

print("END NODE: ", args.end)

ser = serial.Serial("/dev/ttyACM0", baudrate = 115200, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, xonxoff = False, rtscts = False, stopbits = serial.STOPBITS_ONE, timeout = 1, dsrdtr = True)
checkBlue = 0
lineFoundFlag = 0
prev_theta = 0
t1 = 0
#font = cv2.FONT_HERSHEY_SIMPLEX
Images=[]
N_SLICES = 6
ret = b'R'
lineOrient = [0]*(N_SLICES-1)
deltaX = [0]*(N_SLICES-1)

# universal_direction = 'y'
# universal_cardinal = 'y'

for q in range(N_SLICES):
    Images.append(Image())

# datapacket = ser.readline()

with open('/home/dronestark/Yash-DroneStark/yash_nodejs_support/MobileRobot/Debug/Repo/ds_node_table.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        header = next(csv_reader)
        data = list(csv_reader)
    
def stop_to_quit(sig, frame):
    print("Sending stopping signal")
    #send_theta(0)
    #send_theta(0)
    #send_theta(0)
    ser.write('Z'.encode('utf-8'))
    #ack = ser.read(1)
    #if(ack == b'R'):
    #    a = ser.read(1)
    #   print(a)
    sys.exit(0)

def stop_no_line():
    ser.write('Z'.encode('utf-8'))
    return

def clear_no_line():
    ser.write('Y'.encode('utf-8'))
    return

def stop_for_blue():
    ser.write('W'.encode('utf-8'))
    return

def clear_blue():
    ser.write('S'.encode('utf-8'))
    return

def stepBack():
    ser.write('P'.encode('utf-8'))
    return

def setOnSpotTurn():
    ser.write('O'.encode('utf-8'))
    return

def aboutTurn():
    print("About turn")
    ser.write('Z'.encode('utf-8'))
    ser.write('U'.encode('utf-8'))
    #ack = ser.read(1)
    #print(ack)
    return 

def leftTurn():
    print("Left turn")     
    ser.write('L'.encode('utf-8'))
    # datapacket = ser.readline()
    # datapacket = str(datapacket,'utf-8')
    # datapacket = datapacket.strip('\r\n')
    # print(datapacket)
    #ack = ser.read(1)
    #print(ack) 
    return

def rightTurn():
    print("Right turn")   
    ser.write('R'.encode('utf-8'))
    # datapacket = ser.readline()
    # datapacket = str(datapacket,'utf-8')
    # datapacket = datapacket.strip('\r\n')
    # print(datapacket)
    #ack = ser.read(1)
    #print(ack)
    return

def goForward():
    print("Go forward")     
    ser.write('F'.encode('utf-8'))
    # datapacket = ser.readline()
    # datapacket = str(datapacket,'utf-8')
    # datapacket = datapacket.strip('\r\n')
    # print(datapacket)
    #ack = ser.read(1)
    #print(ack) 
    return

def map(x, in_min, in_max, out_min, out_max):
    return int(((x-in_min) * (out_max-out_min)/ (in_max-in_min)+out_min))

def send_theta(theta_l):    
    ser.write('A'.encode("utf-8"))
    ser.write(struct.pack("<i", theta_l))
    #ack = ser.read(1)
    #if(ack == b'R'):
    #    a = struct.unpack("<h",ser.read(2))
    return

def stop_detected_qr_code():
    print("Stopped detected qr code")
    ser.write('B'.encode('utf-8'))

def findQRcode(frame): 
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #thres, gray = cv2.threshold(gray, 127,255, cv2.THRESH_BINARY)
    #gray = cv2.bitwise_not(gray)
    decodedData = ""
    decodedObjects = pyzbar.decode(frame)
    for obj in decodedObjects:
        decodedData = obj.data
    # uncomment this if you want to check blue white qr 
    #if len(decodedData) > 6:
    #    decodedData = decodedData[0: 0:] + decodedData[6 + 1::]
    return decodedData
    
def checkBlueColor(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    global checkBlue
    checkBlue = 0
    # define range of blue color in HSV
    lower_thresh_blue = np.array([116,62,83])
    upper_thresh_blue = np.array([179,255,255])
    # Threshold the HSV image to get only blue color
    maskBlue = cv2.inRange(hsv, lower_thresh_blue, upper_thresh_blue)
    #add erode to remove unneccessory blue color
    #kernel = np.ones((5,5), np.uint8)
    #maskBlue = cv2.erode(maskBlue, kernel, iterations= 1)
    contoursBlue, hierarchyBlue = cv2.findContours(maskBlue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #imgBlue = cv2.bitwise_and(frame,frame, mask= maskBlue)
    if (len(contoursBlue) > 0):
        checkBlue = 1
    else:
        checkBlue = 0
    #cv2.imshow("Blue color", maskBlue)
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    pass
    #return checkBlue,imgBlue
    return checkBlue

def findLine(frame, noLineCount):
    global lineFoundFlag
    global prev_theta
    lineFoundFlag = 0
    #if noLineCount > 15:
    #    clear_no_line()
    #    #send_theta(prev_theta*-1)
    #    noLineCount = 0
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # define range of yellow color in HSV
    lower_thresh = np.array([25,90,20])
    upper_thresh = np.array([50,255,255])    
    mask = cv2.inRange(hsv, lower_thresh, upper_thresh)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)            
    # Bitwise-AND mask and original image
    img = cv2.bitwise_and(frame,frame, mask= mask) 
    fm = img
    if(len(contours) != 0):
        lineFoundFlag = 1
        noLineCount = 0
        if img is not None:
            lineOrient, deltaX =  SlicePart(img, Images, N_SLICES)
            toSendDeltaX = deltaX[0]
            for i in range(len(deltaX)-1):
                if(abs(deltaX[i]) <= 120):
                    toSendDeltaX = deltaX[i]
                    break;                    
            prev_theta = toSendDeltaX*-1
            send_theta(toSendDeltaX*-1)
            #print("toSendDeltaX")
            #print(toSendDeltaX)
            fm = RepackImages(Images)
            cv2.imshow("Mobo Vision", fm)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    pass
        else:
            pass
    else:
        lineFoundFlag = 0
        stop_no_line()
        noLineCount += 1
    #return lineFoundFlag
    # return noLineCount
    return lineFoundFlag

def getMotionPath(worldGraph, start_node, end_node):
    motionPath = pf.getPath(worldGraph, str(start_node), str(end_node))
    motionPath = [int(i) for i in motionPath]

    print(motionPath)
    return motionPath

def get_motion_path_directions(start_node, end_node):
    header_counter = -1
    
    for row in data:
        row[0] = int(row[0])
        row[1] = int(row[1])
        row[2] = int(row[2])
        row[3] = int(row[3])
        row[4] = int(row[4])
        
        if (row[0] == start_node):
            for i in row:
                header_counter = header_counter + 1
                if (i == end_node):
                    return header[header_counter]

def new_func(frame, next_node):
    
    decoded_data = findQRcode(frame)
    
    if (decoded_data == ""):
        pass
    else:
        decodedData = str(decodedData)
        decodedData = decodedData.split("'")
        decodedData = int(decodedData[1])
        
        if (decoded_data != next_node):
            print("going in wrong direction")
        elif (decoded_data == next_node):
            return "ok"

def main():
    global lineFoundFlag
    checkBlue = 0
    decodedData = ""
    countLeft = 0
    countRight = 0
    countU = 0
    signal.signal(signal.SIGINT, stop_to_quit)
    worldGraph = pf.getWorld(args.world, args.room)
    
    try:
        camera = cv2.VideoCapture(0)                                
        print("Main")
        while True:
            # global universal_direction
            # global universal_cardinal
            _, frame = camera.read() 
            frame = cv2.resize(frame,(240,180), cv2.INTER_AREA)
            cv2.imshow("Original Image", frame)
            if cv2.waitKey(1) == ord('c'):
                break
            #checkBlue, imgBlue = checkBlueColor(frame)
            checkBlue = checkBlueColor(frame)
            if(checkBlue == 1):  
                # stop_no_line()                                
                decodedData = findQRcode(frame)
                if decodedData == "":
                    # print("show the complete qr code")
                    continue
                else:
                    decodedData = str(decodedData)
                    decodedData = decodedData.split("'")
                    decodedData = int(decodedData[1])
                    # decodedData = str(decodedData)
                    # print("DECODED DATA: ", decodedData)
                    
                    stop_detected_qr_code()
                    
                    start_node = decodedData
                    
                    end_node = args.end
                    
                    motionPath = getMotionPath(worldGraph, start_node, end_node)        # get path to follow
                    
                    print("MotionPath: ",motionPath)
                    
                    my_cardinal_direction_list = []
                    
                    my_direction_list = []
                    
                    # print("OUR MOTION PATH: ", motionPath)
                    
                    for nnodes in range(len(motionPath) - 1):
                        current_node = motionPath[nnodes]
                        next_node = motionPath[nnodes + 1]
                        direction_to_take = get_motion_path_directions(current_node, next_node)
                        my_cardinal_direction_list.append(direction_to_take)
                        # print("go towards: ", direction_to_take)
                        # status = new_func(frame, next_node)
                    
                    print("these are cardinal directions: ", my_cardinal_direction_list)
                    
                    matrix = [
                        ['S','R','L','T'],
                        ['L','S','T','R'],
                        ['R','T','S','L'],
                        ['T','L','R','S']
                    ]
                    
                    my_dict = {
                        "North": 0,
                        "East": 1,
                        "West": 2,
                        "South": 3
                    }
                    
                    my_direction_list.append('S')
                    
                    for i in range(len(my_cardinal_direction_list)-1):
                        curr_direc = my_cardinal_direction_list[i]
                        next_direc = my_cardinal_direction_list[i+1]
                        to_go = matrix[my_dict[my_cardinal_direction_list[i]]][my_dict[my_cardinal_direction_list[i+1]]]
                        my_direction_list.append(to_go)
                        # print("go in this direction: ", to_go)
                    
                    print("go in these directions: ", my_direction_list)
                        
                    
                    # datapacket = ser.readline()
                    # datapacket = str(datapacket,'utf-8')
                    # datapacket = datapacket.strip('\r\n')
                    # print(datapacket)
                    
                    for i in range(len(motionPath)):
                        print("IIIIIIIIIIII: ", i)
                        if (i==0):
                            send_direction = 'S'
                            if (send_direction == 'S'):
                                goForward()
                            # noLineCount = 0
                            # lineFoundFlag = findLine(frame, noLineCount)
                            # while (ser.in_waiting==0):
                            #     pass
                            # datapacket = ser.readline()
                            # datapacket = str(datapacket,'utf-8')
                            # datapacket = datapacket.strip('\r\n')
                            # print(datapacket)
                        else:
                            # camera1 = cv2.VideoCapture(1)
                            # universal_direction = matrix[my_dict[my_direction_list[i]]][my_dict[my_direction_list[i+1]]]
                            while True:
                                # print("FOLLOW MODE")
                                _1, frame1 = camera.read() 
                                frame1 = cv2.resize(frame1,(240,180), cv2.INTER_AREA)
                                cv2.imshow("Follow Image", frame1)
                                if cv2.waitKey(1) == ord('c'):
                                    break
                                
                                checkBlue = checkBlueColor(frame1)
                                
                                if (checkBlue != 1):
                                    noLineCount = 0
                                    lineFoundFlag = findLine(frame1, noLineCount)
                                    if (lineFoundFlag == 0):
                                        # print("NOT ON THE LINE")
                                        pass
                                    else:
                                        print("FOLLOWING THE LINE")
                                    
                                elif (checkBlue == 1):
                                       
                                    decodedData = findQRcode(frame1)
                                    if decodedData == "":
                                        # print("show the complete qr code")
                                        continue
                                    else:
                                        decodedData = str(decodedData)
                                        decodedData = decodedData.split("'")
                                        decodedData = int(decodedData[1])
                                        
                                        stop_detected_qr_code()
                                        
                                        if (decodedData != motionPath[i]):
                                            print("wrong qr detected")
                                        elif (decodedData == motionPath[len(motionPath) - 1]):
                                            print("--------------REACHED DESTINATION--------------")
                                            break
                                        else:
                                            send_direction = matrix[my_dict[my_cardinal_direction_list[i-1]]][my_dict[my_cardinal_direction_list[i]]]
                                            # break
                                            if (send_direction == 'S'):
                                                # print("i am going forward")
                                                goForward()
                                                # datapacket = ser.readline()
                                                # datapacket = str(datapacket,'utf-8')
                                                # datapacket = datapacket.strip('\r\n')
                                                # print(datapacket)
                                            elif (send_direction == 'R'):
                                                rightTurn()
                                                # datapacket = ser.readline()
                                                # datapacket = str(datapacket,'utf-8')
                                                # datapacket = datapacket.strip('\r\n')
                                                # print(datapacket)
                                            elif (send_direction == 'L'):
                                                leftTurn()
                                                # datapacket = ser.readline()
                                                # datapacket = str(datapacket,'utf-8')
                                                # datapacket = datapacket.strip('\r\n')
                                                # print(datapacket)
                                            elif (send_direction == 'T'):
                                                aboutTurn()
                                                # datapacket = ser.readline()
                                                # datapacket = str(datapacket,'utf-8')
                                                # datapacket = datapacket.strip('\r\n')
                                                # print(datapacket)
                                                
                                            # print("jklsja")
                                            
                                            # datapacket = ser.readline()
                                            # datapacket = str(datapacket,'utf-8')
                                            # datapacket = datapacket.strip('\r\n')
                                            # print(datapacket)
                                            
                                            # print("dkdljdkj")
                                            break
                                # break
                    # print("-------------------REACHED DESTINATION-------------------")             
                    
                    # if (universal_direction == 'S'):
                    #     goForward()
                        
                    # elif (universal_direction == 'R'):
                    #     rightTurn()
                    
                    # elif (universal_direction == 'L'):
                    #     leftTurn()
                    
                    # elif (universal_direction == 'T'):
                    #     aboutTurn()
                    # for i in my_direction_list:
                    #     if (i=='S'):
                    #         goForward()
                    #     elif (i=='R'):
                    #         rightTurn()
                    #     elif (i=='L'):
                    #         leftTurn()
                    #     elif (i=='T'):
                    #         aboutTurn()
                    
                    # arcs = ser.readline()
                    # print("from ARDUINO: ",arcs)
                            
                #cv2.imshow("grayscale",im)
                #maskFrame = imgBlue
                checkBlue = 0
                
            else:
                noLineCount = 0
                lineFoundFlag = findLine(frame, noLineCount)
                if (lineFoundFlag == 0):
                    # print("NOT ON THE LINE")
                    pass
                else:
                    print("FOLLOWING THE LINE")                
                #maskFrame = imgBlue + imgYellow
            #print(countLeft)    
            if(countLeft > 5):
                countLeft = 0
            if(countRight > 5):
                countRight = 0
            if(countU > 5):
                countU = 0
                
            #cv2.imshow("blue image", imgBlue)
            #cv2.imshow("yellow image", imgYellow)
            t2 = time.process_time()
            global t1 
            # print((t2-t1)*1000)
            t1 = t2
            
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #break
            #pass
            # print(b)
    #except:
    #print("Exception :", sys.exc_info())
    finally:
        # Clean up the connection
        camera.release()
        cv2.destroyAllWindows()
        
if __name__=="__main__":
    main()
