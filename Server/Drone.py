__author__ = 'erudhor'

import math
import json

def limit(value, limit):
    if value > 0 and value > limit:
            value = limit
    elif value < -limit:
        value = -limit

    return value


class Point:
    def limit_point(self, width, height):
        self.x = limit(self.x, width) if self.x > 0 else 0
        self.y = limit(self.y, height) if self.y > 0 else 0

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Drone:

    def loadDrone(self, data_json):
        data = json.loads(data_json)
        self.x = data["x"]
        self.y = data["y"]
        self.angle = data["angle"]
        self.speed = data["speed"]
        self.acc   = data["acc"]
        self.turn  = data["turn"]
        self.name = data["name"]
        self.life = data["life"]
        self.history = data["history"]

    def saveDrone(self):
        data = {
            "name": self.name,
            "life": self.life,
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
            "turn": self.turn,
            "acc": self.acc,
            "speed": self.speed,
            "history": self.history
        }
        return json.dumps(data)

    def __init__(self, level, angle=0.0, name="Nameless", origo=None):
        self.level = level
        if origo == None:
            self.x = level.starting_point[0]
            self.y = level.starting_point[1]
        else:
            self.x = origo[0]
            self.y = origo[1]
        self.angle = angle
        self.speed = 0
        self.acc   = 0
        self.turn  = 0
        self.name = name
        self.life = 1
        self.history = [[self.x, self.y, self.angle]]

    def setMovement(self, turn, acc):
        if self.life:
            self.acc  = limit(acc, self.level.max_acc)
            self.turn = limit(turn, self.level.max_turn)

    def crashTest(self):
        point = int(self.level.map[int(self.x)][int(self.y)])
        # print "Drone Crashed at: %d ,%d --> %f" % (self.x, self.y, point)
        return point < 100

    def go(self):
        self.angle += self.turn
        self.speed += self.acc
        self.speed = limit(self.acc+self.speed,
                           self.level.max_speed)
        self.speed = 0 if self.speed < 0 else self.speed

        self.y += math.cos(self.angle)*self.speed
        self.x += math.sin(self.angle)*self.speed

        if self.crashTest():
            self.life = 0
            self.speed = 0

        self.history.append([self.x, self.y, self.angle])

    def drawDrone(self, img_orig):
        img = img_orig[:]
        size = 20
        p = Point(math.floor(self.x), math.floor(self.y))
        p_orig = Point(p.x, p.y)

        # Orientation
        p.y -= math.cos(self.angle)*int(size/2)
        p.x -= math.sin(self.angle)*int(size/2)
        p.limit_point(self.level.img_width,
                      self.level.img_height)
        for i in range(size):
            img[int(p.x)][int(p.y)] = 1
            p.y += math.cos(self.angle)
            p.x += math.sin(self.angle)
            p.limit_point(self.level.img_width,
                          self.level.img_height)

        # Orientation
        size /= 2
        p = Point(p_orig.x, p_orig.y)
        p.y -= math.sin(self.angle)*int(size/2)
        p.x -= math.cos(self.angle)*int(size/2)
        p.limit_point(self.level.img_width,
                      self.level.img_height)
        for i in range(size):
            img[int(p.x)][int(p.y)] = 1
            p.y += math.sin(self.angle)
            p.x += math.cos(self.angle)
            p.limit_point(self.level.img_width,
                          self.level.img_height)


        # Measure
        p = Point(p_orig.x, p_orig.y)
        dist = self.measure()
        for i in range(int(dist)):
            img[int(p.x)][int(p.y)] = 0.5
            p.y += math.cos(self.angle)
            p.x += math.sin(self.angle)

        return img

    def measure(self):
        p = Point(self.x, self.y)

        def go(p, angle):
            p.y += math.cos(angle)
            p.x += math.sin(angle)
            p.limit_point(self.level.img_width, self.level.img_height)
            return p

        def check(p):
            x = int(math.floor(p.x))
            y = int(math.floor(p.y))
            return self.level.map[x][y] > 0

        while True:
            if int(math.floor(p.x)) < 0 or\
                int(math.floor(p.x)) >= self.level.img_width or \
                int(math.floor(p.y)) < 0 or\
                int(math.floor(p.y)) >= self.level.img_height:
                break # Out of image

            if not check(p):
                break # Cave wall

            p = go(p, self.angle)

        return math.sqrt((p.x-self.x)**2 + (p.y-self.y)**2)
