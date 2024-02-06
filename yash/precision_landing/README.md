# precision_landing

## Camera Calibration and Computer Vision Scripts

This Git repository contains Python scripts for various computer vision tasks, including camera calibration and distance estimation using OpenCV.

### Prerequisites

Before you can run the scripts in this repository, you'll need to install some prerequisites on your Ubuntu system. You can do this using the following commands:

1. **Python and OpenCV**:

   sudo apt-get update
   sudo apt-get install python3 python3-pip
   pip3 install opencv-python-headless imutils

* opencv-python-headless provides the OpenCV library.
* imutils is used for image processing.

### Scripts
### 1. camera_calibration.py
### Description: This script performs camera calibration using a chessboard pattern.
    
    python3 camera_calibration.py

* Calibration involves determining the intrinsic and extrinsic parameters of the camera, which are essential for correcting distortion and accurately mapping 3D points to 2D image coordinates. 
* In this explanation, I'll elaborate on how to use the script and provide details about intrinsic and extrinsic camera parameters.

#### Using the camera_calibration.py Script
Prerequisites: Ensure you have the necessary prerequisites installed as mentioned in the README.md of your repository, including Python, OpenCV, NumPy, and Imutils.

#### Checkerboard Pattern
You'll need a checkerboard pattern image to use for calibration. You can download a suitable image from the link you provided: Checkerboard Pattern. Save this image to your local directory.

#### Capture Calibration Images: 
The script will open your camera feed. Hold the checkerboard pattern in front of your camera and move it around to capture different angles and orientations. Try to capture a variety of images covering the checkerboard from different viewpoints.

#### Calibration Process: 
The script will detect the checkerboard corners in the captured images and use this information to calibrate the camera. It will save the camera's intrinsic matrix (K) and distortion coefficients.

#### Results: 
After capturing a sufficient number of calibration images, the script will calculate and print the camera calibration parameters. You will see information about the intrinsic matrix (K) and distortion coefficients.

### Intrinsic and Extrinsic Parameters
### Intrinsic Parameters:

Intrinsic Matrix (K): The intrinsic matrix contains information about the internal properties of the camera. It includes parameters like the focal length, principal point coordinates, and skew factor. The intrinsic matrix is represented as:

    | fx   0   cx |
    |  0  fy   cy |
    |  0   0    1 |

* fx and fy are the focal lengths in the x and y directions, respectively.
* cx and cy are the principal point coordinates (the point where the optical axis intersects the image plane).

* Distortion Coefficients: Distortion coefficients correct lens distortion effects. They are typically represented as k1, k2, p1, p2, and k3. These coefficients account for radial distortion and tangential distortion.

### Extrinsic Parameters:

* Rotation Vector (rvecs): This vector represents the 3D rotation of the camera relative to the world coordinate system. It is often calculated using the Rodrigues' rotation formula and provides information about the orientation of the camera.

* Translation Vector (tvecs): The translation vector specifies the position of the camera in the world coordinate system. It indicates how far the camera is displaced along each of its axes.


### Instructions: Follow the on-screen instructions to capture calibration images by pressing 'q' to exit once enough images are collected.

## 2. focal.py
### Description: This script estimates the focal length of a camera.

* Capture Calibration Images: Execute the script while capturing images of the calibration pattern from different angles and distances. The script will use these images to estimate the camera's intrinsic parameters.

* Image Capture: Hold the calibration pattern in front of the camera and move it around to capture various perspectives. Ensure you capture a sufficient number of images covering different angles.

* Calibration Process: The script will detect the calibration pattern in the captured images and calculate the intrinsic camera parameters, including the focal length.

#### Understanding the Output
After capturing calibration images, the script will provide two key pieces of information:

* Estimated Focal Length (Pixels): This is the estimated focal length of the camera in pixels. It represents how much the camera lens converges or diverges incoming light rays.

* Estimated Focal Length (Millimeters): This is the estimated focal length of the camera in millimeters. It provides a physical measurement of the camera lens's focal distance.

#### Sensor Size Consideration
The script also calculates the sensor size of the camera in millimeters. The sensor size is essential for understanding how the camera records light and affects image framing.

    python3 focal.py

## 3. distance.py

### Description: This script calculates the distance of a QR code from the camera.

* Calibrate the Camera: Execute the camera_calibration.py script with a checkerboard pattern to obtain the intrinsic camera parameters. Calibration is a one-time setup process.

* Run the Distance Estimation Script: Once the camera is calibrated, you can run the distance.py script.

* QR Code Detection and Distance Estimation: Hold a QR code within the camera's view. The script will detect the QR code and estimate the distance between the camera and the QR code in real-time.

* The script uses a feature-based approach to estimate the QR code's position relative to the camera.

* It calculates the distance using the change in position between successive frames and the known camera calibration parameters.

* Visual Feedback: The script provides visual feedback by drawing a bounding box around the detected QR code and displaying the estimated distance in meters on the screen.

    python3 distance.py

## 4. fps.py
### Description: This script calculates and displays the frames per second (FPS) of a webcam stream.

* Webcam Selection: The script initializes the default webcam (usually src=0). If you have multiple webcams, you may need to adjust the src parameter in the script to select the desired camera.

* FPS Measurement: The script will display the FPS of the webcam's video stream on the frame in real-time. This information is valuable for assessing the performance of video processing algorithms.

* Exiting the Script: To exit the script, press the 'q' key. This will close the video window and terminate the script.

    python3 fps.py


### 5. main.py

### Description: This script is the main script as the name defines, where the landing happens

* Combination of camera with computer vision, ROS, mavlink and algorithms implementation this scripts initiates landing once the QR is detected.

* Auto-adjusting feature also included, if the drone drifts while lading on the landing pad.

    python3 main.py


### Service file

    [Unit]
    Description=Run precision landing at boot

    [Service]
    ExecStart=/home/maker/precision_landing/precision_landing.sh
    Restart=always
    User=maker
    Group=your_group
    WorkingDirectory=/home/maker/precision_landing/

    [Install]
    WantedBy=multi-user.target


Enable and start the script

    sudo systemctl enable run_main.service
    sudo systemctl start run_main.service

Check the status of the script

    sudo systemctl status run_main.service
