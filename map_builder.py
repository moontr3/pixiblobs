
import pygame as pg
from typing import *
import os

pg.init()

size = [
    int(input(f'Enter X size > ')),
    int(input(f'Enter Y size > '))
]
name = input(f'Enter map name > ')

zoom = 20

window = pg.display.set_mode((size[0]*zoom,size[1]*zoom))
running = True

drawn: List[Tuple[int,int]] = []

def save():
    if not os.path.exists(f'maps/'):
        os.mkdir('maps/')

    with open(f'maps/{name}.pbmap', 'w') as f:
        data = [size]+drawn
        
        _data = []
        for i in data:
            _data.extend(i)

        text = ';'.join([str(i) for i in _data])

        f.write(text)


print('''
Use LMB to draw
Use RMB to erase
Use S (or close the app) to save
Use Mouse wheel to zoom
''')


while running:
    window.fill((0,0,0))

    # mouse pos
    mouse_pos = pg.mouse.get_pos() # mouse pos relative to the topleft of the window
    tile = [
        max(0, min(int(mouse_pos[0]/zoom), size[0]-1)),
        max(0, min(int(mouse_pos[1]/zoom), size[1]-1))
    ]

    # events
    events = pg.event.get()

    for event in events:
        # quitting the game
        if event.type == pg.QUIT:
            running = False 
            save()

        # saving
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_s:
                try:
                    save()
                except Exception as e:
                    print(f'Error while saving: {e}')
                else:
                    print(f'Saved into maps/{name}.pbmap')

        # zoom
        if event.type == pg.MOUSEWHEEL:
            zoom = max(1, zoom+event.y)
            window = pg.display.set_mode((size[0]*zoom,size[1]*zoom))

    # drawing
    if pg.mouse.get_pressed(3)[0]:
        if tile not in drawn:
            drawn.append(tile)

    # erasing
    if pg.mouse.get_pressed(3)[2]:
        if tile in drawn:
            drawn.remove(tile)

    # displaying
    for i in drawn:
        rect = pg.Rect(i[0]*zoom, i[1]*zoom, zoom,zoom)
        pg.draw.rect(window, (0,255,255), rect)

    rect = pg.Rect(tile[0]*zoom, tile[1]*zoom, zoom,zoom)
    pg.draw.rect(window, (255,255,255), rect, 1)


    pg.display.flip()
