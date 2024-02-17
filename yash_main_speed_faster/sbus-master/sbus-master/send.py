# Import necessary libraries: pygame for joystick input and requests for HTTP requests
import pygame
import requests
import time

# Define the main function for the program
def main_loop():
    # Initialize the pygame library
    pygame.init()
    pygame.font.init()

    # Set up the joystick
    time.sleep(2)
    pygame.joystick.init()
    time.sleep(2)
    
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    # Initialize a flag for the main loop
    running = True
    while running:
        # Check for events (e.g., quit event)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Read RC values from the joystick axes
        roll = joystick.get_axis(3)  # Roll axis 
        pitch = joystick.get_axis(4)  # Pitch axis correct
        throttle = joystick.get_axis(1)  # Throttle axis correct
        yaw = joystick.get_axis(0)  # Yaw axis correct
        # toggle_1 = joystick.get_axis(2)  # 3-way toggle switch axis
        # slider_1 = joystick.get_axis(5)  # Slider 1
        # toggle_2 = joystick.get_axis(6)  # 3-way toggle switch axis
        toggle_1 = -1
        slider_1 = -1
        toggle_2 = -1
        slider_2 = -1

        # Map joystick input values to a desired range (0 to 2000)
        roll = map_value(roll, -1, 1, 170, 1811)
        pitch = map_value(pitch, -1, 1, 1811, 170)
        throttle = map_value(throttle, -1, 1, 1811, 170)
        yaw = map_value(yaw, -1, 1, 170, 1811)
        toggle_1 = map_value(toggle_1, -1, 1, 170, 1811)
        slider_1 = map_value(slider_1, -1, 1, 170, 1811)
        toggle_2 = map_value(toggle_2, -1, 1, 170, 1811)
        slider_2 = map_value(slider_2, -1, 1, 170, 1811)
        
        print("roll: ", roll)
        print("pitch: ", pitch)
        print("throttle: ", throttle)
        print("yaw: ", yaw)
        print("toggle1: ", toggle_1)
        print("slider1: ", slider_1)
        print("toggle2: ", toggle_2)
        print("slider2: ", slider_2)

        # Create a dictionary with the mapped RC values
        rc_values = {
            'roll': roll,
            'pitch': pitch,
            'throttle': throttle,
            'yaw': yaw,
            'toggle_1': toggle_1,
            'slider_1': slider_1,
            'toggle_2': toggle_2,
            'slider_2': slider_2
        }
        
        # Define the URL for sending the RC values via an HTTP POST request
        # url = 'https://gimbalcontrol.ngrok.app/rc_values'
        url = 'http://192.168.1.40:5005/rc_values'  # An alternative local URL

        # Send the RC values as JSON data via an HTTP POST request
        response = requests.post(url, json=rc_values)
        if response.status_code == 200:
            print('RC values sent successfully.')

# Define a function to map a value from one range to another
def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Entry point for the script: Run the main loop
if __name__ == '__main__':
    main_loop()
