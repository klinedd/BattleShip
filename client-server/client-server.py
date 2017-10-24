# Douglas Wise
# client-server in python
# October 21, 2017

from socket import *
import os.path

serverPort = 12000
serverSocket = 0

def main():
    client_server_select = raw_input('Type client or server: ')

    if client_server_select == 'client':
        client()
    elif client_server_select == 'server':
        server()
    else:
        print 'Invalid option. Closing.'

def client():
    serverName = raw_input('Enter server IP: ')

    path = "./store/game_state.txt"
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    print 'Client started.\nValid commands are recieve and send\nEnter \'q\' to quit.'
    while 1:
        message = raw_input('Client>')
        if message == 'q':
            break
        clientSocket.send(message)
        if message == 'recieve':
            fileMessage = clientSocket.recv(1024)
            test = fileMessage.split(":", 1)
            if test[0] == "Failure":
                print fileMessage
            else:
                f = open(path, 'wb')
                while fileMessage:
                    f.write(fileMessage)
                    fileMessage = clientSocket.recv(1024)
                print 'Receive complete.'
                f.close()
            break
        elif message == 'send':
            sendFile(clientSocket, path)
            clientSocket.shutdown(SHUT_WR)
            print 'Send Complete'
            break
        else:
            print ('Bad command: '+ message)
    clientSocket.close()

def server():
    global serverSocket
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',serverPort))
    serverSocket.listen(1)
    print "The server has started.\nUse ctrl-c to quit."
    path = "./store/game_state.txt"
    while 1:
        connectionSocket, addr = serverSocket.accept()
        clientInput = connectionSocket.recv(1024)
        tokens = clientInput.split(' ', 1)
        command = tokens[0]
        if command == 'recieve':
            print 'Request for game_state'
            sendFile(connectionSocket, path)
            connectionSocket.shutdown(SHUT_WR)
        elif command == 'send':
            fileMessage = connectionSocket.recv(1024)
            test = fileMessage.split(":", 1)
            if test[0] == "Failure":
                print fileMessage
            else:
                f = open(path, 'wb')
                while fileMessage:
                    f.write(fileMessage)
                    fileMessage = connectionSocket.recv(1024)
                print 'Receive complete.'
                f.close()
        else:
            print ('Bad command: '+ clientInput)
            connectionSocket.send('Bad command')
        connectionSocket.close()

def sendFile(sock, fileName):
    # path = './store/' + fileName
    path = fileName
    if not os.path.isfile(path):
        message = 'Failure: no file'
        sock.send(message)
        print message
        return
    f = open(path, 'rb')
    l = f.read(1024)
    while l:
        sock.send(l)
        l = f.read(1024)
    f.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Closing.'
        serverSocket.shutdown(SHUT_RDWR)
        serverSocket.close()
