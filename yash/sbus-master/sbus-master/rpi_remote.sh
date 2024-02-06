#!/bin/sh
#!/etc/systemd/system/sbus/rpi_remote.sh

# Define a function to wait for the USB device "/dev/ttyUSB0" to become available
wait_for_usb() {
    while [ ! -e "/dev/ttyUSB0" ]; do
        sleep 1
    done
}

# Call the wait_for_usb function to wait for the USB device
wait_for_usb

# Change the permissions of "/dev/ttyUSB0" to allow read and write for all users
sudo chmod 666 /dev/ttyUSB0

# Print a message indicating the start of the Sender Script
echo "Started Sender Script"

# Start a detached screen session named "Sender" and run a Python script
screen -dmS Sender bash -c "python /etc/systemd/system/sbus/app.py; exec bash"

# Print a message indicating the start of the Receiver Script
echo "Started Receiver Script"

# Start a detached screen session named "Receiver" and run a Python script
screen -dmS Receiver bash -c "python /etc/systemd/system/sbus/ext_receive.py; exec bash"

# Print a message indicating the turning on of the serial monitor
echo "Turning on serial monitor"

# Start a detached screen session named "Serial_Monitor" and run minicom to monitor the serial port
screen -dmS Serial_Monitor bash -c "minicom -D /dev/ttyUSB0 -b 115200"
