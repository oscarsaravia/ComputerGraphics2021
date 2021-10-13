import numpy
from collections import namedtuple
import struct

V2 = namedtuple('Point2', ['x', 'y'])
# V3 = namedtuple('Point3', ['x', 'y', 'z'])

class V3(object):
  def __init__(self, x, y = None, z = None):
    if (type(x) == numpy.matrix):
      self.x, self.y, self.z = x.tolist()[0]
    else:
      self.x = x
      self.y = y
      self.z = z
  
  def __getitem__(self, i):
    if i == 0:
      return self.x
    elif i == 1:
      return self.y
    elif i ==2:
      return self.z

  def __repr__(self):
    return "V3(%s, %s, %s)" % (self.x, self.y, self.z)

class V2(object):
  def __init__(self, x, y = None):
    if (type(x) == numpy.matrix):
      self.x, self.y = x.tolist()[0]
    else:
      self.x = x
      self.y = y

  def __repr__(self):
    return "V2(%s, %s)" % (self.x, self.y)

def color(r, g, b):
  return bytes([b, g, r])

# class color(object):
#   def init(self,r,g,b = None):
#     self.r = r
#     self.g = g 
#     self.b = b

#   def repr(self):
#     b = ccolor(self.b)
#     g = ccolor(self.g)
#     r = ccolor(self.r)
#     return "color(%s, %s, %s)" % (r, g, b)

#   def add(self, other):
#     b = ccolor(self.b + other.b)
#     g = ccolor(self.g + other.g)
#     r = ccolor(self.r + other.r)
#     return color(r,g,b)

#   def mul(self, other):
#     b = ccolor(self.b * other)
#     g = ccolor(self.g * other)
#     r = ccolor(self.r * other)
#     return color(r,g,b)

#   def toBytes(self):
#     b = ccolor(self.b)
#     g = ccolor(self.g)
#     r = ccolor(self.r)
#     return bytes([b,g,r])

def char(caracter):
  return struct.pack('=c', caracter.encode('ascii'))

def word(word):
  return struct.pack('=h', word)

def dobule_word(word):
  return struct.pack('=l', word)

def sum(self, v0, v1):
  return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)

def sub(v0, v1):
  return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)

def mul(v0, k):
  return V3(v0.x * k, v0.y * k, v0.z *k)

def dot(v0, v1):
  return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def cross(v0, v1):
  return V3(
    v0.y * v1.z - v0.z * v1.y,
    v0.z * v1.x - v0.x * v1.z,
    v0.x * v1.y - v0.y * v1.x,
  )

def length(v0):
  return (v0.x**2 + v0.y**2 + v0.z**2)**0.5

def norm(v0):
  v0length = length(v0)
  if not v0length:
    return V3(0, 0, 0)
  return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)

def bbox(*vertices):
  xs = [ vertex.x for vertex in vertices ]
  ys = [ vertex.y for vertex in vertices ]
  xs.sort()
  ys.sort()
  return V2(int(xs[0]), int(ys[0])), V2(int(xs[-1]), int(ys[-1]))

def barycentric(A, B, C, P):
  bary = cross(
    V3(C.x - A.x, B.x - A.x, A.x - P.x), 
    V3(C.y - A.y, B.y - A.y, A.y - P.y)
  )
  if abs(bary.z) < 1:
    return -1, -1, -1
  return (
    1 - (bary.x + bary.y) / bary.z, 
    bary.y / bary.z, 
    bary.x / bary.z
  )
