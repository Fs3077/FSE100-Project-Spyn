#!/usr/bin/env pybricks-micropython
# main.py
import socket
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.ev3devices import TouchSensor
from pybricks.tools import wait
import sys

# Initialize EV3 components
ev3 = EV3Brick()
left_motor = Motor(Port.C)
right_motor = Motor(Port.D)
# weapon = Motor(Port.A)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

touch = TouchSensor(Port.S1)

while True:
    ev3.speaker.beep(frequency=500,duration=500)
    if touch.pressed():
        sys.exit()
    wait(10)


# Server configuration
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
