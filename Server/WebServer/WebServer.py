import web
from PIL import Image
from cStringIO import StringIO
import os

MAX_PIXEL_VALUE = 255

urls = (
    '/', 'index',
    '/(.*).js', 'JavaScript',
    '/team/(.*)', 'team',
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
        map = loadImage(path("level_1.png"))

        return getImageStream(map)


class JavaScript:
    def GET(self, file):
        with open(path(file + '.js'), 'r') as f:
            read_data = f.read()
        return read_data


class team:
    def GET(self, team_name):
        filename = os.path.join(os.path.dirname(__file__), 'team.html')
        render = web.template.frender(filename)
        return render(team_name)


class index:
    def GET(self):
        return "Hello, world!"


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()