import web
from PIL import Image
from cStringIO import StringIO
import os
import threading

MAX_PIXEL_VALUE = 255

urls = (
    '/', 'Index',
    '/(.*).js', 'JavaScript',
    '/team/(.*)', 'Team',
    '/map/(.*)', 'MapDrawer'
)


def path(filename):
    return os.path.join(os.path.dirname(__file__), filename)


def loadImage(filename):
    img = Image.open(filename)
    image_array =  list(img.getdata())
    image = []

    for i in range(512):
        new_line = []
        for j in range(512):
            pixel = image_array[i*512+j]
            avg = 100*float(int(pixel[0])+int(pixel[1])+int(pixel[2]))/(3*MAX_PIXEL_VALUE)
            new_line.append((round(avg, -1)))
        image.append(new_line)

    return image


def getImageStream(map):
    image_array = []

    for line in map:
        for pixel in line:
            val = int(pixel*MAX_PIXEL_VALUE/100)
            touple = (val, val, val)
            image_array.append(touple)

    img = Image.new("RGB", (512, 512))
    img.putdata(image_array)

    img_io = StringIO()
    img.save(img_io, 'png')
    img_io.seek(0)
    return img_io


class MapDrawer:
    def GET(self, team):

        web.header('Content-type','image/png')
        web.header("Cache-Control", "no-cache")
        #map = loadImage(path("level_1.png"))
        map = None
        if WebServer.teams.has_key(team):
            if WebServer.teams[team].has_key("sended_map"):
                map = WebServer.teams[team]["sended_map"]
                print "Map generated for team: ", team
        if map == None:
            print "Map not found for team: ", team
            map = [[50 for j in range(512)] for i in range(512)]

        return getImageStream(map)


class JavaScript:
    def GET(self, file):
        with open(path(file + '.js'), 'r') as f:
            read_data = f.read()
        return read_data


class Team:
    def GET(self, team_name):
        render = web.template.frender(path('team.html'))
        if WebServer.teams.has_key(team_name):
            if WebServer.teams[team_name].has_key("score"):
                score = WebServer.teams[team_name]["score"]
            else:
                score = {
                    "all": "Map not sent --> Score not evaluated!",
                    "good": 0,
                    "bad": 0
                }
            return render(team_name, score)
        else:
            return "Team not registered!"


class Index:
    def GET(self):
        render = web.template.frender(path('index.html'))
        return render(WebServer.teams.keys())

class WebServer(threading.Thread):

    teams = {}

    def __init__(self, teams, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        WebServer.teams = teams
        self.app = web.application(urls, globals())

    def run(self):
        print "Starting webserver"
        self.app.run()

    def stop(self):
        print "Webserver stopped"
        self.app.stop()

if __name__ == "__main__":
    app = WebServer()
    app.start()