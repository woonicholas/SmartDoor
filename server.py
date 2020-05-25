import socket
import threading
from datetime import datetime
import requests
import json

allclients = set()
time_dict = dict()
completed_list = list()
client_lock = threading.Lock()
time = 0

class Visit:
  def __init__(self, name, enter_time, time_spent, day):
    self.name = name
    self.enter_time = int(enter_time)
    self.time_spent = int(time_spent)
    self.day = day
  

def new_client(conn, addr):
  global time
  global completed_list
  global time_dict
  #global allclients

  with client_lock:
    allclients.add(conn)

  try:
    while True:
      data = conn.recv(1024).decode()
      print(data)
      if not data:
        break



      print("from " + str(addr) + ': ' + str(data))

      if data == 'pubsubtest':
        with client_lock:
          for i in allclients:
            i.send('this is a test'.encode())



      elif data.startswith('camera'):
        splitted = data.split()
        name = splitted[1]
        direction = splitted[2]

        with client_lock:
          if name not in time_dict:
            l = list()
            l.extend([name, int(splitted[3]), 0, datetime.today().weekday()])
            time_dict[name] = l

          else:
            time_entered = time_dict[name][1]
            day = time_dict[name][3]
            now = datetime.now()
            time_exitted = int(splitted[3])
            completed_list.append(Visit(name, time_entered, int((time_exitted - time_entered) / 60), day))
            del time_dict[name]

          if len(completed_list) >= 2:
            # send to cloud
            cloud_data = [{'name': x.name, 'enter_time': x.enter_time, 'time_spent': x.time_spent, 'day': x.day} for x in completed_list]
            d = dict()
            d['data'] = cloud_data

            url = 'http://35.236.46.222:8080/newdata'

            r = requests.post(url, data = json.dumps(d))

            print(json.dumps(d, indent = 4))

            print(r.status_code)

            completed_list = list()


            

        if time != 0:
          new_time = int(splitted[3])
          difference = new_time - time
          time = new_time
          if abs(difference) <= 3:
            print('someone went thru the frame')
            conn.send(('someone has gone thru the frame').encode())
            time = 0
            # play music???
            pass

        else:
          time = int(splitted[3])

          conn.send(('person ' + name + ' ' + direction + 'ed at ' +  str(time) + ' seconds').encode())

      else:
        message = input(' -> ')
        conn.send(message.encode())  # send data to the client

  finally:
    with client_lock:
      allclients.remove(conn)
      conn.close()  # close the connection

def server_program():
  host = '128.195.71.227'
  #host = socket.gethostname()
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
