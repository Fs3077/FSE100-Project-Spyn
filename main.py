#!/usr/bin/env pybricks-micropython
# main.py
import socket
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Color
from pybricks.robotics import DriveBase
from pybricks.tools import wait
import sys

# Initialize EV3 components
ev3 = EV3Brick()
left_motor = Motor(Port.C)
right_motor = Motor(Port.D)
touch = TouchSensor(Port.S1)
colorSens = ColorSensor(Port.S2)
# weapon = Motor(Port.A)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)
ev3.speaker.set_volume(10)

greentriggered = False
redtriggered = False
bluetriggered = False

# Server configuration
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 12345))
server_socket.listen(1)
print("Waiting for connection...")
client_socket, address = server_socket.accept()
print("Connected to {}".format(address))

ev3.speaker.beep(frequency=500, duration=-1)


try:
    while True:

        command = client_socket.recv(2).decode()
        # if not command:
        #    break
        
        color = colorSens.color()
        if color == Color.RED and not redtriggered:
            redtriggered = True
            robot.stop()
            wait(1000)
            

        if color == Color.BLUE and not bluetriggered:   
            bluetriggered = True         
            robot.stop()
            ev3.speaker.beep(frequency=1000, duration=500)
            wait(100)
            ev3.speaker.beep(frequency=1000, duration=500)
            wait(500)
            ev3.speaker.beep(frequency=500, duration=-1)
            

        if color == Color.GREEN and not greentriggered:
            greentriggered = True
            robot.stop()
            ev3.speaker.beep(frequency=1000, duration=500)
            wait(100)
            ev3.speaker.beep(frequency=1000, duration=500)
            wait(100)
            ev3.speaker.beep(frequency=1000, duration=500)
            wait(500)
            ev3.speaker.beep(frequency=500, duration=-1)

        # EV3 Connections Code
        if touch.pressed():
            client_socket.close()
            server_socket.close() 
            sys.exit

        key, action = command[0], command[1]
        if action == "d":  # Key press
            if key == "w":
                robot.drive(900, 0)  # Move forward
            elif key == "s":
                robot.drive(-900, 0)  # Move backward
            elif key == "a":
                robot.drive(0, -450)  # Turn left
            elif key == "d":
                robot.drive(0, 450)  # Turn right
            #elif key == "f":
            #    weapon.run(1000)  # Spin weapon motor at max speed
        elif action == "u":  # Key release
            if key in ("w", "a", "s", "d"):
                robot.stop()  # Stop the robot on key release
            #elif key == "f":
            #    weapon.stop()  # Stop the weapon motor on key release

        


finally:
    client_socket.close()
    server_socket.close()


