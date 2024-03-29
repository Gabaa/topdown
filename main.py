from utility import *

import pyglet
from pyglet.window import key
import math
import random

# GLOBAL VARIABLES
npc_counter = 0


# HELPER FUNCTIONS
def create_npc(dt):
    global npc_counter

    npc_counter += 1

    # whether the npc will spawn from the sides or top/bottom
    xspawn, yspawn = random.choice(((0, 1), (0, -1), (1, 0), (-1, 0)))

    # extracting x and y coordinates from the spawnpoint
    if xspawn == 0:
        x = random.randint(0, window.width)
        y = 0.5 * window.height + yspawn * window.height * 0.6
    else:
        x = 0.5 * window.width + xspawn * window.width * 0.6
        y = random.randint(0, window.height)

    NPC(x, y, 150 + npc_counter * 2)


def update(dt):
    # Updating all gameobjects
    for obj in gameobjects:
        obj.update(dt)

    # Removing all gameobjects that are "dirty"
    for obj in dirty_gameobjects:
        if obj in gameobjects:
            gameobjects.remove(obj)
    dirty_gameobjects.clear()


# COMPONENTS
class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Gun:
    direction: tuple
    ammo: int
    max_ammo: int
    reload_time: float
    reload_timer: float

    def __init__(self, max_ammo, reload_time):
        self.direction = (0, 0)

        self.ammo = max_ammo
        self.max_ammo = max_ammo

        self.reload_time = reload_time
        self.reload_timer = 0


# GAMEOBJECTS
class GameObject:
    def __init__(self, x, y, w, h, movespeed, color):
        # Assigns the gameobject's position
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.movespeed = movespeed
        self.vel = Velocity()

        gameobjects.append(self)

    def update(self, dt):
        self.x += self.vel.x * self.movespeed * dt
        self.y += self.vel.y * self.movespeed * dt

    def draw(self):
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                             ('v2f', (self.x, self.y,
                                      self.x, self.y + self.h,
                                      self.x + self.w, self.y + self.h,
                                      self.x + self.w, self.y)),
                             ('c3B', self.color * 4))

    def destroy(self):
        if self not in dirty_gameobjects:
            dirty_gameobjects.append(self)


class NPC(GameObject):
    def __init__(self, x, y, movespeed):
        super().__init__(x, y, 32, 32, movespeed, (255, 120, 0))

    def set_vel_towards(self, obj):
        v = Vector2.between(self.x, self.y, obj.x, obj.y)

        if v.length() > 1:
            v = v.normalized()

        self.vel.x = v.x
        self.vel.y = v.y

    def check_collision(self):
        for obj in gameobjects:
            if type(obj) is Bullet:
                if math.hypot(obj.x - self.x, obj.y - self.y) < 32:
                    self.destroy()
                    obj.destroy()
            elif type(obj) is Player:
                if math.hypot(obj.x - self.x, obj.y - self.y) < 32:
                    pyglet.app.exit()

    def update(self, dt):
        self.set_vel_towards(player)
        super().update(dt)
        self.check_collision()


class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32, 200, (255, 0, 0))
        self.gun = Gun(5, 0.5)

    def update(self, dt):
        super().update(dt)

        self.gun.reload_timer += dt
        if self.gun.ammo < self.gun.max_ammo and self.gun.reload_timer > self.gun.reload_time:
            self.gun.ammo += 1
            self.gun.reload_timer = 0

        if self.gun.direction != (0, 0) and self.gun.ammo > 0:
            Bullet(self.x,
                   self.y,
                   self.gun.direction[0],
                   self.gun.direction[1])

            self.gun.reload_timer = -0.25

            self.gun.ammo -= 1

        self.gun.direction = (0, 0)


class Bullet(GameObject):
    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, 16, 16, 500.0, (0, 0, 255))
        self.vel = Velocity(vx, vy)
        self.age = 0
        self.maxage = 3

    def update(self, dt):
        self.x += self.vel.x * self.movespeed * dt
        self.y += self.vel.y * self.movespeed * dt
        self.age += dt
        if self.age > self.maxage:
            self.destroy()


# INITIALIZE
window = pyglet.window.Window(fullscreen=True)

gameobjects = []
dirty_gameobjects = []

# Run the update function
pyglet.clock.schedule(update)

# Spawn a new NPC every 1 second
pyglet.clock.schedule_interval(create_npc, 1)

player = Player(x=window.width // 2,
                y=window.height // 2)

ammo_label = pyglet.text.Label('Ammo: {}'.format(player.gun.ammo),
                               x=window.width // 2, y=window.height * 0.05,
                               anchor_x='center', anchor_y='center',
                               font_name='Consolas', font_size=30)

npc_label = pyglet.text.Label('NPCs spawned: {}'.format(npc_counter),
                              x=window.width // 2, y=window.height * 0.05 + 50,
                              anchor_x='center', anchor_y='center',
                              font_name='Consolas', font_size=30)


# EVENTS
@window.event
def on_close():
    pyglet.app.exit()


@window.event
def on_draw():
    window.clear()

    for obj in gameobjects:
        obj.draw()

    ammo_label.text = 'Ammo: {}'.format(player.gun.ammo)
    ammo_label.draw()

    npc_label.text = 'NPCs spawned: {}'.format(npc_counter)
    npc_label.draw()

    window.set_caption("Top Down Shooter - Score: " + str(npc_counter))


@window.event
def on_key_press(symbol, modifiers):
    # Movement keys
    if symbol == key.A:
        player.vel.x -= 1
    elif symbol == key.D:
        player.vel.x += 1
    elif symbol == key.W:
        player.vel.y += 1
    elif symbol == key.S:
        player.vel.y -= 1
    # Shooting keys
    elif symbol == key.UP:
        player.gun.direction = (0, 1)
    elif symbol == key.DOWN:
        player.gun.direction = (0, -1)
    elif symbol == key.LEFT:
        player.gun.direction = (-1, 0)
    elif symbol == key.RIGHT:
        player.gun.direction = (1, 0)


@window.event
def on_key_release(symbol, modifiers):
    # Movement keys
    if symbol == key.A:
        player.vel.x += 1
    elif symbol == key.D:
        player.vel.x -= 1
    elif symbol == key.W:
        player.vel.y -= 1
    elif symbol == key.S:
        player.vel.y += 1


# RUN
pyglet.app.run()

save_highscores(npc_counter)
