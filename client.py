
import socket


def client_program():
    # host = socket.gethostname()
    host = '128.195.67.14'  # change this to server ip specified in UCI VPN
    port = 5006  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server
    
    try:
        while True:
            print('connected to (' + str((host, port)) + '')
            message = input(" -> ")  # take input
            client_socket.send(message.encode())  # send message
    except KeyboardInterrupt:
        print('Exiting Client')

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()
