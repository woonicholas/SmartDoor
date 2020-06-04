import socket
import threading
from datetime import datetime
import requests
import json

allclients = set()
time_dict = dict()
songs_dict = dict()
song_map = dict()
visitor_dict = dict()
completed_list = list()
client_lock = threading.Lock()
time = 0
with open('songs_db.json','r') as songs_db:
  songs_dict = json.load(songs_db)
  songs_db.close()
with open('song_map.json','r') as song_file:
  song_map = json.load(song_file)
  song_file.close()

class Visit:
  def __init__(self, name, enter_time, time_spent, day):
    self.name = name
    self.enter_time = int(enter_time)
    self.time_spent = int(time_spent)
    self.day = day

def message_clients(message):
  with client_lock:
    for i in allclients:
      i.send(message.encode())

def get_time_for_api():
  now = datetime.now()
  return '%d/%d/%d' % (now.hour,now.minute,now.weekday())

def new_client(conn, addr):
  global time
  global completed_list
  global time_dict
  global songs_dict
  global song_map
  global visitor_dict
  #global allclients

  with client_lock:
    allclients.add(conn)

  try:
    while True:
      data = conn.recv(1024).decode()
      if not data:
        break



      print("from " + str(addr) + ': ' + str(data))

      if data == 'pubsubtest':
        with client_lock:
          for i in allclients:
            i.send('this is a test'.encode())

      elif data.startswith("songs_db"):
        print('Song Database Received!\nWriting to json file...')
        db_data = json.loads(data[8:])
        songs_dict = db_data
        with open("songs_db.json", "r+") as songs_db:
          songs_db.seek(0)
          json.dump(db_data, songs_db,indent=2)
          songs_db.truncate()
          songs_db.close()

      elif data.startswith("music"):
        message = 'Speaker Connected'
        conn.send(message.encode())  # send data to the client

      #camera person outside 129123
      elif data.startswith('camera'):
        splitted = data.split()
        name = splitted[1]
        location = splitted[2]

        # with client_lock:
        #   if name not in time_dict:
        #     l = list()
        #     l.extend([name, int(splitted[3]), 0, datetime.today().weekday()])
        #     time_dict[name] = l

        #   else:
        #     time_entered = time_dict[name][1]
        #     day = time_dict[name][3]
        #     now = datetime.now()
        #     time_exitted = int(splitted[3])
        #     completed_list.append(Visit(name, time_entered, int((time_exitted - time_entered) / 60), day))
        #     del time_dict[name]

        #   if len(completed_list) >= 2:
        #     # send to cloud
        #     cloud_data = [{'name': x.name, 'enter_time': x.enter_time, 'time_spent': x.time_spent, 'day': x.day} for x in completed_list]
        #     d = dict()
        #     d['data'] = cloud_data

        #     url = 'http://35.236.46.222:8080/newdata'

        #     r = requests.post(url, data = json.dumps(d))

        #     print(json.dumps(d, indent = 4))

        #     print(r.status_code)

        #     completed_list = list()

        if name not in visitor_dict:
          visitor_dict[name] = {
            'location': ''
          }
        
        if location == 'outside':
          if visitor_dict[name]['location'] == '':
            visitor_dict[name]['location'] = 'outside'
          elif visitor_dict[name]['location'] == 'inside':
            message_clients('speaker %s exit %s'%(name,get_time_for_api()))
            visitor_dict[name]['location'] = 'outside'
        
        if location == 'inside':
          if visitor_dict[name]['location'] == '':
            visitor_dict[name]['location'] = 'inside'
          elif visitor_dict[name]['location'] == 'outside':
            song = ''
            for p in songs_dict['people']:
              if p['name'] == name:
                song = p['song']
            song_file = ''
            for s in song_map['songs']:
              if s['song'] == song:
                song_file = s['file']
            music_message = 'speaker ' + name + ' enter ' + song_file #adds person's name and song_file to send to 
            music_message = music_message + ' ' + get_time_for_api()  # adds formatted datetime for cloud
            message_clients(music_message)
            visitor_dict[name]['location'] = 'inside'

        # if time != 0:
        #   new_time = int(splitted[3])
        #   difference = new_time - time
        #   print('time passed: ', difference)
        #   time = new_time
        #   if abs(difference) <= 5:
        #     print('someone went thru the frame')
        #     conn.send(('someone has gone thru the frame').encode())
        #     time = 0
        #     # play music???
        #     song = ''
        #     for p in songs_dict['people']:
        #       if p['name'] == name:
        #         song = p['song']
        #     song_file = ''
        #     for s in song_map['songs']:
        #       if s['song'] == song:
        #         song_file = s['file']
        #     music_message = 'speaker ' + name + ' ' + song_file #adds person's name and song_file to send to 
        #     now = datetime.now()
        #     music_message = music_message + ' %d/%d/%d' % (now.hour,now.minute,now.weekday()) # adds formatted datetime for cloud
        #     with client_lock:
        #       for i in allclients:
        #         i.send(music_message.encode())
        #     pass
        #   else:
        #     conn.send(('took to long to go through the frame').encode())

        # else:
        #   time = int(splitted[3])
        #   print('time changed')
        #   conn.send(('person ' + name + ' ' + location + 'ed at ' +  str(time) + ' seconds').encode())

      else:
        message = input(' -> ')
        conn.send(message.encode())  # send data to the client
  except KeyboardInterrupt:
    print('Exiting Server..')
  finally:
    with client_lock:
      allclients.remove(conn)
      conn.close()  # close the connection

def server_program():
  host = '128.195.68.183'
  # host = socket.gethostname()
  port = 5006

  server_socket = socket.socket()
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server_socket.bind((host, port))

  print('Listening... ')

  server_socket.listen(5) 

  while True:
    conn, address = server_socket.accept()
    #thread.start_new_thread(new_client, (conn, address)) Python 2
    threading.Thread(group = None, target = new_client, args = (conn, address)).start()


  server_socket.close()


if __name__ == '__main__':
  server_program()
