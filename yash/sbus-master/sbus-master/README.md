# sbus

## Overview

This Git repository contains a collection of scripts and configurations for a control system that interfaces with an SBUS-based remote control system. These scripts enable communication with SBUS devices via a USB-to-Serial connection and provide web-based control interfaces. This README provides an overview of the scripts and how to set up and use them.

## Prerequisites

Before using these scripts, ensure you have the following prerequisites:

- A Raspberry Pi or similar single-board computer with an available USB port.
- Python 3.x installed on the Raspberry Pi.
- `screen` and `minicom` installed on the Raspberry Pi.
- An SBUS-based remote control system and SBUS receiver connected to the USB port (`/dev/ttyUSB0`) on the Raspberry Pi.
- Basic knowledge of Git for cloning this repository.

      sudo apt update

      sudo apt install git

      sudo apt install python3

      sudo apt install screen

      sudo apt install minicom


## Repository Structure

The repository is organized as follows:

- `app.py`: Flask-based web application for sending RC control data.
- `ext_receive.py`: Python script for receiving RC control data.
- `receive.py`: Python script for receiving data from a physical remote.
- `rpi_remote.sh`: Shell script for setting up and running the control system.
- `README.md`: This README file.

## Installation and Usage

1. Clone this repository to your Raspberry Pi using the following command:

            git clone https://github.com/flying-monk/sbus.git

2. Navigate to the cloned repository directory:

            cd sbus

3. Make sure that the USB device /dev/ttyUSB0 is connected and recognized by your Raspberry Pi.

4. Run the setup script to configure the USB device permissions and control system scripts:
    
            chmod +x rpi_remote.sh

            ./rpi_remote.sh

### Set of instruction

* Wait for the USB device to become available (/dev/ttyUSB0).
* Set appropriate permissions for /dev/ttyUSB0.
* Start the Flask web application (app.py) for sending RC control data.
* Start the ext_receive.py script for receiving RC control data.
* Start the receive.py script for receiving data from a physical remote.
* Start a serial monitor using minicom for debugging.
* Access the web-based control interface by opening a web browser and navigating to your Raspberry Pi's IP address with port 6000 (e.g., http://raspberrypi.local:6000). This interface allows you to send control commands.

Monitor the system's operation and RC control data in the terminal where the scripts are running.

To stop the control system, you can exit the screen sessions or use the screen -r command to resume a session and then press Ctrl + C.


## Additional Notes

You may need to adjust the script paths and configuration settings in the scripts (app.py, ext_receive.py, and receive.py) to match your setup.

Make sure you have the required permissions to execute the scripts and set up the system.

This README provides a basic setup guide. Additional configuration and customization may be required based on your specific use case.

If you encounter issues, please refer to the script comments and documentation for troubleshooting.


### Start at boot

      sudo nano /etc/systemd/system/sbus-control.service

#### Copy and paste this inside the file

### Service file

      [Unit]
      Description=SBUS Control System Service
      After=network.target

      [Service]
      ExecStart=/home/maker/sbus/rpi_remote.sh
      WorkingDirectory=/home/maker/sbus/
      StandardOutput=inherit
      StandardError=inherit
      Restart=always
      User=maker

      [Install]
      WantedBy=multi-user.target

#### To run all the scripts seperately,
#### To run the virtual joystick receiver script:

      python3 ext_receive.py

#### To run the virtual joystick host script:

      python3 app.py

#### To run the Physical virtual joystick receiver script:

      python3 receive.py

#### To run the Physical virtual joystick host script:

      python3 send.py

#### To initiate minicom 

      sudo minicom -D /dev/ttyUSB0 -b 115200
