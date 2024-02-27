import numpy as np
import cv2
import time
from Image import *
import math
import array

def SlicePart(im, images, slices):
    height, width = im.shape[:2]
    sl = int(height/slices);
    centerX = int(width/2);
    centerY = int(height/2);
    #print(centerX)
    middleY=0
    contourCenterX=[None]*slices
    deltaX = [None]*slices
    lineOrient = [None]*(slices-1)
    contourCenterX.append(None)
    prevcontourCenterX=0;

    for i in range(slices):
        flag = 0
        part = sl*i
        crop_img = im[part:part+sl, 0:width]
        images[i].image = crop_img
        if(i!=0):
            prevcontourCenterX = contourCenterX[i-1]
        contourCenterX[i], middleY, flag = images[i].Process()
        if(contourCenterX[i] == None):
            deltaX[i] = 2000
            lineOrient[i] = 2000
        else:
            deltaX[i] = centerX - contourCenterX[i];
        #print(deltaX[i]);
        #print(contourCenterX)
        #print(prevcontourCenterX)
        #print(middleY*(i+1))
        
        #print(contourCenterX)
        """
        if(contourCenterX[i]-prevcontourCenterX !=0 and i!=0):
            lineOrient[i-1] = math.degrees(math.atan((middleY*(i+2)-middleY*i+1)/(contourCenterX[i]-prevcontourCenterX)))
        """
        if(middleY*(i+2)-middleY*(i+1)):
            lineOrient[i-1] = int(round(math.degrees(math.atan((contourCenterX[i]-prevcontourCenterX)/(middleY*(i+2)-middleY*(i+1)))),0))*-1
            #print("Angle no"  ,i)
            #print(lineOrient[i])
        if(flag == 1):
            lineOrient[i-1] = 2000
            deltaX[i-1] = 2000
    return lineOrient, deltaX

    
def RepackImages(images):
    img = images[0].image
    for i in range(len(images)):
        if i == 0:
            img = np.concatenate((img, images[1].image), axis=0)
        if i > 1:
            img = np.concatenate((img, images[i].image), axis=0)
            
    return img

def Center(moments):
    if moments["m00"] == 0:
        return 0
        
    x = int(moments["m10"]/moments["m00"])
    y = int(moments["m01"]/moments["m00"])

    return x, y
    
def RemoveBackground(image, b):
    up = 100
    # create NumPy arrays from the boundaries
    lower = np.array([0, 0, 0], dtype = "uint8")
    upper = np.array([up, up, up], dtype = "uint8")
    #----------------COLOR SELECTION-------------- (Remove any area that is whiter than 'upper')
    if b == True:
        mask = cv2.inRange(image, lower, upper)
        image = cv2.bitwise_and(image, image, mask = mask)
        image = cv2.bitwise_not(image, image, mask = mask)
        image = (255-image)
        return image
    else:
        return image
    #////////////////COLOR SELECTION/////////////
    
