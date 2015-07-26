__author__ = 'Rudolf'


import zmq
import json
from PIL import Image
import matplotlib.pyplot as plt
import math

socket = None
team_name = "test"
secret = None

MAX_PIXEL_VALUE = 255
IMG_WIDTH  = 512
IMG_HEIGHT = 512


def show(m):
    plt.imshow(m)
    plt.set_cmap('gray')
    plt.show()


def loadImage(filename):
    img = Image.open(filename)
    image_array = list(img.getdata())
    image = []

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


def drawDrone(drone, img_toDraw, img_orig):
    img = img_toDraw[:]
    size = 20
    p = Point(math.floor(drone["x"]), math.floor(drone["y"]))
    p_orig = Point(p.x, p.y)

    # Orientation
    """
    p.y -= math.cos(drone["angle"])*int(size/2)
    p.x -= math.sin(drone["angle"])*int(size/2)
    p.limit()
    for i in range(size):
        img[int(p.x)][int(p.y)] = 1
        p.y += math.cos(drone["angle"])
        p.x += math.sin(drone["angle"])
        p.limit()
    """
    # Orientation
    """
    size /= 2
    p = Point(p_orig.x, p_orig.y)
    p.y -= math.sin(drone["angle"])*int(size/2)
    p.x -= math.cos(drone["angle"])*int(size/2)
    p.limit()
    for i in range(size):
        img[int(p.x)][int(p.y)] = 100
        p.y += math.sin(drone["angle"])
        p.x += math.cos(drone["angle"])
        p.limit()
    """

    # Measure
    p = Point(p_orig.x, p_orig.y)
    dist = drone["measure"]
    for i in range(int(dist)):
        img[int(p.x)][int(p.y)] = 100
        """
        img[int(p.x)+1][int(p.y)] = 100
        img[int(p.x)+1][int(p.y)+1] = 100
        img[int(p.x)+1][int(p.y)] = 100
        img[int(p.x)+1][int(p.y)-1] = 100
        img[int(p.x)-1][int(p.y)] = 100
        img[int(p.x)-1][int(p.y)+1] = 100
        img[int(p.x)-1][int(p.y)] = 100
        img[int(p.x)-1][int(p.y)-1] = 100
        """
        p.y += math.cos(drone["angle"])
        p.x += math.sin(drone["angle"])

    return img


def testing():
    key = getKey()
    print "getKey: ", key
    drones = initLevel()
    print "initLevel: ", drones
    turn = 5*math.pi/180
    acc = 0.0

    img_orig = loadImage("../../levels/level_1.png")
    img = []
    for i in range(512):
        line = []
        for j in range(512):
            line.append(0)
        img.append(line)

    for i in range(50):
        for drone in drones:
            print "Drone [%s]: " % drone
            measure = getMeasure(drone)
            print "\tMeasure: ", measure
            drone_status = moveDrone(turn, acc, drone)
            print "\tmoveDrone[%s](turn=%f, acc=%f): " % (drone, turn, acc)
            print "\t\tx: ", drone_status["x"]
            print "\t\ty: ", drone_status["y"]
            print "\t\ta: ", drone_status["angle"]
            print "\t\tlife: ", drone_status["life"]
            drone_status["measure"] = measure
            img = drawDrone(drone_status, img, img_orig)
        print "tick: ", tick()

    print "Score: ", getScore(img)

    show(img)

def getScore(map):
    req = {
        "action": "getScore",
        "team_name": team_name,
        "secret": secret,
        "map": map
    }
    socket.send(json.dumps(req))
    answer = socket.recv()
    #print "answer: ", answer
    return int(json.loads(answer)["score"])


def tick():
    req = {
        "action": "tick",
        "team_name": team_name,
        "secret": secret
    }
    socket.send(json.dumps(req))
    answer = socket.recv()
    #print "answer: ", answer
    return json.loads(answer)["ticks"]


def moveDrone(turn, acc, drone_name):
    req = {
        "action": "moveDrone",
        "team_name": team_name,
        "secret": secret,
        "drone": drone_name,
        "acceleration": acc,
        "turn": turn
    }
    socket.send(json.dumps(req))
    answer = socket.recv()
    #print "answer: ", answer
    return json.loads(answer)


def initLevel():
    req = {
        "action": "initLevel",
        "team_name": team_name,
        "secret": secret,
        "level": 1
    }
    socket.send(json.dumps(req))
    answer = socket.recv()
    return json.loads(answer)["drones"]


def getKey():
    global secret

    req = {
        "action": "getKey",
        "team_name": "test"
    }
    socket.send(json.dumps(req))
    answer = json.loads(socket.recv())
    secret = answer["secret"]
    return answer["secret"]


def getMeasure(drone):
    req = {
        "action": "getMeasure",
        "team_name": team_name,
        "secret": secret,
        "drone": drone
    }
    socket.send(json.dumps(req))
    answer = json.loads(socket.recv())["result"]
    return float(answer)


def main():
    global socket
    context = zmq.Context()
    connected = False

    #  Socket to talk to server
    print("Connecting to server.")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    while not connected:
        print("Sending handshake request.")
        socket.send(b"Hello")

        #  Get the reply.
        answer = socket.recv()
        if answer == "World!":
            print "Handshake suceed!"
            connected = True
        else:
            print("Handshake failed, received reply: "+answer)

    testing()


if __name__ == "__main__":
    main()