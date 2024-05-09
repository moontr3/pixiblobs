
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
        self.pos.rad = angle
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

            cont = False
            for tag in self.phase_through:
                if tag in obj.tag:
                    cont = True
            if cont: continue

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
        #         pos[0]+(np.sin(self.pos.rad))*15,
        #         pos[1]+(np.cos(self.pos.rad))*15
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

        # checking collisions with projectiles
        for i in map.projectiles:
            if not i.enemy_shot and\
            i.rect.colliderect(self.rect):
                self.damage(i.proj.damage)
                i.deletable = True

        # checking collisions
        if self.phase_through != None:
            self.check_collisions(map)

        # checking if collided
        if self.collided != None:
            self.pos.speed -= td

            if self.pos.speed <= 0.0:
                self.collided = None
                self.pos.rad += np.pi

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
            type =               'Zombie',
            name =               'Maxwell the Undead',
            pos =                pos,
            castle =             target,
            image =              'maxwell.png',
            size =               (16,16),
            speed =              0.5,
            hp =                 7,
            cost =               10,
            clock =              0.5,
            collision_strength = 1
        )


class Skeleton(Enemy):
    def __init__(self, pos:Tuple[int,int], target:Tuple[int,int]):
        super().__init__(
            type =               'Skeleton',
            name =               'Bob the Boneful',
            pos =                pos,
            castle =             target,
            image =              'bob.png',
            size =               (16,16),
            speed =              1,
            hp =                 20,
            cost =               35,
            clock =              0.5,
            collision_strength = 1
        )


class Witch(Enemy):
    def __init__(self, pos:Tuple[int,int], target:Tuple[int,int]):
        super().__init__(
            type =               'Witch',
            name =               'Anastasiya the Best',
            pos =                pos,
            castle =             target,
            image =              'anastasiya.png',
            size =               (16,24),
            speed =              0.5,
            hp =                 75,
            cost =               100,
            clock =              2.5,
            collision_strength = 1
        )
        self.projectile = ProjectileMeta(
            3.0, 'mana_blob.png', (8,8),
            2, False, 3.0
        ) 


    def call_clock(self, map:"Map"):
        '''
        Shooting the mana balls.
        '''
        map.projectiles.append(Projectile(
            self.projectile, self.pos.pos,
            utils.angle_between(self.pos.pos, self.castle)+np.pi/2
        ))


class Poop(Enemy):
    def __init__(self, pos:Tuple[int,int], target:Tuple[int,int]):
        super().__init__(
            type =               'French poop',
            name =               'Zifuaro the Moustachy',
            pos =                pos,
            castle =             target,
            image =              'zifuaro.png',
            size =               (16,24),
            speed =              1.5,
            hp =                 150,
            cost =               300,
            clock =              0.6,
            collision_strength = 1.2
        )
        self.projectile = ProjectileMeta(
            0, 'no.png', (64,64),
            1, False, 0.5
        ) 


    def call_clock(self, map:"Map"):
        '''
        Damaging the area around.
        '''
        map.projectiles.append(Projectile(
            self.projectile, self.pos.pos, 0,
            destroy_everything=True
        ))


class Cloud(Enemy):
    def __init__(self, pos:Tuple[int,int], target:Tuple[int,int]):
        super().__init__(
            type =               'Cloud',
            name =               'Clyde the Blissful',
            pos =                pos,
            castle =             target,
            image =              'cloud.png',
            size =               (24,16),
            speed =              1,
            hp =                 750,
            cost =               750,
            clock =              0.3,
            collision_strength = 1.2,
            phase_through =      ['wood']
        )
        self.projectile = ProjectileMeta(
            2, 'cloud_bit.png', [8,8],
            3, False, 1.5
        ) 


    def call_clock(self, map:"Map"):
        '''
        Damaging the area around.
        '''
        map.projectiles.append(Projectile(
            self.projectile, self.pos.pos,
            random.random()*3.14*2
        ))


# object classes

class ObjMeta:
    def __init__(self, name:str,
        images:List[str], size:Tuple[int,int],
        tiles:"List[Tuple[int,int]] | None"=None,
        tags:"List[str] | str | None"=None,
        hp:int=1, player_damage:bool=False,
        player_sell:bool=False, walkable:bool=False,
        wood:int=0, crystals:int=0, clock:"float|None"=None
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
        self.player_sell: bool = player_sell

        self.walkable: bool = walkable

        self.crystals: int = crystals
        self.wood: int = wood

        self.clock: "float | None" = clock

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
            data.get('player_sell', False),
            data.get('walkable', False),
            data.get('wood', False)
        )
    

    def call_clock(self, obj:"Object", enemies:List["Enemy"]=[]) -> List[Event]:
        '''
        Gets called every `self.clock` seconds.
        '''
        pass
    

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
        self.hold_sell: float = 0.0

        self.pos: Tuple[int,int] = list(pos)
        self.update_rect()

        self.hp: int = deepcopy(self.meta.hp)
        self.player_damage: bool = self.meta.player_damage

        self.clock: float = deepcopy(self.meta.clock)


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


    def update(self, td:float, map:"Map") -> List[Event]:
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

        # clock
        if self.clock != None:
            self.clock -= td
            if self.clock <= 0.0:
                self.clock += self.meta.clock
                self.events.extend(
                    self.meta.call_clock(self, map.enemies)
                )

        events = self.events.copy()
        self.events = []
        return events

        
# objects in shop 

class SmallTower(ObjMeta):
    def __init__(self):
        super().__init__(
            name =        'Small crystal',
            images =      ['pink_crystal.png'],
            size =        [1, 1],
            player_sell = True,
            hp =          50,
            crystals =    80,
            clock =       1.5,
            tags =        'player'
        )
        self.proj = ProjectileMeta(
            2.0, 'pink_shard.png', [12,8],
            1, True, 2.0
        )
        self.dst: float = 3
        

    def call_clock(self, obj:Object, enemies:List[Enemy]=[]) -> List[Event]:
        '''
        Shoots on enemies.
        '''
        events: List[Event] = []

        check_rect = pg.FRect(0,0,
            TILESIZE*2*self.dst,TILESIZE*2*self.dst
        )
        check_rect.center = obj.center

        # checking enemies
        for i in enemies:
            # checking enemy in bounding box
            if i.rect.colliderect(check_rect):
                # checking enemy in shooting distance
                if utils.get_distance(obj.center, i.pos.pos) < self.dst:
                    # shooting
                    events.append(Event('proj',
                        Projectile(
                            self.proj, obj.center,
                            utils.angle_between(obj.center, i.pos.pos)+np.pi/2,
                            False, phase_through=['player']
                        )
                    ))
                    obj.kick(0.7)
                    break

        return events


class MedTower(ObjMeta):
    def __init__(self):
        super().__init__(
            name =        'Medium crystal',
            images =      ['violet_crystal.png'],
            size =        [1, 1],
            player_sell = True,
            hp =          75,
            crystals =    200,
            clock =       1.5,
            tags =        'player'
        )
        self.proj = ProjectileMeta(
            2.0, 'violet_shard.png', [12,8],
            4, True, 3.5
        )
        self.dst: float = 5
        

    def call_clock(self, obj:Object, enemies:List[Enemy]=[]) -> List[Event]:
        '''
        Shoots on enemies.
        '''
        events: List[Event] = []

        check_rect = pg.FRect(0,0,
            TILESIZE*2*self.dst,TILESIZE*2*self.dst
        )
        check_rect.center = obj.center

        # checking enemies
        for i in enemies:
            # checking enemy in bounding box
            if i.rect.colliderect(check_rect):
                # checking enemy in shooting distance
                if utils.get_distance(obj.center, i.pos.pos) < self.dst:
                    # shooting
                    events.append(Event('proj',
                        Projectile(
                            self.proj, obj.center,
                            utils.angle_between(obj.center, i.pos.pos)+np.pi/2,
                            False, phase_through=['player']
                        )
                    ))
                    obj.kick(0.7)
                    break

        return events


class LargeTower(ObjMeta):
    def __init__(self):
        super().__init__(
            name =        'Large crystal',
            images =      ['blue_crystal.png'],
            size =        [1, 2],
            player_sell = True,
            hp =          125,
            crystals =    600,
            clock =       1,
            tags =        'player'
        )
        self.proj = ProjectileMeta(
            2.5, 'blue_shard.png', [12,8],
            7, True, 4
        )
        self.dst: float = 6
        

    def call_clock(self, obj:Object, enemies:List[Enemy]=[]) -> List[Event]:
        '''
        Shoots on enemies.
        '''
        events: List[Event] = []

        check_rect = pg.FRect(0,0,
            TILESIZE*2*self.dst,TILESIZE*2*self.dst
        )
        check_rect.center = obj.center

        # checking enemies
        for i in enemies:
            # checking enemy in bounding box
            if i.rect.colliderect(check_rect):
                # checking enemy in shooting distance
                if utils.get_distance(obj.center, i.pos.pos) < self.dst:
                    # shooting
                    events.append(Event('proj',
                        Projectile(
                            self.proj, obj.center,
                            utils.angle_between(obj.center, i.pos.pos)+np.pi/2,
                            False, phase_through=['player']
                        )
                    ))
                    obj.kick(0.7)
                    break

        return events
    

class Landmine(ObjMeta):
    def __init__(self):
        super().__init__(
            name =        'Crystal landmine',
            images =      ['landmine.png'],
            size =        [1, 1],
            player_sell = True,
            crystals =    200,
            clock =       0.1,
            tags =        'player',
            walkable =    True
        )
        

    def call_clock(self, obj:Object, enemies:List[Enemy]=[]) -> List[Event]:
        '''
        Shoots on enemies.
        '''
        events: List[Event] = []
        
        # damaging enemies nearby
        for i in enemies:
            # damaging enemy that stepped
            if i.rect.colliderect(obj.rect):
                # removing object
                obj.events.append(Event('delete'))

                # shooting
                proj = ProjectileMeta(
                    0, 'no.png', [TILESIZE, TILESIZE],
                    random.randint(25,50),
                    False, 0.01
                )
                events.append(Event('proj',
                    Projectile(
                        proj, obj.center, 0,
                        False, phase_through=['player']
                    )                    
                ))

        return events
        

class StickWall(ObjMeta):
    def __init__(self):
        super().__init__(
            name =        'StickWall',
            images =      ['sticks.png'],
            size =        [1, 1],
            hp =          25,
            player_sell = True,
            wood =        3,
            tags =        ['player','wood']
        )
        

class WoodBlock(ObjMeta):
    def __init__(self):
        super().__init__(
            name =        'Wood block',
            images =      ['wood.png'],
            size =        [1, 1],
            hp =          100,
            player_sell = True,
            wood =        12,
            tags =        ['player','wood']
        )
        

class LogStack(ObjMeta):
    def __init__(self):
        super().__init__(
            name =        'Log Stack',
            images =      ['logs.png'],
            size =        [2, 1],
            hp =          500,
            player_sell = True,
            wood =        30,
            tags =        ['player','wood']
        )


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

        if self.sellable_check:
            if (self.obj.meta.wood == 0 and self.obj.meta.crystals == 0):
                self.str_cost: str = ' free'
            else:
                self.str_cost: str = ''
                if self.obj.meta.wood != 0:
                    self.str_cost += f' {self.obj.meta.wood}w'
                if self.obj.meta.crystals != 0:
                    self.str_cost += f' {self.obj.meta.crystals}c'

        self.update_pos(pos)


    @property
    def sellable_check(self) -> bool:
        return self.type == 'block' and self.obj.meta.player_sell


    def update_rect(self):
        '''
        Updates the popup's rect.
        '''
        height = 25\
            +int(self.type == 'enemy')*9\
            +int(self.sellable_check)*9
        
        max_hp = self.obj.meta.hp if self.type == 'block'\
            else self.obj.max_hp
        
        self.rect = pg.Rect(0,0,
            (100+int(self.sellable_check)*20)\
                *self.smooth_key,height
            )
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

        # player sellable
        if self.sellable_check:
            draw.text(
                surface, f'Hold RMB to sell for{self.str_cost}',
                (self.rect.left+4, self.rect.bottom-20),
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
    def __init__(self,
        objects: List[ObjMeta],
        weights:List[float],
        empty_chance:float,
        wave_empty_chance:float=0.0
    ):
        '''
        Stores the information about how to populate the map.
        '''
        assert len(objects) == len(weights),\
            '`objects` and `lengths` are not the same length'
        
        self.objects: List[ObjMeta] = objects
        self.weights: List[float] = weights
        self.empty_chance: float = empty_chance
        self.wave_empty_chance: float = wave_empty_chance


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
            data['empty_chance'], data.get('waves',0.0)
        )


# projectile classes

class ProjectileMeta:
    def __init__(self,
        speed:float,
        image:str,
        size:Tuple[int,int],
        damage:int,
        point:bool=True,
        lifetime:float=15
    ):
        '''
        Stores metadata of a projectile.
        '''
        self.image: str = image
        self.size: Tuple[int,int] = size
        
        self.speed: float = speed
        self.damage: int = damage
        self.point: bool = point

        self.lifetime: float = lifetime


class Projectile:
    def __init__(self,
        proj:ProjectileMeta,
        pos:Tuple[int,int],
        rad:float,
        enemy_shot:bool=True,
        destroy_everything:bool=False,
        phase_through:List[str]=[]
    ):
        '''
        Represents a projectile on the map.
        '''
        self.enemy_shot: bool = enemy_shot
        self.proj: ProjectileMeta = proj
        self.pos = utils.VectorCoord(pos, rad, proj.speed, 0)

        self.deletable: bool = False
        self.lifetime = proj.lifetime
        self.destroy_everything: bool = destroy_everything

        self.phase_through: List[str] = phase_through


    def draw(self, surface:pg.Surface, pos:Tuple[int,int]):
        '''
        Draws the projectile at a designated position.
        '''
        draw.image(
            surface, self.proj.image, pos,
            self.proj.size, 0.5, 0.5,
            0 if not self.proj.point else np.rad2deg(self.pos.rad+np.pi/2)
        )

    
    def update_rect(self):
        '''
        Updates rect.
        '''
        self.rect = pg.FRect(0, 0, *(
            self.proj.size[0]/TILESIZE,
            self.proj.size[1]/TILESIZE
        ))
        self.rect.center = self.pos.pos


    def update(self, td:float, map:"Map"):
        '''
        Updates the projectile.
        '''
        self.pos.update(td)
        self.update_rect()

        # lifetime
        self.lifetime -= td

        if self.lifetime <= 0.0:
            self.deletable = True

        # colliding
        for obj in map.objects:
            if ((not obj.meta.walkable and not self.destroy_everything)\
            or self.destroy_everything)\
            and self.rect.colliderect(obj.rect):
                # checking tags
                for i in self.phase_through:
                    if i in obj.tag: break
                else:
                    obj.damage(self.proj.damage)
                    self.deletable = True


# map class

class Map:
    def __init__(self,
        size:Tuple[int,int],
        objects:List[Object],
        biome:Biome,
        water_tiles:List[Tuple[int,int]]=[]
    ):
        '''
        Represents a map.
        '''
        self.size: Tuple[int,int] = size
        self.rect = pg.Rect(0,0,*size)

        self.objects: List[Object] = objects
        self.biome: Biome = biome
        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []

        self.water_tiles: List[Tuple[int,int]] = water_tiles

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


    def populate_empty(self, chance:float=1.0):
        '''
        Adds random objects to the map.
        '''
        time_offset = 0.0
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                pos = (x, y)
                if pos in self.occupied or pos in self.water_tiles:
                    continue
                
                obj = self.biome.get_random_obj()
                if obj != None and random.random() < chance:
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
        elif self.enemy_key == 'witch':
            self.enemy: Enemy = Witch
        elif self.enemy_key == 'poop':
            self.enemy: Enemy = Poop
        elif self.enemy_key == 'cloud':
            self.enemy: Enemy = Cloud

        else:
            print(f'Unknown enemy {self.enemy_key}')
            self.enemy: Enemy = Zombie


    def next_wave(self):
        '''
        Skips to next wave.
        '''
        self.wave += 1

        # increasing amount
        if self.wave > self.starting_wave:
            self.amount += max(0,random.randint(*self.amount_increase))
            self.amount = min(self.amount, self.max_amount)


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
    

# cursor class

class CurUpgrade:
    def __init__(self,
        kills:int,
        damage_inc:int=0,
        timeout_dec:float=0.0
    ):
        self.kills: int = kills
        self.damage_inc: int = damage_inc
        self.timeout_dec: float = timeout_dec


    @staticmethod
    def from_dict(data:dict) -> "CurUpgrade":
        return CurUpgrade(
            data['kills'], data.get('damage',0),
            data.get('timeout', 0.0)
        )
    

class Cursor:
    def __init__(self,
        upgrades:List[CurUpgrade],
        timeout:float=1.0, damage:int=1
    ):
        self.level: int = 0
        self.kills: int = 0

        self.timeout: float = timeout
        self.damage: int = damage

        self.upgrades: List[CurUpgrade] = upgrades
        self.max_level: int = len(self.upgrades)
        self.kill_pts: List[int] = sorted(
            [i.kills for i in upgrades]
        )


    def kill(self):
        '''
        Adds one kill to the kill counter and updates upgrades.
        '''
        self.kills += 1

        if self.level < self.max_level:
            for i in self.upgrades:
                # leveling up
                if i.kills == self.kills:
                    self.level += 1

                    self.timeout -= i.timeout_dec
                    if self.timeout < 0.0:
                        self.timeout = 0.0
                    self.damage += i.damage_inc

    
# shop class

class ShopButton:
    def __init__(self, item:ObjMeta, wood:int=0, crystals:int=0):
        '''
        Represents a button in the shop.
        '''
        self.item: ObjMeta = item
        self.wood: int = wood
        self.crystals: int = crystals

        self.rect: "pg.Rect | None" = None
        self.hovered: bool = False

        self.update_cost_text()


    def set_rect(self, rect:pg.Rect):
        '''
        Sets the button rect to the passed one.
        '''
        self.rect = rect

        # cost rect
        self.cost_rect = pg.Rect(
            rect.left, rect.bottom-12, self.text_size+7, 12
        )


    def update_cost_text(self):
        '''
        Updates the text and the size depending on the cost.
        '''
        self.text: str =\
            (f'{self.crystals}c' if self.crystals != 0 else '')\
            +(f'{self.wood}w' if self.wood != 0 else '')
        
        self.text_size: int = draw.get_text_size(
            self.text, 6, 'small'
        )[0]


    def draw(self, surface:pg.Surface):
        '''
        Draws the button.
        '''
        # button
        pg.draw.rect(surface, 
            (180,180,180) if self.hovered else (210,210,210),
            self.rect, 0, 4
        )
        # cost
        pg.draw.rect(surface, 
            (160,160,160) if self.hovered else (180,180,180),
            self.cost_rect, 0, -1, 0,4,4,0
        )
        draw.text(
            surface, self.text,
            (self.cost_rect.centerx+1, self.cost_rect.centery),
            (80,80,80), 6, 'small', 0.5, 0.5
        )
        
        # object
        draw.image(surface, self.item.image,
            self.rect.center, 
            [self.item.size[0]*TILESIZE, self.item.size[1]*TILESIZE],
            0.5,0.5           
        )


class Shop:
    def __init__(self, crystals:int, wood:int, cursor:"Cursor"):
        '''
        Represents a shop overlay.
        '''
        self.crystals: int = crystals
        self.wood: int = wood
        self.cursor: "Cursor" = cursor

        self.size: "Tuple[int,int] | None" = None
        self.opened: bool = False

        self.open_key: float = 0.0
        self.smooth_open_key: float = 0.0
        self.ease = easing.CubicEaseOut()
        self.surface: "pg.Surface | None" = None

        self.wi_buttons: List[ShopButton] = [
            ShopButton(StickWall(), wood=5),
            ShopButton(WoodBlock(), wood=15),
            ShopButton(LogStack(),  wood=40)
        ]
        self.ci_buttons: List[ShopButton] = [
            ShopButton(SmallTower(), crystals=100),
            ShopButton(MedTower(),   crystals=250),
            ShopButton(LargeTower(), crystals=750),
            ShopButton(Landmine(),   crystals=250)
        ]

        self.wi_start_pos: float =\
            (APPX-(len(self.wi_buttons)-1)*80)/2
        self.ci_start_pos: float =\
            (APPX-(len(self.ci_buttons)-1)*80)/2

    
    def update_buttons(self):
        '''
        Updates buttons' rects.
        '''
        # wood button rects
        pos = self.wi_start_pos

        for i in range(len(self.wi_buttons)):
            rect = pg.Rect(0,0,75,70*self.smooth_open_key)
            rect.midtop = (pos, self.rect.top+21)

            self.wi_buttons[i].set_rect(rect)
            pos += 80

        # crystal button rects
        pos = self.ci_start_pos

        for i in range(len(self.ci_buttons)):
            rect = pg.Rect(0,0,75,70*self.smooth_open_key)
            rect.midbottom = (pos, self.rect.bottom-10)

            self.ci_buttons[i].set_rect(rect)
            pos += 80
        

    def draw(self, surface:pg.Surface):
        '''
        Draws the shop.
        '''
        if self.size == None:
            self.size = surface.get_size()
            self.surface = pg.Surface(self.size)
            self.update_rect()

        if self.open_key <= 0.0: return

        # dark bg
        if self.surface.get_alpha() > 0:
            surface.blit(self.surface, (0,0))

        # rect
        pg.draw.rect(surface, (230,230,230), self.rect, 0, 7)
        # level bar
        pg.draw.rect(surface, (230,230,230), self.bar_rect, 0, 4)


        # wooden items title
        draw.text(surface, f'Wood (balance: {self.wood})', 
            (self.rect.centerx, self.rect.top+8),
            (128,128,128), 6, 'small', 0.5
        )

        # wooden items
        for i in self.wi_buttons:
            i.draw(surface)

        # crystal items title
        draw.text(surface, f'Crystal (balance: {self.crystals})', 
            (self.rect.centerx, self.rect.centery+7*self.smooth_open_key),
            (128,128,128), 6, 'small', 0.5
        )

        # crystal items
        for i in self.ci_buttons:
            i.draw(surface)

        # max level
        if self.cursor.kill_pts == [] or\
        self.cursor.kills >= self.cursor.kill_pts[-1]:
            text = f'Max level ({self.cursor.kills} kills)'

        # normal bar
        else:
            
            # level up points
            for i in self.bar_kill_pts:
                pg.draw.rect(surface, (200,200,200),
                    pg.Rect(i, self.bar_rect.top, 1,10)             
                )

            pg.draw.rect(
                surface, (50,150,230),
                self.bar_fill_rect, 0, -1, 4,1,4,1
            )
            
            text = f'Level {self.cursor.level} '\
                f'({self.cursor.kills} kills)'

        # bar text
        draw.text(surface, text,
            self.bar_rect.center,
            h=0.5,v=0.5,size=6,style='small'          
        )


    def update_rect(self):
        '''
        Updates the UI rect.
        '''
        if self.size == None: return

        # bg rect
        self.rect = pg.Rect(0,0,400,200*self.smooth_open_key)
        self.rect.center = [self.size[0]/2, self.size[1]/2]

        # level bar rect
        self.bar_rect = pg.Rect(0,0,150,10)
        self.bar_rect.center = (
            self.size[0]/2,
            self.rect.bottom-8+18*self.smooth_open_key
        )

        if self.cursor.kill_pts == [] or\
        self.cursor.kills >= self.cursor.kill_pts[-1]:
            pass

        else:
            progress = self.cursor.kills/self.cursor.kill_pts[-1]
            self.bar_fill_rect = pg.Rect(0,0,2+146*progress,8)
            self.bar_fill_rect.topleft = (
                self.bar_rect.left+1, self.bar_rect.top+1
            )

            # level bar levelup points
            max = self.cursor.kill_pts[-1]
            self.bar_kill_pts: List[int] = []
            
            for i in self.cursor.kill_pts:
                if i == max: continue
                percentage = i/max
                self.bar_kill_pts.append(
                    self.bar_fill_rect.left+int(percentage*148)
                )

        # buttons
        self.update_buttons()


    def update(self, td:float):
        '''
        Updates the shop.
        '''
        # updating key
        changed = False 

        if self.opened and self.open_key < 1.0:
            self.open_key += td*3
            if self.open_key > 1.0:
                self.open_key = 1.0

            changed = True

        if not self.opened and self.open_key > 0.0:
            self.open_key -= td*5
            if self.open_key < 0.0:
                self.open_key = 0.0

            changed = True

        # updating rect and animation
        if changed:
            self.smooth_open_key = self.ease.ease(self.open_key)

            if self.surface != None:
                self.surface.set_alpha(int(self.smooth_open_key*100))
            
            self.update_rect()


# builder class

class Builder:
    def __init__(self,
        block:ObjMeta, shop:Shop,
        wood:int=0, crystals:int=0,
        max_amount:"int | None"=None
    ):
        '''
        Class that places blocks.
        '''
        self.block: ObjMeta = block
        self.shop: Shop = shop

        self.wood: int = wood
        self.crystals: int = crystals

        self.amount: "int | None" = max_amount


    @property
    def placeable(self) -> bool:
        '''
        Returns True or False if player balance is sufficient.
        '''
        return self.wood <= self.shop.wood and\
            self.crystals <= self.shop.crystals and\
            (self.amount == None or self.amount > 0)


    def placed(self):
        '''
        Performs the actions needed after placing an object.
        '''
        self.shop.wood -= self.wood
        self.shop.crystals -= self.crystals
        if self.amount != None:
            self.amount -= 1


# game class

class Game:
    def __init__(self,
        map_size:Tuple[int,int], data:dict,
        biome:str, wave:str, castle_pos:Tuple[int,int],
        water_tiles:List[Tuple[int,int]]=[
            (1,1),(1,2),(2,1),(1,3),(2,4)
        ]
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

        self.biome: Biome = Biome(
            objects, weights, empty_chance, self.biome.get('waves',0.3)
        )

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

        self.castle = Object(['castle','player'], castle_pos, ObjMeta(
            'Castle', ['castle.png'], (3,2), hp=100
        ))

        self.map = Map(map_size, [self.castle], self.biome, water_tiles)
        self.map.populate_empty()

        # todo particles (maybe sometime in the future)
        # self.particles: List[Particle] = []

        self.cursor_timeout: float = 0.0
        self.cursor_timeout_max: float = 0.0
        self.cursor_tile: "Tuple[int,int] | None" = None

        self.popup: "Popup | None" = None

        self.code: str = ''

        self.kills: int = 0
        self.cursor = Cursor(
            [CurUpgrade.from_dict(i) for i in\
             self.data['waves'][wave]['cur_upgrades']]
        )

        self.shop = Shop(50, 0, self.cursor)
        self.builder: "Builder | None" = None

        self.crystals_rot = utils.SValue(6)
        self.wood_rot = utils.SValue(6)
        self.builder_key: float = 0.0
        self.builder_sin: float = 0.0


    def cheat_code(self):
        '''
        Checks the current cheatcode.
        '''
        # spawning enemies
        if self.code in ['0333','0334','0335','0336','0337']:
            print(f'Enemy:      {self.code}')

            if self.code == '0333': enemy = Zombie
            if self.code == '0334': enemy = Skeleton
            if self.code == '0335': enemy = Witch
            if self.code == '0336': enemy = Poop
            if self.code == '0337': enemy = Cloud

            old = deepcopy(self.spawn_pos)
            self.gen_spawn_pos()
            self.map.enemies.append(enemy(
                self.spawn_pos, self.castle.center
            ))
            self.spawn_pos = old

        # kill all
        elif self.code == '1488':
            print(f'Kill all:   {self.code}')

            for i in self.map.enemies:
                i.deletable = True

        # skip wave
        elif self.code == '6912':
            print(f'Wave skip:  {self.code}')

            self.map.enemies = []
            self.spawn_list = []

        # free blocks 
        elif self.code in ['8007','8008','8009','8010','8011','8012','8013']:
            print(f'Build:      {self.code}')

            if self.code == '8007': block = StickWall()
            if self.code == '8008': block = WoodBlock()
            if self.code == '8009': block = LogStack()
            if self.code == '8010': block = SmallTower()
            if self.code == '8011': block = MedTower()
            if self.code == '8012': block = LargeTower()
            if self.code == '8013': block = Landmine()

            self.builder = Builder(block, self.shop, 0, 1)

        # incorrect message
        else:
            print(f'Incorrect:  {self.code}')

        self.code = ''


    def add_wood(self, amount:int):
        '''
        Adds wood to the inventory.
        '''
        self.shop.wood += amount
        self.wood_rot.value =\
            random.randint(15,25)*random.choice([1,-1])


    def add_crystals(self, amount:int):
        '''
        Adds crystals to the player balance.
        '''
        self.shop.crystals += amount
        self.crystals_rot.value =\
            random.randint(15,25)*random.choice([1,-1])


    def timeout(self, time:"int | None"=None):
        '''
        Timeouts the cursor.
        '''
        if time == None:
            time = self.cursor.timeout
            
        self.cursor_timeout += time
        self.cursor_timeout_max = time


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
        taken = True
        iterations = 0
        # generationg position
        while taken:
            side = random.choice(['l','r','t','b'])
            
            if side == 'l':
                self.spawn_pos = [
                    0, random.randint(0,self.map.size[1]-1)
                ]
            if side == 'r':
                self.spawn_pos = [
                    self.map.size[0]-1, random.randint(0,self.map.size[1]-1)
                ]

            if side == 't':
                self.spawn_pos = [
                    random.randint(0,self.map.size[0]-1), 0
                ]
            if side == 'b':
                self.spawn_pos = [
                    random.randint(0,self.map.size[0]-1), self.map.size[1]-1
                ]
            
            iterations += 1
            taken = False if iterations > 100 else\
                self.get_obj_at(self.spawn_pos, check_topleft=True) != None


    def spawn_enemy(self):
        '''
        Spawns an enemy.
        '''
        self.map.enemies.append(
            self.spawn_list[0](
                (self.spawn_pos[0]+0.5,self.spawn_pos[1]+0.5),
                self.castle.center
            )
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

        # spawn tile
        if len(self.spawn_list) > 0 and self.spawn_pos != None:
            rect = pg.Rect(self.map_to_cam(self.spawn_pos), (TILESIZE,TILESIZE))
            pg.draw.rect(surface, (230,170,170), rect, 0, 7)

            # gradient
            for i in range(5):
                pg.draw.rect(surface,
                    (230,180+i*10,180+i*10), 
                rect, 7-i, 7)
            
            # outline
            pg.draw.rect(surface,
                (230,150,150), 
            rect, 1, 7)

        # bg water tiles
        for i in self.map.water_tiles:
            pos = self.map_to_cam(i)

            rect = pg.Rect(pos[0]-1,pos[1]-1 ,TILESIZE+2,TILESIZE+2)
            pg.draw.rect(surface, (50,200,200), rect, 0, 2)

        # fg water tiles
        for i in self.map.water_tiles:
            pos = self.map_to_cam(i)

            rect = pg.Rect(*pos,TILESIZE,TILESIZE)
            pg.draw.rect(surface, (50,130,200), rect)

        # cursor
        if self.cursor_tile != None:
            pos = self.map_to_cam(self.cursor_tile)
            rect = pg.Rect(
                pos[0]+1,pos[1]+1,
                TILESIZE-2,TILESIZE-2
            )
            
            # normal cursor
            if self.cursor_tile not in map(list, self.map.water_tiles):
                pg.draw.rect(surface, (200,200,200), rect, 2, 2)
            # water cursor
            else:
                pg.draw.rect(surface, (50,200,200), rect, 2, 2)

            # building rect
            if self.builder != None:
                pos = self.map_to_cam(self.cursor_tile)
                rect = pg.Rect(pos[0]-1,pos[1]-1,
                    TILESIZE*self.builder.block.size[0]+2,
                    TILESIZE*self.builder.block.size[1]+2
                )
                # checking if placeable
                block_rect = pg.Rect(self.cursor_tile, self.builder.block.size)
                water_tiles = [pg.Rect(*i,1,1) for i in self.map.water_tiles]

                occupied =\
                    block_rect.collidelistall(water_tiles) != []\
                    or block_rect.collidelistall([i.rect for i in self.map.objects]) != []
                placeable = not occupied and self.builder.placeable

                # drawing
                pg.draw.rect(surface,
                    (200,200,200) if placeable else (200,50,50),
                rect, 1, 4)

        # objects
        for obj in self.map.objects:
            pos = self.map_to_cam(obj.pos)
            obj.draw(surface, pos)

        # enemies
        for i in self.map.enemies:
            pos = self.map_to_cam(i.pos.pos)
            i.draw(surface, pos)

        # projectiles
        for i in self.map.projectiles:
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
                shadows=[(0,1),(0,-1),(-1,0),(1,0)],
                shadow_color=bg_color
            )

        # popup
        if self.popup != None and self.builder == None:
            self.popup.draw(surface)

        # composing wave data
        if self.wave_ongoing:
            number = len(self.spawn_list)+len(self.map.enemies)
            text = 'enemies remaining'

        elif self.wave_timeout >= 5:
            number = f"{int(self.wave_timeout)+1}s"
            text = f'(i to skip) wave {self.wave+1} in'
        else:
            number = f"{int(self.wave_timeout)+1}s"
            text = f'get ready for wave {self.wave+1}!'
        
        # drawing wave data
        textoffset = draw.text(
            surface, str(number),
            (size[0]-11, size[1]-10), h=1, v=1,
            style='title', antialias=True,
            size=18
        )[0]
        draw.text(
            surface, text,
            (size[0]-14-textoffset, size[1]-15), h=1, v=1
        )
        
        # crystals
        textoffset = draw.text(
            surface, str(self.shop.crystals),
            (size[0]-11, 10), h=1,
            style='title', antialias=True,
            size=18, rotation=int(self.crystals_rot)
        )[0]
        draw.text(
            surface, 'crystals',
            (size[0]-14-textoffset, 12), h=1,
        )

        # wood
        textoffset = draw.text(
            surface, str(self.shop.wood),
            (size[0]-11, 27), h=1,
            style='title', antialias=True,
            size=18, rotation=int(self.wood_rot)
        )[0]
        draw.text(
            surface, 'wood',
            (size[0]-14-textoffset, 29), h=1,
        )

        # shop string
        if self.builder != None: text = 'esc to exit building mode'
        else: text = 'space to open shop'

        draw.text(
            surface, text,
            (size[0]/2, size[1]-15), h=0.5,v=1,
        )

        # builder mode string
        if self.builder:
            draw.text(
                surface, f'building mode (placing {self.builder.block.name})',
                (size[0]/2, size[1]-30),
                (128-int(self.builder_sin*100), 25, 25),
                h=0.5,v=1,opacity=191+int(self.builder_sin*64)
            )

        # big wave timer
        if not self.wave_ongoing and self.wave_timeout < 5.0:
            draw.text(
                surface, str(int(self.wave_timeout)+1),
                (size[0]/2, size[1]/2-50), h=0.5, v=0.5,
                style='title', antialias=True,
                size=24+int(self.big_timer_font_size*28)
            )

        # shop
        self.shop.draw(surface)


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
                # populating biome again
                self.map.populate_empty(self.biome.wave_empty_chance)


    def process_shop_input(self):
        '''
        Does the clicking in the shop.
        '''
        # shop buttons
        for i in self.shop.wi_buttons+self.shop.ci_buttons:
            i.hovered = i.rect.collidepoint(self.mouse_pos)

            if self.lmb_down and i.hovered:
                # button clicked
                self.shop.opened = False

                self.builder = Builder(
                    i.item, self.shop,
                    i.wood, i.crystals, None
                )

                break


    def process_input(self, td:float):
        '''
        Does the clicking and stuff.
        '''
        if self.cursor_tile != None:
            obj = self.get_obj_at(self.cursor_tile)
        else:
            obj = None

        # entering cheat codes
        if self.keys_held[pg.K_RSHIFT]:
            try:
                number = [
                    pg.K_0, pg.K_1, pg.K_2, pg.K_3, pg.K_4,
                    pg.K_5, pg.K_6, pg.K_7, pg.K_8, pg.K_9,
                ].index(self.keys_down[0])

                self.code += str(number)
                print(f'Cheat code: {self.code:<4s}',end='\r')

                # checking code
                if len(self.code) >= 4:
                    self.cheat_code()

            except:
                pass

        # moving camera
        if self.mouse_press[1]:
            self.cam_offset[0] -= self.mouse_moved[0]
            self.cam_offset[1] -= self.mouse_moved[1]

            # a fun way to bring the cam in bounds
            mapsize = [
                self.map.size[0]*TILESIZE,
                self.map.size[1]*TILESIZE
            ]
            if self.cam_offset[0] < -APPX:
                self.cam_offset[0] += APPX*2+mapsize[0]
                
            if self.cam_offset[0] > mapsize[0]+APPX:
                self.cam_offset[0] -= APPX*2+mapsize[0]
                
            if self.cam_offset[1] < -APPY:
                self.cam_offset[1] += APPY*2+mapsize[1]
                
            if self.cam_offset[1] > mapsize[1]+APPY:
                self.cam_offset[1] -= APPY*2+mapsize[1]

        # updating build mode
        if self.builder != None:
            # placing
            if self.lmb_down and self.cursor_tile != None:
                # placing
                block_rect = pg.Rect(self.cursor_tile, self.builder.block.size)
                water_tiles = [pg.Rect(*i,1,1) for i in self.map.water_tiles]

                occupied =\
                    block_rect.collidelistall(water_tiles) != []\
                    or block_rect.collidelistall([i.rect for i in self.map.objects]) != []
                
                if self.builder.placeable and not occupied:
                    # adding block
                    self.map.add_object(Object(
                        self.builder.block.tags,
                        self.cursor_tile, self.builder.block
                    ))

                    # cost
                    self.shop.wood -= self.builder.wood
                    self.shop.crystals -= self.builder.crystals

            # exiting builder mode
            if pg.K_ESCAPE in self.keys_down or\
            (self.builder.amount != None and self.builder.amount <= 0):
                self.builder = None

            return

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
                    hovered_enemy.damage(self.cursor.damage)
                    self.timeout()

            # clicking on objects
            elif obj != None and obj.player_damage:
                if self.cursor_timeout > 0.0:
                    obj.kick(0.4)
                else:
                    obj.damage(self.cursor.damage)
                    self.timeout()

                    # adding wood
                    if obj.hp <= 0 and obj.meta.wood > 0:
                        self.add_wood(obj.meta.wood)
                    # adding crystals
                    if obj.hp <= 0 and obj.meta.crystals > 0:
                        self.add_crystals(obj.meta.crystals)

        # right-clicking on objects
        if self.mouse_press[2]:
            if obj != None and obj.meta.player_sell:
                obj.hold_sell += td*2
                obj.kick(obj.hold_sell*2, reset=False)
                
                if obj.hold_sell > 1:
                    obj.events.append(Event('delete'))

                    # adding wood
                    if obj.meta.wood > 0:
                        self.add_wood(obj.meta.wood)
                    # adding crystals
                    if obj.meta.crystals > 0:
                        self.add_crystals(obj.meta.crystals)

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


    def update_game(self, td:float):
        '''
        Updates the ongoing game.
        '''
        # updating wave
        self.update_wave(td)

        # updating objects
        new = []
        deleted = False

        for obj in self.map.objects:
            if obj.hold_sell > 0.0:
                obj.hold_sell -= td
            events: List[Event] = obj.update(td, self.map)
            delete: bool = False

            # processing object events
            for i in events:
                # removing object
                if i.type == 'delete':
                    delete = True
                # adding projectile to the map
                if i.type == 'proj':
                    self.map.projectiles.append(
                        i.meta
                    )

            if not delete:
                new.append(obj)
            else:
                deleted = True
        
        self.map.objects = new
        if deleted:
            self.map.update_objects()
        
        # updating projectiles
        new = []

        for proj in self.map.projectiles:
            proj.update(td, self.map)

            if not proj.deletable:
                new.append(proj)

        self.map.projectiles = new

        # updating enemies
        new = []
        water_tiles = [
            pg.FRect(*i,1,1) for i in self.map.water_tiles
        ]

        for i in self.map.enemies:
            # checking collision with water
            this_td = deepcopy(td)
            if i.rect.collidelistall(water_tiles):
                this_td *= 0.5

            # updating
            i.update(this_td, self.map)

            if not i.deletable:
                new.append(i)
            else:
                self.cursor.kill()
                self.add_crystals(i.cost)

        self.map.enemies = new

        # cursor timeout
        if self.cursor_timeout > 0.0:
            self.cursor_timeout -= td

        # updating popup
        if self.popup != None:
            self.popup.update(td)

        # updating ui
        self.wood_rot.update(td)
        self.crystals_rot.update(td)
        
        # builder mode string flash
        if self.builder:
            self.builder_key += td*7 % 3.14
            self.builder_sin = np.sin(self.builder_key)

    
    def update(self, td:float, events:List[pg.Event], mouse_pos:Tuple[int,int]):
        '''
        Updates the current menu.
        '''
        # input
        self.update_input(events, mouse_pos)

        if not self.shop.opened:
            self.process_input(td)
        else:
            self.process_shop_input()

        # opening shop
        if pg.K_SPACE in self.keys_down:
            self.shop.opened = not self.shop.opened
            
        # game
        if not self.shop.opened:
            self.update_game(td)
        
        # shop
        self.shop.update(td)
