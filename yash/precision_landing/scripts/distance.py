import cv2
import numpy as np

# Set the QR code size (in meters)
qr_size = 0.1

# Set the camera calibration parameters
K = np.array([[2.41349143e+03, 0.00000000e+00, 4.18830352e+02],
              [0.00000000e+00, 2.40521250e+03, 3.62104578e+02],
              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
dist_coef = np.array([[-1.07446362e+00, 7.53248091e+01, 1.02590751e-02, 1.26756809e-03, -1.97741070e+03]])

# Initialize the video capture
cap = cv2.VideoCapture(0)

# Create a SIFT detector object
sift = cv2.SIFT_create()

# Detect keypoints and compute descriptors of the object template
obj_keypoints, obj_descriptors = sift.detectAndCompute(cap, None)

# Initialize the detector and matcher for the QR code
detector = cv2.QRCodeDetector()
matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)

# Initialize the position of the QR code
qr_position = None

# Loop over frames from the video
while True:
    # Capture a frame
    ret, frame = cap.read()
    if not ret:
        break

    # Undistort the frame
    frame = cv2.undistort(frame, K, dist_coef)

    # Detect the QR code in the frame
    bbox, _, _ = detector.detectAndDecode(frame)
    if bbox is not None:
        # Extract the keypoints and descriptors from the QR code
        qr_keypoints, qr_descriptors = cv2.ORB_create().detectAndCompute(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), None)

        # Match the keypoints and descriptors of the QR code to the keypoints and descriptors of the calibration pattern
        matches = matcher.match(qr_descriptors, obj_descriptors)

        # Compute the position of the QR code relative to the camera
        if len(matches) > 10:
            qr_points = np.float32([qr_keypoints[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            _, rvecs, tvecs, inliers = cv2.solvePnPRansac(obj_points, qr_points, K, None)
            qr_position = -np.dot(cv2.Rodrigues(rvecs)[0].T, tvecs)

        # Draw the bounding box and position of the QR code on the frame
        bbox = np.int32(bbox)
        cv2.polylines(frame, [bbox], True, (0, 255, 0), thickness=2)
        if qr_position is not None:
            cv2.putText(frame, f'({qr_position[0]:.2f}, {qr_position[1]:.2f}, {qr_position[2]:.2f})', (bbox[0, 0], bbox[0, 1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                # Calculate the distance travelled by the QR code
        if qr_position is not None:
            if prev_position is not None:
                qr_distance = np.sqrt(np.sum(np.square(qr_position - prev_position)))
                print(f'QR code travelled {qr_distance:.2f} meters')

            prev_position = qr_position

    # Display the frame
    cv2.imshow('frame', frame)

    # Check for key press
    if cv2.waitKey(1) == ord('q'):
        break

# Release the video capture
cap.release()

# Close all windows
cv2.destroyAllWindows()
