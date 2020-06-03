#music_client.py
import os
import zmq
import requests
import multiprocessing
import time
from playsound import playsound
import pyttsx3

##imports from parent directory
import sys
sys.path.insert(0, '..')
from constants import *



def music_client_program():
  
  context = zmq.Context()
  socket = context.socket(zmq.SUB)

  socket.connect("tcp://%s:%s" % (HOST, OUT_PORT))  # connect to the server
  socket.setsockopt_string(zmq.SUBSCRIBE, "speaker")

  print('Speaker connected to (' + str((HOST, OUT_PORT)) + ')')
  print('Waiting to play music..')

  names = {
    'scissors': 'Ivan',
    'banana' : 'Preston',
    'fork': 'Nick',
    'person': 'Henry'
  }

  try:
    while True:
      song_rec = socket.recv().decode()
      #speaker banana enter ymca.mp3 2/4/20
      #speaker banana exit 2/4/20
      print(song_rec)
      splitted = song_rec.split()
      name = splitted[1]
      action = splitted[2]
      if(action == 'enter'):
        song = splitted[3]
        datetime = splitted[4]
        p = multiprocessing.Process(target=playsound, args=('songs/'+song,))
        p.start()
        input('Press Enter to Stop Playing')
        p.terminate()
        
        prediction = requests.get('http://35.236.46.222:8080/%s/%s' % (names[name], datetime), 
                auth=('smartdoorcool',
                      'smartdoorpass'))

        engine = pyttsx3.init()
        engine.say(prediction.text)
        engine.runAndWait()
      else:
        engine = pyttsx3.init()
        engine.say('%s has left' % (name))
        engine.runAndWait()

  except KeyboardInterrupt:
    print('Exiting Music Client..')

    # receive response
  print('Received from server: ' + song_rec)  # show in terminal

    

if __name__ == '__main__':
  music_client_program()