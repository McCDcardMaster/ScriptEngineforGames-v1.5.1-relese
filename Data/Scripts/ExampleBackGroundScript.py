import pygame # <- import PyGame Lib
from utils.gamewindow import size # <- Load utils game window

from utils.res.ResourceManager import resource_manager # <- Import ResManager Util

bg = resource_manager.get_image("Images\\backgrounds\\bg2.png") # <- Load background image

def background_script(event): # <- Script function
    size.window_size.blit(bg, (0, 0)) # <- Draw background