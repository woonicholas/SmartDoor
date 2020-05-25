import socket
import threading


allclients = set()
client_lock = threading.Lock()

def new_client(conn, addr):
  with client_lock:
    allclients.add(conn)

  try:
    while True:
      data = conn.recv(1024).decode('utf-8')
      if not data:
        break

      print("from " + str(addr) + ': ' + str(data))

      if data == 'pubsubtest':
        with client_lock:
          for i in allclients:
            i.send('this is a test'.encode())

      else:
        message = input(' -> ')
        conn.send(message.encode())  # send data to the client

  finally:
    with client_lock:
      allclients.remove(conn)
      conn.close()  # close the connection

def server_program():
  #host = '128.195.79.138'
  host = socket.gethostname()
  port = 5001

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
