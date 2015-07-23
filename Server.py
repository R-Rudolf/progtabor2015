__author__ = 'Rudolf'

import time
import zmq
import json
from scipy import misc
import numpy as np
import math
import random
import matplotlib.pyplot as plt

MAX_PIXEL_VALUE = 255
NUM_OF_DRONES   = 3
STARTING_POINT  = [256, 256]
MAX_SPEED = 10
MAX_ACC   = 1
MAX_TURN  = 10*math.pi/180

IMG_WIDTH  = 511
IMG_HEIGHT = 511

def show(m):
    plt.imshow(m)
    plt.set_cmap('gray')
    plt.show()

def limit(value, limit):
    if value > 0 and value > limit:
            value = limit
    elif value < -limit:
        value = -limit

    return value

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Drone:

    def __init__(self,origo, angle):
        self.x = origo[0]
        self.y = origo[1]
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

    def drawDrone(self, img_orig):
        img = img_orig[:]
        len = 20
        p = Point(math.floor(self.x), math.floor(self.y))

        def limit_p(p):
            p.x = limit(p.x, IMG_WIDTH) if p.x > 0 else 0
            p.y = limit(p.y, IMG_HEIGHT) if p.y > 0 else 0
            return p

        # Horizontal line
        p.x -= int(len/2)
        p = limit_p(p)
        for i in range(len):
            img[int(p.x)][int(p.y)] = 1
            p.x += 1
            p = limit_p(p)

        # Vertical line
        p.x -= int(len/2)
        p.y -= int(len/2)
        p = limit_p(p)
        for i in range(len):
            img[int(p.x)][int(p.y)] = 1
            p.y += 1
            p = limit_p(p)

        # Orientation
        p.y -= int(len/2)
        p = limit_p(p)
        for i in range(int(len*1.25)):
            img[int(p.x)][int(p.y)] = 1
            p.y += math.cos(self.angle)
            p.x += math.sin(self.angle)
            p = limit_p(p)


        # Orientation
        p.y -= int(len/2)
        p = limit_p(p)
        dist = self.measure(img_orig)
        for i in range(int(len*1.25)):
            img[int(p.x)][int(p.y)] = 1
            p.y += math.cos(self.angle)
            p.x += math.sin(self.angle)
            p = limit_p(p)

        return img

    def measure(self, img):
        p = Point(self.x, self.y)

        def go(p, angle):
            p.y += math.cos(angle)
            p.x += math.sin(angle)
            return p

        def check(p, img):
            return img[math.floor(p.x)][math.floor(p.y)] > 0

        while True:
            if (math.floor(p.x) > 0 and math.floor(p.x) < IMG_WIDTH) or \
            (math.floor(p.y) > 0 and math.floor(p.y) < IMG_HEIGHT):
                break # Out of image

            if check(p, img):
                break # Cave wall

            p = go(p, self.angle)

        return math.sqrt((p.x-self.x)**2 + (p.y-self.y)**2)

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

    d = Drone(STARTING_POINT, 0)
    cave_draw = cave[:]

    for i in range(10):
        tmp = d.drawDrone(cave)
        d.setMovement(5*(math.pi/180), 5)
        d.go()
        for i in range(len(tmp)):
            for j in range(len(tmp[i])):
                cave_draw[i][j] +=

    cave_draw = d.drawDrone(cave)

    show(cave)

    exit()

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