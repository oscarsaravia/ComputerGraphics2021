from lib import *
from math import pi, tan
from random import random

BLACK = color(0, 0, 0)

class Raytracer(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.clear()

  def clear(self):
    self.pixels = [
      [BLACK for _ in range(self.width)]
      for _ in range(self.height)
    ]

  def write(self, filename):
    writeBMP(filename, self.width, self.height, self.pixels)

  def point(self, x, y, color):
    self.pixels[y][x] = color
  
  def cast_ray(self, origin, direction):
    return color(0, 0, 255)

  def render(self):
    fov = pi/2
    ar = self.width / self.height
    for y in range(self.height):
      for x in range(self.width):
        if random() > 0:
          i = (2 * ((x + 0.5) / self.width) - 1) * ar * tan(fov/2)
          j = 1 - 2 * ((y + 0.5) / self.height) * tan(fov/2)
          direction = norm(V3(i, j, -1))
          color = self.cast_ray(V3(0, 0, 0), direction)
          self.point(x, y, color)

r = Raytracer(1000, 1000)
r.render()
r.write('r.bmp')
