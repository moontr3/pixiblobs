
import pygame as pg
import draw
import time
from typing import *
from manager import *
from config import *

pg.init()

# window size, changes on resize
screenx = 1280
screeny = 720
# screen aspect ratio x:y
ratiox = 16
ratioy = 9

clock = pg.time.Clock()
dfps = 0.0       # current fps
prev_dfps = 0.0  # previous fps
fps = 0          # target fps (0 - no limit)
timedelta = 0.0  # timedelta
                 # how much time passed between two frames
                 # used to run the game independent of framerate

window = pg.display.set_mode((screenx,screeny), pg.RESIZABLE) # the window surface
screen = pg.Surface((APPX, APPY)) # the surface that everything gets
                                        # drawn on, this surface is then scaled
                                        # to fit in the window correctly and then gets
                                        # drawn to the window surface

running = True
pg.display.set_caption('くそ')
pg.display.set_icon(pg.image.load('res/images/unknown.png'))


# app functions 

def draw_debug(surface:pg.Surface):
    '''
    Draws debug data on top of the screen.
    '''    
    # fps graph
    if dfps != prev_dfps:
        fps_graph.append(dfps)
    if len(fps_graph) > APPX:
        fps_graph.pop(0)
    if len(fps_graph) >= 2:
        pg.draw.lines(screen, (255,255,255), False, [(i,APPY-val/2) for i, val in enumerate(fps_graph)])

    # text
    draw.text(surface, f'fps: {dfps}{f" / {fps}" if fps != 0 else ""}', (2,2))
    draw.text(surface, f'timedelta: {round(timedelta,6)}', (2,12))


def update_size():
    '''
    This function updates the values of how the window
    is supposed to scale. Should be called when the window
    gets resized.
    '''
    global sizex, sizey, screenx, screeny, windowrect

    # calculating the size of the screen
    if screenx/ratiox > screeny/ratioy:
        sizex = screeny/ratioy*ratiox
        sizey = screeny
    elif screeny/ratioy > screenx/ratiox:
        sizex = screenx
        sizey = screenx/ratiox*ratioy
    else:
        sizex = screenx
        sizey = screeny

    # updating rect of the screen
    windowrect = pg.Rect(0,0,sizex, sizey)
    windowrect.center = (screenx/2, screeny/2)


# app variables

app = Manager()
debug_opened = False
fps_graph = []


# preparation 

update_size()


# main loop

while running:
    # timedelta
    start_timedelta = time.time()

    # mouse pos
    global_mouse_pos = pg.mouse.get_pos() # mouse pos relative to the topleft of the window
    
    mouse_pos = [
        int((global_mouse_pos[0]-windowrect.left)/(sizex/APPX)),
        int((global_mouse_pos[1]-windowrect.top)/(sizey/APPY))
    ] # mouse pos relative to the topleft of the "screen" variable

    # events
    events = pg.event.get()

    for event in events:
        # quitting the game
        if event.type == pg.QUIT:
            running = False 

        if event.type == pg.VIDEORESIZE:
            # resizing the window
            screenx = event.w
            screeny = event.h
            # limiting window dimensions
            if screenx <= APPX:
                screenx = APPX
            if screeny <= APPY:
                screeny = APPY
            # updating size
            update_size()
            window = pg.display.set_mode((screenx,screeny), pg.RESIZABLE)

        # enabling/disabling debug mode
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_F3:
                debug_opened = not debug_opened
                fps_graph = []

    # updating app
    if app != None:
        app.update(timedelta, events, mouse_pos)
        app.draw(screen)

    # drawing debug
    if debug_opened:
        draw_debug(screen)

    # drawing window
    surface = pg.transform.scale(screen, (sizex, sizey)) # scaling the surface
    window.blit(surface, windowrect) # drawing the surface on screen
    pg.display.flip()

    # timing stuff
    clock.tick(fps)
    prev_dfps = float(dfps)
    dfps = round(clock.get_fps(), 2) # getting fps
    timedelta = time.time()-start_timedelta # calculating timedelta for the next frame