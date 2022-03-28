#!/usr/bin/env python3

import os      # to set font
import time    # to use sleep()
import socket  # to get host name
from ev3dev2.sound   import Sound
from ev3dev2.display import Display
from ev3dev2.button  import Button
from ev3dev2.led     import Leds
from ev3dev2.motor   import MoveSteering, MediumMotor
from ev3dev2.motor   import OUTPUT_A, OUTPUT_D
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

# === Various functions to simplify calls ============================

def clear_display(display):
    display.clear()
    display.update()

def print_display(display, text):
    # using display.text_grid(text, ...) instead of print(test)
    display.text_grid(text, True, 0, 10) # clear screen, 11th row / 22
    display.update()

def show_image(display, name):
    """ Print on the display the image of given name. """
    display.image.paste( Image.open('/home/robot/images/'+name+'.bmp'),
                         (0, 0) )
    display.update()

def set_colors(leds, left_color, right_color):
    """ Change the leds colors to those given. """
    leds.set_color('LEFT',  left_color)
    leds.set_color('RIGHT', right_color)
    
def wait_for_any_release(button):
    """ Wait for any button to be released. """
    button.wait_for_released([ 'backspace', 'up', 'down',
                               'left', 'right', 'enter' ])
    
# === Checking sound and text to speach convertor ====================

def intro(noisy, sound, display, tune = False):
    """ Checking sound (song & text to speach convertor)
    and display (clear & . """
    show_image(display, 'EV3')
    if (noisy):
        host_letter = socket.gethostname()[4]
        sound.speak('Hello, I am E V 3 ' + host_letter + '!')
    show_image(display, 'Neutral')

    # Star Wars' first notes (from ev3dev-lang.readthedocs.io)
    if (noisy and tune):
        sound.play_song(( ('D4', 'e3'), ('D4', 'e3'), ('D4', 'e3'),
                          ('G4', 'h'),  ('D5', 'h'),
                          ('C5', 'e3'), ('B4', 'e3'), ('A4', 'e3'), 
                          ('G5', 'h'),  ('D5', 'q'),  
                          ('C5', 'e3'), ('B4', 'e3'), ('A4', 'e3'), 
                          ('G5', 'h'),  ('D5', 'q'),  
                          ('C5', 'e3'), ('B4', 'e3'),
                          ('C5', 'e3'), ('A4', 'h.') ))
    return sound

# === Checking motors and sensors ====================================

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

def medium_motor_check(noisy, sound, display, button): #--------------
    med_motor = MediumMotor()
    if (noisy):  sound.speak('Checking Medium Motor!')
    speed       = 50
    orientation = 0
    looping     = True
    while (looping):
        # display state (speed & steer)
        print_display(display,  'Motor''s orientation = '
                      + str(orientation) )
        # wait for a button to be pressed
        while ( not button.any() ):  time.sleep(0.1)
        if (looping):  # otherwise
            if   (button.down):
                med_motor.on_for_degrees(speed, -90 - orientation)
                orientation = -90
            elif (button.up):
                med_motor.on_for_degrees(speed, 90 - orientation)
                orientation = 90
            elif (button.left):
                if (orientation > -90):
                    med_motor.on_for_degrees(speed, -30)
                    orientation -= 30
            elif (button.right):
                if (orientation <  90):
                    med_motor.on_for_degrees(speed, 30)
                    orientation += 30
            else: # center button at a stop quits the loop
                if (orientation == 0): looping = False
                else:  # otherwise stops the motors
                    med_motor.on_for_degrees(speed, - orientation)
                    orientation = 0
        wait_for_any_release(button)
        med_motor.off()

def US_sensor_check(noisy, sound, display, button): #-----------------
    us_sensor = UltrasonicSensor()
    if (noisy):  sound.speak('Checking US Sensor!')
    while (not button.enter):
        dist = us_sensor.distance_centimeters
        print_display(display,  'Distance clear: ' + str(dist) )
        time.sleep(0.5)  # Slow down the loop

def color_sensor_check(noisy, sound, display, button): #--------------
    color_sensor = ColorSensor()
    if (noisy):
        sound.speak('Checking Color Sensor!')
        sound.speak('Do you want to calibrate it?')
    print_display(display,
                  'Calibration? (right = yes, left = reset, rest = no.)' )
    # wait for a button to be pressed
    while ( not button.any() ):  time.sleep(0.1)
    if (button.right):
        show_image( display, 'Hourglass 0' )
        if (noisy):  sound.speak('Calibration!')
        # calibrate_white often generate a division by zero exception
        # and sometimes set incorrect values for max
        not_calibrated = True
        while (not_calibrated):
            try:
                color_sensor.calibrate_white()
                # not good if one of the max is zero
                not_calibrated = ( (color_sensor.red_max == 0) 
                                   or (color_sensor.green_max == 0)
                                   or (color_sensor.blue_max == 0) )
            except:
                not_calibrated = True
        clear_display(display)
    elif (button.left):
          color_sensor.red_max = 300
          color_sensor.green_max = 300
          color_sensor.blue_max = 300
    while (not button.enter):
        rgb_color = color_sensor.rgb
        print_display(display,  'Color detected: ' + str(rgb_color) )
        if (color_sensor.color != 0):
            sound.speak('Color detected is '
                        + color_sensor.color_name)
        time.sleep(0.5)  # Slow down the loop

def gyro_sensor_check(noisy, sound, display, button): #---------------
    gyro_sensor = GyroSensor()
    if (noisy):  sound.speak('Checking Gyro Sensor!')
    show_image( display, 'Warning' )
    if (noisy):  sound.speak('Calibration, do not move me!')
    gyro_sensor.calibrate()
    clear_display(display)
    while (not button.enter):
        values = gyro_sensor.angle_and_rate
        print_display(display,  'Angle ' + str(values[0])
                      + '°, rate ' + str(values[1]) + '°/s' )
        time.sleep(0.5)  # Slow down the loop

def touch_sensor_check(noisy, sound, display, button): #--------------
    touch_sensor = TouchSensor()
    if (noisy):  sound.speak('Checking Touch Sensor!')
    state = 0
    while (not button.enter):
        show_image( display, 'Dots ' + str(state) )
        if (touch_sensor.is_pressed):
            if (state == 3):  state = 0
            else:             state += 1
            touch_sensor.wait_for_released()

def motor_sensor_check(noisy, sound, display, button, choice): #------
    """ Select the motor or sensor check according to choice. """
    clear_display(display)
    # no switch/case in Python
    if   (choice == 0):
        large_motor_check(noisy, sound, display, button)
    elif (choice == 1):
        medium_motor_check(noisy, sound, display, button) 
    elif (choice == 2):
        US_sensor_check(noisy, sound, display, button) 
    elif (choice == 3):
        color_sensor_check(noisy, sound, display, button) 
    elif (choice == 4):
        gyro_sensor_check(noisy, sound, display, button)
    else:  touch_sensor_check(noisy, sound, display, button)
    clear_display(display)
                
# === Main function and module call ==================================

# Using a main function is cleaner than having global variables
# and function calls.

def main(noisy = True):
    """Select which test to start using the box buttons."""
    sound   = Sound()
    display = Display()
    looping = True
    choice  = 0
    button  = Button()
    leds    = Leds()
    colors  = ['GREEN', 'YELLOW', 'AMBER', 'ORANGE', 'RED', 'BLACK']
    img_nms = [ 'Large motor', 'Medium motor', 'US sensor',
                'Color sensor', 'Gyro sensor', 'Touch sensor' ]
    max_choice = len(colors) - 1

    os.system('setfont Lat15-TerminusBold14')
    intro(noisy, sound, display)
    while (looping):
        # display choice (image and leds' color)
        show_image(display, img_nms[choice])
        color = colors[choice]
        set_colors(leds, color, color)
        # wait for a button to be pressed
        while ( not button.any() ):  time.sleep(0.1)
        # upper right button (backspace) quits the loop
        looping = not button.backspace
        if (looping):  # otherwise
            # down or left decrease choice (cycling)
            if (button.down or button.left):
                if (choice > 0):
                    choice -= 1
                else:
                    choice = max_choice
            # up or right increase choice (cycling)
            elif (button.up or button.right):
                if (choice < max_choice):
                    choice += 1
                else:
                    choice = 0
            else:  # enter select the check
                button.wait_for_released('enter')
                motor_sensor_check(noisy, sound, display, button, 
                                   choice)

            # Avoid taking twice the same action
            wait_for_any_release(button) 

# When this module is called, it starts the main function.
if __name__ == "__main__":
    main()
