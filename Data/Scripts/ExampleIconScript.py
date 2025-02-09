import pygame
from utils.res.ResourceManager import resource_manager

icon = resource_manager.get_image("Icons\\winico\\icon_16x16_python.png")

def main(event):
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Game Test")
    