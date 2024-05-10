
from typing import *
import pygame as pg
from config import *
import game
import json
import config
import os
import glob
import easing_functions as easing
import random
import draw


# map dataclass

class SaveMap:
    def __init__(self,
        size: Tuple[int,int],
        water_tiles: List[Tuple[int,int]],
        name: str
    ):
        '''
        Represents a map data.
        '''
        self.size: Tuple[int,int] = size
        self.water_tiles: List[Tuple[int,int]] = water_tiles

        self.ratio_x_to_y: float = size[0]/size[1]

        self.name: str = name


    @staticmethod
    def from_file(path:str) -> "SaveMap | None":
        '''
        Loads the passed file and returns a SaveMap object.

        None if unable to read the map.
        '''
        try:
            # reading file
            with open(path) as f:
                data = f.read()

            # deserialising
            _coords = [int(i) for i in data.split(';')]
            assert len(_coords)%2 == 0,\
                'Non-even position data length'
            
            coords: List[Tuple[int,int]] = []
            
            for i in range(len(_coords)//2):
                coords.append([_coords[i], _coords[i+1]])

            # saving data to object
            assert len(coords) >= 1, 'No size in file'

            size: Tuple[int,int] = coords[0]
            tiles: List[Tuple[int,int]] = list(coords[1:])
            name: str = os.path.basename(path)

            return SaveMap(size, tiles, name)

        except Exception as e:
            print(f'Unable to load map {path}: {e}')


# button class

class Button:
    def __init__(self,
        rect: pg.Rect,
        text: str, 
        callback: Callable
    ):
        '''
        Represents a button on the screen.
        '''
        self.rect: pg.Rect = rect
        self.text: str = text
        self.callback: Callable = callback

        self.hovered: bool = False


    def draw(self, surface:pg.Surface):
        '''
        Draws the button on the screen.
        '''
        # rect
        pg.draw.rect(surface,
            (180,180,180) if self.hovered else (210,210,210),
            self.rect, 0, 4
        )

        # text
        draw.text(surface, self.text,
            (self.rect.left+7, self.rect.centery),
            v=0.5
        )


# menu template

class Menu:
    def __init__(self):
        '''
        Represents a menu.
        '''


    def update_input(self, events:List[pg.Event], mouse_pos:Tuple[int,int]):
        '''
        Updates all the input variables.
        '''
        self.mouse_pos: Tuple[int,int] = mouse_pos
        self.mouse_press: Tuple[bool,bool,bool] = pg.mouse.get_pressed(3)
        self.mouse_wheel: float = 0.0
        self.keys_held = pg.key.get_pressed() # keys that are being held
        self.keys_down: List[int] = [] # list of keys that are just pressed in the current frame
        self.lmb_down = False # whether the left mouse button just got held in the current frame

        # processing events
        for event in events:
            # registering pressed keys
            if event.type == pg.KEYDOWN:
                self.keys_down.append(event.key)
            
            # registering mouse wheel events
            if event.type == pg.MOUSEWHEEL:
                self.mouse_wheel = event.y

            # registering mouse events
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == pg.BUTTON_LEFT:
                    self.lmb_down = True


    def draw(self, surface:pg.Surface):
        '''
        Draws the menu.
        '''
        surface.fill((230,230,230))


    def update(self, td:float, events:List[pg.Event], mouse_pos:Tuple[int,int]):
        '''
        Updates the menu.
        '''
        self.update_input(events, mouse_pos)


# main menu

class MainMenuObject:
    def __init__(self, image:str, rect:pg.FRect):
        '''
        Represents an object on the background of the menu.
        '''
        self.rect: pg.FRect = rect
        self.image: str = image
        self.deletable: bool = False


    def draw(self, surface:pg.Surface):
        '''
        Draws the object.
        '''
        draw.image(
            surface, self.image,
            (self.rect.centerx, round(self.rect.centery)),
            (TILESIZE,TILESIZE), 0.5, 0.5
        )


    def update(self, td:float):
        '''
        Updates the object.
        '''
        self.rect.y += td*15

        if self.rect.top > APPY:
            self.deletable = True


class MainMenu(Menu):
    def __init__(self, start_cb):
        '''
        Represents a main menu.
        '''
        super().__init__()

        self.buttons: List[Button] = [
            Button(
                pg.Rect(30,130,100,20), 'play', start_cb
            ),
            Button(
                pg.Rect(30,160,100,20), 'quit', exit
            )
        ]

        self.pos: float = 0.0
        self.objects: List[MainMenuObject] = []

        # filling the screen with objects
        pos = 0
        index = 0
        while pos-TILESIZE < APPY:
            self.populate_objects(index)
            index += 1
            pos += TILESIZE


    def populate_objects(self, row:int=0):
        '''
        Populates objects on the chosen row.
        '''
        pos = 0
        while pos-TILESIZE < APPX:
            if random.random() < 0.85:
                pos += TILESIZE
                continue

            # generating rect
            rect = pg.FRect(0,0,TILESIZE,TILESIZE)
            rect.bottomleft = (pos,row*TILESIZE)

            # generating image
            image: str = random.choices(
                ['tree.png','tree2.png','grass.png','grass2.png'],
                weights=[1.0, 1.0, 0.7, 0.7]
            )[0]

            # continuing
            self.objects.append(MainMenuObject(
                image, rect
            ))
            pos += TILESIZE

    
    def draw(self, surface:pg.Surface):
        '''
        Draws the main menu.
        '''
        surface.fill((230,230,230))

        # objects
        for i in self.objects:
            i.draw(surface)
        
        # game title
        draw.text(
            surface, 'pixiblobs', (30, 70),
            size=32, style='title', antialias=True
        )

        # buttons
        for i in self.buttons:
            i.draw(surface)

    
    def update(self, td:float, *args, **kwargs):
        '''
        Updates the main menu.
        '''
        self.update_input(*args, **kwargs)

        # objects
        new = []

        for i in self.objects:
            i.update(td)
            if not i.deletable:
                new.append(i)

        self.objects = new

        # generating new objects
        self.pos += td*15

        while self.pos >= TILESIZE:
            self.pos -= TILESIZE
            self.populate_objects()

        # buttons
        for i in self.buttons:
            i.hovered = i.rect.collidepoint(self.mouse_pos)

            # button clicked
            if self.lmb_down and i.hovered:
                i.callback()


# transition

class Transition:
    def __init__(self, old_menu: Menu, new_menu: Menu):
        '''
        Represents a transition between two menus.
        '''
        self.old: Menu = old_menu
        self.new: Menu = new_menu

        self.key: float = 0.0
        self.smooth_key: float = 0.0
        self.ease = easing.QuadEaseInOut(0,2,2)

        self.pattern: List[int] = []
        for i in range(APPX//6):
            self.pattern.extend([random.randint(0,APPY), 0])


    def draw(self, surface:pg.Surface):
        '''
        Draws the transition and the menu.
        '''
        # old menu
        if self.key < 1.0:
            self.old.draw(surface)

        # new menu
        else:
            self.new.draw(surface)

        # rect
        rect = pg.Rect(
            0, APPY-(APPY*self.smooth_key),
            APPX, APPY
        )
        pg.draw.rect(surface, (255,255,255), rect)

        # these white lines on top
        if self.key < 1.0:
            pos = 0
            points = [(0,rect.top)]
            for i in self.pattern:
                points.append(
                    (pos, rect.top-i*self.smooth_key)
                )
                pos += 3

            pg.draw.polygon(surface, (255,255,255), points)

        # these white lines on the bottom
        else:
            pos = 0
            points = [(0,0)]
            for i in self.pattern:
                points.append(
                    (pos, rect.bottom+i*(2-self.smooth_key))
                )
                pos += 3

            pg.draw.polygon(surface, (255,255,255), points)

    
    def update(self, td:float):
        '''
        Updates the transition.
        '''
        self.key += td*3
        
        self.smooth_key = self.ease.ease(self.key)


# manager class

class Manager:
    def __init__(self):
        '''
        Manages all scenes, menus and so on.
        '''
        self.reload_data()

        self.saved_game: "game.Game | None" = None
        self.menu = MainMenu(self.start_cb)
        self.transition: "Transition | None" = None


    def biome_cb(self):
        '''
        Updates the biome on the background of the menu.
        '''


    def start_cb(self):
        '''
        Callback for starting or continuing a game.
        '''
        if self.saved_game == None:
            self.saved_game = game.Game(
                self.pause_cb, self.maps[0].size,
                self.data, 'default', 'default',
                [10,10], self.maps[0].water_tiles
            )

        self.transition = Transition(
            self.menu, self.saved_game
        )


    def pause_cb(self):
        '''
        Callback for pausing the game.
        '''
        self.saved_game = self.menu

        self.transition = Transition(
            self.menu, MainMenu(self.start_cb)
        )

    
    def reload_data(self):
        '''
        Reloads file data.
        '''
        # datapack
        with open(config.DATAPACK_FILE, encoding='utf-8') as f:
            self.data = json.load(f)

        # maps
        self.maps: List[SaveMap] = []

        for i in glob.glob(config.MAPS_FOLDER+'/*.pbmap'):
            map = SaveMap.from_file(i)
            if map != None:
                self.maps.append(map)


    def draw(self, surface:pg.Surface):
        '''
        Draws the current menu.
        '''
        if self.transition != None:
            self.transition.draw(surface)
            return
        
        self.menu.draw(surface)
    
    
    def update(self, td:float, events:List[pg.Event], mouse_pos:Tuple[int,int]):
        '''
        Updates the current menu.
        '''
        if self.transition != None:
            self.transition.update(td)

            if self.transition.key >= 2.0:
                self.menu = self.transition.new
                self.transition = None
            return

        self.menu.update(td, events, mouse_pos)