# Untitled - By: ds-dev - Mon Jul 13 2020

# Detects datamatrix and activates servo if datamatrix is valid

import sensor, image, time, math
import pyb

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False)  # must turn this off to prevent image washout...
sensor.set_auto_whitebal(False)  # must turn this off to prevent image washout...
clock = time.clock()

s1 = pyb.Servo(1)       # on pin P7

red_led = pyb.LED(1)
green_led = pyb.LED(2)

open_angle = 180
close_angle = 0
s1.angle(close_angle, 1000)
open_flag = 0

tags = ["CH001082020", "CH002082020", "CH003082020"]    # currently allowed tags. Will be changed later

while(True):
    clock.tick()
    img = sensor.snapshot()
    img.lens_corr(1.8) # strength of 1.8 is good for the 2.8mm lens.
    print(open_flag)
    matrices = img.find_datamatrices()
    for matrix in matrices:                 # can eliminate for loop for single datamatrix detection
        img.draw_rectangle(matrix.rect(), color = (255, 0, 0))
        #print_args = (matrix.rows(), matrix.columns(), matrix.payload(), (180 * matrix.rotation()) / math.pi, clock.fps())
        #print("Matrix [%d:%d], Payload \"%s\", rotation %f (degrees), FPS %f" % print_args)
        red_led.toggle()
        for i in tags:

            if matrix.payload() == i:
                print("Found matching payload")
                red_led.off()
                green_led.on()
                s1.angle(open_angle, 1000)      # activating servo
                pyb.delay(3000)
                open_flag = 1
                break

        if open_flag == 1:
            print("flag is open, now closing")
            pyb.delay(3000)
            open_flag = 0
            s1.angle(close_angle, 1000)         # deactivating servo
            green_led.off()
            break

    if not matrices:
        #open_flag = 0
        green_led.off()
        red_led.on()
        #print("FPS %f" % clock.fps())
        print("Waiting for tag")
