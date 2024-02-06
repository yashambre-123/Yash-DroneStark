# Import necessary modules: Flask for creating a web server and request for handling HTTP requests
from flask import Flask, request
import serial

# Create a Flask web application instance
app = Flask(__name__)

# Initialize a serial connection with a specific device
ser = serial.Serial('/dev/ttyUSB0', 115200)

# Define a route "/rc_values" for handling POST requests
@app.route('/rc_values', methods=['POST'])
def receive_rc_values():
    # Get JSON data from the POST request
    rc_data = request.get_json()

    # Extract RC values from the received JSON data
    roll_value = int(rc_data.get('roll', 0))
    pitch_value = int(rc_data.get('pitch', 0))
    throttle_value = int(rc_data.get('throttle', 0))
    yaw_value = int(rc_data.get('yaw', 0))
    toggle_1_value = int(rc_data.get('toggle_1', 0))
    slider_1_value = int(rc_data.get('slider_1', 0))
    toggle_2_value = int(rc_data.get('toggle_2', 0))
    slider_2_value = int(rc_data.get('slider_2', 0))

    # Create a string containing the formatted data to send via serial communication
    data_to_send = f"PHYSICAL_REMOTE,{roll_value},{pitch_value},{throttle_value},{yaw_value},{toggle_1_value},{slider_1_value},{toggle_2_value},{slider_2_value}\n"
    
    # Write the formatted data to the serial device
    try:
        ser.write(data_to_send.encode('utf-8'))
        print("I have sent the data") 
    except Exception as e:
        print(f"Error sending data: {e}")

    # Print the received RC values for debugging
    print("Roll: ", roll_value)
    print("Pitch: ", pitch_value)
    print("Throttle: ", throttle_value)
    print("Yaw: ", yaw_value)
    print("Toggle 1: ", toggle_1_value)
    print("Slider 1: ", slider_1_value)
    print("Toggle 2: ", toggle_2_value)
    print("Slider 2: ", slider_2_value)

    # Return a response to indicate successful reception of RC values
    return "RC values received successfully"
    
# Entry point for the script: Run the Flask web application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6007, debug=True)
