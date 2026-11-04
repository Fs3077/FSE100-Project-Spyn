#!/usr/bin/env pybricks-micropython
import socket
import sys
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Color
from pybricks.robotics import DriveBase
from pybricks.tools import wait

ev3 = EV3Brick()
left_motor = Motor(Port.C)
right_motor = Motor(Port.D)
touch = TouchSensor(Port.S1)
colorSens = ColorSensor(Port.S2)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)
ev3.speaker.set_volume(10)


CONFIRM_COUNT = 5
current_candidate = None
candidate_count = 0
triggered = {Color.RED: False, Color.GREEN: False, Color.BLUE: False}      

def classify():
    r, g, b = colorSens.rgb()

    if r > 25 and r > g * 2 and r > b * 2:
        return Color.RED
    if b > 20 and b > g * 1.4 and b > r * 2:
        return Color.BLUE
    if g > 20 and g > b * 1.05 and g > r * 2:
        return Color.GREEN
    
def handle_color(c):
    robot.stop()
    ev3.speaker.beep(frequency=0, duration=0)
    if c == Color.RED:
        print("Red detected")
        wait(1000)
    elif c == Color.BLUE:
        print("Blue detected")
        ev3.speaker.beep(frequency=1000, duration=500)
        wait(100)
        ev3.speaker.beep(frequency=1000, duration=500)
        wait(500)
    elif c == Color.GREEN:
        print("Green detected")
        for _ in range(3):
            ev3.speaker.beep(frequency=1000, duration=500)
            wait(100)
        wait(400)
    ev3.speaker.beep(frequency=500, duration=-1)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 12345))
server_socket.listen(1)
print("Waiting for connection...")
client_socket, address = server_socket.accept()
print("Connected to {}".format(address))
client_socket.setblocking(False)

ev3.speaker.beep(frequency=500, duration=-1)

buf = ""
try:
    while True:
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
            if action == "d":
                if key == "w":
                    robot.drive(900, 0)
                elif key == "s":
                    robot.drive(-900, 0)
                elif key == "a":
                    robot.drive(0, -450)
                elif key == "d":
                    robot.drive(0, 450)
            elif action == "u":
                if key in ("w", "a", "s", "d"):
                    robot.stop()
                
        seen = classify()
        if seen == current_candidate:
            candidate_count += 1
        else:
            current_candidate = seen
            candidate_count = 1

        if (seen is not None and candidate_count >= CONFIRM_COUNT and not triggered[seen]):
            triggered[seen] = True
            handle_color(seen)

        if touch.pressed():
            break

        wait(10)
finally:
    robot.stop()
    client_socket.close()
    server_socket.close()