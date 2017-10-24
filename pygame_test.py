#!/usr/bin/env python3
import os
import pygame
import time
import random
import sys
from pygame.locals import *
 
class pyscope :
    screen = None;
    
    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print "I'm running under X display = {0}".format(disp_no)
        
        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                print 'Driver: {0} failed.'.format(driver)
                continue
            found = True
            break
    
        if not found:
            raise Exception('No suitable video driver found!')
        
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        print "Framebuffer size: %d x %d" % (size[0], size[1])
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))        
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.display.update()
 
    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."
 
    def test(self):
       pygame.init()

size = input('What X by X size grid do you want?')
screen = pygame.display.set_mode((100*size,100*size))

#variables used to keep track of where the "etch-a-sketch" is writing
x=0
y=0

#variables used to increment the lines being drawn to create the grid on the screen
x1 = 0
y1 = 0

#initializing a blank screen and creating a clock 
clock = pygame.time.Clock()
screen.fill((255,255,255))

#a continuous while loop so key inputs can always be searched for
while 1:
    #set the frequency on how often to check for user input
    clock.tick(13)

    #creates the rectangle that is drawn where the x and y variables are pointing to
    Rect = pygame.Rect(x, y, 100, 100)
    pygame.draw.rect(screen, (0,0,0), Rect)

    #draws the lines for the grid on the screen
    for i in range(size - 1):
        pygame.draw.line(screen, (0,0,0), (x1, y1+(i*100)+100), (x1+100*size, y1+(i*100)+100))
        pygame.draw.line(screen, (0,0,0), (x1+100+(i*100), y1), (x1+100+(i*100), y1+100*size))
    pygame.display.update()

    #looks for when any of the arrow keys are pressed and sets the x and y variables accordingly
    #also checks to make sure the "etch-a-sketch" does not go off the edge of the screen
    key = pygame.key.get_pressed()
    if key[pygame.K_RIGHT]:
        if x < 100*(size-1): x+=100
    if key[pygame.K_LEFT]:
        if x > 50: x-=100
    if key[pygame.K_UP]:
        if y > 50: y-=100
    if key[pygame.K_DOWN]:
        if y < 100*(size-1): y+=100

    #event handlers to eithe quit the program or whipe the board back to  a blank grid
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_SPACE:
            screen.fill((255,255,255))
 
# Create an instance of the PyScope class
scope = pyscope()
scope.test()
time.sleep(10)
