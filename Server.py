__author__ = 'Rudolf'

import time
import zmq
import json
import numpy as np
import math
import random
import matplotlib.pyplot as plt
#from scipy.misc import imread, toimage

from PIL import Image

TIMEOUT = 60*60*2 # Two hours

MAX_PIXEL_VALUE = 255
NUM_OF_DRONES   = 3
STARTING_POINT  = [256, 256]
MAX_SPEED = 10
MAX_ACC   = 1
MAX_TURN  = 10*math.pi/180
CAVE_MAP = [[1, 2], [1, 2]]

SECRET_LEN = 10
SECRET_CHARS = "QWERTYUPASDFGHJKLMNBVCXZqwertyuiopasdfghjkzxcvbnm123456789"
teams = {}

IMG_WIDTH  = 512
IMG_HEIGHT = 512

def show(m):
    plt.imshow(m)
    plt.set_cmap('gray')
    plt.show()

def saveImage(image, filename):
    image_array = []

    for line in image:
        new_line = []
        for pixel in line:
            #new_line.append([pixel*MAX_PIXEL_VALUE, pixel*MAX_PIXEL_VALUE, pixel*MAX_PIXEL_VALUE])
            new_line.append(pixel*MAX_PIXEL_VALUE)
        image_array.append(new_line)
    Image.fromarray(image_array).save(filename)
    #toimage(np.array(image_array)).save(filename)

def loadImage(filename):
    #image_array = imread(filename)
    img = Image.open(filename)
    image_array =  list(img.getdata())
    image = []
    # MAX_PIXEL_VALUE = image_array.max()

    for i in range(512):
        new_line = []
        for j in range(512):
            pixel = image_array[i*512+j]
            avg = 100*(int(pixel[0])+int(pixel[1])+int(pixel[2]))/(3*MAX_PIXEL_VALUE)
            new_line.append((round(avg, -1)))
        image.append(new_line)

    return image

def limit(value, limit):
    if value > 0 and value > limit:
            value = limit
    elif value < -limit:
        value = -limit

    return value

class Point:
    def limit(self):
        self.x = limit(self.x, IMG_WIDTH) if self.x > 0 else 0
        self.y = limit(self.y, IMG_HEIGHT) if self.y > 0 else 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

class Drone:

    def loadDrone(self, data_json):
        data = json.loads(data_json)
        self.x = data.x
        self.y = data.y
        self.angle = data.angle
        self.speed = data.speed
        self.acc   = data.acc
        self.turn  = data.turn
        self.name = data.name
        self.life = data.life

    def saveDrone(self):
        data = {
            "name": self.name,
            "life": self.life,
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
            "turn": self.turn,
            "acc": self.acc,
            "speed": self.speed
        }
        return json.dumps(data)

    def __init__(self, origo=STARTING_POINT, angle=0, name="Nameless"):
        self.x = origo[0]
        self.y = origo[1]
        self.angle = angle
        self.speed = 0
        self.acc   = 0
        self.turn  = 0
        self.name = name
        self.life = 1

    def setMovement(self, turn, acc):
        if self.life:
            self.acc  = limit(acc, MAX_ACC)
            self.turn = limit(turn, MAX_TURN)

    def crashTest(self, map):
        point = map[int(self.x)][int(self.y)]
        return point > 0

    def go(self, map):
        self.angle += self.turn
        self.speed += self.acc
        self.speed = limit(self.acc+self.speed, MAX_SPEED)

        self.y += math.cos(self.angle)*self.speed
        self.x += math.sin(self.angle)*self.speed

        if self.crashTest(map):
            self.life = 0
            self.speed = 0

    def drawDrone(self, img_orig, img_measure=None):
        img = img_orig[:]
        len = 0
        p = Point(math.floor(self.x), math.floor(self.y))
        p_orig = Point(p.x, p.y)
        img_measure = img_orig if img_measure == None else img_measure


        # Horizontal line
        p.x -= int(len/2)
        p.limit()
        for i in range(len):
            img[int(p.x)][int(p.y)] = 1
            p.x += 1
            p.limit()

        # Vertical line
        p = Point(p_orig.x, p_orig.y)
        p.y -= int(len/2)
        p.limit()
        for i in range(len):
            img[int(p.x)][int(p.y)] = 1
            p.y += 1
            p.limit()

        # Orientation
        p = Point(p_orig.x, p_orig.y)
        for i in range(int(20)):
            img[int(p.x)][int(p.y)] = 1
            p.y += math.cos(self.angle)
            p.x += math.sin(self.angle)
            p.limit()
        p = Point(p_orig.x, p_orig.y)
        for i in range(int(20)):
            img[int(p.x)][int(p.y)] = 1
            p.y -= math.cos(self.angle)
            p.x -= math.sin(self.angle)
            p.limit()

        # Orientation
        p = Point(p_orig.x, p_orig.y)
        for i in range(int(10)):
            img[int(p.x)][int(p.y)] = 1
            p.y += math.cos(self.angle+math.pi/2)
            p.x += math.sin(self.angle+math.pi/2)
            p.limit()
        p = Point(p_orig.x, p_orig.y)
        for i in range(int(10)):
            img[int(p.x)][int(p.y)] = 1
            p.y -= math.cos(self.angle+math.pi/2)
            p.x -= math.sin(self.angle+math.pi/2)
            p.limit()


        # Measure
        p = Point(p_orig.x, p_orig.y)
        dist = self.measure(img_measure)
        print "dist: ", dist
        for i in range(int(dist)):
            img[int(p.x)][int(p.y)] = 0.5
            p.y += math.cos(self.angle)
            p.x += math.sin(self.angle)
            #p = limit_p(p)

        return img

    def measure(self, img):
        p = Point(self.x, self.y)

        def go(p, angle):
            p.y += math.cos(angle)
            p.x += math.sin(angle)
            p.limit()
            return p

        def check(p, img):
            return img[int(math.floor(p.x))][int(math.floor(p.y))] > 0

        while True:
            if (int(math.floor(p.x)) < 0 or int(math.floor(p.x)) >= IMG_WIDTH) or \
            (int(math.floor(p.y)) < 0 or int(math.floor(p.y)) >= IMG_HEIGHT):
                print "out of image"
                break # Out of image

            if not check(p, img):
                print "cave"
                break # Cave wall

            p = go(p, self.angle)

        return math.sqrt((p.x-self.x)**2 + (p.y-self.y)**2)


"""
request:

 - getKey(teamName)
    returns a secret key, which is needed
    for the other requests

 - initLevel(stage)
    resets drones, maps, timers, sets map to the given level
    return a the list of drone names

 - getScore(map)
    evaluates sended map and original map similarity
    only once per minute can be evaluated per user!
    returns last evaluated score and time to new access

 - tick()
    all drones: turn, accelerate, go ahead
    increment clock
    check Drone crash --> removes from list

 - moveDrone(name, acc, angle)
    returns actual datas (life, cooordinates, angle, acc, speed)
    if already crashed life is 0

 - getMeasure(index)
    return measurement of the indexed drone

"""


def getKey_handler(req):
    print "getKey handler triggered!"
    team = req["team_name"]

    secret = ""
    for i in range(SECRET_LEN):
        secret += random.choice(SECRET_CHARS)

    if teams.has_key(team):
        print "Team got new key!"

    print "team name: ", team
    print "secret key: ", secret
    teams[team] = {"secret": secret, "ts": time.time()}

    answer = {"secret": secret}
    return json.dumps(answer)

def initLevel_handler(req):
    try:
        level = int(req["level"])
    except ValueError:
        return "Level value not a number!"

    if level != 1:
        return "Level not yet implemented!"

    drones = []
    names = random.sample(DRONE_NAMES, NUM_OF_DRONES)

    for i in range(NUM_OF_DRONES):
        angle = random.randrange(0, 360)/(math.pi*2)
        drones.append(Drone(STARTING_POINT,
                            angle, names[i]))

    teams[req["team_name"]]["drones"] = drones
    teams[req["team_name"]]["orig_map"] = CAVE_MAP

    return json.dumps(names)

def score(orig, sended):
    max = IMG_WIDTH * IMG_HEIGHT
    error = 0

    for i in range(IMG_HEIGHT):
        for j in range(IMG_WIDTH):
            dev = (orig[i][j] - sended[i][j])
            error += math.sqrt(dev**2)

    return 100 - 100*(error/max)

def getScore_handle(req):
    map = req["map"]
    if len(map) != IMG_WIDTH or\
        len(map) != IMG_WIDTH+1:
        return "Wrong formatted map!"

    if len(map[0]) != IMG_HEIGHT or\
        len(map[0]) != IMG_HEIGHT+1:
        return "Wrong formatted map!"

    team = teams[req["team_name"]]
    team["sended_map"] = map

    return score(team["orig_map"], map)

handlers = {
    "getKey": getKey_handler,
    "initLevel": initLevel_handler
}

def processRequest(req_msg):
    if req_msg == b"Hello":
        return b"World!"

    try:
        req = json.loads(req_msg)
    except:
        return "Json formatting error!"

    if not req.has_key("action"):
        return "No action field!"
    if not req.has_key("team_name"):
        return "No team_name field!"

    action = req["action"]

    if not handlers.has_key(action):
        return "Not valid action!"

    if action != "getKey":
        team = req["team_name"]
        if team not in teams.keys():
            return "Not registered team!"
        if req["secret"] != teams[team]["secret"]:
            return "Secret not valid!"
        teams[team]["ts"] = time.time()

    #try:
    answer = handlers[action](req)
    #except:
    #    return "Something went wrong executing the action."

    return answer


def main():

    global  CAVE_MAP

    CAVE_MAP = loadImage("cave-system.png")

    d = Drone(STARTING_POINT, 0)
    cave_draw = CAVE_MAP[:]

    for i in range(30):
        cave_draw = d.drawDrone(cave_draw, CAVE_MAP)
        d.setMovement(5*(math.pi/180), 5)
        d.go(CAVE_MAP)

    cave_draw = d.drawDrone(cave_draw, CAVE_MAP)

    show(cave_draw)
    saveImage(cave_draw, "draw_route.png")

    exit()

    print "Start ZMQ response server."

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5556")

    while True:
        #  Wait for next request from client
        print "Waiting for next request..."
        message = socket.recv()
        print "Request: ", message

        answer = processRequest(message)

        #  Send reply back to client
        socket.send(answer)
        print "\tResponse: ", answer


DRONE_NAMES = [
    "Lucky",
    "Oreo",
    "Heisenberg",
    "Sweetie",
    "Beloved",
    "Babe",
    "Pumpkin",
    "Sweetheart",
    "Muffin",
    "Baboo",
    "Bambi",
    "Beautiful",
    "Big_Boy",
    "Big_Daddy",
    "Sailor",
    "Rosie",
    "Simba",
    "Sleeping_Beauty",
    "Tarzan",
    "Tinkerbell",
    "Twinkle",
    "Tiger",
    "Papito",
    "Peanut",
    "Perfect",
    "Old_Lady",
    "Prince_Charming",
]

if __name__ == "__main__":
    main()