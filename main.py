#!/usr/bin/env pybricks-micropython

# This is the main code for the EV3, haandles basically everything except the manual driving.
# TODO: Add autonomous driving that works with both the color and ultrasonic detection, as well as lift motor capability

# For those reading, PLEASE do not push any changes to github without reviewing them first, especially with AI code!!
# I really don't want to have to hunt a bug through 5 different pushes to main because an AI made a mistake.

import socket
import sys
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Port, Color
from pybricks.robotics import DriveBase
from pybricks.tools import wait


# Setup EV3 brick and devices
ev3 = EV3Brick()
lift_motor = Motor(Port.A)
left_motor = Motor(Port.C)
right_motor = Motor(Port.B)
ultrasonic = UltrasonicSensor(Port.S1)
colorSens = ColorSensor(Port.S2)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)
ev3.speaker.set_volume(10)

# Color detection constants and variables
CONFIRM_COUNT = 5
current_candidate = None
candidate_count = 0
triggered = {Color.RED: False, Color.GREEN: False, Color.BLUE: False, Color.YELLOW: False}      

# Wall detection distance
DISTANCE = 250
# All boolean variables to determine when the bot is in manual or autonomous mode
wait_green = True
to_pickup = False
pick_up = False
to_drop_off = False
drop_off = False
# Prevents the bot from repeatedly stopping at the same red stop sign
red_latched = False
# End the program when the bot is at dropoff
done = False
# Color detection 1, defines the threshold for R G and B.
# This is kinda complicated but it basically just checks using rgb rather than Color.X that is setup in the ev3 code.
# If this needs to be changed, the multipliers are what defines the threshold for each color.
def classify():
    r, g, b = colorSens.rgb()

    if r > 25 and r > g * 2 and r > b * 2:
        return Color.RED
    if b > 20 and b > g * 1.4 and b > r * 2:
        return Color.BLUE
    if g > 20 and g > b * 1.05 and g > r * 2:
        return Color.GREEN
    if r > 25 and g > 20 and r > b * 1.5 and g > b * 1.5:
        return Color.YELLOW
    
def lift_up():
    lift_motor.run(400)

def lift_down():
    lift_motor.run(-400)

def lift_stop():
    lift_motor.stop()


# Color detection 2, handles color when its detected and beeps. The duration=-1 makes it return to the constant tone.
def handle_color(c):
    robot.stop()
    ev3.speaker.beep(frequency=0, duration=0)
    if c == Color.RED:
        print("Red detected")
        wait(1000)
        # Implement code to stop the robot entirely
    elif c == Color.BLUE:
        print("Blue detected")
        ev3.speaker.beep(frequency=1000, duration=500)
        wait(100)
        ev3.speaker.beep(frequency=1000, duration=500)
        wait(500)
        # End autonomous driving and switch to manual, then off of autonomous after blue is no longer detected
    elif c == Color.GREEN:
        # Start autonomous driving
        print("Green detected")
        for _ in range(3):
            ev3.speaker.beep(frequency=1000, duration=500)
            wait(100)
        wait(400)
    ev3.speaker.beep(frequency=500, duration=-1)

# Distance detection, stops and checks both sides when detecting a wall then turn to the side with the greatest distance
def navigate_maze():
    distance = ultrasonic.distance()
    if distance > DISTANCE:
        robot.drive(900, 0)
    else:
        robot.stop()
        robot.turn(-90)
        wait(200)
        left_distance = ultrasonic.distance()
        robot.turn(180)
        wait(200)
        right_distance = ultrasonic.distance()
        robot.turn(-90)
        if left_distance <= DISTANCE and right_distance <= DISTANCE:
            robot.turn(180)
        elif left_distance > right_distance:
            robot.turn(-90)
        else:
            robot.turn(90)
        robot.drive(900, 0)

# Server setup, this was in the provided code rather than being custom.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 12345))
server_socket.listen(1)
print("Waiting for connection...")
client_socket, address = server_socket.accept()
print("Connected to {}".format(address))
client_socket.setblocking(False)

# Default beep that plays when the robot is running.
ev3.speaker.beep(frequency=500, duration=-1)

# Driving function with an added buffer to fix color detection not running unless driving.
# Don't really touch this section unless you know what you're doing.
buf = ""
try:
    while not done:
        try:
            data = client_socket.recv(16)
            if data == b"":          
                break
            if data:                 
                buf += data.decode()
        except OSError:
            pass                     

        
        while len(buf) >= 2:
            key, action = buf[0], buf[1]
            buf = buf[2:]
            if pick_up or drop_off:
                if action == "d":
                    if key == "w":
                        robot.drive(900, 0)
                    elif key == "s":
                        robot.drive(-900, 0)
                    elif key == "a":
                        robot.drive(0, -450)
                    elif key == "d":
                        robot.drive(0, 450)
                    elif key == "e":
                        lift_up()
                    elif key == "r":
                        lift_down()
                    elif key == "f": # The f button turns the bot into autonomous mode 
                        robot.stop()
                        lift_stop()            
                        if pick_up:
                            print("Pickup finished!")
                            pick_up = False
                            to_drop_off = True
                        elif drop_off:
                            print("Drop-off finished!")
                            drop_off = False
                            done = True
                elif action == "u":
                    if key in ("w", "a", "s", "d"):
                        robot.stop()
                    elif key in ("e", "r"):
                        lift_stop()
                    
                
        seen = classify()
        if seen == current_candidate:
            candidate_count += 1
        else:
            current_candidate = seen
            candidate_count = 1

         # WAIT FOR GREEN TO START
        if (
            wait_green
            and seen == Color.GREEN
            and candidate_count >= CONFIRM_COUNT
        ):
            wait_green = False
            to_pickup = True

            ev3.speaker.beep(frequency=1000, duration=500)

        # RED STOP SIGNS
        if (
            (to_pickup or to_drop_off)
            and seen == Color.RED
            and candidate_count >= CONFIRM_COUNT
            and not red_latched
        ):
            robot.stop()
            wait(1000)
            red_latched = True
        if seen != Color.RED:
            red_latched = False

        # BLUE PICKUP LOCATION
        if (
            to_pickup
            and seen == Color.BLUE
            and candidate_count >= CONFIRM_COUNT
        ):
            robot.stop()
            lift_stop()
            to_pickup = False
            pick_up = True
            ev3.speaker.beep(frequency=1000, duration=500)

        # YELLOW DROP-OFF LOCATION
        elif (
            to_drop_off
            and seen == Color.YELLOW
            and candidate_count >= CONFIRM_COUNT
        ):
            robot.stop()
            lift_stop()
            to_drop_off = False
            drop_off = True
            ev3.speaker.beep(frequency=1000, duration=500)

        # AUTONOMOUS NAVIGATION
        if to_pickup or to_drop_off:
            navigate_maze()

        wait(10)
finally:
    robot.stop()
    lift_stop()
    client_socket.close()
    server_socket.close()
