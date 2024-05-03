
from typing import *
import pygame as pg
from config import *
import draw
import random
import utils
import easing_functions as easing
import numpy as np
from copy import deepcopy

# event class

class Event:
    def __init__(self, type:str, meta:any=None):
        self.type: str = type
        self.meta: any = meta


# enemy classes

# todo - base enemy class
# todo - different enemy classes
# todo - spawning enemies on click


class Enemy:
    def __init__(self,
        type:str,
        name:str,
        pos:Tuple[int,int],
        castle:Tuple[int,int],
        image:str,
        size:Tuple[int,int],
        speed:float, 
        hp:int,
        cost:int,
        clock:float = 1.0,
        phase_through:"List[str] | None"=[],
        collision_strength:float=1.0
    ):
        '''
        A base enemy class to inherit from.
        '''
        self.type: str = type
        self.name: str = name
        self.image: str = image
        self.size: Tuple[int,int] = size
        self.cost: int = cost

        self.speed: float = speed
        self.pos = utils.VectorCoord(
            pos, 0, 0, 0
        )
        self.walk_towards(castle)

        self.castle: Tuple[int,int] = castle
        self.update_rect()

        self.clock: float = clock
        self.clock_timer: float = 0

        self.hp: int = hp
        self.max_hp: int = hp
        self.deletable: bool = False

        self.phase_through: "List[str] | None" = phase_through
            # set above to None to phase through everything
        self.collision_strength: float = collision_strength
        self.collided: "Object | None" = None

        self.ease = easing.ElasticEaseOut()
        self.wobbliness: float = 0.0
        self.wobbliness_sin: float = 0.0


    def kick(self, strength:float, add:bool=False, reset:bool=True):
        '''
        Wobbles the object. There is no particular
        reason on calling the function "kick" btw.
        '''
        if add:
            self.wobbliness += strength
        elif self.wobbliness < strength:
            self.wobbliness = strength

        if reset:
            self.wobbliness_sin = 0.0


    def damage(self, amount:int=1):
        '''
        Damages the enemy.
        '''
        self.kick(1.5)
        self.hp -= amount
        if self.hp <= 0:
            self.deletable = True


    def update_rect(self):
        '''
        Updates the enemy's rect.
        '''
        self.rect = pg.FRect(0,0,
            self.size[0]/TILESIZE, self.size[1]/TILESIZE
        )
        self.rect.center = self.pos.pos

    
    def walk_towards(self, pos:Tuple[int,int]):
        '''
        Makes the enemy walk towards the passed tile.
        '''
        self.pos.point_towards(pos)
        self.pos.speed = self.speed


    def call_clock(self, map:"Map"):
        '''
        Gets called every `self.clock` seconds.
        '''
        pass


    def call_collision(self, obj:"Object"):
        '''
        Gets called if collided with an object.
        '''
        # jumping away
        angle = utils.angle_between(obj.center, self.pos.pos)+np.pi/2
        self.pos.deg = angle
        self.pos.speed = self.collision_strength
        self.collided = obj


    def check_collisions(self, map:"Map"):
        '''
        Checks the collisions with all the
        tiles on the map and calls 
        `self.call_collision()` for each collided tile
        '''
        for obj in map.objects:
            if obj.meta.walkable:
                continue

            if self.collided and obj.pos == self.collided.pos:
                continue

            for tag in self.phase_through:
                if tag in obj.tag:
                    continue

            if self.rect.colliderect(obj.rect):
                self.call_collision(obj)
                obj.damage()
                self.kick(1.2)
                break


    def draw(self, surface:pg.Surface, pos:Tuple[int,int]):
        '''
        Draws the enemy at a designated position.
        '''
        size = list(self.size)
        
        # wobbliness
        if self.wobbliness > 0.0:
            size[1] *= (np.sin(self.wobbliness_sin)*self.wobbliness)*0.3 + 1

        # drawing enemy
        draw.image(surface,
            self.image, pos, size, 0.5, 0.5,
            fliph=self.pos.pos[0] < self.castle[0],
            smooth=False
        )

        # debug - draws the vector lines and
        # debug - speeds of the entities
        # pg.draw.line(
        #     surface, (255,0,0), pos, (
        #         pos[0]+(np.sin(self.pos.deg))*15,
        #         pos[1]+(np.cos(self.pos.deg))*15
        #     ), 2
        # )
        # draw.text(
        #     surface, round(self.pos.speed, 2),
        #     (pos[0], pos[1]-20),
        #     h=0.5
        # )


    def update(self, td:float, map:"Map"):
        '''
        Updates the enemy.
        '''
        self.pos.update(td)
        self.update_rect()

        # clock
        if self.collided == None:
            self.clock_timer -= td

        if self.clock_timer <= 0.0:
            self.clock_timer = deepcopy(self.clock)
            self.walk_towards(self.castle)
            self.call_clock(map)

        # checking collisions
        if self.phase_through != None:
            self.check_collisions(map)

        # checking if collided
        if self.collided != None:
            self.pos.speed -= td

            if self.pos.speed <= 0.0:
                self.collided = None
                self.pos.deg += np.pi

        elif self.pos.speed < self.speed:
            self.pos.speed += td

            if self.pos.speed > self.speed:
                self.pos.speed = self.speed

        # updating wobbliness
        if self.wobbliness > 0.0:
            self.wobbliness -= td
            self.wobbliness_sin += (td*25) % 3.14



# different enemies

class Zombie(Enemy):
    def __init__(self, pos:Tuple[int,int], target:Tuple[int,int]):
        super().__init__(
            type='Zombie',
            name='Maxwell the Undead',
            pos=pos,
            castle=target,
            image='maxwell.png',
            size=(16,16),
            speed=0.5,
            hp=5,
            cost=10,
            clock=0.5,
            collision_strength=1
        )


class Skeleton(Enemy):
    def __init__(self, pos:Tuple[int,int], target:Tuple[int,int]):
        super().__init__(
            type='Skeleton',
            name='Bob the Boneful',
            pos=pos,
            castle=target,
            image='bob.png',
            size=(16,16),
            speed=1,
            hp=10,
            cost=35,
            clock=0.5,
            collision_strength=1
        )


# object classes

class ObjMeta:
    def __init__(self, name:str,
        images:List[str], size:Tuple[int,int],
        tiles:"List[Tuple[int,int]] | None"=None,
        tags:"List[str] | str | None"=None,
        hp:int=1, player_damage:bool=False,
        walkable:bool=False
    ):
        '''
        Represents an object's data.
        '''
        self.name: str = name
        
        self.images: List[str] = images
        self.size: Tuple[int,int] = size
        self.tiles: List[Tuple[int,int]] = tiles\
            if type(tiles) == list else None
        self.tags: List[str] = tags

        self.hp: int = hp
        self.player_damage: bool = player_damage

        self.walkable: bool = walkable

        # filling in tiles if there's none passed
        if self.tiles == None:
            self.tiles = []
            for y in range(size[1]):
                for x in range(size[0]):
                    self.tiles.append((x,y))
        

    @property
    def image(self) -> str:
        '''
        Returns a random image.
        '''
        return random.choice(self.images)
    

    @staticmethod
    def from_dict(data:dict) -> "ObjMeta":
        '''
        Converts a dict object to a ObjMeta object.
        '''
        return ObjMeta(
            data['name'], data['images'],
            data.get('size', [1,1]),
            data.get('tiles', None),
            data.get('tags', None),
            data.get('hp', 1),
            data.get('player_damage', False),
            data.get('walkable', False)
        )
    

class Object:
    def __init__(self,
        tag:"List[str] | str | None",
        pos:Tuple[int,int], meta:ObjMeta,
        intro_offset:float=0.0
    ):
        '''
        Represents an object on the map.
        '''
        self.image: str = meta.image

        self.tag: List[str] = [] if tag == None else\
            tag if type(tag) == list else [tag]
        self.meta: ObjMeta = meta
        self.events: List[Event] = []

        self.intro_offset: float = intro_offset
        self.intro_key: float = 0.0
        self.ease = easing.ElasticEaseOut()
        self.wobbliness: float = 0.0
        self.wobbliness_sin: float = 0.0

        self.pos: Tuple[int,int] = list(pos)
        self.update_rect()

        self.hp: int = deepcopy(self.meta.hp)
        self.player_damage: bool = self.meta.player_damage


    def kick(self, strength:float, add:bool=False, reset:bool=True):
        '''
        Wobbles the object. There is no particular
        reason on calling the function "kick" btw.
        '''
        if add:
            self.wobbliness += strength
        elif self.wobbliness < strength:
            self.wobbliness = strength

        if reset:
            self.wobbliness_sin = 0.0


    def damage(self, amount:int=1):
        '''
        Damages the object.
        '''
        self.hp -= amount
        self.kick(1.2)

        if self.hp <= 0:
            self.events.append(Event('delete'))

    
    def update_rect(self):
        '''
        Updates the rect of the object.
        '''
        # tiles
        self.tiles: List[Tuple[int,int]] = [(
            self.pos[0]+i[0],
            self.pos[1]+i[1]
        ) for i in self.meta.tiles]

        # rect
        self.rect = pg.FRect(self.pos, self.meta.size)
        self.center = self.rect.center


    def draw(self, surface:pg.Surface, pos:Tuple[int,int]):
        '''
        Draws the sprite at the designates position on the
        given surface.
        '''
        if self.intro_offset > 0.0:
            return

        size = [
            (self.meta.size[0]*TILESIZE),
            (self.meta.size[1]*TILESIZE)
        ]
        if self.intro_key < 1.0 or self.wobbliness > 0.0:
            # intro wobble
            if self.intro_key < 1.0:
                size[1] *= self.ease.ease(self.intro_key)

            # wobbliness
            if self.wobbliness > 0.0:
                size[1] *= (np.sin(self.wobbliness_sin)*self.wobbliness)*0.3 + 1
            
            # drawing
            pos[1] += self.meta.size[1]*TILESIZE
            draw.image(surface, self.image, pos, size, v=1, smooth=False)
            return
        
        draw.image(surface, self.image, pos, size)


    def update(self, td:float) -> List[Event]:
        '''
        Updates the object.

        Returns a list of events.
        '''
        # updating intro
        if self.intro_offset > 0.0:
            self.intro_offset -= td

        elif self.intro_key < 1.0:
            self.intro_key += td

        # updating wobbliness
        if self.wobbliness > 0.0:
            self.wobbliness -= td
            self.wobbliness_sin += (td*25) % 3.14

        events = self.events.copy()
        self.events = []
        return events



# popup class

class Popup:
    def __init__(self, type:str, obj:Object, pos:Tuple[int,int]):
        '''
        Represents a popup that gets displayed
        when the object or the enemy is covered.
        '''
        self.type: str = type
        
        self.obj: "Object | Enemy" = obj
        self.fade_in_key: float = 0.0
        self.smooth_key: float = 0.0
        self.ease = easing.QuinticEaseOut()

        self.update_pos(pos)


    def update_rect(self):
        '''
        Updates the popup's rect.
        '''
        height = 25+int(self.type == 'enemy')*9
        max_hp = self.obj.meta.hp if self.type == 'block'\
            else self.obj.max_hp
        
        self.rect = pg.Rect(0,0,100*self.smooth_key,height)
        self.rect.midbottom = self.pos
        self.rect.y -= 32-24*self.smooth_key

        self.bar_rect = pg.Rect(
            self.rect.left+3,
            self.rect.bottom-10,
            self.rect.width-6, 7
        )
        self.filled_bar_rect = pg.Rect(
            self.rect.left+3,
            self.rect.bottom-10,
            (self.rect.width-6)*(self.obj.hp/max_hp), 7
        )

        # triangle points
        self.pts: List[Tuple[int,int]] = [
            [self.rect.centerx-3, self.rect.bottom],
            [self.rect.centerx, self.rect.bottom+3],
            [self.rect.centerx+3, self.rect.bottom]
        ]


    def update_pos(self, pos:Tuple[int,int]):
        '''
        Updates the popup's rect and position.
        '''
        self.pos: Tuple[int,int] = pos
        self.update_rect()


    def draw(self, surface:pg.Surface):
        '''
        Draws the popup.
        '''
        pg.draw.rect(surface, (200,200,200), self.rect, 0, 4)

        # name
        name = self.obj.meta.name if self.type == 'block'\
            else self.obj.type
        
        draw.text(
            surface, name,
            (self.rect.left+4, self.rect.top+3)    
        )

        # enemy character name
        if self.type == 'enemy':
            draw.text(
                surface, self.obj.name,
                (self.rect.left+4, self.rect.top+14),
                size=6, style='small', color=(128,128,128)    
            )

        # bar
        pg.draw.rect(surface, (180,180,180), self.bar_rect, 0, 2)
        pg.draw.rect(surface, (200,100,100), self.filled_bar_rect, 0, 2)

        # bar text
        max_hp = self.obj.meta.hp if self.type == 'block'\
            else self.obj.max_hp
        
        draw.text(
            surface, f'{self.obj.hp} / {max_hp}',
            (self.bar_rect.centerx+1, self.bar_rect.centery+1),
            h=0.5, v=0.5, size=6, style='small'
        )

        # triangle
        pg.draw.polygon(surface, (200,200,200), self.pts)


    def update(self, td:float):
        '''
        Updates the popup.
        '''
        if self.fade_in_key < 1.0:
            self.fade_in_key += td*3
            self.smooth_key = self.ease.ease(self.fade_in_key)
            self.update_rect()

            if self.fade_in_key > 1.0:
                self.fade_in_key = 1.0



# biome class

class Biome:
    def __init__(self, objects: List[ObjMeta], weights:List[float], empty_chance:float):
        '''
        Stores the information about how to populate the map.
        '''
        assert len(objects) == len(weights),\
            '`objects` and `lengths` are not the same length'
        
        self.objects: List[ObjMeta] = objects
        self.weights: List[float] = weights
        self.empty_chance: float = empty_chance


    def get_random_obj(self) -> "ObjMeta | None":
        '''
        Returns a random object based on the biome.

        Returns None if the generated object is empty.
        '''
        if random.random() < self.empty_chance:
            return None
        
        obj = random.choices(self.objects, weights=self.weights)
        return obj[0]
    

    @staticmethod
    def from_dict(data:dict) -> "Biome":
        '''
        Converts a dict object to a Biome object.
        '''
        return Biome(
            [ObjMeta.from_dict(i) for i in data.get('objects',[])],
            [i.get('weight',1.0) for i in data.get('objects', [])],
            data['empty_chance']
        )


# map class

class Map:
    def __init__(self, size:Tuple[int,int], objects:List[Object], biome:Biome):
        '''
        Represents a map.
        '''
        self.size: Tuple[int,int] = size
        self.rect = pg.Rect(0,0,*size)

        self.objects: List[Object] = objects
        self.biome: Biome = biome
        self.enemies: List[Enemy] = []

        self.update_objects()


    def update_objects(self):
        '''
        Updates the variable which has the list of occupied tile positions.
        '''
        self.occupied: List[Tuple[int,int]] = []

        for obj in self.objects:
            self.occupied.extend(obj.tiles.copy())


    def add_object(self, object:"Object | List[Object]"):
        '''
        Adds the objects to the map.
        '''
        if type(object) != list:
            self.objects.append(object)
        else:
            self.objects.extend(object)

        self.update_objects()


    def populate_empty(self):
        '''
        Adds random objects to the map.
        '''
        time_offset = 0.0
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                pos = (x, y)
                if pos in self.occupied:
                    continue
                
                obj = self.biome.get_random_obj()
                if obj != None:
                    self.add_object(Object(obj.tags, pos, obj, time_offset))
                    time_offset += 0.02


# wave class

class WaveEnemy:
    def __init__(self,
        enemy:str, waves:Tuple[int,int],
        amount:Tuple[int,int],
        amount_increase:Tuple[int,int],
        max_amount:Tuple[int,int]
    ):
        '''
        Represents the enemy data in the wave.
        '''
        self.enemy_key: str = enemy
        self.update_enemy()
        self.wave: int = 0
        
        self.starting_wave: int = random.randint(*waves)
        self.amount: int = random.randint(*amount)
        self.amount_increase: Tuple[int,int] = amount_increase
        self.max_amount: int = random.randint(*max_amount)


    @property
    def spawnable(self) -> bool:
        return self.wave >= self.starting_wave


    def update_enemy(self):
        '''
        Updates the `self.enemy` corresponding to the enemy key.
        '''
        if self.enemy_key == 'zombie':
            self.enemy: Enemy = Zombie
        elif self.enemy_key == 'skeleton':
            self.enemy: Enemy = Skeleton
        else:
            self.enemy: Enemy = Zombie


    def next_wave(self):
        '''
        Skips to next wave.
        '''
        self.wave += 1

        # increasing amount
        if self.wave > self.starting_wave:
            self.amount += min(0,random.randint(*self.amount_increase))
            self.amount = min(self.amount, self.max_amount)
            print(self.amount)


    @staticmethod
    def from_dict(data:dict) -> "WaveEnemy":
        return WaveEnemy(
            data['enemy'],
            data['waves'],
            data['amount'],
            data['amount_increase'],
            data['max_amount']
        )


class Wave:
    def __init__(self,
        wave_enemies:List[WaveEnemy],
        spawn_time:Tuple[float,float]         
    ):
        '''
        Represents a difficulty/wave setup.
        '''
        self.enemies: List[WaveEnemy] = wave_enemies
        self.spawn_time_range: Tuple[float,float] = spawn_time
        self.wave: int = 0


    @property
    def spawn_time(self) -> float:
        return random.random()*abs(
            self.spawn_time_range[0]-self.spawn_time_range[1]
        ) + self.spawn_time_range[0]

    
    def next_wave(self):
        '''
        Skips to the next wave.
        '''
        self.wave += 1
        
        for i in self.enemies:
            i.next_wave()


    def get_spawn_list(self) -> List[Enemy]:
        '''
        Generates and returns a list of enemies to
        spawn in the current wave.
        '''
        enemies: List[Enemy] = []

        for i in self.enemies:
            if not i.spawnable: continue

            for _ in range(i.amount):
                enemies.append(i.enemy)

        random.shuffle(enemies)
        return enemies


    @staticmethod
    def from_dict(data:List[dict]) -> "Wave":
        return Wave(
            [WaveEnemy.from_dict(i) for i in data['enemies']],
            data['spawn_time']
        )



# game class

class Game:
    def __init__(self,
        map_size:Tuple[int,int], data:dict,
        biome:str, wave:str, castle_pos:Tuple[int,int]
    ):
        '''
        Represents an ongoing game.
        '''
        self.data: dict = data
        self.mouse_pos: Tuple[int,int] = [0,0]

        self.objects: Dict[str, ObjMeta] = {
            k: ObjMeta.from_dict(v) for k, v in data['objects'].items()
        } 
        self.biome: dict = self.data['biomes'][biome]

        empty_chance: float = self.biome['empty_chance']
        weights: List[float] = [i.get('weight',1.0) for i in self.biome['objects']]
        objects: List[ObjMeta] = [self.objects[i['object']] for i in self.biome['objects']]

        self.biome: Biome = Biome(objects, weights, empty_chance)

        self.cam_offset: Tuple[int,int] = [
            (map_size[0]*TILESIZE/2) - APPX/2,
            (map_size[1]*TILESIZE/2) - APPY/2
        ]

        self.wave: int = 0
        self.wave_timeout: float = 60.0
        self.wave_ongoing: bool = False
        self.wave_data = Wave.from_dict(self.data['waves'][wave])
        self.spawn_list: List[Enemy] = []
        self.spawn_timer: float = 0.0
        self.spawn_pos: "Tuple[int,int] | None" = None

        self.big_timer_font_size: float = 0
        self.wave_timeout_int: int = 0

        self.castle = Object('castle', castle_pos, ObjMeta(
            'Castle', ['castle.png'], (3,2), hp=100
        ))

        self.map = Map(map_size, [self.castle], self.biome)
        self.map.populate_empty()

        # todo particle
        # self.particles: List[Particle] = []

        self.coins: int = 50

        self.cursor_timeout: float = 0.0
        self.cursor_timeout_max: float = 0.0
        self.cursor_tile: "Tuple[int,int] | None" = None

        self.popup: "Popup | None" = None


    def timeout(self, time:"int | None"=None):
        '''
        Timeouts the cursor.
        '''
        if time == None:
            time = 1.0
            
        self.cursor_timeout += time
        self.cursor_timeout_max = time


    def add_coins(self, amount:int):
        '''
        Adds coins to the player balance.
        '''
        self.coins += amount


    def skip_intermission(self):
        '''
        Skips the intermission.
        '''
        if self.wave_ongoing: return
        if self.wave_timeout < 5.0: return
        self.wave_timeout = 5.0


    def gen_spawn_pos(self):
        '''
        Generates a new spawn_pos to spawn the next enemy at.
        '''
        side = random.choice(['l','r','t','b'])

        if side == 'l':
            self.spawn_pos = [
                0, random.randint(0,self.map.size[1])
            ]
        if side == 'r':
            self.spawn_pos = [
                self.map.size[0], random.randint(0,self.map.size[1])
            ]

        if side == 't':
            self.spawn_pos = [
                random.randint(0,self.map.size[0]), 0
            ]
        if side == 'b':
            self.spawn_pos = [
                random.randint(0,self.map.size[0]), self.map.size[1]
            ]


    def spawn_enemy(self):
        '''
        Spawns an enemy.
        '''
        self.map.enemies.append(
            self.spawn_list[0](self.spawn_pos, self.castle.center)
        )
        self.spawn_list.pop(0)
        self.spawn_timer = self.wave_data.spawn_time
        self.gen_spawn_pos()


    def get_obj_at(self,
        pos:Tuple[int,int],
        check_tiles:bool=True,
        check_topleft:bool=False
    ) -> "Object | None":
        '''
        Returns an object on the specified coordinates.

        If there's no object, will return None.
        '''
        for obj in self.map.objects:
            if check_topleft and obj.pos == pos:
                return obj
            
            if check_tiles and tuple(pos) in [tuple(i) for i in obj.tiles]:
                return obj

        return None


    def map_to_cam(self, pos:Tuple[int,int]) -> Tuple[int,int]:
        '''
        Converts map coordinates to a point on the screen.
        '''
        return [
            (pos[0]*TILESIZE)-self.cam_offset[0],
            (pos[1]*TILESIZE)-self.cam_offset[1]
        ]


    def update_input(self, events:List[pg.Event], mouse_pos:Tuple[int,int]):
        '''
        Updates all the input variables.
        '''
        self.mouse_moved: Tuple[int,int] = [
            mouse_pos[0]-self.mouse_pos[0],
            mouse_pos[1]-self.mouse_pos[1]
        ]
        self.mouse_pos: Tuple[int,int] = mouse_pos
        self.mouse_press: Tuple[bool,bool,bool] = pg.mouse.get_pressed(3)
        self.mouse_wheel: float = 0.0
        self.keys_held = pg.key.get_pressed() # keys that are being held
        self.keys_down: List[int] = [] # list of keys that are just pressed in the current frame
        self.lmb_down = False # whether the left mouse button just got held in the current frame

        self.cursor_map: Tuple[float,float] = [
            (mouse_pos[0]+self.cam_offset[0])/TILESIZE,
            (mouse_pos[1]+self.cam_offset[1])/TILESIZE
        ]
        self.cursor_tile: Tuple[int,int] = [int(i) for i in self.cursor_map]
        
        if not self.map.rect.collidepoint(self.cursor_map):
            self.cursor_map = None
            self.cursor_tile = None

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


    def draw_board(self, surface:pg.Surface):
        '''
        Draws the game on the surface.
        '''
        # occupied rects
        # for obj in self.map.objects:
        #     for i in obj.tiles:
        #         pos = self.map_to_cam(i)
        #         rect = pg.Rect(*pos, TILESIZE,TILESIZE)
        #         pg.draw.rect(surface, (190,190,190), rect, 1)

        # cursor
        if self.cursor_tile != None:
            rect = pg.Rect(self.map_to_cam(self.cursor_tile), (TILESIZE,TILESIZE))
            pg.draw.rect(surface, (200,200,200), rect, 2, 4)

        # objects
        for obj in self.map.objects:
            pos = self.map_to_cam(obj.pos)
            obj.draw(surface, pos)

        # enemies
        for i in self.map.enemies:
            pos = self.map_to_cam(i.pos.pos)
            i.draw(surface, pos)



    def draw_ui(self, surface:pg.Surface):
        '''
        Draws the UI on the surface
        '''
        size: Tuple[int,int] = surface.get_size()

        # cursor timeout circle
        if self.cursor_timeout > 0.0:
            angle = 5.2*(self.cursor_timeout/self.cursor_timeout_max)

            pts = []
            for i in range(int(angle*15)):
                pts.append([
                    np.sin((i+12)/15)*15+self.mouse_pos[0],
                    np.cos((i+12)/15)*15+self.mouse_pos[1]
                ])

            bg_color = (230,230,230)
            main_color = (150,150,150)

            if len(pts) > 2:
                pg.draw.lines(surface, bg_color, False, pts, 3)
                pg.draw.aalines(surface, main_color, False, pts)

            # text
            draw.text(
                surface, str(round(self.cursor_timeout,1)),
                (self.mouse_pos[0]+2, self.mouse_pos[1]+9), h=0.5,
                style='small', size=6, color=main_color,
                shadows=[(-1,1),(-1,-1),(1,-1),(1,1)],
                shadow_color=bg_color
            )

        # popup
        if self.popup != None:
            self.popup.draw(surface)

        # wave data
        if self.wave_ongoing:
            text = f'{len(self.spawn_list)+len(self.map.enemies)} enemies remaining'

        else:
            text = f'{int(self.wave_timeout)}s until wave {self.wave+1}'

        draw.text(
            surface, text, (size[0]-5, size[1]-5), h=1,v=1
        )

        # big wave timer
        if not self.wave_ongoing and self.wave_timeout < 5.0:
            draw.text(
                surface, str(int(self.wave_timeout)+1),
                (size[0]/2, size[1]/2-50), h=0.5, v=0.5,
                style='title', antialias=True,
                size=24+int(self.big_timer_font_size*28)
            )


    def draw(self, surface:pg.Surface):
        '''
        Draws the current menu.
        '''
        surface.fill((230,230,230))

        self.draw_board(surface)
        self.draw_ui(surface)


    def update_wave(self, td:float):
        '''
        Updates the current wave.
        '''
        # intermission
        if not self.wave_ongoing:
            self.wave_timeout -= td

            # switching to wave
            if self.wave_timeout <= 0:
                self.wave += 1
                self.wave_data.next_wave()

                self.spawn_list = self.wave_data.get_spawn_list()
                self.wave_ongoing = True
                self.spawn_timer = self.wave_data.spawn_time
                self.gen_spawn_pos()

            # updating big timer
            if self.wave_timeout_int != int(self.wave_timeout):
                self.wave_timeout_int = int(self.wave_timeout)
                self.big_timer_font_size = 1.0

            if self.big_timer_font_size > 0.0:
                self.big_timer_font_size -= td*10
                if self.big_timer_font_size < 0.0:
                    self.big_timer_font_size = 0.0
                

        # wave
        else:
            if len(self.spawn_list) > 0:
                self.spawn_timer -= td
                
                # spawning enemy
                if self.spawn_timer <= 0.0:
                    self.spawn_enemy()

            # switching to intermission
            if len(self.spawn_list) == 0 and len(self.map.enemies) == 0:
                self.wave_ongoing = False
                self.wave_timeout = 20.0



    def process_input(self):
        '''
        Does the clicking and stuff.
        '''
        if self.cursor_tile != None:
            obj = self.get_obj_at(self.cursor_tile)
        else:
            obj = None

        # moving camera
        if self.mouse_press[1]:
            self.cam_offset[0] -= self.mouse_moved[0]
            self.cam_offset[1] -= self.mouse_moved[1]

        # checking if enemy is hovered
        hovered_enemy: "Enemy | None" = None

        if self.cursor_map != None:
            for i in self.map.enemies[::-1]:
                if i.rect.collidepoint(self.cursor_map):
                    hovered_enemy = i
                    break
            
        # popup
        if self.popup != None:
            posx = self.popup.pos[0]+self.mouse_moved[0]
            posy = self.popup.pos[1]+self.mouse_moved[1]
            self.popup.update_pos((posx,posy))

        # clicking
        if self.lmb_down:
            # clicked on enemy
            if hovered_enemy != None:
                if self.cursor_timeout > 0.0:
                    pass
                else:
                    hovered_enemy.damage()
                    self.timeout()

            # clicking on objects
            elif obj != None and obj.player_damage:
                if self.cursor_timeout > 0.0:
                    obj.kick(0.4)
                else:
                    obj.damage()
                    self.timeout()

            # debug
            # elif self.cursor_map != None:
            #     self.map.enemies.append(Zombie(
            #         self.cursor_map, self.castle.center
            #     ))


        # hovering over objects
        if hovered_enemy != None and (
            self.popup == None or self.popup.type == 'block' or (
                self.popup.obj != hovered_enemy
            )
        ):
            self.popup = Popup('enemy', hovered_enemy, self.mouse_pos)

        elif obj != None and (
            self.popup == None or (
                self.popup.type == 'block' and\
                self.popup.obj.pos != obj.pos
            ) or (
                self.popup.type == 'enemy' and\
                hovered_enemy == None
            )
        ):
            self.popup = Popup('block', obj, self.mouse_pos)

        elif obj == None and hovered_enemy == None and\
            self.popup != None:
                self.popup = None

        # skipping wave intermission
        if pg.K_i in self.keys_down:
            self.skip_intermission()
    
    
    def update(self, td:float, events:List[pg.Event], mouse_pos:Tuple[int,int]):
        '''
        Updates the current menu.
        '''
        # input
        self.update_input(events, mouse_pos)
        self.process_input()

        # updating wave
        self.update_wave(td)

        # updating objects
        new = []

        for obj in self.map.objects:
            events: List[Event] = obj.update(td)
            delete: bool = False

            for i in events:
                # processing object events
                if i.type == 'delete':
                    delete = True

            if not delete:
                new.append(obj)
        
        self.map.objects = new

        # updating enemies
        new = []

        for i in self.map.enemies:
            i.update(td, self.map)
            if not i.deletable:
                new.append(i)
                self.add_coins(i.cost)

        self.map.enemies = new

        # cursor timeout
        if self.cursor_timeout > 0.0:
            self.cursor_timeout -= td

        # updating popup
        if self.popup != None:
            self.popup.update(td)
