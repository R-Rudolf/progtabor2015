__author__ = 'erudhor'

import json
from PIL import Image


MAX_PIXEL_VALUE = 255


def loadImage(filename):
    img = Image.open("levels/"+filename)
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

class Level:

    def __init__(self, filename):
        f = open(filename, "r")
        fileText = ""
        for line in f.readlines():
            fileText += line+"\n"
        f.close()
        datas = json.loads(fileText)
        self.img_width = datas["img_width"]
        self.img_height = datas["img_height"]
        self.max_turn = datas["max_turn"]
        self.max_acc = datas["max_acc"]
        self.max_speed = datas["max_speed"]
        self.number_of_drones = datas["number_of_drones"]
        self.starting_point = datas["starting_point"]
        map_file = datas["map"]
        self.map = loadImage(map_file)

    def score(self, sent):
        max_good = 0
        max_error = 0
        error = 0
        good = 0

        for i in range(self.img_height):
            for j in range(self.img_width):
                if self.map[i][j] == 100:
                    max_good += 1
                    if sent[i][j] == 100:
                        good += 1
                else:
                    max_error += 1
                    if sent[i][j] != 0:
                        error += 1
        print "good: ", good
        print "error: ", error
        print "max error: ", max_error
        print "max good: ", max_good

        return int(100*(float(good)/max_good - float(error)/max_error))
