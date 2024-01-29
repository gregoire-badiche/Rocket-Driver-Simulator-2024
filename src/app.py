#!/usr/bin/env python3

import pygame
import math
from random import randint
from os import listdir
from os.path import isfile, join

G:int = 1000000
planet = [join("src/textures/Planets/",files) for files in listdir("src/textures/Planets/") if isfile(join("src/textures/Planets/", files))]
black_hole=[join("src/textures/Blackhole/",files) for files in listdir("src/textures/Blackhole/") if isfile(join("src/textures/Blackhole/", files))]

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

CENTERX = screen.get_width() / 2
CENTERY = screen.get_height() / 2

class Chunk:
    def __init__(self, x, y) -> None:
        self.sprites = []
        return

    def __len__(self) -> int:
        return len(self.sprites)

    def addsprite(self, sprite) -> None:
        self.sprites.append(sprite)
        return len(self.sprites) - 1
    
    def update(self, *args) -> None:
        for s in self.sprites:
            if(isinstance(s, Sprite)):
                s.update(*args)
        return
    
    def draw(self, x, y, *args) -> None:
        for s in self.sprites:
            if(isinstance(s, Sprite)):
                s.draw(x, y, *args)
        return

class Sprite:
    def __init__(self, chunk:Chunk, x, y) -> None:
        self.chunk = chunk
        self.chunkindex = chunk.addsprite(self)
        self.x = x
        self.y = y
        self.speedx = 0
        self.speedy = 0
        self.angle = 0
        return

    def kill(self) -> None:
        del self.chunk.sprites[self.chunkindex]
        return
    
    def draw(self, *args):
        pass

    def update(self, *args):
        pass

class MainCharacter(Sprite):
    def __init__(self, chunk: Chunk, x, y) -> None:
        super().__init__(chunk, 0, 0)
        self.mass = 2
        self.drawx = x
        self.drawy = y
        self.angle = 0
        self.rotation = 0
        self.texture_forward=pygame.image.load("src/textures/Rocket/player.png")
        self.texture_right=pygame.image.load("src/textures/Rocket/player_right.png")
        self.texture_left=pygame.image.load("src/textures/Rocket/player_left.png")
        self.texture=self.texture_forward
        return
    
    def update(self, dt) -> None:
        self.x += self.speedx * dt
        self.y += self.speedy * dt
        self.angle += self.rotation * dt
        self.texture_forward=pygame.transform.rotate(pygame.image.load("src/textures/Rocket/player.png"), -math.degrees(self.angle)) 
        self.texture_right=pygame.transform.rotate(pygame.image.load("src/textures/Rocket/player_right.png"), -math.degrees(self.angle))
        self.texture_left=pygame.transform.rotate(pygame.image.load("src/textures/Rocket/player_left.png"), -math.degrees(self.angle))
        print('\033[3J')
        print(f"x: {int(self.x)}, y: {int(self.y)}")
        print(f"speed: {int(math.sqrt(self.speedx ** 2 + self.speedy ** 2))}")
        # if(self.x < 0 or self.x > screen.get_width()):
        #     self.speedx = -1 * self.speedx
        # if(self.y < 0 or self.y > screen.get_height()):
        #     self.speedy = -1 * self.speedy
        return
    
    def draw(self, *args) -> None:
        screen.blit(self.texture, (CENTERX, CENTERY))
        return


class CelestialBody(Sprite):
    def __init__(self, chunk: Chunk, x, y, radius, mass) -> None:
        super().__init__(chunk, x, y)
        self.radius = radius
        self.mass = mass
        return

    def update(self, dt, sprite:MainCharacter):
        x = self.x - sprite.x
        y = self.y - sprite.y
        m2 = self.mass
        dist = math.sqrt(x ** 2 + y ** 2)
        if(dist > self.radius + 5):
            unitx = x / dist
            unity = y / dist
            force = G * m2 / (x ** 2 + y ** 2)
            if(force < 10):
                return
            sprite.speedx += unitx * force * dt
            sprite.speedy += unity * force * dt

class Planet(CelestialBody):
    def __init__(self, chunk: Chunk, x, y, radius) -> None:
        super().__init__(chunk, x, y, radius, radius)
        randnum=randint(0,len(planet)-1)
        self.directory=planet[randnum]
        del planet[randnum]
        self.texture=pygame.image.load(self.directory)
        self.texture = pygame.transform.scale(self.texture, (radius*2, radius*2))
        return
    
    def draw(self, x, y, *args) -> None:
        screen.blit(self.texture, (CENTERX + self.x - x - self.radius, CENTERY + self.y - y - self.radius))
        return

class BlackHole(CelestialBody):
    def __init__(self, chunk: Chunk, x, y, radius, mass) -> None:
        super().__init__(chunk, x, y, radius, mass)
        self.directory=black_hole[randint(0,len(black_hole)-1)]
        self.texture=pygame.image.load(self.directory)
        self.texture = pygame.transform.scale(self.texture, (radius*2, radius*2))
        
    def draw(self, x, y, *args) -> None:
        screen.blit(self.texture, (CENTERX + self.x - x - self.radius, CENTERY + self.y - y - self.radius))
        return

class BackgroundStar(Sprite):
    def __init__(self, chunk: Chunk, x, y) -> None:
        self.generate(x, y)
        super().__init__(chunk, self.x, self.y)
    
    def draw(self, x, y):
        if(self.y - y > screen.get_height() + 20):
            self.relocate(x, y, 0)
        elif(-20 > self.y - y):
            self.relocate(x, y, 1)
        elif(self.x - x > screen.get_width() + 20):
            self.relocate(x, y, 2)
        elif(-20 > self.x - x):
            self.relocate(x, y, 3)
        else:
            pygame.draw.circle(screen, "yellow", (self.x - x, self.y - y), self.radius)
        return
    
    def generate(self, x, y):
        self.x = randint(0, screen.get_width()) + x
        self.y = randint(0, screen.get_height()) + y
        self.radius = randint(1, 3)
    
    def relocate(self, posx, posy, code):
        x = 0
        y = 0
        if(code == 0):
            x = randint(0, screen.get_width())
            y = -10
        if(code == 1):
            x = randint(0, screen.get_width())
            y = screen.get_height() + 10
        if(code == 2):
            y = randint(0, screen.get_height())
            x = -10
        if(code == 3):
            y = randint(0, screen.get_height())
            x = screen.get_width() + 10
        
        self.x = x + posx
        self.y = y + posy
        self.radius = randint(1, 3)
        return
    


ch = Chunk(0, 0)
ch2 = Chunk(0, 1)
sp = MainCharacter(ch2, screen.get_width() / 2, screen.get_height() / 2)
pl = Planet(ch, 400, 400, 30)
pl2 = Planet(ch, 600, 300, 15)
pl3 = Planet(ch, 1000, 600, 25)
pl4 = Planet(ch, 700, 200, 20)
bh = BlackHole(ch, 2000, 2000, 75, 300)

for i in range(100):
    x = BackgroundStar(ch, 0, 0)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close the window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    momentumx = 0
    momentumy = 0
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] or keys[pygame.K_s]:
        momentumy += math.sin(sp.angle)
        momentumx += math.cos(sp.angle)
    if keys[pygame.K_q]:
        sp.rotation -= 100 * dt
        sp.texture=sp.texture_left
        move=False
    else:
        sp.texture=sp.texture_forward
        move=True
    if keys[pygame.K_d]:
        sp.rotation += 100 * dt
        sp.texture=sp.texture_right
    elif move:
        sp.texture=sp.texture_forward

        
    print(sp.rotation)

    sp.speedx += momentumx * 800 * dt
    sp.speedy += momentumy * 800 * dt
    
    ch2.update(dt)
    ch.update(dt, sp)

    # fill the screen with a color to wipe away anything from last frame
    screen.fill((0, 0, 50))

    ch.draw(sp.x, sp.y)
    ch2.draw(0, 0)

    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(120) / 5000