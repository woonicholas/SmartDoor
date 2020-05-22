import socket
import thread

def new_client(conn, addr):
  while True:
    data = conn.recv(1024).decode()
    if not data:
      break
    print("from " + str(addr) + ': ' + str(data))
    message = raw_input(' -> ')
    conn.send(message.encode())  # send data to the client
  conn.close()  # close the connection

def server_program():
  host = '128.195.79.138'
  port = 5000

  server_socket = socket.socket()
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server_socket.bind((host, port))

  print('Listening... ')

  server_socket.listen(5)

  while True:
    conn, address = server_socket.accept()
    thread.start_new_thread(new_client, (conn, address))


  server_socket.close()


if __name__ == '__main__':
  server_program()
