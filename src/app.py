#!/usr/bin/env python3

import pygame
import math
from random import randint
import textures

G:int = 10

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
        self.chunk.sprites.remove(self)
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
        self.isboosting = False
        self.timeboosting = 0
        self.particlechunk = Chunk(0, 0)
        return
    
    def update(self, dt) -> None:
        self.particlechunk.update(dt)

        self.x += self.speedx * dt
        self.y += self.speedy * dt
        self.angle += self.rotation * dt

        if(self.isboosting):
            self.timeboosting += dt
            n = 0
            if(self.timeboosting > 1):
                n = self.timeboosting // 1
                self.timeboosting = 0
            for i in range(int(n)):
                x = randint(0, 2)
                if(x == 0):
                    radius = randint(2, 3)
                    timeout = randint(500, 750)
                    speed = randint(400, 800) / 1000
                    velocity = {
                        "x": (speed * math.cos(self.angle + math.pi)) + self.speedx,
                        "y": (speed * math.sin(self.angle + math.pi)) + self.speedy
                    }
                    color = "yellow"
                elif(x == 1):
                    radius = randint(4, 5)
                    timeout = randint(250, 500)
                    speed = randint(400, 800) / 1000
                    velocity = {
                        "x": (speed * math.cos(self.angle + math.pi)) + self.speedx,
                        "y": (speed * math.sin(self.angle + math.pi)) + self.speedy
                    }
                    color = "darkorange"
                else:
                    radius = 6
                    timeout = randint(50, 250)
                    speed = randint(400, 800) / 1000
                    velocity = {
                        "x": (speed * math.cos(self.angle + math.pi)) + self.speedx,
                        "y": (speed * math.sin(self.angle + math.pi)) + self.speedy
                    }
                    color = "red"
                Particle(self.particlechunk, CENTERX + self.x, CENTERY + self.y, radius, color, velocity, timeout)

        print('\033[3J')
        print(f"x: {int(self.x)}, y: {int(self.y)}")
        print(f"speed: {int(math.sqrt(self.speedx ** 2 + self.speedy ** 2) * 1000)}")
        return
    
    def draw(self, x, y, *args) -> None:
        self.particlechunk.draw(x, y)
        p1 = (CENTERX + (20 * math.cos(self.angle)), CENTERY + (20 * math.sin(self.angle)))
        p2 = (CENTERX + (10 * math.cos(self.angle + (2 * math.pi / 3))), CENTERY + (10 * math.sin(self.angle + (2 * math.pi / 3))))
        p3 = (CENTERX + (10 * math.cos(self.angle + (4 * math.pi / 3))), CENTERY + (10 * math.sin(self.angle + (4 * math.pi / 3))))
        pygame.draw.polygon(screen, "white", (p1, p2, p3))
        return

class Particle(Sprite):
    def __init__(self, chunk: Chunk, x, y, radius, color, velocity, timeout) -> None:
        super().__init__(chunk, x, y)
        self.timeout = timeout
        self.timelived = 0
        self.velocity = velocity
        self.color = color
        self.radius = radius
        self.ogradius = radius
    
    def update(self, delta, *args):
        self.timelived += delta
        self.radius = self.ogradius * (self.timeout - self.timelived) / self.timeout
        if(self.timelived > self.timeout):
            self.kill()
        self.x += self.velocity["x"] * delta
        self.y += self.velocity["y"] * delta
        return
    
    def draw(self, x, y):
        pygame.draw.circle(screen, self.color, (self.x - x, self.y - y), self.radius)
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
            if(force < .001):
                return
            sprite.speedx += unitx * force * dt / 10000
            sprite.speedy += unity * force * dt / 10000

class Planet(CelestialBody):
    def __init__(self, chunk: Chunk, x, y, radius) -> None:
        super().__init__(chunk, x, y, radius, radius ** 2)
        self.planet_texture=textures.Planet_texture(self.radius).texture
        return
    
    def draw(self, x, y, *args) -> None:
        screen.blit(self.planet_texture, (CENTERX + self.x - x - self.radius, CENTERY + self.y - y - self.radius))
        return

class BlackHole(CelestialBody):
    def __init__(self, chunk: Chunk, x, y, radius, mass) -> None:
        super().__init__(chunk, x, y, radius, mass)
        
    def draw(self, x, y, *args) -> None:
        pygame.draw.circle(screen, "black", (CENTERX + self.x - x, CENTERY + self.y - y), self.radius)
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

for i in range(100):
    x = BackgroundStar(ch, 0, 0)

sp = MainCharacter(ch2, screen.get_width() / 2, screen.get_height() / 2)
pl = Planet(ch, 4000, 4000, 300)
pl2 = Planet(ch, 3000, 300, 150)
pl3 = Planet(ch, 1000, 600, 250)
pl4 = Planet(ch, 700, 2500, 200)
pl5 = Planet(ch, 2000, 900, 100)
# bh = BlackHole(ch, 2000, 2000, 10, 3000)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close the window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    momentumx = 0
    momentumy = 0
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] or keys[pygame.K_z]:
        momentumy += math.sin(sp.angle)
        momentumx += math.cos(sp.angle)
        sp.isboosting = True
    else:
        sp.isboosting = False
    if keys[pygame.K_q]:
        sp.rotation -= .00001 * dt
    if keys[pygame.K_d]:
        sp.rotation += .00001 * dt

    sp.speedx += momentumx * dt * .0001
    sp.speedy += momentumy * dt * .0001

    ch2.update(dt)
    ch.update(dt, sp)

    # fill the screen with a color to wipe away anything from last frame
    screen.fill((0, 0, 50))

    ch.draw(sp.x, sp.y)
    ch2.draw(sp.x, sp.y)

    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(120)
