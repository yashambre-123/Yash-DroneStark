import sys
import os, signal
import numpy as np
import pdb
import serial, struct
import cv2
import time
import RPi.GPIO as GPIO
#import wiringpi

from Image import *
from Utils import *

motion = 0
turn = 0
mode = 1 
direction = "straight"
ser = serial.Serial("/dev/ttyAMA0", baudrate = 115200, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, xonxoff = False, rtscts = False, stopbits = serial.STOPBITS_ONE, timeout = 1, dsrdtr = True)

# register handler for virtual pin V11 reading

def stop_to_quit(sig, frame):
    print("Sending stopping signal")
    send_theta(0)
    send_theta(0)
    send_theta(0)
    ser.write('Z'.encode('utf-8'))
    ack = ser.read(1)

    if(ack == b'R'):
        a = ser.read(1)
        print(a)
    sys.exit(0)

def stop_no_line():
    print("Stop the rover")
    ser.write('Z'.encode('utf-8'))
    return 

def aboutTurn():
    print("About turn")
    ser.write('Z'.encode('utf-8'))
    ser.write('Z'.encode('utf-8'))
    ser.write('U'.encode('utf-8'))
    ack = ser.read(1)
    print(ack)
    return 
  
def map(x, in_min, in_max, out_min, out_max):
    return int(((x-in_min) * (out_max-out_min)/ (in_max-in_min)+out_min))

def send_theta(theta_l):    
    ser.write('A'.encode("utf-8"))
    ser.write(struct.pack("<i", theta_l))
    #ack = ser.read(1)
    #print(ack)
    #if(ack == b'R'):
    #    a = struct.unpack("<h",ser.read(2))
    #    print(a)
    return  
t1 = 0
font = cv2.FONT_HERSHEY_SIMPLEX
Images=[]
N_SLICES = 6
ret = b'R'
lineOrient = [0]*(N_SLICES-1)
deltaX = [0]*(N_SLICES-1)
start_roi_l_point = (5,5)
end_roi_l_point = (60,60)
start_roi_r_point = (180,5)
end_roi_r_point = (210,60)
thickness = 1
color = (255,0,0)

for q in range(N_SLICES):
    Images.append(Image())

def main():
    signal.signal(signal.SIGINT, stop_to_quit)
    global direction
    try:
        camera = cv2.VideoCapture(0)
        while True:
            if(1):
                _, frame = camera.read()
                frame = cv2.resize(frame,(240,120), cv2.INTER_AREA)
                #cv2.imshow("original video",frame)
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                # define range of yellow color in HSV
                lower_thresh = np.array([30,120,20])
                upper_thresh = np.array([45,255,255])
                # define range of blue color in HSV
                #lower_thresh = np.array([100,50,50])
                #lower_thres = np.array([110,255,255])
                # Threshold the HSV image to get only blue colors
                mask = cv2.inRange(hsv, lower_thresh, upper_thresh)
                contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                # Bitwise-AND mask and original image
                img = cv2.bitwise_and(frame,frame, mask= mask)
                if(len(contours) != 0):
                    if img is not None:
                        """
                        roi_L = mask[start_roi_l_point, end_roi_l_point]
                        
                        roi_R = mask[start_roi_r_point, end_roi_r_point]
                        contoursL, hierarchyL = cv2.findContours(roi_L,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                        
                        contoursR, hierarchyR = cv2.findContours(roi_R,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                        if(len(contoursR) !=0 and len(contoursL) !=0):
                            direction = "T junction"
                            if(len(contoursR) != 0):
                                #direction = "right"
                                print("right")
                            if(len(contoursL) != 0):
                                #direction = "left"
                                print("left")
                        else:
                            direction = "straight"
                        """
                        lineOrient, deltaX =  SlicePart(img, Images, N_SLICES)
                        #print("Angle : ")
                        #print(lineOrient)
                        #print("X drift : ")
                        #print(deltaX)
                        toSendDeltaX = deltaX[0]
                        for i in range(len(deltaX)-1):
                            #if (i!=0):
                            #if (abs(deltaX[i]-deltaX[i-1]) > 1000):
                            #deltaX[i] = deltaX[i-1]
                            if(abs(deltaX[i]) <= 120):
                                toSendDeltaX = deltaX[i]
                                break;
                                
                        send_theta(toSendDeltaX*-1)

                        #print("X drift : ")
                        print(toSendDeltaX)

                            #if(ret != b'R'):
                            #print("Could not send theta values")
                            #time.sleep(0.1)
                        fm = RepackImages(Images)
                        t2 = time.process_time()
                        global t1
                        print((t2-t1)*1000)
                        t1 = t2
                        """
                        fm = cv2.rectangle(fm, start_roi_l_point, end_roi_l_point, color, thickness)
                        fm = cv2.rectangle(fm, start_roi_r_point, end_roi_r_point, color, thickness)
                        fm = cv2.putText(fm, direction, (50,50), cv2.FONT_HERSHEY_SIMPLEX ,  0.5, (255,0,0), 2, cv2.LINE_AA) 
                        """ 
                        #cv2.imshow("Mobo Vision", fm)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    else:
                        break
                else:
                    stop_no_line()
                    #time.sleep(1)
                    #aboutTurn()
                    #time.sleep(5)
                    #send_theta(120)
                    print("line not found")
    #except:
    #print("Exception :", sys.exc_info())
    finally:
        # Clean up the connection
        cv2.destroyAllWindows()
        
if __name__=="__main__":
    main()
