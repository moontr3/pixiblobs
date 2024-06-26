# LIGRARIES
import pygame as pg
from typing import *
from copy import deepcopy


# CLASSES
class FontGroup:
    def __init__(self, font_folder:str):
        '''
        A class that manages all loaded fonts and
        saves the loaded objects for later use.
        '''
        self.font_folder: str = font_folder
        self.fonts: Dict[str, Dict[int, pg.font.Font]] = {}

    def init_font(self, size:int, style:str):
        '''
        Creates a new saved font object or replaces current
        with the new one.
        '''
        if style not in self.fonts:
            self.fonts[style] = {}
        self.fonts[style][size] =\
            pg.font.Font(self.font_folder+style+'.ttf', size)

    def find(self, size:int, style:str):
        '''
        Request the font object.

        If font is not loaded, creates a new saved font
        using `init_font` and returns it.
        '''
        if style in self.fonts:
            if size in self.fonts[style]:
                return self.fonts[style][size]
        
        self.init_font(size, style)
        return self.find(size, style)

class ImageType:
    def __init__(self, image_path:str):
        '''
        A class that manages a single image and
        saves the resized versions of the image for later use.
        '''
        self.image_path: str = image_path
        self.base_image: pg.Surface = pg.image.load(image_path).convert_alpha()
        self.base_image_size = self.base_image.get_size()
        self.resized_images: Dict[str, pg.Surface] = {}

    def param_to_str(self, size:Union[int, int], smooth:bool, fliph=False, flipv=False):
        '''
        Converts data used to request the image to `str` format.
        
        This is required for indexing in dicts.
        '''
        return str(int(smooth))+str(int(fliph))+str(int(flipv))+f'{size[0]},{size[1]}'
    
    def init_image(self, size:Union[int, int], smooth:bool, fliph:bool, flipv:bool, str_param:str):
        '''
        Resizes the base image and saves it for
        later use.
        '''
        func = pg.transform.scale if not smooth else pg.transform.smoothscale
        image = func(self.base_image, size)
        if fliph != False or flipv != False:
            image = pg.transform.flip(image, fliph, flipv)
        self.resized_images[str_param] = image

    def find(self, size:Union[int, int], smooth=True, fliph=False, flipv=False):
        '''
        Request the resized image.

        If the image was not resized yet (and thus not
        saved in the dictionary), resizes the image using
        `init_image` and returns it.
        '''
        if size == self.base_image_size and fliph == False and flipv == False:
            return self.base_image

        str_param = self.param_to_str(size, smooth, fliph, flipv)

        if str_param in self.resized_images:
            return self.resized_images[str_param]
        else:
            self.init_image(size, smooth, fliph, flipv, str_param)
            return self.find(size, smooth, fliph, flipv)

class ImageGroup:
    def __init__(self, image_folder:str, unknown_image_path:str):
        '''
        A class that manages all images inside a
        folder and all folders inside the parent
        folder recursively.
        '''
        self.image_folder: str = image_folder
        self.unknown_image_path: str = unknown_image_path
        self.images: Dict[str, ImageType] = {}

    def init_image(self, image:str, image_path:str):
        '''
        Creates a new `ImageType` if it was not
        created yet.
        '''
        self.images[image] = ImageType(image_path)

    def find(self, image:str, size:Union[int,int], smooth=True, fliph=False, flipv=False):
        '''
        Request a resized image.
        
        If the image is not loaded yet, loads it using
        `init_image` and returns the correct image.
        '''
        if image in self.images:
            return self.images[image].find(size, smooth, fliph, flipv)
        else:
            try:
                self.init_image(image, self.image_folder+image)
                return self.find(image, size, smooth, fliph, flipv)
            except:
                return self.find(self.unknown_image_path, size, smooth, fliph, flipv)

# INITIALIZING OBJECTS
pg.font.init()

DEFAULT_FONT_SIZE = 8
fonts = FontGroup("res/fonts/")
images = ImageGroup("res/images/", "unknown.png")


# TEXT DRAWING
def text(
    surface: pg.Surface,
    target_text: str = '',
    pos: Tuple[int,int] = (0,0),
    color: Tuple[int,int,int] = (25,25,25), 
    size: int = DEFAULT_FONT_SIZE,
    style: str = 'regular', 
    h: float = 0.0, 
    v: float = 0.0, 
    antialias: bool = False, 
    rotation: int = 0,
    opacity: int = 255,
    shadows: List[Tuple[int,int]] = [],
    shadow_color: Tuple[int,int,int] = (255,255,255)
) -> Tuple[int,int]:
    '''
    Draws text on the specified surface.
    '''

    target_text = str(target_text)

    # drawing shadows
    for i in shadows:
        text(
            surface, target_text,
            [pos[0]+i[0], pos[1]+i[1]],
            shadow_color, size,
            style, h, v, antialias,
            rotation, opacity
        )

    # getting font
    font = fonts.find(size, style)
    rtext = font.render(target_text, antialias, color)

    # rotation
    if rotation != 0:
        rtext = pg.transform.rotate(rtext, rotation)

    # opacity
    if opacity != 255:
        rtext.set_alpha(opacity)

    # aligning
    btext = rtext.get_rect()
    btext.topleft = pos

    # shifting the image
    # both 0.0 = pos variable is topleft
    # both 0.5 = pos variable is the center
    # both 1.0 = pos variable is bottomright
    # you get the idea
    # same for the image function (too lazy to write this there)
    if h != 0.0:
        btext.x -= btext.size[0]*h
    if v != 0.0:
        btext.y -= btext.size[1]*v
    
    # drawing
    surface.blit(rtext, btext)
    return btext.size


# IMAGE DRAWING
def image(
    surface: pg.Surface,
    image: str,
    pos: Tuple[int,int] = (0,0),
    size: Tuple[int,int] = (48,48), 
    h: float = 0.0, 
    v: float = 0.0, 
    rotation: int = 0,
    opacity: int = 255,
    fliph: bool = False,
    flipv: bool = False,
    smooth: bool = True,
    blending: int = 0
):
    '''
    Draws an image on the specified surface.
    '''
    # size
    size = [max(1,size[0]), max(1,size[1])]

    # getting image
    image = deepcopy(images.find(image, size, smooth, fliph, flipv))

    # rotation
    if rotation != 0:
        image = pg.transform.rotate(image, rotation)

    # opacity
    if opacity != 255:
        image.set_alpha(opacity)

    # aligning
    rect = image.get_rect()
    rect.topleft = pos

    # shifting the image
    # more in `text` func
    if h != 0.0:
        rect.x -= rect.size[0]*h
    if v != 0.0:
        rect.y -= rect.size[1]*v
    
    # drawing
    surface.blit(image, rect, special_flags=blending)


# TEXT SIZE
def get_text_size(text='', size=DEFAULT_FONT_SIZE, style='regular'):
    '''
    Returns the dimensions of the text in the specified font.
    '''
    font = fonts.find(size, style)
    return font.size(text)