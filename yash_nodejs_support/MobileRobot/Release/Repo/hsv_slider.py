# #import opencv and numpy
# import cv2  
# import numpy as np

# #trackbar callback fucntion to update HSV value
# def callback(x):
# 	global H_low,H_high,S_low,S_high,V_low,V_high
# 	#assign trackbar position value to H,S,V High and low variable
# 	H_low = cv2.getTrackbarPos('low H','controls')
# 	H_high = cv2.getTrackbarPos('high H','controls')
# 	S_low = cv2.getTrackbarPos('low S','controls')
# 	S_high = cv2.getTrackbarPos('high S','controls')
# 	V_low = cv2.getTrackbarPos('low V','controls')
# 	V_high = cv2.getTrackbarPos('high V','controls')


# #create a seperate window named 'controls' for trackbar
# cv2.namedWindow('controls',2)
# cv2.resizeWindow("controls", 550,10);


# #global variable
# H_low = 0
# H_high = 179
# S_low= 0
# S_high = 255
# V_low= 0
# V_high = 255

# #create trackbars for high,low H,S,V 
# cv2.createTrackbar('low H','controls',0,179,callback)
# cv2.createTrackbar('high H','controls',179,179,callback)

# cv2.createTrackbar('low S','controls',0,255,callback)
# cv2.createTrackbar('high S','controls',255,255,callback)

# cv2.createTrackbar('low V','controls',0,255,callback)
# cv2.createTrackbar('high V','controls',255,255,callback)

 

# while(1):
# 	#read source image
# 	#img=cv2.imread("ballimage.jpg")
# 	try:
# 		img = cv2.VideoCapture(0)                                
#         #print("Main")
#         while True:   
#             _, frame = camera.read() 
#             frame = cv2.resize(frame,(240,180), cv2.INTER_AREA)
            
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
# 	#convert sourece image to HSC color mode
# 	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 	#
# 	hsv_low = np.array([H_low, S_low, V_low], np.uint8)
# 	hsv_high = np.array([H_high, S_high, V_high], np.uint8)

# 	#making mask for hsv range
# 	mask = cv2.inRange(hsv, hsv_low, hsv_high)
# 	print (mask)
# 	#masking HSV value selected color becomes black
# 	res = cv2.bitwise_and(img, img, mask=mask)



# 	#show image
# 	cv2.imshow('mask',mask)
# 	cv2.imshow('res',res)
	
# 	#waitfor the user to press escape and break the while loop 
# 	k = cv2.waitKey(1) & 0xFF
# 	if k == 27:
# 		break
		
# #destroys all window
# cv2.destroyAllWindows()

import cv2
import numpy as np

def nothing(x):
    pass

camera = cv2.VideoCapture(0)
cv2.namedWindow("Trackbars")

cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)

while True:
    _, frame = camera.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")
    
    lower_blue = np.array([l_h, l_s, l_v])
    upper_blue = np.array([u_h, u_s, u_v])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    result = cv2.bitwise_and(frame, frame, mask=mask)
    
    cv2.imshow("frame", frame)
    cv2.imshow("mask", mask)
    cv2.imshow("result", result)
    
    key = cv2.waitKey(1)
    if key == 27:
        break

camera.release()
camera.destroyAllWindows()
