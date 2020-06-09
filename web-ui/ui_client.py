

import zmq
import sys
import json
import time

##imports from parent directory
sys.path.insert(0, '..')
from constants import *


def client_program():
    context = zmq.Context()
    client_socket = context.socket(zmq.PUB)  # instantiate
    client_socket.connect("tcp://%s:%s" %(HOST, IN_PORT))

    data=json.dumps(json.load(open("db.json")))


    try:
        client_socket.connect("tcp://%s:%s" %(HOST, IN_PORT))
        print('connected to (' + str((HOST, IN_PORT)) + '')
        
        data = "songs_db " + data

        client_socket.send_string(data)  # send json


    finally:
        client_socket.close()  # close the connection
    
    print("Sent: " + data)
    


if __name__ == '__main__':
    client_program()
