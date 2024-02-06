import cv2
from pyzbar.pyzbar import decode
import time
import threading
import numpy as np
import rospy
from mavros_msgs.srv import CommandTOL, CommandBool, SetMode
from mavros_msgs.msg import State, PositionTarget
from geometry_msgs.msg import TwistStamped, Vector3
from std_msgs.msg import Float64
import psutil
import os
from pymavlink import mavutil

class DronePrecisionLanding:
    def __init__(self):
        self.speed = 5.15 # m/s
        self.update_rect_left_min = -6
        self.update_rect_left_max = 531
        self.update_rect_top_min = -3
        self.update_rect_top_max = 373
        self.map_output_min = 0
        self.map_output_max = 100
        self.distance_traveled = 0
        self.focal_length_pixels = 1647.0570575931897 # Get the focal length from focal.py script
        self.focal_length_mm = 6.478093452518387
        self.prev_frame_time = 0 # used to record the time when we processed last frame
        self.new_frame_time = 0 # used to record the time at which we processed current frame
        self.center = None # Initialize the center of the QR code
        self.arm_status = None
        self.flight_mode = "GUIDED"
        self.curr_alt = None
        self.orientation_ = None
        self.rect_left_ = None
        self.rect_top_ = None
        self.rect_width_ = None
        self.rect_height_ = None
        self.fps = 0
        self.distance_traveled = 0, 
        self.linear_velocity = 0, 
        self.rotational_velocity = 0, 
        self.time_now = 0, 
        self.twist_stamped_msg = 0, 
        self.altitude_speed = 0,
        self.master = mavutil.mavlink_connection('udpout:localhost:14550', source_system=1)
        self.master.mav.statustext_send(mavutil.mavlink.MAV_SEVERITY_INFO, "QR SEARCH INITIATED !!".encode())

        # ROS Initialization
        rospy.init_node('move_drone', anonymous=False)
        self.twist_stamped_msg = TwistStamped()
        self.setpoint_pub = rospy.Publisher('/mavros/setpoint_position/local', PositionTarget, queue_size=10)
        self.pub = rospy.Publisher('/mavros/setpoint_velocity/cmd_vel', TwistStamped, queue_size=10)
        self.record = cv2.VideoCapture(0) # Turn on camera and capture video, assign this to a variable
        self.record.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.record.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.record.set(cv2.CAP_PROP_FPS, 30)
        rospy.Subscriber("/mavros/state", State, self.checkStateCb)
        rospy.Subscriber("/mavros/global_position/rel_alt", Float64, self.checkCurrLocCb)


    def armDrone(self, status):
        rospy.wait_for_service("/mavros/cmd/arming")
        try:
            arm_drone = rospy.ServiceProxy("/mavros/cmd/arming", CommandBool)
            response = arm_drone(status)
            rospy.loginfo("DRONE ARMED: SUCCESS")
        except rospy.ServiceException as e:
            rospy.loginfo("DRONE ARMED: FAILED")

    def setFlightMode(self, mode):
        rospy.wait_for_service("/mavros/set_mode")
        try:
            set_mode = rospy.ServiceProxy("/mavros/set_mode", SetMode)
            set_mode(0, str(mode))
            flight_mode = str(mode)
        except rospy.ServiceException as e:
            rospy.loginfo("SET MODE CALL: FAILED")

    def takeOffDrone(self):
        rospy.wait_for_service("/mavros/cmd/takeoff")
        try:
            drone_takeoff = rospy.ServiceProxy("/mavros/cmd/takeoff", CommandTOL)
            response = drone_takeoff(0.0, 0.0, 0.0, 0.0, 15)
            rospy.loginfo("DRONE TakeOff: SUCCESS")
        except rospy.ServiceException as e:
            rospy.loginfo("DRONE TakeOff: FAILED")

    def checkStateCb(self, state):
        self.arm_status = state.armed
        self.flight_mode = state.mode
        rospy.loginfo("FLIGHT MODE : " '{0}'.format(self.flight_mode))

    def checkCurrLocCb(self, curr_location):
        self.curr_alt = curr_location.data
        rospy.loginfo("CURRENT ALTITUDE : " '{0}'.format(self.curr_alt))

    def distance_control(self, x_distnace, y_distance, z_altitude, x_speed, y_speed, z_spped):
        # Create a PositionTarget message to send the desired position and velocity to the drone
        setpoint_msg = PositionTarget()
        setpoint_msg.coordinate_frame = PositionTarget.FRAME_LOCAL_NED
        setpoint_msg.type_mask = PositionTarget.IGNORE_VX + PositionTarget.IGNORE_VY + PositionTarget.IGNORE_VZ + \
                                PositionTarget.IGNORE_AFX + PositionTarget.IGNORE_AFY + PositionTarget.IGNORE_AFZ + \
                                PositionTarget.IGNORE_YAW + PositionTarget.IGNORE_YAW_RATE

        # Set the desired position to move forward by 1 meter
        setpoint_msg.position.x = x_distnace
        setpoint_msg.position.y = y_distance
        setpoint_msg.position.z = z_altitude

        # Set the desired velocity to move forward at a constant speed
        setpoint_msg.velocity.x = x_speed
        setpoint_msg.velocity.y = y_speed
        setpoint_msg.velocity.z = z_spped

        # Publish the PositionTarget message to move the drone forward
        self.setpoint_pub.publish(setpoint_msg)

    def qr_info(self, orientation, rect_left, rect_top, rect_width, rect_height):
        self.orientation_ = orientation # orientation of the QR obtained from the i list
        self.rect_left_ = rect_left     # rect_left of the QR obtained from the i list
        self.rect_top_ = rect_top       # rect_top of the QR obtained from the i list
        self.rect_width_ = rect_width    # rect_width of the QR obtained from the i list
        self.rect_height_ = rect_height  # rect_height of the QR obtained from the i list

    def pilot_ability(self):
        # If the orientation of the QR code is facing UP, then the drone will change to GUIDED mode
        # After switching to GUIDED mode, the condition will check whether drone is armed or not
        # If not then it will ARM the drone
        if self.orientation_ == 'UP':
            self.setFlightMode("GUIDED")
            if self.arm_status == False:
                self.armDrone(True)
        # If the QR code facing downwards, then the drone will disarm
        elif self.orientation_ == 'DOWN':
            self.armDrone(False)

        self.x_y_dir_vel_control()

    def x_y_dir_vel_control(self):
        # left = -5 to 1082
        # top = -8 to 777
        # Mapping the update_rect_left_ from 0 to 100
        self.update_rect_left_ = (self.rect_left_ - self.update_rect_left_min) * (self.map_output_max - self.map_output_min) / (self.update_rect_left_max - self.update_rect_left_min) + self.map_output_min
        # printing the value of update_rect_left_
        print("Left: ", self.update_rect_left_)
        # Mapping the update_rect_top_ from 0 to 100
        self.update_rect_top_ = (self.rect_top_ - self.update_rect_top_min) * (self.map_output_max - self.map_output_min) / (self.update_rect_top_max - self.update_rect_top_min) + self.map_output_min
        # printing the value of update_rect_top_
        print("Top: ", self.update_rect_top_)
        # printing the value of orientation_
        print("Orientation: ", self.orientation_)

        # if QR code's orientation is Right + ARMED + GUIDED, then it will takeoff
        if self.orientation_ == "RIGHT" and self.arm_status == True and self.flight_mode == "GUIDED":
            # self.takeOffDrone()
            pass

        # if QR code's orientation is Right + ARMED + GUIDED + value of update_rect_top_ above 50 then it will move towards x- direction
        if self.orientation_ == "RIGHT" and self.update_rect_top_ > 50 and self.arm_status == True and self.flight_mode == "GUIDED":
            self.speed_control(-self.speed, 0.0, 0.0)
            print(self.update_rect_top_)
        # if QR code's orientation is Right + ARMED + GUIDED + value of update_rect_top_ less than 50 then it will move towards x+ direction
        elif self.orientation_ == "RIGHT" and self.update_rect_top_ < 50 and self.arm_status == True and self.flight_mode == "GUIDED":
            self.speed_control(self.speed, 0.0, 0.0)

        # if QR code's orientation is Left + ARMED + GUIDED + value of update_rect_left_ above than 50 then it will move towards y- direction
        if self.orientation_ == "LEFT" and self.update_rect_left_ > 50 and self.arm_status == True and self.flight_mode == "GUIDED":
            self.speed_control(0.0, -self.speed, 0.0)
        # if QR code's orientation is Left + ARMED + GUIDED + value of update_rect_left_ less than 50 then it will move towards y+ direction
        elif self.orientation_ == "LEFT" and self.update_rect_left_ < 50 and self.arm_status == True and self.flight_mode == "GUIDED":
            self.speed_control(0.0, self.speed, 0.0)
        
        # Returning the update_rect_left_, update_rect_top_ values from the function
        return self.update_rect_left_, self.update_rect_top_

    def callback(self, event):
        time_now = rospy.Time.now()
        time_elapsed = event.current_real - time_now
        self.distance_traveled = self.linear_velocity * time_elapsed.to_sec() * 100
        self.pub.publish(self.twist_stamped_msg)

    def land_drone(self):
        if self.arm_status == True and self.flight_mode == "GUIDED" or self.flight_mode == 29 and self.dy != 0 and self.dx != 0:
            self.speed_control(self.dy/100, self.dx/100, 0.0)
        
        if self.arm_status == True and self.flight_mode == "GUIDED" or self.flight_mode == 29 and -0.5 <= self.dx <= 0.5 and -0.5 <= self.dy <= 0.5:
            self.speed_control(0.0, 0.0, -0.1)

    def speed_control(self, speed_forward, speed_sideways, alti_speed):
        # Create a publisher to send messages to the setpoint_velocity topic    
        # Create a new Twist message with the desired velocity
        self.time_now_speed = self.twist_stamped_msg.header.stamp = rospy.Time.now()
        self.linear_velocity = self.twist_stamped_msg.twist.linear.x = speed_sideways  # move forward with a velocity of  m/s
        self.rotational_velocity = self.twist_stamped_msg.twist.linear.y = speed_forward  # move to the right with a velocity of  m/s
        self.altitude_speed = self.twist_stamped_msg.twist.linear.z = alti_speed  # move up with a velocity of m/s
        self.twist_stamped_msg.twist.angular.z = 0.0  # turn clockwise with an angular velocity of rad/s
        rospy.Timer(rospy.Duration(self.dy), self.callback)

    def read_camera_parameters(self, path = 'intrinsic.dat'):
        inf = open(path, 'r')

        cmtx = []
        dist = []

        # ignore first line
        line = inf.readline()
        for _ in range(3):
            line = inf.readline().split()
            line = [float(en) for en in line]
            cmtx.append(line)

        # ignore line that says "distortion"
        line = inf.readline()
        line = inf.readline().split()
        line = [float(en) for en in line]
        dist.append(line)

        # cmtx = camer_matrix, dist = distortion_parameters
        return np.array(cmtx), np.array(dist)

    def get_qr_coords(self, cmtx, dist, points):

        # Selected coordinate points for each corner of QR code
        qr_edges = np.array([[0,0,0],
                            [0,1,0],
                            [1,1,0],
                            [1,0,0]], dtype = 'float32').reshape((4,1,3))
        
        # determine the orientation of the QR code coordinate system with respect to camera coordinate system
        ret, rvec, tvec = cv2.solvePnP(qr_edges, points, cmtx, dist)

        # Define unit XYZ axes. These are then projected to camera view using the rotation matrix and translation vector
        unity_points = np.array([[0,0,0], [1,0,0], [0,1,0], [0,0,1]], dtype='float32').reshape((4,1,3))

        if ret:
            points, jac = cv2.projectPoints(unity_points, rvec, tvec, cmtx, dist)
            return points, rvec, tvec
        
        # return empty arrays if rotation and translation values not found
        else:
            return [], [], []

    def qr_recognize(self, cmtx, dist):
        qr = cv2.QRCodeDetector()
        # Infinite loop to capture video and analyze it
        while True:
            # Read frames from the camera using the record variable we assigned above
            ret, frame = self.record.read()
            if not ret:
                # If frame not captured, break loop
                break
            height, width = frame.shape[:2]
            # Convert each frame to Grayscale 
            gray_scale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Decode the QR code in each frame
            qr_code = decode(gray_scale)
            # Loop through the detected QR codes
            for i in qr_code:
                if (self.flight_mode != "GUIDED"):
                    self.setFlightMode("GUIDED")
                self.master.mav.statustext_send(mavutil.mavlink.MAV_SEVERITY_INFO, "QR DETECTED !!".encode())
                # Draw bounding box around the QR code
                x, y ,w, h = i.rect
                # Draw a red rectangle around the QR code
                # cv2.rectangle(frame, (x, y), (x+w, y+h), (0,0,255), 2)
                # Draw the QR code data on the frame
                # cv2.putText(frame, i.data.decode(), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                # Calculate the width of the QR code in the real world 7 cm
                real_width = 6.9
                # Calculate the distance to the QR code using the width of the QR code and the focal length of the camera
                distance = (real_width * self.focal_length_pixels) / w
                # Calculate the center of the QR code
                qr_center = (int(x+w/2), int(y+h/2))
                # Calculate the center of the frame
                frame_center = (int(width/2), int(height/2))
                # Draw circle at the center of the frame
                cv2.circle(frame, frame_center, 5, (0,255,0), -1)
                # Draw circle at the center of the QR_Code
                cv2.circle(frame, qr_center, 5, (0,0,255), -1)
                # If the QR code is not at the center, then find the direction it is moving towards
                # if center is not None:
                # Update the initial position of the QR code current center position
                center = frame_center
                # Calculating the distance traveled by the QR code in the x and y directions
                self.dx = (qr_center[0] - center[0]) * distance / self.focal_length_pixels
                self.dy = (qr_center[1] - center[1]) * distance / self.focal_length_pixels
                # Print the distance traveled by QR on the frame
                cv2.putText(frame, f"dx:{self.dx:.2f} cm, dy:{self.dy:.2f} cm", (x, y-45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                # Update the QR code current center position
                # center = qr_center
                # Draw the estimated distance on the frame
                cv2.putText(frame, 'Distance: {:.2f} cm'.format(distance), (x, y-25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                # Get frame dimensions
                ret_qr, points = qr.detect(frame)
                if ret_qr:
                    axis_points, rvec, tvec = self.get_qr_coords(cmtx, dist, points)
                    # BGR color format
                    colors = [(255,0,0), (0,255,0), (0,0,255), (0,0,0)]
                    # Check axes points are projected to camera view
                    # if len(axis_points) > 0:
                    axis_points = axis_points.reshape((4,2))
                    origin = (int(axis_points[0][0]), int(axis_points[0][1]))

                    for p, c in zip(axis_points[1:], colors[:3]):
                        p = (int(p[0]), int(p[1]))

                        # Sometimes QR detector will make a mistake and projected point will overflow integer value, let's skip these cases
                        if origin[0] > 5*frame.shape[1] or origin[1] > 5*frame.shape[1]:
                            break
                        if p[0] > 5*frame.shape[1] or p[1] > 5*frame.shape[1]:
                            break
                        cv2.line(frame, origin, p, c, 5)
                # Assign a variable to read and store what text the QR code read
                text_read = i.data.decode()
                if text_read != None:
                    # qr_info function called and assigned values of the QR
                    self.qr_info(i.orientation, i.rect.left, i.rect.top, i.rect.width, i.rect.height)
                    # print(i.rect.top)
                    # Calling the pilot_ability function and the decisions are taken
                    self.pilot_ability()
                    # self.land_drone()
            # time when we finish processing for this frame
            self.new_frame_time = time.time()
            # Calculating the fps
            # fps will be number of frame processed in given time frame
            # since their will be most of time error of 0.001 second
            # we will be subtracting it to get more accurate result
            self.fps = 1/(self.new_frame_time - self.prev_frame_time)
            self.prev_frame_time = self.new_frame_time
            # converting the fps into integer
            self.fps = int(self.fps)
            # converting the fps to string so that we can display it on frame
            # by using putText function
            self.fps = str(self.fps)
            cv2.putText(frame, 'FPS: {:d}'.format(int(self.fps)), (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cpu_usage = psutil.Process(os.getpid()).cpu_percent()
            ram_usage_percent = psutil.Process(os.getpid()).memory_percent()
            ram_usage_gb = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
            # cv2.putText(frame, 'CPU: {:.2f}%, RAM: {:.2f}% ({:.2f} MB)'.format(cpu_usage, ram_usage_percent, ram_usage_gb), (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            # Display the output frame
            cv2.imshow('QR Code Decoder', frame)
            # Exit if the 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # Release the VideoCapture object and close the window
        self.record.release()
        cv2.destroyAllWindows()

    def main(self):
        cmtx , dist = self.read_camera_parameters()
        self.qr_thread = threading.Thread(target=self.qr_recognize(cmtx, dist))
        # Starting the threads
        self.qr_thread.start()
        # Waiting for the threads to complete
        self.qr_thread.join()
        rospy.spin()


if __name__ == '__main__':
    DroneControl = DronePrecisionLanding()
    DroneControl.main()
