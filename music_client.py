#music_client.py
import os
import socket
import requests
import multiprocessing
import time
# from playsound import playsound
import pyttsx3
import pygame

pygame.mixer.init()


def music_client_program():
  # host = socket.gethostname()
  host = '128.195.67.14'  # change this to server ip specified in UCI VPN
  port = 5006  # socket server port number

  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate

  try:
    client_socket.connect((host, port))  # connect to the server
    print('connected to (' + str((host, port)) + '')

    client_socket.sendall(bytes('music',encoding="utf-8"))  # send message

    song_rec = client_socket.recv(1024).decode() #receivied successful connections message

    print(song_rec)    

    names = {
      'scissors': 'Ivan',
      'banana' : 'Preston',
      'fork': 'Nick',
      'person': 'Henry'
    }
    try:
      while True:
        song_rec = client_socket.recv(1024).decode()
        #speaker banana enter ymca.mp3 2/4/20
        #speaker banana exit 2/4/20
        if song_rec.startswith('speaker'):
          print(song_rec)
          splitted = song_rec.split()
          name = splitted[1]
          action = splitted[2]
          if(action == 'enter'):
            song = splitted[3]
            datetime = splitted[4]
            pygame.mixer.music.load('songs/' + song)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play()
            
            time.sleep(10)
            pygame.mixer.music.stop()
            #p = multiprocessing.Process(target=playsound, args=('songs/'+song,))
            #p.start()
            #input('Press Enter to Stop Playing')
            #p.terminate()
            
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

  finally:
    client_socket.close()  # close the connection

    

if __name__ == '__main__':
  music_client_program()