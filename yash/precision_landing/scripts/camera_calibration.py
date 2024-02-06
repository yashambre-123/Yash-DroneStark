import cv2
import numpy as np

# Set the width and height of the calibration pattern
pattern_size = (6, 8)

# Set the size of the squares in the calibration pattern (in meters)
square_size = 0.03

# Generate the object points for the calibration pattern
objp = np.zeros((np.prod(pattern_size), 3), np.float32)
objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
objp *= square_size

# Initialize the arrays to store the object points and image points
objpoints = []
imgpoints = []

# Initialize the video capture
cap = cv2.VideoCapture(0)

# Calibrate the camera
while len(imgpoints) < 20:
    # Capture a frame
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Find the corners of the calibration pattern
    ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)

    if ret:
        # Draw the corners on the frame
        cv2.drawChessboardCorners(frame, pattern_size, corners, ret)

        # Append the object points and image points
        objpoints.append(objp)
        imgpoints.append(corners)

    # Display the frame
    cv2.imshow('Calibration', frame)

    # Check for key press
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

# Calculate the camera calibration parameters
ret, K, dist_coef, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# Print the camera calibration parameters
print("Intrinsic Matrix (K):")
print(K)
print("Distortion Coefficients:")
print(dist_coef)
