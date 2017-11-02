# Douglas Wise
# client-server in python
# October 21, 2017
#
# client-server code to send game_state file back and forth
# between the server(Player 1) and the client(Player 2)
#

from socket import *
import os.path
import simplejson

serverPort = 12000
serverSocket = 0
path = "./store/game_state.txt"             #location of game_state file



#
#
#   initial code for starting client-server
#
# takes user input to be either client or server
# then runs appropriate method
# if bad input is given, notifies user and closes
#

def main():
    client_server_select = raw_input('Type client or server: ')

    if client_server_select == 'client':
        client()
    elif client_server_select == 'server':
        server()
    else:
        print 'Invalid option. Closing.'

#
#
#   code for client also considered Player 2
#
#
# enter IP of server(Player 1) and establishes connection
# while in send() method:
#       typing 'send' will send the game_state file to the server(Player 1)
#       typing 'q' will quit and close the socket
# recieve() waits for server to send game_state
#       if server severs connection user is notified
#       then the socket is closed

def client():
    #input server IP
    serverName = raw_input('Enter server IP: ')

    #socket setup
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    print 'Client started.\nValid command is send\nEnter \'q\' to quit.'

    while 1:

        board = clientSocket.recv(1024)
        print board

        Board = simplejson.loads(board)

    #closes socket after quit
    clientSocket.shutdown(SHUT_RDWR)
    clientSocket.close()

#
#
#   code for server also considered Player 1
#
#
# initialy sets up socket and accepts from client(Player 2)
# while in send() method:
#       typing 'send' will send the game_state file to the client(Player 2)
#       typing 'q' will quit and close the socket
# recieve() waits for client to send game_state
#       if client severs connection user is notified
#       then the socket is closed

def server():
    #socket setup
    global serverSocket

    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',serverPort))
    serverSocket.listen(1)

    print "The server has started.\nUse ctrl-c to quit."
    #waiting for connection
    connectionSocket, addr = serverSocket.accept()

    while 1:
        #sends file to opponent
        #also checks for quit
        w, h = 10,10
        Board = [[0 for x in range(w)] for y in range(h)]
        for i in range(w):
            for j in range(h):
                Board[i][j] = 'blue'

        board = simplejson.dumps(Board)

        raw_input('send board')
        connectionSocket.sendall(board)


    #closes socket after quit
    connectionSocket.shutdown(SHUT_RDWR)
    connectionSocket.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Closing.'
        serverSocket.shutdown(SHUT_RDWR)
        serverSocket.close()
