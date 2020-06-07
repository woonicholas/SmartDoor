#music_client.py
import os
import zmq
import requests
import multiprocessing
import time
import pyttsx3

##imports from parent directory
import sys
sys.path.insert(0, '..')
from constants import *

from dotenv import load_dotenv

from pathlib import Path
env_path = Path("/home/pi/Desktop/SmartDoor/.env")
load_dotenv(dotenv_path=env_path)

import os 
import spotipy
import spotipy.util as util
import time

username="ivanhuang77@gmail.com"
raspotify_id = os.getenv("raspotify_device_id")
phone_id = "43a0a1a8680013a0974a9aaf5eac96700e2007f4"
spotify_client_id = os.getenv("spotify_client_id")
spotify_client_secret = os.getenv("spotify_client_secret")

# scope = 'user-library-read'
scope = "user-read-playback-state,user-modify-playback-state"


def music_client_program():

  token = util.prompt_for_user_token( username, 
                                    scope, 
                                    client_id=spotify_client_id,
                                    client_secret=spotify_client_secret,
                                    redirect_uri='http://localhost:8000/'  )
  
  context = zmq.Context()
  socket = context.socket(zmq.SUB)
  socket.connect("tcp://%s:%s" % (HOST, OUT_PORT))  # connect to the server
  socket.setsockopt_string(zmq.SUBSCRIBE, "speaker")

  print('Speaker connected to (' + str((HOST, OUT_PORT)) + ')')
  print('Waiting to play music..')

  try:
    while True:
      song_rec = socket.recv().decode()
      print(song_rec)
      #speaker banana enter ymca.mp3 2/4/20
      #speaker banana exit 2/4/20

      splitted = song_rec.split()
      name = splitted[1]
      action = splitted[2]
      if(action == 'enter'):
        song = splitted[3]
        datetime = splitted[4]

        if token:
            sp = spotipy.Spotify(auth=token)
            
            results = sp.search(q=song, limit=3)
            
            firstResult = results['tracks']['items'][0]
            print('Spotify search result: ' + firstResult['name'])
            print(firstResult['name'] + ' is now playing!')

            ## Change playback on the active device
            sp.start_playback(device_id=raspotify_id, uris=['spotify:track:' + firstResult['id']])    
            
            time.sleep(10)
            sp.pause_playback(device_id=raspotify_id)
        else:
            print("Can't get token for", username)        


        prediction = requests.get('http://35.236.46.222:8080/leave/%s/%s' % (name, datetime), 
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