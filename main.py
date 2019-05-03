import pyglet
from pyglet.window import key
import math
import random

### GLOBAL VARIABLES
npc_counter = 0

### HELPER FUNCTIONS
def create_NPC(dt):
    global npc_counter
    npc_counter += 1
    vertical = random.choice([True, False])
    if vertical:
        x = random.randint(0, window.width)
        y = random.choice([-1.5, 1.5]) * window.height + (window.height // 2)
    else:
        x = random.choice([-1.5, 1.5]) * window.width + (window.width // 2)
        y = random.randint(0, window.height)
    NPC(
        pyglet.resource.image('images/orange_block.png'),
        x,
        y,
        100 + npc_counter * 2
    )
    pyglet.clock.schedule_once(create_NPC, 2)

def destroy_gameobject(obj):
    if not obj in gameobjects_to_destroy:
        gameobjects_to_destroy.append(obj)

def destroy_gameobjects(dt):
    global gameobjects_to_destroy
    for obj in gameobjects_to_destroy:
        if obj in gameobjects:
            gameobjects.remove(obj)
    gameobjects_to_destroy = []

def update(dt):
    for obj in gameobjects:
        obj.update(dt)

### COMPONENTS
class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

class Shooting:
    def __init__(self, image):
        self.direction = (0, 0)
        self.image = image

class Collider:
    def __init__(self, rect):
        self.rect = rect

### GAMEOBJECTS
class GameObject:
    def __init__(self, image, x=0.0, y=0.0):
        # Assigns the image of the gameobject, and sets the pivot to center
        self.image = image
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2

        # Assigns the gameobject's position
        self.pos = Position(x, y)
        
        gameobjects.append(self)
    
    def update(self, dt):
        pass

class Human(GameObject):
    def __init__(self, image, x=0.0, y=0.0):
        super().__init__(image, x, y)
        self.vel = Velocity()
        self.movespeed = 200.0
        
    def update(self, dt):
        self.pos.x += self.vel.x * self.movespeed * dt
        self.pos.y += self.vel.y * self.movespeed * dt

class NPC(Human):
    def __init__(self, image, x=0.0, y=0.0, movespeed=100.0):
        super().__init__(image, x, y)
        self.movespeed = movespeed

    def set_vel_towards_player(self):
        x_diff = player.pos.x - self.pos.x
        y_diff = player.pos.y - self.pos.y
        max_diff = max(abs(x_diff), abs(y_diff))
        if max_diff < 1:
            ratio = 1
        else:
            ratio = 1 / abs(max_diff)
        self.vel.x = ratio * x_diff
        self.vel.y = ratio * y_diff

    def check_collision(self):
        for obj in gameobjects:
            if type(obj) is Bullet:
                if math.hypot(obj.pos.x - self.pos.x, obj.pos.y - self.pos.y) < 32:
                    destroy_gameobject(self)
                    destroy_gameobject(obj)
            elif type(obj) is Player:
                if math.hypot(obj.pos.x - self.pos.x, obj.pos.y - self.pos.y) < 32:
                    event_loop.exit()

    def update(self, dt):
        self.set_vel_towards_player()
        super().update(dt)
        self.check_collision()

class Player(Human):
    def __init__(self, image, bulletimage, x=0.0, y=0.0):
        super().__init__(image, x, y)
        self.shoot = Shooting(bulletimage)

    def update(self, dt):
        super().update(dt)
        if self.shoot.direction != (0, 0):
            Bullet(
                self.shoot.image,
                self.pos.x,
                self.pos.y,
                self.shoot.direction[0],
                self.shoot.direction[1]
            )
            self.shoot.direction = (0, 0)

class Bullet(GameObject):
    def __init__(self, image, x, y, vx, vy):
        super().__init__(image)

        self.pos = Position(x, y)
        self.vel = Velocity(vx, vy)
        self.movespeed = 500.0

        self.age = 0
        self.maxage = 3

    def update(self, dt):
        self.pos.x += self.vel.x * self.movespeed * dt
        self.pos.y += self.vel.y * self.movespeed * dt
        self.age += dt
        if self.age > self.maxage:
            destroy_gameobject(self)

### INITIALIZE
window = pyglet.window.Window(fullscreen=False)
window.set_caption("GAME")
event_loop = pyglet.app.EventLoop()
gameobjects = []
gameobjects_to_destroy = []

pyglet.clock.schedule(destroy_gameobjects)
pyglet.clock.schedule(update)

player = Player(
    pyglet.resource.image('images/red_block.png'),
    pyglet.resource.image('images/small_blue_block.png'),
    x = window.width // 2,
    y = window.height // 2
)

create_NPC(0)

### EVENTS
@window.event
def on_close():
    event_loop.exit()

@window.event
def on_draw():
    window.clear()
    player.image.blit(player.pos.x, player.pos.y)
    for obj in gameobjects:
        obj.image.blit(obj.pos.x, obj.pos.y)

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
        player.shoot.direction = (0, 1)
    elif symbol == key.DOWN:
        player.shoot.direction = (0, -1)
    elif symbol == key.LEFT:
        player.shoot.direction = (-1, 0)
    elif symbol == key.RIGHT:
        player.shoot.direction = (1, 0)

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

### RUN
event_loop.run()