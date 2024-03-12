import numpy as np
import cv2
import math

class Image:
    
    def __init__(self):
        self.image = None
        self.contourCenterX = 0
        self.MainContour = None
        self.middleY = 0
    def Process(self):
        flag = 0
        #imgray = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY) #Convert to Gray Scale
        #ret, thresh = cv2.threshold(imgray,0,255,cv2.THRESH_BINARY_INV) #Get Threshold
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        # define range of blue color in HSV
        lower_blue = np.array([30,120,20])
        upper_blue = np.array([45,255,255])

        # Threshold the HSV image to get only blue colors
        thresh = cv2.inRange(hsv, lower_blue, upper_blue)
        self.contours, _ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #Get contour
        
        self.prev_MC = self.MainContour
        if self.contours:
            self.MainContour = max(self.contours, key=cv2.contourArea)
        
            self.height, self.width  = self.image.shape[:2]
            #self.prevmiddleY = self.middleY
            self.middleX = int(self.width/2) #Get X coordenate of the middle point
            self.middleY = int(self.height/2) #Get Y coordenate of the middle point
            
            self.prev_cX = self.contourCenterX
            if self.getContourCenter(self.MainContour) != 0:
                self.contourCenterX = self.getContourCenter(self.MainContour)[0]
                if abs(self.prev_cX-self.contourCenterX) > 5:
                    self.correctMainContour(self.prev_cX)
            else:
                #self.contourCenterX = 0
                self.contourCenterX = 2000
                flag = 1
            if self.contourCenterX == None:
                self.dir = 2000
            else:
                self.dir =  int((self.middleX-self.contourCenterX) * self.getContourExtent(self.MainContour))
            
            cv2.drawContours(self.image,self.MainContour,-1,(0,255,0),3) #Draw Contour GREEN
            cv2.circle(self.image, (self.contourCenterX, self.middleY), 3, (255,255,255), -1) #Draw dX circle WHITE
            #print(self.prev_cX);
            #print(self.contourCenterX);
            #print(self.middleY+self.height);
            cv2.circle(self.image, (self.middleX, self.middleY), 3, (0,0,255), -1) #Draw middle circle RED
            
        return self.contourCenterX, self.middleY, flag 
        
    def getContourCenter(self, contour):
        M = cv2.moments(contour)
        
        if M["m00"] == 0:
            return 0
        
        x = int(M["m10"]/M["m00"])
        y = int(M["m01"]/M["m00"])
        
        return [x,y]
        
    def getContourExtent(self, contour):
        area = cv2.contourArea(contour)
        x,y,w,h = cv2.boundingRect(contour)
        rect_area = w*h
        if rect_area > 0:
            return (float(area)/rect_area)
            
    def Aprox(self, a, b, error):
        if abs(a - b) < error:
            return True
        else:
            return False
            
    def correctMainContour(self, prev_cx):
        if abs(prev_cx-self.contourCenterX) > 5:
            for i in range(len(self.contours)):
                if self.getContourCenter(self.contours[i]) != 0:
                    tmp_cx = self.getContourCenter(self.contours[i])[0]
                    if self.Aprox(tmp_cx, prev_cx, 5) == True:
                        self.MainContour = self.contours[i]
                        if self.getContourCenter(self.MainContour) != 0:
                            self.contourCenterX = self.getContourCenter(self.MainContour)[0]
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
