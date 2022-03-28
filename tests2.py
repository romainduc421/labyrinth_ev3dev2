#!/usr/bin/env python3

import random
import os      # to set font
import sys
import time    # to use sleep()
import socket
import math
from ev3dev2._platform.fake import INPUT_2, INPUT_3  # to get host name
from ev3dev2.sound   import Sound
from ev3dev2.display import Display
from ev3dev2.button  import Button
from ev3dev2.led     import Leds
from ev3dev2.motor   import MoveTank,MoveSteering, MediumMotor, LargeMotor, SpeedPercent
from ev3dev2.motor   import OUTPUT_A, OUTPUT_D
from ev3dev2.sensor   import INPUT_1, INPUT_4
from ev3dev2.sensor.lego import UltrasonicSensor, ColorSensor
from ev3dev2.sensor.lego import GyroSensor, TouchSensor
from PIL             import Image  # should not be needed, but IT IS!

######################################################################
###                                                                ###
###       THIS PROGRAM WORKS BADLY IF STARTED IN CONSOLE!!!        ###
###                                                                ###
### It switches between the image displayed and the brick display. ###
###                                                                ###
###      You'd better start it from the brick's file browser!      ###
###                                                                ###
######################################################################

## To do: add DeviceNotFound exception handling!..

# === Various global variables commonly used =========================

distance_sensor = UltrasonicSensor(INPUT_4)
color_sensor = ColorSensor(INPUT_2)
gyro_sensor = GyroSensor(INPUT_3)
e_stop = TouchSensor(INPUT_1)
spkr = Sound()
tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)

# === VARIABLES     ==================================================
maze_end_color = "Red"
maze_start_color = "Green"

# === Various functions to simplify calls ============================

# === Checking motors and sensors ====================================

def print_display(display, text):
    # using display.text_grid(text, ...) instead of print(test)
    display.text_grid(text, True, 0, 10) # clear screen, 11th row / 22
    display.update()

def wait_for_any_release(button):
    """ Wait for any button to be released. """
    button.wait_for_released([ 'backspace', 'up', 'down',
                               'left', 'right', 'enter' ])

def large_motor_check(noisy, sound, display, button): #---------------
    steer_motors = MoveSteering(OUTPUT_A, OUTPUT_D)
    if (noisy):  sound.speak('Checking Large Motor!')
    speed   = 0
    steer   = 0
    looping = True
    while (looping):
        # display state (speed & steer)
        print_display(display,  'Motors: speed = ' + str(speed)
                      + ', steer =' + str(steer) )
        steer_motors.on(steer, speed)
        # wait for a button to be pressed
        while ( not button.any() ):  time.sleep(0.1)
        if (looping):  # otherwise
            if   (button.down):
                if (speed > -100): speed -= 25
            elif (button.up):
                if (speed <  100): speed += 25
            elif (button.left):
                if (steer > -100): steer -= 25
            elif (button.right):
                if (steer <  100): steer += 25
            else: # center button at a stop quits the loop
                if ( (speed == 0) and (steer == 0) ):
                    looping = False
                else:  # otherwise stops the motors
                    speed = 0
                    steer = 0
        wait_for_any_release(button)
        steer_motors.off()

def debug_printing(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

### this function gets the bot to say something
def speak( text ):
    spkr.speak(text)

def beep(tone, time):
    spkr.play_tone(tone, time, play_type=Sound.PLAY_NO_WAIT_FOR_COMPLETE)

### 
# This function makes the bot turning left
# def on_for_degrees(self, left_speed, right_speed, degrees, brake=True, block=True)
def turnleft():
    print("Turning left")
    if tank_drive:
        tank_drive.on_for_degrees(-10 , 10, 200)

###
# This function makes the bot turning right
# def on_for_degrees(self, left_speed, right_speed, degrees, brake=True, block=True)
def turnright():
    print("Turning right")
    if tank_drive:
        tank_drive.on_for_degrees(10 , -10, 200)

###
# This function makes the bot turning back (180 degrees rotation)
# def on_for_degrees(self, left_speed, right_speed, degrees, brake=True, block=True)
def demitour():
    print("Turning back")
    if tank_drive:
        tank_drive.on_for_degrees(10 , -10, 470)

###
# This function makes the bot moving forward.
# def on(self, steering, speed)
def forward():
    print("Moving forward")
    if tank_drive:
        tank_drive.on(10,10)

###
# This function makes the bot turning left back >---
#                                                  |
#                                                  v
def turnbackleft():
    if tank_drive:
        tank_drive.on_for_degrees(-10,10,-200)

###
# This function makes the bot turning right back    ----<
#                                                  |
#                                                  v
def turnbackright():
    if tank_drive:
        tank_drive.on_for_degrees(10,-10,-200)

###
# This function makes the bot turning off its motors
def stop_motors():
    if tank_drive:
        tank_drive.off(brake=True)

def getColour():
    return color_sensor.color_name


###
# Main function executable
def main():
    #med_motor = MediumMotor()
    tank_drive=MoveTank(OUTPUT_A,OUTPUT_D)
    button  = Button()
    looping = True

    solved = False

    host_letter = socket.gethostname()[4]
    while looping and (not solved):
        cpt_left, cpt_right=0,0
        #distance=distance_sensor.distance_centimeters
        looping = not button.backspace
        print('Ultrasonic: ' + str(distance_sensor.distance_centimeters))
        #print('Gyro: ' + str(gyro_sensor.angle_and_rate))
        print(getColour(), "Recherche le : ", maze_end_color)

        if (getColour() == maze_end_color):
            speak("resolved labyrinth")
            stop_motors()
            solved = True
            #demitour()
            break

        while distance_sensor.distance_centimeters > 20 and looping:
            looping = not button.backspace
            forward()
        tank_drive.stop()
        

        if distance_sensor.distance_centimeters < 20:
            if cpt_left==0 and cpt_right==0:
                nb = random.randint(1,2)
                if (nb==1) :
                    turnleft()
                    cpt_left+=1
                if (nb==2): 
                    turnright()
                    cpt_right+=1
            else:
                if cpt_left ==1 :
                    turnright()
                elif cpt_right ==1 :
                    turnleft()
                else:
                    cpt_left, cpt_right = 0,0
            stop_motors()
                    
        stop_motors()
    tank_drive.stop()
    time.sleep(0.7)
    speak('Hello, I am E V 3 ' + host_letter + '!')
    #spkr.speak("i've stopped")
    #while not e_stop.value():
     #   distance = distance_sensor.value()/10
     #   while distance <= 20:
     #       tank_drive.on_for_seconds(0, -75, 1)
     #       tank_drive.on_for_seconds()
    #speak("i've reversed")
    #time.sleep(5)
###
# End of the main


## execute the code inside the if statement only when the program 
## is executed directly by the Python-interpreter
## when this module is called, it starts the main function
if __name__ == "__main__":
    # checking the value of the __name__ variable
    main()
