import cv2

camera = cv2.VideoCapture(0)

while True:
    _, frame = camera.read()
    cv2.imshow("og frame", frame)
    
    if cv2.waitKey(1) == ord('c'):
        break
    # cv2.waitKey()
    
camera.release()
cv2.destroyAllWindows()
