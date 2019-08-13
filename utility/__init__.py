import math
import datetime


def save_highscores(score):
    with open('highscores.txt', 'a') as f:
        f.write('{} - {}\n'.format(datetime.datetime.now(), score))


class Vector2:
    x: float
    y: float

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def normalized(self) -> 'Vector2':
        length = self.length()
        return Vector2(self.x / length, self.y / length)

    def length(self):
        return math.hypot(self.x, self.y)

    @classmethod
    def between(cls, x1, y1, x2, y2):
        return Vector2(x2 - x1, y2 - y1)

