from os import listdir
from os.path import isfile, join
from random import randint
import pygame



#define lists with all directories for our sprite textures
planet = ("src/textures/Planets/",[files for files in listdir("src/textures/Planets/") if isfile(join("src/textures/Planets/", files))])

def extract_extension(text):
    go=False
    c=str()
    for i in text:
        if not(go) and i==".":
            go=True
        elif go:
            c+=i

class Planet_texture:
    def __init__(self,radius)-> None:
        directory=join(planet[0], planet[1][randint(0,len(planet[1])-1)])
        self.texture=pygame.image.load(directory)
        self.texture = pygame.transform.scale(self.texture, (radius*2, radius*2))
        return

