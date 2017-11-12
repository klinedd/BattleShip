#!/usr/bin/env python2

import copy, random, math, time
import pygame, sys
from pygame.locals import *
from socket import *
import os.path
import simplejson
import Adafruit_BBIO.GPIO as GPIO

miscBtn = "PAUSE"
upBtn = "GREEN"
downBtn = "RED"
leftBtn = "GP1_4"
rightBtn = "GP1_3"

GPIO.setup(miscBtn, GPIO.IN)
GPIO.setup(upBtn, GPIO.IN)
GPIO.setup(downBtn, GPIO.IN)
GPIO.setup(leftBtn, GPIO.IN)
GPIO.setup(rightBtn, GPIO.IN)


serverPort = 12000
serverSocket = 0

pygame.init()
pygame.font.init()

pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((320,240))
pygame.display.set_caption('Battleship')
clock = pygame.time.Clock()
screen.fill((255,255,255))
size = 10

ships = ['A', 'B', 'S', 'C', 'D']
map = {'A': 5, 'B': 4, 'S': 3, 'C': 3, 'D': 2}

#keep track of where the key presses have moved the 'cursor'
x = 0
y = 0

#used to draw the grid lines
x1 = 0
y1 = 0


#win status counter
hitCount = 0

#create matrix that will hold information of the board game
w, h = 10,10
Board = [[0 for x in range(w)] for y in range(h)]
opponent_board = [[0 for x in range(w)] for y in range(h)]
play_board = [[0 for x in range(w)] for y in range(h)]


def btnUpdate(channel):
    print "button pressed"
    if channel == upBtn:
        pygame.event.post(pygame.event.Event(KEYDOWN, key = K_UP))
        print ("up posted")
    if channel == downBtn:
        pygame.event.post(pygame.event.Event(KEYDOWN, key = K_DOWN))
        print ("down posted")
    if channel == leftBtn:
        pygame.event.post(pygame.event.Event(KEYDOWN, key = K_LEFT))
        print "left posted"
    if channel == rightBtn:
        pygame.event.post(pygame.event.Event(KEYDOWN, key = K_RIGHT))
        print "right posted"
    if channel == miscBtn:
        pygame.event.post(pygame.event.Event(KEYDOWN, key = K_RETURN))
        print "misc posted"


GPIO.add_event_detect(miscBtn, GPIO.HIGH, callback = btnUpdate)
GPIO.add_event_detect(upBtn, GPIO.HIGH, callback = btnUpdate)
GPIO.add_event_detect(downBtn, GPIO.HIGH, callback = btnUpdate)
GPIO.add_event_detect(leftBtn, GPIO.HIGH, callback = btnUpdate)
GPIO.add_event_detect(rightBtn, GPIO.HIGH, callback = btnUpdate)



for i in range(w):
    for j in range(h):
        Board[i][j] = 'blue'
        opponent_board[i][j] = 'blue'
        play_board[i][j] = 'blue'

def main():
    client_server_select = raw_input('Type "player 1" or "player 2": ')

    if client_server_select == "player 2":
        client()
    elif client_server_select == "player 1":
        server()
    else:
        print 'Invalid option. Closing.'

    try:
        while True:
            time.sleep(0.25)

    except KeyboardInterrupt:
        print "Cleaning Up"
        GPIO.cleanup()
    GPIO.cleanup()







def server():
    #socket setup
    global serverSocket
    global Board
    global opponent_board
    global play_board
    global hitCount

    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',serverPort))
    serverSocket.listen(1)

    print "The server has started.\nUse ctrl-c to quit."
    #waiting for connection
    connectionSocket, addr = serverSocket.accept()
    while 1:
        draw_board(Board)
        place_ship()

        #sends file to opponent
        #also checks for quit
        print 'sending'
        connectionSocket.sendall(simplejson.dumps(Board))

        print 'waiting'
        temp = connectionSocket.recv(1024)
        opponent_board = simplejson.loads(temp)
        print 'board recieved'
        play(connectionSocket, 'Player 1')
        response = raw_input('Continue? (yes/no): ')
        if response == 'no':
            break
        if response == 'yes':
            hitCount = 0
            for i in range(w):
                for j in range(h):
                    Board[i][j] = 'blue'
                    opponent_board[i][j] = 'blue'
                    play_board[i][j] = 'blue'

    #closes socket after quit
    connectionSocket.shutdown(SHUT_RDWR)
    connectionSocket.close()

def client():
    global Board
    global opponent_board
    global play_board
    global hitCount
    #input server IP
    serverName = raw_input('Enter server IP: ')

    #socket setup
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    print 'Client started.\nValid command is send\nEnter \'q\' to quit.'
    while 1:
        draw_board(Board)
        place_ship()
        print 'waiting'
        temp = clientSocket.recv(1024)
        opponent_board = simplejson.loads(temp)
        print 'recieved'
        print 'sending'
        clientSocket.sendall(simplejson.dumps(Board))
        print 'sent'
        play(clientSocket, 'Player 2')
        response = raw_input('Continue? (yes/no): ')
        if response == 'no':
            break
        if response == 'yes':
            hitCount = 0
            for i in range(w):
                for j in range(h):
                    Board[i][j] = 'blue'
                    opponent_board[i][j] = 'blue'
                    play_board[i][j] = 'blue'

    #closes socket after quit
    clientSocket.shutdown(SHUT_RDWR)
    clientSocket.close()

def draw_board(board):
    clock.tick(13)
    screen.fill((255,255,255))
    for i in range(w):
        for j in range(h):
            if board[i][j] == 'blue':
                Rect = pygame.Rect((i)*24, (j)*24, 24, 24)
                pygame.draw.rect(screen, (0,0,255), Rect)
            if board[i][j] == 'red':
                Rect = pygame.Rect((i)*24, (j)*24, 24, 24)
                pygame.draw.rect(screen, (255,0,0), Rect)
            if board[i][j] == 'yellow':
                Rect = pygame.Rect((i)*24, (j)*24, 24, 24)
                pygame.draw.rect(screen, (249,237,2), Rect)
            if board[i][j] == 'grey':
                Rect = pygame.Rect((i)*24, (j)*24, 24, 24)
                pygame.draw.rect(screen, (122,111,111), Rect)

    cursor = pygame.Rect(x-3, y-3, 12, 12)
    pygame.draw.rect(screen, (0,0,0), cursor)
    pygame.display.update()

    #draws the lines for the grid on the screen
    for i in range(size):
        pygame.draw.line(screen, (0,0,0), (x1, y1+(i*24)+24), (x1+24*size, y1+(i*24)+24))
        pygame.draw.line(screen, (0,0,0), (x1+24+(i*24), y1), (x1+24+(i*24), y1+24*size))
    pygame.display.update()

def shoot():
    global opponent_board
    global play_board
    global x
    global y
    global hitCount

    while 1:
        draw_board(play_board)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if x < 24*(size-1): x+=24
                if event.key == pygame.K_LEFT:
                    if x > 24: x-=24
                if event.key == pygame.K_UP:
                    if y > 24: y-=24
                if event.key == pygame.K_DOWN:
                    if y < 24*(size-1): y+=24
                if event.key == pygame.K_RETURN:
                    if opponent_board[x/24][y/24] == 'grey':
                        play_board[x/24][y/24]  = 'red'
                        opponent_board[x/24][y/24]  = 'red'
                        draw_board(play_board)
                        hitCount += 1
                        return
                    if opponent_board[x/24][y/24] == 'blue':
                        play_board[x/24][y/24] = 'yellow'
                        opponent_board[x/24][y/24] = 'yellow'
                        draw_board(play_board)
                        return

def check_win():
    global hitCount
    if hitCount == 17:
        message_display('YOU WIN')
        return 1
    else:
        return 0

def check_loss():
    for i in range(w):
        for j in range(h):
            if Board[i][j] == 'grey':
                return 0
    return 1

def text_objects(text, font):
    textSurface = font.render(text, True, (0,0,0))
    return textSurface, textSurface.get_rect()

def message_display(text):
    largeText = pygame.font.Font('freesansbold.ttf',15)
    TextSurf, TextRect = text_objects(text,largeText)
    TextRect.center = ((240/2),(240/2))
    screen.blit(TextSurf, TextRect)

    pygame.display.update()

    time.sleep(2)

    return


def ship_location():
    global x
    global y
    global Board
    while 1:
        draw_board(Board)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if x < 24*(size-1): x+=24
                if event.key == pygame.K_LEFT:
                    if x > 24: x-=24
                if event.key == pygame.K_UP:
                    if y > 24: y-=24
                if event.key == pygame.K_DOWN:
                    if y < 24*(size-1): y+=24
                if event.key == pygame.K_RETURN:
                   if ( Board[x/24][y/24] != 'grey'):
			Board[x/24][y/24] = 'grey'
                    	draw_board(Board)
                    	return
		   else:
			print "Pick valid ship placement"

def ship_direction(ship):
    global map
    global Board
    while 1:
        draw_board(Board)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and (x/24+(map[ship]-1)) < 10:
                    if (check_direction(ship, "right")):
                        for i in range(1, map[ship]):
                            Board[x/24 + i][y/24] = 'grey'
                        draw_board(Board)
                        return
                if event.key == pygame.K_LEFT and (x/24-(map[ship]-1)) > -1:
                    if (check_direction(ship, "left")):
                        for i in range(1, map[ship]):
                            Board[x/24 - i][y/24] = 'grey'
                        draw_board(Board)
                        return
                if event.key == pygame.K_UP and (y/24-(map[ship]-1)) > -1:
                    if (check_direction(ship, "up")):
                        for i in range(1, map[ship]):
                            Board[x/24][y/24 - i] = 'grey'
                        draw_board(Board)
                        return
                if event.key == pygame.K_DOWN and (y/24+(map[ship]-1)) < 10:
                    if (check_direction(ship, "down")):
                        for i in range(1, map[ship]):
                            Board[x/24][y/24 + i] = 'grey'
                        draw_board(Board)
                        return


def check_direction(ship, direction):
    check = True
    if (direction == "right"):
        for i in range(1, map[ship]):
            if (Board[x/24 + i][y/24] == 'grey'):
                check = False
    if (direction == "left"):
        for i in range(1, map[ship]):
            if (Board[x/24 - i][y/24] == 'grey'):
                check = False
    if (direction == "up"):
        for i in range(1, map[ship]):
            if (Board[x/24][y/24 - i] == 'grey'):
                check = False
    if (direction == "down"):
        for i in range(1, map[ship]):
            if (Board[x/24][y/24 + i] == 'grey'):
                check = False
    if (check == False):
        print "Pick valid direction!"
    return check



def place_ship():
    global x
    global y
    global Board


    print "place ship"
    for ship in ships:
        ship_location()
        ship_direction(ship)

def resume():
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return


def play(socket, player):
    global Board
    global play_board
    global opponent_board

    while 1:
        #set the frequency on how often to check for user input
        draw_board(play_board)
        if player == 'Player 1':

            shoot()

            socket.send('sending')
            if socket.recv(1024) == 'send':
                socket.sendall(simplejson.dumps(opponent_board))

            if check_win():
                break

            temp = socket.recv(1024)
            Board = simplejson.loads(temp)
            draw_board(Board)

            if check_loss():
                break
            resume()


        if player == 'Player 2':

            if socket.recv(1024) == 'sending':
                socket.send('send')

            temp = socket.recv(1024)
            Board = simplejson.loads(temp)
            draw_board(Board)

            if check_loss():
                break

            resume()

            shoot()

            socket.sendall(simplejson.dumps(opponent_board))
            if check_win():
                break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Closing.'
        serverSocket.shutdown(SHUT_RDWR)
        serverSocket.close()
