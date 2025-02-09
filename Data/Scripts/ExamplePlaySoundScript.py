import pygame  # - import PyGame Lib
from utils.res.ResourceManager import resource_manager  # <- Import ResManager util

sound_played = False  # - Check status

def play_sound(event):  # <- script function
    global sound_played  # <- Setting the main variable
    if not sound_played:  # <- checking whether the sound was played, if not then play it
        try:
            pygame.mixer.init()
            sound = resource_manager.get_sound('Sounds\\mus\\test.ogg')
            sound.play(loops=-1) 
            sound_played = True
        except Exception as e:
            print(f"Error: {e}")
