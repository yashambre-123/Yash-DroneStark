# Import necessary modules from Flask and requests libraries
from flask import Flask, render_template, request
import requests
import math
import time
import threading
import aiohttp
import asyncio
# Create a Flask web application instance
app = Flask(__name__)

# Define two dictionaries to store joystick data
joystick_data_1 = {}  
joystick_data_2 = {} 

# Initialize variables for various control parameters
throttle = 0
yaw = 0
roll = 0
pitch = 0
slider_1 = 0
slider_2 = 0
zoom_value = 0
toggle_2 = 0

# Define a route for the root URL ("/") that renders an HTML template
@app.route('/')
def index():
    return render_template('joy2.html')

# Define a route for handling POST requests with joystick data
@app.route("/joystick_data", methods=["POST"])
def joystick_data():
    data = request.get_json()

    # Update joystick_data_1 if "joy1Div" key is present in the received data
    if "joy1Div" in data:
        joystick_data_1.update(data["joy1Div"])
        process_joy1_data(joystick_data_1)

    # Update joystick_data_2 if "joy2Div" key is present in the received data
    if "joy2Div" in data:
        joystick_data_2.update(data["joy2Div"])
        process_joy2_data(joystick_data_2)

    return "Data received successfully"

@app.route("/joystick_data_new", methods=["POST"])
def joystick_data_new():
    data = request.get_json()
    
    if "a" in data:
        process_joy1_physical_entire_data(data["a"])
    # if "b" in data:
    #     # joystick_data_1.update(data["b"])
    #     process_joy1_new_buggy_up_down_data(data["b"])
    # if "c" in data:
    #     process_joy2_new_camera_left_right_data(data["c"])
    # if "d" in data:
    #     process_joy2_new_camera_up_down_data(data["d"])
        
    return "data new received successfully"

def process_joy1_physical_entire_data(data):
    
    roll = 0
    pitch = 0
    throttle = data[1]
    yaw = data[0]
    toggle_2 = 0
    zoom_value = 0
    slider_1 = 0
    slider_2 = 0
    yaw = map_value(yaw, -1, 1, 170, 1811)
    throttle = map_value(throttle, -1, 1, 1811, 170)
    
    send_rc_values(throttle, yaw, roll, pitch, slider_1, slider_2, zoom_value, toggle_2, "virtual")
    
# def process_joy1_new_buggy_left_right_data(data):
#     # x = int(float(data))
#     x = data
#     # print("yaw: ", x)
#     yaw = map_value(x, -1, 1, 170, 1811)
#     # print("yaw: ", yaw)
#     send_rc_values(throttle, yaw, roll, pitch, slider_1, slider_2, zoom_value, toggle_2, "virtual")

# def process_joy1_new_buggy_up_down_data(data):
#     # y = int(float(data))
#     y = data
#     throttle = map_value(y, -1, 1, 1811, 170)
#     # print("throttle: ", y)
#     # throttle = map_value(y, -1, 1, 1811, 170)
#     # print("throttle: ", throttle)
#     send_rc_values(throttle, yaw, roll, pitch, slider_1, slider_2, zoom_value, toggle_2, "virtual")

# def process_joy2_new_camera_left_right_data(data):
#     # x = int(float(data))
#     x = data
#     # print("roll: ", x)
#     roll = map_value(x, -1, 1, 1811, 170)
#     # print("roll: ", roll)
#     send_rc_values(throttle, yaw, roll, pitch, slider_1, slider_2, zoom_value, toggle_2, "virtual")

# def process_joy2_new_camera_up_down_data(data):
#     # y = int(float(data))
#     y = data
#     # print("pitch: ", y)
#     pitch = map_value(y, -1, 1, 170, 1811)
#     # print("pitch: ", pitch)
#     send_rc_values(throttle, yaw, roll, pitch, slider_1, slider_2, zoom_value, toggle_2, "virtual")

# Define a function to process joystick data for joystick 1
def process_joy1_data(data):
    global throttle, yaw
    x = data.get("x", 0)
    y = data.get("y", 0)
    # Map joystick data to control parameters (throttle and yaw)
    if (x > 0 and y > 0):
        x = ((math.sqrt(x*x*x)) / 10)
        y = ((math.sqrt(y*y*y)) / 10)
    elif (x < 0 and y < 0):
        x = -1 * x
        y = -1 * y
        x = -1 * ((math.sqrt(x*x*x)) / 10)
        y = -1 * ((math.sqrt(y*y*y)) / 10)
    elif (x > 0 and y < 0):
        y = -1 * y
        x = ((math.sqrt(x*x*x)) / 10)
        y = -1 * ((math.sqrt(y*y*y)) / 10)
    elif (x < 0 and y > 0):
        x = -1 * x
        x = -1 * ((math.sqrt(x*x*x)) / 10)
        y = ((math.sqrt(y*y*y)) / 10)
    
    yaw = map_value(x, -100, 100, 170, 1811) # 170 and 1811
    throttle = map_value(y, -100, 100, 170, 1811)
    
    # yaw = map_value(x, -100, 100, 0, 2000)
    # throttle = map_value(y, -100, 100, 0, 2000)
    # Send RC values to a remote control server
    send_rc_values(throttle, yaw, roll, pitch, slider_1, slider_2, zoom_value, toggle_2, "virtual")

# Define a function to process joystick data for joystick 2
def process_joy2_data(data):
    global roll, pitch
    x = data.get("x", 0)
    y = data.get("y", 0)
    # Map joystick data to control parameters (pitch and roll)
    
    if (x > 0 and y > 0):
        x = ((math.sqrt(x*x*x)) / 10)
        y = ((math.sqrt(y*y*y)) / 10)
    elif (x < 0 and y < 0):
        x = -1 * x
        y = -1 * y
        x = -1 * ((math.sqrt(x*x*x)) / 10)
        y = -1 * ((math.sqrt(y*y*y)) / 10)
    elif (x > 0 and y < 0):
        y = -1 * y
        x = ((math.sqrt(x*x*x)) / 10)
        y = -1 * ((math.sqrt(y*y*y)) / 10)
    elif (x < 0 and y > 0):
        x = -1 * x
        x = -1 * ((math.sqrt(x*x*x)) / 10)
        y = ((math.sqrt(y*y*y)) / 10)
        
    pitch = map_value(x, -100, 100, 170, 1811)
    roll = map_value(y, -100, 100, 170, 1811)
    # pitch = map_value(x, -100, 100, 0, 2000)
    # roll = map_value(y, -100, 100, 0, 2000)
    # Send RC values to a remote control server
    send_rc_values(throttle, yaw, roll, pitch, slider_1, slider_2, zoom_value, toggle_2, "virtual")
    

# Define a route for handling POST requests with slider data
@app.route("/slider_data", methods=["POST"])
def slider_data():
    global slider_1  
    data = request.get_json()
    if "sliderValue" in data:
        slider_value_1 = int(data["sliderValue"])
        # Map slider value to slider_1 variable
        slider_1 = map_value(slider_value_1, 0, 100, 170, 1810)
        # slider_1 = map_value(slider_value_1, 0, 100, 0, 2000)
        # Send RC values to a remote control server
        send_rc_values(throttle, yaw, roll, pitch, slider_1, slider_2, zoom_value, toggle_2, "virtual")
    return "Slider 1 data received successfully"

# Define a route for handling POST requests with slider 2 data
@app.route("/slider2_data", methods=["POST"])
def slider2_data():
    global slider_2
    data = request.get_json()
    if "sliderValue2" in data:
        slider_value_2 = int(data["sliderValue2"])
        # Map slider value to slider_2 variable
        slider_2 = map_value(slider_value_2, 0, 100, 170, 1810)
        # slider_2 = map_value(slider_value_2, 0, 100, 0, 2000)
        # Send RC values to a remote control server
        send_rc_values(throttle, yaw, roll, pitch, slider_1, slider_2, zoom_value, toggle_2, "virtual")
    return "Slider 2 data received successfully"

# Define a route for handling POST requests with zoom data
@app.route("/zoom_data", methods=["POST"])
def zoom_data():
    global zoom_value
    data = request.get_json()
    # print("Received zoom data:", data)

    if "zoom" in data:
        zoom_value = int(data["zoom"])
        # print("Zoom Value:", zoom_value)

        # Map zoom value to zoom_value variable
        zoom_value = map_value(zoom_value, 0, 100, 170, 1810)
        # zoom_value = map_value(zoom_value, 0, 100, 0, 2000)

    # Send RC values to a remote control server
    send_rc_values(throttle, yaw, roll, pitch, slider_1, slider_2, zoom_value, toggle_2, "virtual")
    return "Zoom 1 data received successfully"

# Define a route for handling POST requests with toggle 2 data
@app.route("/toggle2_data", methods=["POST"])
def toggle2_data():
    global toggle_2
    data = request.get_json()
    if "toggleValue2" in data:
        toggle_value_2 = int(data["toggleValue2"])
        # Map toggle value to toggle_2 variable
        # toggle_2 = map_value(toggle_value_2, 0, 100, 170, 1810)
        toggle_2 = map_value(toggle_value_2, 0, 100, 0, 2000)
        # Send RC values to a remote control server
        send_rc_values(throttle, yaw, roll, pitch, slider_1, slider_2, zoom_value, toggle_2, "virtual")
    return "Toggle 2 data received successfully"
    
async def post_with_json(url, json_data):
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json_data) as response:
            return response

# Define a function to send RC values to a remote control server
async def send_rc_values(throttle_data, yaw_data, pitch_data, roll_data, slider_1, slider_2, toggle_1, toggle_2, joystick_type):
    
    # print("Roll: ", roll_data)
    # print("Pitch: ", pitch_data)
    # print("Throttle: ", throttle_data)
    # print("Yaw: ", yaw_data)
    # print("Toggle 1: ", toggle_1)
    # print("Slider 1: ", slider_1)
    # print("Toggle 2: ", toggle_2)
    # print("Slider 2: ", slider_2)
    
    rc_values = {
        'roll_data': roll_data,
        'pitch_data': pitch_data,
        'throttle_data': throttle_data,
        'yaw_data': yaw_data,        
        'toggle_1': toggle_1,
        'slider_1': slider_1,        
        'toggle_2': toggle_2,
        'slider_2': slider_2,
    }
    
    # time.sleep(2)
    
    # print(rc_values)
    # print("Roll: ", roll_data)
    # print("Pitch: ", pitch_data)
    # print("Throttle: ", throttle_data)
    # print("Yaw: ", yaw_data)
    # print("Toggle 1: ", toggle_1)
    # print("Slider 1: ", slider_1)
    # print("Toggle 2: ", toggle_2)
    # print("Slider 2: ", slider_2)

    # Define the URL for the remote control server
    
    if (joystick_type == "virtual"):
        
        url = 'http://127.0.0.1:6002/rc_values'
        json_data = rc_values
        
        start = time.time()
        
        response = await post_with_json(url, json_data)
        
        end = time.time()
        
        print(f"Time taken: {(end-start)*10**3:.03f}ms")
        
        # if (response.status == 200):
        #     print('RC values sent successfully.')
        # else:
        #     print('Failed to send RC values. Status code:', response.status_code)

        # try:
        #     # Send a POST request with JSON data to the remote control server
        #     # start = time.perf_counter_ns()
        #     start = time.time()
        #     response = requests.post(url, json=rc_values)
        #     # end = time.perf_counter_ns()
        #     end = time.time()
        #     print(f"Time taken: {(end-start)*10**3:.03f}ms")
        #     # print(f"time of execution: {(end-start)}")
        #     if response.status_code == 200:
        #         print('RC values sent successfully.')
        #     else:
        #         print('Failed to send RC values. Status code:', response.status_code)
        #     # end = time.time()
        #     # print(f"Time taken: {(end-start)*10**3:.03f}ms")
        # except Exception as e:
        #     print('Error while sending RC values:', e)
    
    # time.sleep()
    
    # elif (joystick_type == "physical"):
        
    #     url = 'http://127.0.0.1:6007/rc_values'

    #     try:
    #         # Send a POST request with JSON data to the remote control server
    #         response = requests.post(url, json=rc_values)
    #         if response.status_code == 200:
    #             print('physical RC values sent successfully.')
    #         else:
    #             print('Failed to send physical RC values. Status code:', response.status_code)
    #     except Exception as e:
    #         print('Error while sending physical RC values:', e)

# Define a function to map a value from one range to another
def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Start the Flask web application if this script is executed
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6001, debug=True) #OG
    # app.run(host="0.0.0.0", debug=True)
    # app.run()
