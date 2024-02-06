import cv2
from pyzbar.pyzbar import decode
import numpy as np

# function to draw the pose estimation on the image
def draw_pose(image, corners, rvecs, tvecs, camera_matrix, dist_coeffs):
    obj_points = np.array([[0, 0, 0],
                           [1, 0, 0],
                           [1, 1, 0],
                           [0, 1, 0]], dtype=np.float32)

    # project the 3D points to 2D image plane
    img_points, _ = cv2.projectPoints(obj_points, rvecs, tvecs, camera_matrix, dist_coeffs)

    # draw the QR code outline
    cv2.polylines(image, [np.int32(corners)], True, (0, 255, 0), 2)

    # draw the axes of the QR code
    img_points = np.int32(img_points).reshape(-1, 2)
    cv2.drawContours(image, [img_points[:4]], -1, (0, 255, 0), 3)
    for i, j in zip(range(4), range(4, 8)):
        cv2.line(image, tuple(img_points[i]), tuple(img_points[j]), (0, 0, 255), 2)

# initialize the camera
cap = cv2.VideoCapture(0)

# set the camera resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# initialize the QR code decoder
decoder = cv2.QRCodeDetector()

# loop over the frames from the camera
while True:
    # read a frame from the camera
    ret, frame = cap.read()

    # decode the QR code
    decoded_objs = decode(frame)

    # loop over the decoded objects
    for decoded_obj in decoded_objs:
        # get the QR code corners
        corners = np.array(decoded_obj.polygon, dtype=np.int32)

        # decode the QR code data
        data = decoded_obj.data.decode('utf-8')

        # draw the QR code outline and pose estimation
        if len(corners) == 4:
            # get the camera matrix and distortion coefficients
            _, camera_matrix, dist_coeffs, _, _ = cv2.getOptimalNewCameraMatrix(np.array([[640, 0, 640/2], [0, 640, 480/2], [0, 0, 1]]),
                                                                                np.array([0, 0, 0, 0]), (1280, 720), 1)

            # estimate the pose of the QR code
            _, rvecs, tvecs = cv2.solvePnP(np.float32([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]), corners, camera_matrix, dist_coeffs)

            draw_pose(frame, corners, rvecs, tvecs, camera_matrix, dist_coeffs)

        # print the QR code data
        print('QR Code:', data)

    # show the frame
    cv2.imshow('frame', frame)

    # Wait for key press
    key = cv2.waitKey(1)

    # If 'q' is pressed, exit loop
    if key == ord('q'):
        break

# Release camera and close window
cap.release()
cv2.destroyAllWindows()
