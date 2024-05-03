
from typing import *
import pygame as pg
from config import *
import game
import json
import config


# manager class

class Manager:
    def __init__(self):
        '''
        Manages all scenes, menus and so on.
        '''
        with open(config.DATAPACK_FILE, encoding='utf-8') as f:
            self.data = json.load(f)

        self.menu = game.Game((25,25), self.data, 'default', 'default', (10,10))


    def draw(self, surface:pg.Surface):
        '''
        Draws the current menu.
        '''
        self.menu.draw(surface)
    
    
    def update(self, td:float, events:List[pg.Event], mouse_pos:Tuple[int,int]):
        '''
        Updates the current menu.
        '''
        self.menu.update(td, events, mouse_pos)