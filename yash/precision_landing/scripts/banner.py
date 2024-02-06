#!/usr/bin/env python
import rospy
from mavros_msgs.srv import SetMode
import time
import struct
rospy.init_node('mode_change', anonymous=False)
def setFlightMode(mode):
    rospy.wait_for_service("/mavros/set_mode")
    try:
        set_mode = rospy.ServiceProxy("/mavros/set_mode", SetMode)
        # if (type(mode) == int):
        #     mode_bytes = struct.pack("<I", mode)
        #     set_mode(0, mode_bytes)
        #     flight_mode = mode
        # else:
        set_mode(0, str(mode))
        flight_mode = str(mode)
    except rospy.ServiceException as e:
        rospy.loginfo("SET MODE CALL: FAILED")

if __name__ == "__main__":
    setFlightMode(29)
    time.sleep(5)
    setFlightMode("STABILIZE")
    rospy.spin()