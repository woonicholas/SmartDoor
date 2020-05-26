
import socket
import sys
import json

def client_program():
    # host = socket.gethostname()
    host = '128.195.78.119'  # change this to server ip specified in UCI VPN
    port = 5006  # socket server port number

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
    
    data=json.dumps(json.load(open("db.json")))


    try:
        client_socket.connect((host, port))  # connect to the server
        print('connected to (' + str((host, port)) + '')
        
        data = "songs_db " + data

        client_socket.sendall(bytes(data,encoding="utf-8"))  # send message

        rec = client_socket.recv(1024).decode()  # receive response
        print('Received from server: ' + rec)  # show in terminal

    finally:
        client_socket.close()  # close the connection
    
    print("Sent: " + data)
    


if __name__ == '__main__':
    client_program()
