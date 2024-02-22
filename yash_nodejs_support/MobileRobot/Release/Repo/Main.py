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
from qr_detect_test import decodeQR

ser = serial.Serial("/dev/ttyACM0", baudrate = 115200, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, xonxoff = False, rtscts = False, stopbits = serial.STOPBITS_ONE, timeout = 1, dsrdtr = True)
checkBlue = 0
lineFoundFlag = 0
t1 = 0
#font = cv2.FONT_HERSHEY_SIMPLEX
Images=[]
N_SLICES = 6
ret = b'R'
lineOrient = [0]*(N_SLICES-1)
deltaX = [0]*(N_SLICES-1)

for q in range(N_SLICES):
    Images.append(Image())
    
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

def stepBack():
    ser.write('P'.encode('utf-8'))

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
    #ack = ser.read(1)
    #print(ack) 
    return

def rightTurn():
    print("Right turn")   
    ser.write('R'.encode('utf-8'))
    #ack = ser.read(1)
    #print(ack)
    return

def goForward():
    print("Go forward")     
    ser.write('F'.encode('utf-8'))
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

def findQRcode(frame): 
    decodedData = ""
    decodedObjects = pyzbar.decode(frame)
    for obj in decodedObjects:
        decodedData = obj.data
    return decodedData
    
def checkBlueColor(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    global checkBlue
    checkBlue = 0
    # define range of blue color in HSV
    lower_thresh_blue = np.array([90,120,50])
    upper_thresh_blue = np.array([110,255,200])
    # Threshold the HSV image to get only blue color
    maskBlue = cv2.inRange(hsv, lower_thresh_blue, upper_thresh_blue)
    #add erode to remove unneccessory blue color
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

def findLine(frame):
    global lineFoundFlag
    lineFoundFlag = 0
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
        if img is not None:
            lineOrient, deltaX =  SlicePart(img, Images, N_SLICES)
            toSendDeltaX = deltaX[0]
            for i in range(len(deltaX)-1):
                if(abs(deltaX[i]) <= 120):
                    toSendDeltaX = deltaX[i]
                    break;                    
            send_theta(toSendDeltaX*-1)
            #print("toSendDeltaX")
            #print(toSendDeltaX)
            fm = RepackImages(Images)
            #cv2.imshow("Mobo Vision", fm)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    pass
        else:
            pass
    else:
        lineFoundFlag = 0
        stop_no_line()
    return lineFoundFlag

def main():
    global lineFoundFlag
    checkBlue = 0
    decodedData = ""
    countLeft = 0
    countRight = 0
    countU = 0
    signal.signal(signal.SIGINT, stop_to_quit)
    try:
        camera = cv2.VideoCapture(0)                                
        print("Main")
        while True:   
            _, frame = camera.read() 
            frame = cv2.resize(frame,(240,180), cv2.INTER_AREA)
            #checkBlue, imgBlue = checkBlueColor(frame)
            checkBlue = checkBlueColor(frame)
            if(checkBlue == 1):  
                stop_no_line()                                
                decodedData = findQRcode(frame)
                print(decodedData)
                """
                if(decodedData == b'left'):
                    if(countLeft == 0):
                        leftTurn()
                        print("sent left")
                    countLeft += 1
                    #time.sleep(3)
                elif(decodedData == b'right'):
                    if(countRight == 0):
                        rightTurn()
                        print("sent right")
                    countRight += 1
                    #time.sleep(3)
                elif (decodedData == b'aboutturn'):
                    if(countU == 0):
                        #stop_no_line()
                        aboutTurn()
                        print("sent about turn")
                    countU += 1
                else:
                    pass
                """
                #cv2.imshow("grayscale",im)
                #maskFrame = imgBlue
                checkBlue = 0
            else:
                lineFoundFlag = findLine(frame)                
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
            print((t2-t1)*1000)
            t1 = t2
            
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #break
            #pass
    #except:
    #print("Exception :", sys.exc_info())
    finally:
        # Clean up the connection
        camera.release()
        cv2.destroyAllWindows()
        
if __name__=="__main__":
    main()
