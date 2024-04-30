from typing import *

import numpy as np

# todo PARTICLE DAMN
# class Particle:
#     def __init__(
#         self,
#         starting_pos:Tuple[float,float],
#         starting_deg:float,
#         starting_spd:float,
#         acceleration:float,
#         lifetime:float,
#         start_size:int, end_size:int,
#         color:Tuple[int,int,int],
#         blink_time:float=0.0
#     ):
#         self.pos: Tuple[float,float] = starting_pos
#         self.deg: float = starting_deg
#         self.speed: float = starting_spd
#         self.acceleration: float = acceleration
        
#         self.lifetime: float = lifetime
#         self.ticks: float = 0.0

#         self.start_size: int = start_size
#         self.end_size: int = end_size
#         self.blink_time: float = blink_time
#         self.color: Tuple[int,int,int] = color


#     @property
#     def size(self) -> int:
#         '''
#         Returns the size of the particle.
#         '''
#         return int(lerp(self.start_size, self.end_size), self.ticks/self.lifetime)


class VectorCoord:
    def __init__(
        self,
        starting_pos:Tuple[float,float],
        starting_deg:float,
        starting_spd:float,
        acceleration:float,
        allow_subzero_spd:bool=False
    ):
        self.pos: Tuple[float,float] = list(starting_pos)
        self.deg: float = starting_deg
        self.speed: float = starting_spd
        self.acceleration: float = acceleration
        self.subzero_spd: bool = allow_subzero_spd


    def point_towards(self, pos:Tuple[int,int]):
        '''
        Points the vector towards the position.
        '''
        self.deg = angle_between(self.pos, pos)+np.pi/2


    def update(self, step:float) -> int:
        '''
        Updates the vector.
        '''
        # updating speed
        if self.subzero_spd or\
        (not self.subzero_spd and self.speed > 0.0):
            self.speed += self.acceleration*step
            if not self.subzero_spd and self.speed < 0.0:
                self.speed = 0.0

        # moving
        self.pos[0] += np.sin(self.deg)*self.speed*step
        self.pos[1] += np.cos(self.deg)*self.speed*step
        

def angle_between(a:Tuple[int,int], b:Tuple[int,int]) -> float:
    '''
    Returns an angle between 2 points in radians.
    '''
    angle = np.arctan2(a[1] - b[1], b[0] - a[0])
    if angle < 0:
        angle += np.pi*2
    return angle


def get_distance(p1: Tuple[float,float], p2: Tuple[float,float]) -> float:
    '''
    Returns distance between two 2D points.
    '''
    return ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5


def lerp(a:float, b:float, t:float) -> float:
    '''
    Interpolates between A and B.
    '''
    t = max(0,min(1,t))
    return (1 - t) * a + t * b