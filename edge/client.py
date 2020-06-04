
import zmq
import sys
import time

##imports from parent directory
sys.path.insert(0, '..')
from constants import *


def client_program():

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://%s:%s" % (HOST,IN_PORT))
    try:
        while True:
            print('connected to (' + str((HOST, IN_PORT)) + '')
            message = input(" -> ")  # take input
            socket.send_string(message)  # send message
    except KeyboardInterrupt:
        print('Exiting Client')

    socket.close()  # close the connection


if __name__ == '__main__':
    print(HOST)
    client_program()
