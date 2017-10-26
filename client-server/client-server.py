# Douglas Wise
# client-server in python
# October 21, 2017
#
# client-server code to send game_state file back and forth
# between the server(Player 1) and the client(Player 2)
#

from socket import *
import os.path

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

        #recieves file from opponent
        #also checks for opponent quit
        if recieve(clientSocket) == 0:
            break

        #sends file to opponent
        #also checks for quit
        if send('Player 2', clientSocket) == 0:
            break

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
        if send('Player 1', connectionSocket) == 0:
            break

        #recieves from opponent
        #also checks for opponent quit
        if recieve(connectionSocket) == 0:
            break

    #closes socket after quit
    connectionSocket.shutdown(SHUT_RDWR)
    connectionSocket.close()

#
#
#   code to send game_state
#
# given user(Player 1 or 2) and socket, will send the game_state
# valid commnads are:
#          'q': will quit and close the socket
#       'send': will send the game_state
#
# else it notifies of bad command
#

def send(user, socket):
    command = raw_input(user + ': ')

    #checks for quit command
    if command == 'q':
        print 'Quiting'
        socket.send(command)                #sends quit command
        return 0                            #returns. nothing sent

    #checks if "player 1" wants to send
    elif command == 'send':
        socket.send(command)                #sends send notification
        request = socket.recv(1024)         #waits for ack
        if request == 'send file':          #if ack
            sendFile(socket)                #sends file
            print 'Send Complete'           #user notification
            return 1                        #successful return
        else:
            print 'request failed'
    #bad command notification
    else:
        print 'Bad command: ' + command

#
#
#   code to recieve game_state
#
# given the socket, will wait for command
# upon recieving command will either:
#       (1) quit
#       (2) send game_state file
#       (3) notify of bad command
#

def recieve(socket):
    print 'Waiting for input from opponent'

    #recieves command
    command = socket.recv(1024)

    #opponent quit
    if command == 'q':
        print 'opponent quit'
        return 0

    #recieve send request
    elif command == 'send':
        socket.send('send file')            #send ack
        fileMessage = socket.recv(1024)     #get file
        test = fileMessage.split(":", 1)    #split for testing
        if test[0] == "Failure":            #test for failed recieve
            print fileMessage

        else:                               #didn't fail
            socket.settimeout(0.5)          #set timeout
            f = open(path, 'wb')            #open file for writing
            while fileMessage:              #write to file
                try:
                    f.write(fileMessage)
                    fileMessage = socket.recv(1024)
                except timeout:             #timesout assumed done sending
                    print 'timed out'
                    break
            print 'Receive complete.'
            f.close()                       #close file
            socket.settimeout(None)         #removes timeout
            return 1
    #bad command notification
    else:
        print ('Bad command: '+ command)
        socket.send('Bad command')


#
#
#   code to send file(game_state)
#
# given the socket, will send file at path through the socket
#

def sendFile(sock):
    #checks for file
    if not os.path.isfile(path):
        message = 'Failure: no file'        #error message
        sock.send(message)
        print message
        return
    else:
        f = open(path, 'rb')                 #opens file
        l = f.read(1024)                     #reads chunck of file
        #loop to send whole file
        while l:
            sock.send(l)
            l = f.read(1024)
        f.close()                            #closes file


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Closing.'
        serverSocket.shutdown(SHUT_RDWR)
        serverSocket.close()
