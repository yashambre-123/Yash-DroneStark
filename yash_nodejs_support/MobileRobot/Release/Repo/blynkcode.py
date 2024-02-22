import blynklib, socket, json
import signal, time
#rohan's phone
BLYNK_AUTH = '2tkhhZ1R1E4PsSpIDuqS_H9dBoiNTUtb'
#shardul's phone
#BLYNK_AUTH = 'altBGggALHu2aCuzjelkyS-LrqjW6PSD'
#tablet rover main
#BLYNK_AUTH = '5aaJKIuqOsY4hm8WzMESByXXQbztKnco'
#tablet rover user
#BLYNK_AUTH = 'TDPyaGcB6Q9tEPbopPQMuh8kZ83W7Oki'
userData = {}
bed_valid = 0
valid_send = 0
# initialize Blynk
blynk = blynklib.Blynk(BLYNK_AUTH)
WRITE_EVENT_PRINT_MSG = "Bed Number Pin: V{} Value: '{}'"
WRITE_EVENT_PRINT_MSG_1 = "Status: V{} Value: '{}'"
robot_motion = 0
#WidgetLED led1(V2)
#open socket for sending data from client to server
def open_socket(port):
    sock = socket.socket()
    sock.connect((socket.gethostname(), port))
    print("Client up")
    return sock

#send data from socket after validating
def sendCmd(data):
    global valid_send, sock, robot_motion
    #sock = open_socket(40000)
    #print(valid_send)
    datapacket = json.dumps(data)
    sock.send(datapacket.encode('utf-8'))
    print("SendCmd")
    blynk.virtual_write(2, 255)
    r = sock.recv(1024)
    print(r)
    while(r != b'R'):
        r = sock.recv(1024)
        print("Waiting for ack")
        valid_send = 1
        #robot_motion = 1
        #blynk.virtual_write(2, 255)
        print("led on")
        #led1.on()
    #robot_motion = 0
    valid_send = 0
    print("led off")
    #led1.off()
    print("Valid_send: %d" % valid_send)
    if r == b'R':
        blynk.virtual_write(2, 0)
    #sock.close()


#button in blynk app
@blynk.handle_event('write V1')
def write_virtual_pin_handler(pin, value):
    global userData, valid_send, bed_valid
    print(value[0])
    if value[0] == '1':
        if userData["status"][0] == '2' and valid_send == 0:
            print("sent return to home")
            sendCmd(userData)
        elif bed_valid == 1 and valid_send == 0:
            print("Sending bed location")
            sendCmd(userData)
            bed_valid = 0

    

# register handler for virtual pin V0 write event
# check for each status 1 - go to bed,2 - done check  
@blynk.handle_event('write V0')
def write_virtual_pin_handler(pin, value):
    global userData, valid_send, bed_valid
    #print(WRITE_EVENT_PRINT_MSG_1.format(pin, value))
    userData["status"] = value
    print("Valid_send: %d" % valid_send)
    print("Value: ")
    print(userData["status"])

#read data from blynk app control numeric up down 
# register handler for virtual pin V4 write event
@blynk.handle_event('write V4')
def write_virtual_pin_handler(pin, value):
    global userData, bed_valid
    print(WRITE_EVENT_PRINT_MSG.format(pin, value))
    userData["Bed"] = value
    bed_valid = 1
"""
#glow Led if the robot is moving
@blynk.handle_event('read V2')
def read_virtual_event(pin):
    global robot_motion
    blynk.virtual_write(pin, robot_motion*255)
"""
#def stop_event(sig, frame):
#    global sock
#    sock.close()
#    sys.exit(0)

###########################################################
# infinite loop that waits for event
###########################################################
if __name__ == "__main__":
    time.sleep(10)
    sock = open_socket(40000)
    #signal.signal(signal.SIGINT, stop_event)
    while True:
        blynk.run()
    
    sock.close()
