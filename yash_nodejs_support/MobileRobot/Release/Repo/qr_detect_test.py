import cv2
import numpy as np
import sys
import time
from collections import deque

node_list = {0:"ZeroQR", 1:"OneQR", 2:"TwoQR", 3:"ThreeQR", 4:"FourQR", 5:"FiveQR"}
qr_list = ["qr_0.png", "qr_1.png", "qr_2.png"]
next_node_proxy = [1,2,3,4,5]

cur_node = None
#end_node = int(sys.argv[1])
start_node = None
n_cnt = start_node
next_node = 2

prev_node = 0

#camera = cv2.VideoCapture(0)

# Display barcode and QR code location
def display(im, bbox):
    n = len(bbox)
    for j in range(n):
        cv2.line(im, tuple(bbox[j][0]), tuple(bbox[ (j+1) % n][0]), (255,0,0), 3)

    # Display results
    cv2.imshow("Results", im)

def get_turn(num):
    if(num == 1):
        print("Go Straight")
        return
    if(num == 2):
        print("Go Left")
        return
    if(num == 3):
        print("Go Right")
        return
    print("Get turn failed")
    return

def makeSenseOfQRData(data):
    global cur_node, prev_node
    split_data = data.split(':')
    print("QR name: %s" % split_data[0])
    #print("Node 1: %s \nNode 2: %s \nNode 3: %s \nNode 4: %s" % (split_data[1], split_data[2], split_data[3], split_data[4]))
    if int(split_data[0]) == end_node:
        print("Reached required QR")
        return 1
    else:
        cur_node = int(split_data[0])
        n = decodeData(split_data[1:])
        prev_node = int(split_data[0])
        if n == -1:
            print("No turn")
            return -1
        else:
            get_turn(n)
        return 0

    return 0


def decodeQR(data, next_node, prev_node):
    #global cur_node, next_node, prev_node
    valid = -1
    data = data.decode('utf-8')
    cur_node = int(data.split(":")[0])
    print("Current QR is: %s" % cur_node)
    if prev_node == cur_node:
        valid = -2
        return -1, cur_node, valid
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
        return -1, cur_node, valid

    for j in range(len(inter)):
        if int(inter[j]) == next_node:
            return j, cur_node, valid

    return -1, -1, valid

"""
while(True):
    qr_name = qr_list[2]
    #inputImage = cv2.imread(qr_name)
    _, inputImage = camera.read()
    qrDecoder = cv2.QRCodeDetector()

    # Detect and decode the qrcode
    data,bbox,rectifiedImage = qrDecoder.detectAndDecode(inputImage)
    if len(data)>0:
        #print("Decoded Data : {}".format(data))
        display(inputImage, bbox)
        #rectifiedImage = np.uint8(rectifiedImage);
        #print(decodeQR(data))
        break
        #cv2.imshow("Rectified QRCode", rectifiedImage);
    else:
        print("QR Code not detected")
        #cv2.imshow("Results", inputImage)

cv2.waitKey(1)
cv2.destroyAllWindows()
"""
