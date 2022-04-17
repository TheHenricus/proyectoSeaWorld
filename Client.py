import socket
import sys
from threading import Thread
import time
from Utils import encondeAndSend, decodeReceived


class Client():
    def __init__(self, socket: socket, name: str):
        self.socket = socket
        self.name = name
        self.status = 'AVAILABLE'

    def setUnavailable(self):
        self.status = 'UNAVAILABLE'

    def setAvailable(self):
        self.status = 'AVAILABLE'

    def getSocket(self):
        return self.socket


class ListSender(Thread):
    def __init__(self, socket: socket, sleepTime: int):
        super(ListSender, self).__init__(daemon=True)

        self.socket = socket
        self.isChatting = False
        self.sleepTime = sleepTime

    def run(self):
        while True:
            if not self.isChatting:
                try:
                    encondeAndSend(self.socket, 'LIST')
                    msg = decodeReceived(self.socket)
                    if msg.upper().startswith('CONNECT'):
                        print('Received Connect')
                        listTh.setIsChatting(True)
                    else:
                        print('Automatic LIST ping: ', msg)
                    time.sleep(self.sleepTime)
                except Exception as e:
                    print(f'ERROR| {str(e)}')

    def setIsChatting(self, val: bool):
        self.isChatting = val


def handleUserInput(socket: socket, input: str, listTh: ListSender):
    command = input.upper()
    if command.startswith('DISCONNECT'):
        # Si no esta chateando, se desconecta del servidor
        if not listTh.isChatting:
            encondeAndSend(socket, 'DISCONNECT')
            print('Closing client connection...')
            sys.exit(0)

        # Se desconecta del usuario y activa el ping LIST
        listTh.setIsChatting(False)

        # Desactiva el ping LIST
    elif command.startswith('CONNECT'):
        listTh.setIsChatting(True)

    encondeAndSend(socket, input)


def handleReceivedMsg(socket: socket, listTh: ListSender):
    # Recive el mensaje del servidor y analiza si se conecto a alguien

    msg = decodeReceived(socket)
    command = msg.upper()
    if command.startswith('CONNECT'):
        listTh.setIsChatting(True)
    elif command.startswith('DISCONNECT'):
        listTh.setIsChatting(False)


    print(msg)


if __name__ == '__main__':

    # if(len(sys.argv) != 3):
    #     print('ERROR: Argumentos invalidos!')
    #     print('Args -> <ServerIP> <ServerPort>')
    #     exit(1)

    serverIP = 'localhost'  # sys.argv[1]
    serverPort = 10023  # int(sys.argv[2])

    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))
    except socket.error as err:
        print(f'An error has occurred: {err}')

    resp = clientSocket.recv(1024).decode('ASCII')
    print(resp)
    name = input('Insert your name: ')
    clientSocket.sendall(name.encode('ASCII'))
    mensaje = clientSocket.recv(1024).decode('ASCII')

    print(mensaje)  # conectado con servidor

    # Thread para envio de comando LIST
    listTh = ListSender(clientSocket, 20)
    listTh.start()

    while True:
        # Handle Commandos y Envio de informacion
        data = None
        data = input('')
        handleUserInput(clientSocket, data, listTh)

        # Lectura de mensaje
        handleReceivedMsg(clientSocket, listTh)
