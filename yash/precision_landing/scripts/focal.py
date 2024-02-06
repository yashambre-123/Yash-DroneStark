import cv2
import numpy as np

# Define the size of the calibration pattern (number of inner corners)
pattern_size = (6, 8)

# Define the real-world size of the calibration pattern (in meters)
square_size = 0.03

# Initialize the list of object points and image points for calibration
obj_points = []
img_points = []

# Initialize the camera capture object
cap = cv2.VideoCapture(0)

# Capture and process calibration images
while True:
    # Capture an image from the camera
    ret, img = cap.read()
    
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Find the calibration pattern in the image
    ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)
    
    # If the pattern is found, add the object points and image points to the lists
    if ret:
        obj_point = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
        obj_point[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2) * square_size
        obj_points.append(obj_point)
        img_points.append(corners)
        
        # Draw the calibration pattern on the image
        cv2.drawChessboardCorners(img, pattern_size, corners, ret)
        
    # Display the image with the calibration pattern
    cv2.imshow('Calibration', img)
    
    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera capture object
cap.release()

# Calibrate the camera
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, gray.shape[::-1], None, None)

# Estimate the focal length of the camera in pixels
focal_length_pixels = mtx[0, 0]

# Set the sensor size of the camera (in mm)
sensor_size_mm = 5.6

# Get the image width and height
image_width_pixels = gray.shape[1]
image_height_pixels = gray.shape[0]

# Calculate the focal length in mm
focal_length_mm = (focal_length_pixels * sensor_size_mm) / image_width_pixels

# Display the estimated focal length
print('Estimated focal length: {} pixels'.format(focal_length_pixels))
print('Estimated focal length: {} mm'.format(focal_length_mm))

# Destroy all windows
cv2.destroyAllWindows()
