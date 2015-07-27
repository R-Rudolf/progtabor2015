__author__ = 'Rudolf'

import time
import json
import math
import random
import traceback
import os
import sys
import zmq
import matplotlib.pyplot as plt
from PIL import Image
import threading

from Drone import Drone
from Level import Level
sys.path.append("Webserver/")
from WebServer import WebServer


TIMEOUT = 60*60*2 # Two hours
MAX_PIXEL_VALUE = 255
SECRET_LEN = 10
SECRET_CHARS = "QWERTYUPASDFGHJKLMNBVCXZqwertyuiopasdfghjkzxcvbnm123456789"
FINISHED_LEVELS = [1]

teams = {}

def main():
    web_server = WebServer(teams)
    web_server.start()

    print "Start ZMQ response server."
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    while True:
        print "Waiting for next request..."
        message = socket.recv()
        max = len(message)
        max = 150 if max > 150 else max
        print "Request: ", message[:max]

        answer = processRequest(message)

        socket.send(answer)
        print "\tResponse: ", answer

    web_server.stop()

def processRequest(req_msg):
    if req_msg == b"Hello":
        return b"World!"

    try:
        req = json.loads(req_msg)
    except:
        return "!Json formatting error!"

    if not req.has_key("action"):
        return "!No action field!"
    if not req.has_key("team_name"):
        return "!No team_name field!"

    action = req["action"]

    if not handlers.has_key(action):
        return "!Not valid action!"

    if action != "getKey":
        team = req["team_name"]
        if team not in teams.keys():
            return "!Not registered team!"
        if req["secret"] != teams[team]["secret"]:
            return "!Secret not valid!"
        teams[team]["ts"] = time.time()

    try:
        answer = handlers[action](req)
    except:
        print "Error:"
        traceback.print_exc()
        return "!Something went wrong executing the action."

    return answer


def show(m):
    plt.imshow(m)
    plt.set_cmap('gray')
    plt.show()

def saveImage(image, filename):
    image_array = []

    for line in image:
        new_line = []
        for pixel in line:
            new_line.append(pixel*MAX_PIXEL_VALUE)
        image_array.append(new_line)
    Image.fromarray(image_array).save(filename)


def loadImage(filename):
    img = Image.open(filename)
    image_array =  list(img.getdata())
    image = []

    for i in range(512):
        new_line = []
        for j in range(512):
            pixel = image_array[i*512+j]
            avg = 100*(int(pixel[0])+int(pixel[1])+int(pixel[2]))/(3*MAX_PIXEL_VALUE)
            new_line.append((round(avg, -1)))
        image.append(new_line)

    return image


def mapChek(map, width, height):
    if len(map) != width:
        print "width: ", len(map)
        return "!Wrong formatted map: Width problem!"

    if len(map[0]) != height:
        print "height: ", len(map[0])
        return "!Wrong formatted map: Height problem!"
    try:
        for line in map:
            for pixel in line:
                val = int(pixel)
                if val < 0 or val > 100:
                    raise ValueError
    except ValueError:
        return "!Not valid values in sent map!"

    return "OK"


"""
teams = {
    "team_name1": {
        "secret" : "dsds",
        "ts": 155475544.544645,
        "drones": [drone1, drone2 ],
        "score_ts": 155445448.545767,
        "ticks": 0,
        "level": level
        "sended_map": [[], [], []]
    }
}
"""

def getKey_handler(req):
    print "getKey handler triggered!"
    team = req["team_name"]

    secret = ""
    for i in range(SECRET_LEN):
        secret += random.choice(SECRET_CHARS)

    if teams.has_key(team):
        print "Team '%s' got new key!" % team
    else:
        print "Team '%s' registered!" % team

    teams[team] = {
        "secret": secret,
        "ts": time.time()
    }

    answer = {
        "secret": secret
    }
    return json.dumps(answer)


def initLevel_handler(req):
    try:
        level_index = int(req["level"])
    except ValueError:
        return "!Level value not a number!"

    lvl_filename = '../levels/level_%d.json'%(level_index)
    if os.path.exists(lvl_filename) and \
        level_index in FINISHED_LEVELS:
            level = Level(lvl_filename)
    else:
        return "!Level not yet implemented!"

    drones = []
    names = random.sample(DRONE_NAMES, level.number_of_drones)

    for name in names:
        angle = random.randrange(0, 360)/(math.pi*2)
        drone = Drone(level, angle, name)
        drones.append(drone)

    team = teams[req["team_name"]]
    team["drones"] = drones
    team["score_ts"] = time.time()
    team["ticks"] = 0
    team["level"] = level

    answer = {
        "drones": names
    }
    return json.dumps(answer)

def getScore_handler(req):
    map = req["map"]
    team = teams[req["team_name"]]
    level = team["level"]

    map_validity = mapChek(map, level.img_width,
                           level.img_height)
    if map_validity != "OK":
        return map_validity

    team["sended_map"] = map
    score = team["level"].score(map)
    team["score"] = score

    answer = {
        "score": score
    }
    return json.dumps(answer)

def moveDrone_handler(req):
    team = teams[req["team_name"]]
    drone_name = req["drone"]

    drone = None
    for item in team["drones"]:
        if item.name == drone_name:
            drone = item
    if drone == None:
        return "!Drone with the given name not found!"

    try:
        acc = float(req["acceleration"])
    except ValueError:
        return "!Not valid acceleration value (float)!"

    try:
        turn = float(req["turn"])
    except ValueError:
        return "!Not valid turn value (float)!"

    drone.setMovement(turn, acc)

    answer = {
        "life": drone.life,
        "x": drone.x,
        "y": drone.y,
        "angle": drone.angle,
        "acceleration": drone.acc,
        "speed": drone.speed
    }

    return json.dumps(answer)

def getMeasure_handler(req):
    team = teams[req["team_name"]]
    drone_name = req["drone"]

    drone = None
    for item in team["drones"]:
        if item.name == drone_name:
            drone = item
    if drone == None:
        return "!Drone with the given name not found!"

    measure = drone.measure()
    answer = {
        "result": measure
    }

    return json.dumps(answer)

def tick_handler(req):
    team = teams[req["team_name"]]

    for drone in team["drones"]:
        if drone.life is 1:
            drone.go()

    team["ticks"] += 1

    answer = {
        "ticks": team["ticks"]
    }
    return json.dumps(answer)

handlers = {
    "getKey": getKey_handler,
    "initLevel": initLevel_handler,
    "moveDrone": moveDrone_handler,
    "getMeasure": getMeasure_handler,
    "tick": tick_handler,
    "getScore": getScore_handler
}

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