from lib import *
from math import pi, tan
from random import random
from shpere import *

BLACK = color(0, 0, 0)

class Raytracer(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.light = None
    self.background_color = BLACK
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
    material, intersect = self.scene_intersect(origin, direction)

    if material is None :
      return self.background_color

    light_dir = norm(sub(self.light.position, intersect.point))
    intensity = self.light.intensity * max(0, dot(light_dir, intersect.normal))
    # diffuse = material.diffuse * intensity
    diffuse = color(
      int(material.diffuse[2] * intensity * material.albedo[0]),
      int(material.diffuse[1] * intensity * material.albedo[0]),
      int(material.diffuse[0] * intensity * material.albedo[0]),
    )
    c = diffuse
    return c
    if (material):
      return material.diffuse
    else:
      return self.background_color

  def scene_intersect(self, origin, direction):
    zbuffer = float('inf')
    material = None
    intersect = None
    for obj in self.scene:
      r_intersect = obj.ray_intersect(origin, direction)
      if r_intersect:
        if r_intersect.distance < zbuffer:
          zbuffer = r_intersect.distance
          material = obj.material
          intersect = r_intersect
      # if (intersect and intersect.distance < zbuffer):
      #   zbuffer = intersect.distance
      #   material = obj.material
    return material, intersect

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
r.light = Light(
  position = V3(10, 10, 10),
  intensity = 1
)
ivory = Material(diffuse=color(100, 100, 80), albedo=[0.6])
rubber = Material(diffuse=color(80, 0, 0), albedo=[0.9])
# m = Material(diffuse=color(255, 255, 0), albedo=[0.1])
# s = Sphere(V3(-3, 0, -16), 2, m)
r.scene = [
  Sphere(V3(0, -1.5, -10), 1.5, ivory),
  Sphere(V3(-2, 1, -12), 2, rubber),
  Sphere(V3(1, 1, -8), 1.7, rubber),
  Sphere(V3(0, 5, -20), 5, ivory),
]
r.render()
r.write('r.bmp')
