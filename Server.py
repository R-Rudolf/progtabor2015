__author__ = 'Rudolf'

import time
import zmq
import json
from scipy import misc
import numpy as np
import math
import random

MAX_PIXEL_VALUE = 255
NUM_OF_DRONES   = 3
STARTING_POINT  = [256, 256]
MAX_SPEED = 3
MAX_ACC   = 0.2
MAX_TURN  = 10*math.pi/180

IMG_WIDTH  = 511
IMG_HEIGHT = 511

def limit(value, limit):
    if value > 0 and value > limit:
            value = limit
    elif value < -limit:
        value = -limit
        
    return value

class Drone:

    def __init__(self, angle):
        self.x = STARTING_POINT[0]
        self.y = STARTING_POINT[1]
        self.angle = angle
        self.speed = 0
        self.acc   = 0
        self.turn  = 0

    def setMovement(self, turn, acc):
        self.acc  = limit(acc, MAX_ACC)
        self.turn = limit(turn, MAX_TURN)

    def go(self):
        self.angle += self.turn

        self.speed = limit(self.acc+self.speed, MAX_SPEED)

        self.y += math.cos(self.angle)*self.speed
        self.x += math.sin(self.angle)*self.speed

    def measure(self, image):
        return 5

class ClientSession:

    def __init__(self, name, image):
        self.name = name
        self.image = image[:]
        self.drones = [Drone(random.randrange(0, 360)/(math.pi*2))
                       for i in range(NUM_OF_DRONES)]


def saveImage(image, filename):
    #image = json.loads(image_json)
    image_array = []
    for line in image:
        new_line = []
        for pixel in line:
            #new_line.append([pixel*MAX_PIXEL_VALUE, pixel*MAX_PIXEL_VALUE, pixel*MAX_PIXEL_VALUE])
            new_line.append(pixel*MAX_PIXEL_VALUE)
        image_array.append(new_line)

    misc.toimage(np.array(image_array)).save(filename)

def loadImage(filename):
    image_array = misc.imread(filename)
    image = []
    #MAX_PIXEL_VALUE = image_array.max()

    for line in image_array:
        new_line = []
        for pixel in line:
            avg = 100*(int(pixel[0])+int(pixel[1])+int(pixel[2]))/(3*MAX_PIXEL_VALUE)
            new_line.append((round(avg, -1)))
        image.append(new_line)

    return image#json.dumps(image)

def main():
    cave = loadImage("cave-system.png")

    print "Start ZMQ response server."

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    while True:
        #  Wait for next request from client
        message = socket.recv()
        print("Received request: %s" % message)

        #  Do some 'work'
        time.sleep(1)

        #  Send reply back to client
        socket.send(b"World")
        print("Sended response: World")


if __name__ == "__main__":
    main()