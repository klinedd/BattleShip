#!/usr/bin/env python2

import copy, random, math
import pygame, sys
from pygame.locals import *
from socket import *
import os.path
import simplejson

serverPort = 12000
serverSocket = 0

pygame.init()

screen = pygame.display.set_mode((320,240))
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

#create matrix that will hold information of the board game
w, h = 10,10
Board = [[0 for x in range(w)] for y in range(h)]
opponent_board = [[0 for x in range(w)] for y in range(h)]
play_board = [[0 for x in range(w)] for y in range(h)]

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

def server():
    #socket setup
    global serverSocket
    global Board
    global opponent_board

    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',serverPort))
    serverSocket.listen(1)

    print "The server has started.\nUse ctrl-c to quit."
    #waiting for connection
    connectionSocket, addr = serverSocket.accept()

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

    #closes socket after quit
    connectionSocket.shutdown(SHUT_RDWR)
    connectionSocket.close()

def client():
    global Board
    global opponent_board
    #input server IP
    serverName = raw_input('Enter server IP: ')

    #socket setup
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    print 'Client started.\nValid command is send\nEnter \'q\' to quit.'

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

def key_press(key):
    global opponent_board
    global play_board
    global x
    global y
    if key[pygame.K_RIGHT]:
        if x < 24*(size-1): x+=24
    if key[pygame.K_LEFT]:
        if x > 24: x-=24
    if key[pygame.K_UP]:
        if y > 24: y-=24
    if key[pygame.K_DOWN]:
        if y < 24*(size-1): y+=24
    if key[pygame.K_RETURN]:
        if opponent_board[x/24][y/24] == 'grey':
            play_board[x/24][y/24]  = 'red'
            opponent_board[x/24][y/24]  = 'red'
            return 1
        elif play_board[x/24][y/24]  == 'red':
            pass
        elif play_board[x/24][y/24]  == 'yellow':
            pass
        else:
            play_board[x/24][y/24] = 'yellow'
            opponent_board[x/24][y/24] = 'yellow'
            return 1


def ship_location(key):
    global x
    global y
    if key[pygame.K_RETURN]:
        Board[x/24][y/24] = 'grey'
        return 1
    if key[pygame.K_RIGHT]:
        if x < 24*(size-1): x+=24
    if key[pygame.K_LEFT]:
        if x > 24: x-=24
    if key[pygame.K_UP]:
        if y > 24: y-=24
    if key[pygame.K_DOWN]:
        if y < 24*(size-1): y+=24

def ship_direction(key, ship):
    global map
    if key[pygame.K_RIGHT] and (x/24+(map[ship]-1)) < 10:
        for i in range(1, map[ship]):
            Board[x/24 + i][y/24] = 'grey'
        return 1
    if key[pygame.K_LEFT] and (x/24-(map[ship]-1)) > -1:
        for i in range(1, map[ship]):
            Board[x/24 - i][y/24] = 'grey'
        return 1
    if key[pygame.K_UP] and (y/24-(map[ship]-1)) > -1:
        for i in range(1, map[ship]):
            Board[x/24][y/24 - i] = 'grey'
        return 1
    if key[pygame.K_DOWN] and (y/24+(map[ship]-1)) < 10:
        for i in range(1, map[ship]):
            Board[x/24][y/24 + i] = 'grey'
        return 1
    else:
        return 0

def place_ship():
    global x
    global y
    global Board

    print "place ship"
    for ship in ships:
        while 1:
            clock.tick(13)
            draw_board(Board)
            key = pygame.key.get_pressed()
            if ship_location(key) == 1:
                break
            pygame.event.pump()

        while 1:
            clock.tick(13)
            draw_board(Board)
            key = pygame.key.get_pressed()
            if ship_direction(key, ship) == 1:
                draw_board(Board)
                break
            pygame.event.pump()

def shoot():
    global play_board
    print pygame.event.peek()
    pygame.event.clear()
    print pygame.event.peek()
    while 1:
        draw_board(play_board)
        clock.tick(13)
        key = pygame.key.get_pressed()
        if key_press(key) == 1:
            draw_board(play_board)
            break
        pygame.event.pump()

def resume():
    print pygame.event.peek()
    pygame.event.clear()
    print pygame.event.peek()
    while 1:
        key = pygame.key.get_pressed()
        if key[pygame.K_RETURN]:
            break
        pygame.event.pump()

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

            temp = socket.recv(1024)
            Board = simplejson.loads(temp)
            draw_board(Board)

            resume()
            clock.tick(100)

        if player == 'Player 2':

            if socket.recv(1024) == 'sending':
                socket.send('send')

            temp = socket.recv(1024)
            Board = simplejson.loads(temp)
            draw_board(Board)

            resume()
            clock.tick(100)
            shoot()

            socket.sendall(simplejson.dumps(opponent_board))





        #event handlers to eithe quit the program or whipe the board back to  a blank grid
        pygame.event.pump()
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

# def print_board(s,board):

# 	# WARNING: This function was crafted with a lot of attention. Please be aware that any
# 	#          modifications to this function will result in a poor output of the board
# 	#          layout. You have been warn.

# 	#find out if you are printing the computer or user board
# 	player = "Computer"
# 	if(s == "u"):
# 		player = "User"

# 	print("The " + player + "'s board look like this: \n")

# 	#print the horizontal numbers
# 	print( " "),
# 	for i in range(10):
# 		print( "  " + str(i+1) + "  "),
# 	print( "\n")

# 	for i in range(10):

# 		#print the vertical line number
# 		if i != 9:
# 			print( str(i+1) + "  "),
# 		else:
# 			print( str(i+1) + " "),

# 		#print the board values, and cell dividers
# 		for j in range(10):
# 			if board[i][j] == -1:
# 				print( ' '),
# 			elif s == "u":
# 				print( board[i][j]),
# 			elif s == "c":
# 				if board[i][j] == "*" or board[i][j] == "$":
# 					print( board[i][j]),
# 				else:
# 					print( " "),

# 			if j != 9:
# 				print( " | "),
# 		print

# 		#print a horizontal line
# 		if i != 9:
# 			print( "   ----------------------------------------------------------")
# 		else:
# 			print("")

# def user_place_ships(board,ships):

# 	for ship in ships.keys():

# 		#get coordinates from user and validate the postion
# 		valid = False
# 		while(not valid):

# 			print_board("u",board)
# 			print( "Placing a/an " + ship)
# 			x,y = get_coor()
# 			ori = v_or_h()
# 			valid = validate(board,ships[ship],x,y,ori)
# 			if not valid:
# 				print( "Cannot place a ship there.\nPlease take a look at the board and try again.")
# 				raw_input("Hit ENTER to continue")

# 		#place the ship
# 		board = place_ship(board,ships[ship],ship[0],ori,x,y)
# 		print_board("u",board)

# 	raw_input("Done placing user ships. Hit ENTER to continue")
# 	return board


# def computer_place_ships(board,ships):

# 	for ship in ships.keys():

# 		#genreate random coordinates and vlidate the postion
# 		valid = False
# 		while(not valid):

# 			x = random.randint(1,10)-1
# 			y = random.randint(1,10)-1
# 			o = random.randint(0,1)
# 			if o == 0:
# 				ori = "v"
# 			else:
# 				ori = "h"
# 			valid = validate(board,ships[ship],x,y,ori)

# 		#place the ship
# 		print( "Computer placing a/an " + ship)
# 		board = place_ship(board,ships[ship],ship[0],ori,x,y)

# 	return board


# def place_ship(board,ship,s,ori,x,y):

# 	#place ship based on orientation
# 	if ori == "v":
# 		for i in range(ship):
# 			board[x+i][y] = s
# 	elif ori == "h":
# 		for i in range(ship):
# 			board[x][y+i] = s

# 	return board

# def validate(board,ship,x,y,ori):

# 	#validate the ship can be placed at given coordinates
# 	if ori == "v" and x+ship > 10:
# 		return False
# 	elif ori == "h" and y+ship > 10:
# 		return False
# 	else:
# 		if ori == "v":
# 			for i in range(ship):
# 				if board[x+i][y] != -1:
# 					return False
# 		elif ori == "h":
# 			for i in range(ship):
# 				if board[x][y+i] != -1:
# 					return False

# 	return True

# def v_or_h():

# 	#get ship orientation from user
# 	while(True):
# 		user_input = raw_input("vertical or horizontal (v,h) ? ")
# 		if user_input == "v" or user_input == "h":
# 			return user_input
# 		else:
# 			print( "Invalid input. Please only enter v or h")

# def get_coor():

# 	while (True):
# 		user_input = raw_input("Please enter coordinates (row,col) ? ")
# 		try:
# 			#see that user entered 2 values seprated by comma
# 			coor = user_input.split(",")
# 			if len(coor) != 2:
# 				raise Exception("Invalid entry, too few/many coordinates.");

# 			#check that 2 values are integers
# 			coor[0] = int(coor[0])-1
# 			coor[1] = int(coor[1])-1

# 			#check that values of integers are between 1 and 10 for both coordinates
# 			if coor[0] > 9 or coor[0] < 0 or coor[1] > 9 or coor[1] < 0:
# 				raise Exception("Invalid entry. Please use values between 1 to 10 only.")

# 			#if everything is ok, return coordinates
# 			return coor

# 		except ValueError:
# 			print( "Invalid entry. Please enter only numeric values for coordinates")
# 		except Exception as e:
# 			print( e)

# def make_move(board,x,y):

# 	#make a move on the board and return the result, hit, miss or try again for repeat hit
# 	if board[x][y] == -1:
# 		return "miss"
# 	elif board[x][y] == '*' or board[x][y] == '$':
# 		return "try again"
# 	else:
# 		return "hit"

# def user_move(board):

# 	#get coordinates from the user and try to make move
# 	#if move is a hit, check ship sunk and win condition
# 	while(True):
# 		x,y = get_coor()
# 		res = make_move(board,x,y)
# 		if res == "hit":
# 			print( "Hit at " + str(x+1) + "," + str(y+1))
# 			check_sink(board,x,y)
# 			board[x][y] = '$'
# 			if check_win(board):
# 				return "WIN"
# 		elif res == "miss":
# 			print( "Sorry, " + str(x+1) + "," + str(y+1) + " is a miss.")
# 			board[x][y] = "*"
# 		elif res == "try again":
# 			print( "Sorry, that coordinate was already hit. Please try again")

# 		if res != "try again":
# 			return board

# def computer_move(board):

# 	#generate user coordinates from the user and try to make move
# 	#if move is a hit, check ship sunk and win condition
# 	while(True):
# 		x = random.randint(1,10)-1
# 		y = random.randint(1,10)-1
# 		res = make_move(board,x,y)
# 		if res == "hit":
# 			print( "Hit at " + str(x+1) + "," + str(y+1))
# 			check_sink(board,x,y)
# 			board[x][y] = '$'
# 			if check_win(board):
# 				return "WIN"
# 		elif res == "miss":
# 			print( "Sorry, " + str(x+1) + "," + str(y+1) + " is a miss.")
# 			board[x][y] = "*"

# 		if res != "try again":

# 			return board

# def check_sink(board,x,y):

# 	#figure out what ship was hit
# 	if board[x][y] == "A":
# 		ship = "Aircraft Carrier"
# 	elif board[x][y] == "B":
# 		ship = "Battleship"
# 	elif board[x][y] == "S":
# 		ship = "Submarine"
# 	elif board[x][y] == "D":
# 		ship = "Destroyer"
# 	elif board[x][y] == "P":
# 		ship = "Patrol Boat"

# 	#mark cell as hit and check if sunk
# 	board[-1][ship] -= 1
# 	if board[-1][ship] == 0:
# 		print( ship + " Sunk")


# def check_win(board):

# 	#simple for loop to check all cells in 2d board
# 	#if any cell contains a char that is not a hit or a miss return false
# 	for i in range(10):
# 		for j in range(10):
# 			if board[i][j] != -1 and board[i][j] != '*' and board[i][j] != '$':
# 				return False
# 	return True

# def main():

# 	#types of ships
# 	ships = {"Aircraft Carrier":5,
# 		     "Battleship":4,
#  		     "Submarine":3,
# 		     "Destroyer":3,
# 		     "Patrol Boat":2}

# 	#setup blank 10x10 board
# 	board = []
# 	for i in range(10):
# 		board_row = []
# 		for j in range(10):
# 			board_row.append(-1)
# 		board.append(board_row)

# 	#setup user and computer boards
# 	user_board = copy.deepcopy(board)
# 	comp_board = copy.deepcopy(board)

# 	#add ships as last element in the array
# 	user_board.append(copy.deepcopy(ships))
# 	comp_board.append(copy.deepcopy(ships))

# 	#ship placement
# 	user_board = user_place_ships(user_board,ships)
# 	comp_board = computer_place_ships(comp_board,ships)

# 	#game main loop
# 	while(1):

# 		#user move
# 		print_board("c",comp_board)
# 		comp_board = user_move(comp_board)

# 		#check if user won
# 		if comp_board == "WIN":
# 			print( "User WON! :)")
# 			quit()

# 		#display current computer board
# 		print_board("c",comp_board)
# 		raw_input("To end user turn hit ENTER")

# 		#computer move
# 		user_board = computer_move(user_board)

# 		#check if computer move
# 		if user_board == "WIN":
