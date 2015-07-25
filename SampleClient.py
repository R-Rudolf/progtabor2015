__author__ = 'Rudolf'

import time
import zmq
import json

socket = None

def testing():
    key = getKey()
    print "getKey: "+key
    print "initLevel: "+initLevel()
    print "set"

team_name = "test"
secret = None

def initLevel():
    req = {
        "action": "initLevel",
        "team_name": team_name,
        "secret": secret,
        "level": 1
    }
    socket.send(json.dumps(req))
    answer = socket.recv()
    return answer

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