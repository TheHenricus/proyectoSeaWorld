import socket
from threading import Thread

from Client import Client
from Utils import encondeAndSend, decodeReceived

#Variables Globales
port_number = 10023
host_address = ''
dict_conn = {}
ProtocolCommands = {'LIST', 'CONNECT', 'DISCONNECT'}

class ChatController(Thread):
    def __init__(self, client1: Client, client2: Client, debug= False):
        super(ChatController, self).__init__(daemon=True)
        self.client1 = client1
        self.client2 = client2
        self.chatting = True
        self.debug = debug

    #Chat
    def run(self):
        global dict_conn

        nameClienteA = self.client1.name
        nameClienteB = self.client2.name

        self.client1.setUnavailable()
        self.client2.setUnavailable()

        socketClienteA:socket = self.client1.getSocket()
        socketClienteB:socket = self.client2.getSocket()
        # socketClienteA.sendall(f'Connecting you to {nameClienteB}'.encode('ASCII'))
        socketClienteB.sendall(f'Connecting you to {nameClienteA}'.encode('ASCII'))

        print(f'Connecting {nameClienteA} to {nameClienteB}')

        turn = 1
        while True:

            #turn = 2
            # Matar el hilo cuando dejen de conversar
            if not self.chatting:
                self.client1.setAvailable()
                self.client2.setAvailable()
                break

            # Logica del chat
            #data2 = None
            if turn == 1:
                # socketClienteA.sendall(f'prueba cl2'.encode('ASCII'))
                print(f'{nameClienteB} s turn') if self.debug else None
                #----------------------------------------------------------------
                data2 = decodeReceived(socketClienteB)

                if data2.upper().startswith('DISCONNECT'):
                    self.client1.setAvailable()
                    self.client2.setAvailable()

                    encondeAndSend(socketClienteA, f'DISCONNECTED FROM CHAT')
                    encondeAndSend(socketClienteB, f'DISCONNECTED FROM CHAT - ONLINE USERS {str(list(dict_conn.keys()))}')

                    print(f'CHAT BETWEEN {nameClienteA} AND {nameClienteB} ENDED')
                    break

                print(f'{nameClienteB} wrote {data2}') if self.debug else None
                dato_B = str(nameClienteB) + " says: " + data2
                encondeAndSend(socketClienteA, dato_B)

                turn = 2
                continue

            else:
                #data2 = None
                # ocketClienteB.sendall(f'prueva cl1'.encode('ASCII'))
                print(f'{nameClienteA} s turn') if self.debug else None

                #dato_A = str(nameClienteA) + " says: " + data2-----------abajo opt
                #encondeAndSend(socketClienteB, dato_A)

                data2 = decodeReceived(socketClienteA)

                dato_A = str(nameClienteA) + " says: " + data2
                encondeAndSend(socketClienteB, dato_A)

                print(f'{nameClienteA} wrote {data2}') if self.debug else None

                #dato_A = str(nameClienteA) + " says: " + data2
                #encondeAndSend(socketClienteB, dato_A)
                turn = 1
                continue



    def stopChatting(self):
        self.chatting = False


def sendConnectedUsers(s:socket):
    encondeAndSend(s, str(list(dict_conn.keys())))

def handleReceivedMsg(s: socket, currentUser: str, conversationTh: ChatController):
    currentClient = dict_conn[currentUser]

    if currentClient.status == 'AVAILABLE':
        msg = decodeReceived(s)
        command = msg.upper()

        print(f'Received in handling {msg}')

        if command.startswith('CONNECT'):
            desiredUser = command[len('CONNECT')+1:]
            if dict_conn.get(desiredUser) is None:
                encondeAndSend(s, 'ERROR| User does not exist')
                return
            elif dict_conn[desiredUser].status == 'UNAVAILABLE':
                encondeAndSend(s, f'ERROR| {desiredUser} is unavailable at this moment. Try again in a few minutes...')
            else:
                conversationThread = ChatController(dict_conn[currentUser], dict_conn[desiredUser], debug=True)
                conversationThread.start()
                return conversationThread
        elif command == 'LIST':
            sendConnectedUsers(s)
        elif command.startswith('DISCONNECT'):
            print(f'Deleting conection with {currentUser}')
            del(dict_conn[currentUser])
            s.close()
        else:
            encondeAndSend(s, f'ERROR| {command} is not a valid command')

def multiThreadClientConnection(conn: socket):
    conn.send('Server is working: '.encode('ASCII'))
    try:
        name = conn.recv(2014).decode('ASCII').upper()
        dict_conn[name] = Client(conn, name)
        conn.sendall(str('Connected to server').encode('ASCII'))
    except:
        print(f'Failed to connect to {conn}')

    conversationTh = None

    while True:
        try:
            result = handleReceivedMsg(conn, name, conversationTh)
            if result:
                conversationTh = result

        except ConnectionResetError as err:
            del dict_conn[name]
            break

if __name__ == "__main__":

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        serverSocket.bind((host_address, port_number))
    except socket.error as err:
        print(f'An error has occurred: {str(err)}')

    print(f'ServerSocket is listening at port number {port_number} in host address {serverSocket.getsockname()[0]}')
    serverSocket.listen() #No se determina un numero de conexiones

    while True:

        try:
            client, address = serverSocket.accept()
            print(f'Connected to {address[0]}:{address[1]}')
            th = Thread(target=multiThreadClientConnection, args=(client,))
            th.start()

        except KeyboardInterrupt:
            break

    serverSocket.close()