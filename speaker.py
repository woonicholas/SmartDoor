import socket
import threading
from datetime import datetime
import requests
import json

from pydub import AudioSegment
from pydub.playback import play
import pyttsx3
import requests


def play_audio(song_name='3on.mp3', 
              prediction=requests.get('http://35.236.46.222:8080/Henry/20/2/4', 
                  auth=('smartdoorcool',
                        'smartdoorpass'))):
  #song = '3on.mp3'  
  song = AudioSegment.from_mp3(song_name)

  beg = song[5000:10000]
  play(beg)

  #prediction = requests.get('http://35.236.46.222:8080/Henry/20/2/4', 
  #              auth=('smartdoorcool',
  #                    'smartdoorpass'))

  engine = pyttsx3.init()
  engine.say(prediction.text)
  engine.runAndWait()
  return 'finished'

def server_program():
  # host = '128.195.78.119'
  host = socket.gethostname()
  port = 5006

  server_socket = socket.socket()
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server_socket.bind((host, port))

  print('Listening... ')

  server_socket.listen(5)
  
  # ideally the fog when finding out someone entered, send a request to the cloud for a prediction
  # then the fog sends to the this speaker edge that prediction along with which song to play
  
  while True:
    conn, address = server_socket.accept()
    #thread.start_new_thread(new_client, (conn, address)) Python 2
    threading.Thread(group = None, target = new_client, args = (conn, address)).start()

  server_socket.close()


if __name__ == '__main__':
  play_audio()
  server_program()

