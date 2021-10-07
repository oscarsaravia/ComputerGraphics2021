from lib import *

class Sphere(object):
  def __init__(self, center, radius, material):
    self.center = center
    self.radius = radius
    self.material = material

  def ray_intersect(self, origin, direction):
    L = sub(self.center, origin)
    tca = dot(L, direction)
    l = length(L)
    d2 = l**2 - tca**2

    if (d2 > self.radius**2):
      return None

    tch = (self.radius**2 -d2)**2
    t0 = tca - tch
    t1 = tca + tch

    if (t0 < 0):
      t0 = t1
    if t0 < 0:
      return None
    
    return Intersect(
      distance = t0
    )

