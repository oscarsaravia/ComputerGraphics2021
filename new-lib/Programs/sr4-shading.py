# Librerias
import struct
import random
from obj import Obj
from figures import Figures
from collections import namedtuple

V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])

def sum(v0, v1):
  """
    Input: 2 size 3 vectors
    Output: Size 3 vector with the per element sum
  """
  return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)

def sub(v0, v1):
  """
    Input: 2 size 3 vectors
    Output: Size 3 vector with the per element substraction
  """
  return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)

def mul(v0, k):
  """
    Input: 2 size 3 vectors
    Output: Size 3 vector with the per element multiplication
  """
  return V3(v0.x * k, v0.y * k, v0.z *k)

def dot(v0, v1):
  """
    Input: 2 size 3 vectors
    Output: Scalar with the dot product
  """
  return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def cross(v0, v1):
  """
    Input: 2 size 3 vectors
    Output: Size 3 vector with the cross product
  """  
  return V3(
    v0.y * v1.z - v0.z * v1.y,
    v0.z * v1.x - v0.x * v1.z,
    v0.x * v1.y - v0.y * v1.x,
  )

def length(v0):
  """
    Input: 1 size 3 vector
    Output: Scalar with the length of the vector
  """  
  return (v0.x**2 + v0.y**2 + v0.z**2)**0.5

def norm(v0):
  """
    Input: 1 size 3 vector
    Output: Size 3 vector with the normal of the vector
  """  
  v0length = length(v0)

  if not v0length:
    return V3(0, 0, 0)

  return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)

def bbox(*vertices):
  """
    Input: n size 2 vectors
    Output: 2 size 2 vectors defining the smallest bounding rectangle possible
  """  
  xs = [ vertex.x for vertex in vertices ]
  ys = [ vertex.y for vertex in vertices ]
  xs.sort()
  ys.sort()

  return V2(xs[0], ys[0]), V2(xs[-1], ys[-1])

def barycentric(A, B, C, P):
  """
    Input: 3 size 2 vectors and a point
    Output: 3 barycentric coordinates of the point in relation to the triangle formed
            * returns -1, -1, -1 for degenerate triangles
  """  
  cx, cy, cz = cross(
    V3(B.x - A.x, C.x - A.x, A.x - P.x), 
    V3(B.y - A.y, C.y - A.y, A.y - P.y)
  )

  if abs(cz) < 1:
    return -1, -1, -1   # this triangle is degenerate, return anything outside

  # [cx cy cz] = [u v 1]

  u = cx/cz
  v = cy/cz
  w = 1 - (u + v)

  return w, v, u


# FUNCIONES

def char(caracter):
  return struct.pack('=c', caracter.encode('ascii'))

# Devuelve un 'short'
def word(word):
  return struct.pack('=h', word)

# Devuelve un 'long'
def dobule_word(word):
  return struct.pack('=l', word)

# Devuelve un color en bits
def color(r, g, b):
  return bytes([b, g, r])

# COLORES
WHITE = color(255, 255, 255)
BLACK = color(0, 0, 0)
BLUE = color(0, 0, 255)
AQUA = color(0, 255, 255)
PIKACHU = color(244,220,38)
RED = color(255, 0, 0)


class Renderer(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.glCreateWindow(self.width, self.height)
    self.glViewPort(0, 0, width, height)
  
  def glCreateWindow(self, width, height):
    self.framebuffer = [
      [BLACK for x in range(self.width)]
      for y in range(self.height)
    ]
    
  # Llena el framebuffer con el color indicado
  def glClear(self, color = None):
    # Lo que hace el framebuffer es colocar los bytes de color en todo el 
    # ancho y alto de la pantalla (Array 2D)
    if color:
      self.framebuffer = [
        [color for x in range(self.width)]
        for y in range(self.height)
      ]
    else:
      self.framebuffer = [
        [BLACK for x in range(self.width)]
        for y in range(self.height)
      ]
        
  def glClearColor(self, color):
    self.glClear(color)

  def glViewPort(self, x, y, width, height):
    self.vpx = x
    self.vpy = y
    self.vpw = width
    self.vph = height

  def glFinish(self, filename):
    file = open(filename, 'bw')

    # File Header
    file.write(char('B'))
    file.write(char('M'))
    file.write(dobule_word(54 + 3*(self.width*self.height)))
    file.write(dobule_word(0))
    file.write(dobule_word(54))

    # Info Header
    file.write(dobule_word(40))
    file.write(dobule_word(self.width))
    file.write(dobule_word(self.height))
    file.write(word(1))
    file.write(word(24))
    file.write(dobule_word(0))
    file.write(dobule_word(3*(self.width*self.height)))
    file.write(dobule_word(0))
    file.write(dobule_word(0))
    file.write(dobule_word(0))
    file.write(dobule_word(0))

    # Bitmap
    for y in range(self.height):
      for x in range(self.width):
        file.write(self.framebuffer[y][x])

    file.close()

  def glVertex(self, x, y, color):
    #x = int( (x + 1) * (self.vpw / 2) + self.vpx )
    #y = int( (y + 1) * (self.vph / 2) + self.vpy)
    self.framebuffer[y][x] = color
    # print(x, y)
  
  def glLine(self, x0, y0, x1, y1, color):
    # 100 100 500 100
    dy = abs(y1 - y0)
    dx = abs(x1 - x0)

    steep = dy > dx

    if steep:
      x0, y0 = y0, x0
      x1, y1 = y1, x1

    if x0 > x1:
      x0, x1 = x1, x0
      y0, y1 = y1, y0

    dy = abs(y1 - y0)
    dx = abs(x1 - x0)

    offset = 0 * 2 * dx
    threshold = 0.5 * 2 * dx
    y = y0

    points = []
    for x in range(x0, x1):
      if steep:
        points.append((y, x))
      else:
        points.append((x, y))

      offset += (dy/dx) * 2 * dx
      if offset >= threshold:
        y += 1 if y0 < y1 else -1
        threshold += 1 * 2 * dx

    for point in points:
      self.glVertex(*point, color)

  def transform(self, vertex, translate=(0, 0, 0), scale=(1, 1, 1)):
    # returns a vertex 3, translated and transformed
    return V3(
      round((vertex[0] + translate[0]) * scale[0]),
      round((vertex[1] + translate[1]) * scale[1]),
      round((vertex[2] + translate[2]) * scale[2])
    )
  
  def load(self, filename, translate, scale, color):
    model = Obj(filename)
    light = V3(0, 0, 1)
    for face in model.faces:
      vcount = len(face)

      if vcount ==3:
        f1 = face[0][0] - 1
        f2 = face[1][0] - 1
        f3 = face[2][0] - 1

        a = self.transform(model.vertices[f1], translate, scale)
        b = self.transform(model.vertices[f2], translate, scale)
        c = self.transform(model.vertices[f3], translate, scale)

        normal = norm(cross(sub(b, a), sub(c, a)))
        intensity = dot(normal, light)
        grey = round(255 * intensity)
        if grey < 0:
          continue 

        self.triangle(a, b, c, color(grey, grey, grey))
      else:
        f1 = face[0][0] - 1
        f2 = face[1][0] - 1
        f3 = face[2][0] - 1
        f4 = face[3][0] - 1 

        vertices = [
            self.transform(model.vertices[f1], translate, scale),
            self.transform(model.vertices[f2], translate, scale),
            self.transform(model.vertices[f3], translate, scale),
            self.transform(model.vertices[f4], translate, scale)
        ]

        normal = norm(cross(sub(vertices[0], vertices[1]), sub(vertices[1], vertices[2])))  # no necesitamos dos normales!!
        intensity = dot(normal, light)
        grey = round(255 * intensity)
        if grey < 0:
          continue # dont paint this face

        # vertices are ordered, no need to sort!
        # vertices.sort(key=lambda v: v.x + v.y)

        A, B, C, D = vertices 
      
        self.triangle(A, B, C, color(grey, grey, grey))
        self.triangle(A, C, D, color(grey, grey, grey))

      # for j in range(vcount):
      #   f1 = face[j][0]
      #   f2 = face[(j + 1) % vcount][0]

      #   v1 = model.vertices[f1 - 1]
      #   v2 = model.vertices[f2 - 1]

      #   x1 = round((v1[0] + translate[0]) * scale[0])
      #   y1 = round((v1[1] + translate[1]) * scale[1])
      #   x2 = round((v2[0] + translate[0]) * scale[0])
      #   y2 = round((v2[1] + translate[1]) * scale[1])

      #   self.glLine(x1, y1, x2, y2, color)

  def drawPolygon(self, filename, color):
    xpoints = []
    ypoints= []
    polygon = Figures(filename)
    for i in  range(0, len(polygon.draws)):
      if i < len(polygon.draws)-1:
        x0 = int(polygon.draws[i][0])
        y0 = int(polygon.draws[i][1])
        x1 = int(polygon.draws[i+1][0])
        y1 = int(polygon.draws[i+1][1])
        self.glLine(x0, y0, x1, y1, color)
        xpoints.extend([x0, x1])
        ypoints.extend([y0, y1])
      else:
        x0 = int(polygon.draws[i][0])
        y0 = int(polygon.draws[i][1])
        x1 = int(polygon.draws[0][0])
        y1 = int(polygon.draws[0][1])
        self.glLine(x0, y0, x1, y1, color)
        xpoints.extend([x0, x1])
        ypoints.extend([y0, y1])
    xpoints.sort()
    ypoints.sort()
    left = xpoints[0]
    right = xpoints[len(xpoints)-1]
    bottom = ypoints[0]
    top = ypoints[len(ypoints)-1]

    # Making a square
    # self.glLine(left, bottom, left, top)
    # self.glLine(left, top, right, top)
    # self.glLine(right, top, right, bottom)
    # self.glLine(right, bottom, left, bottom)

    # for i in range(1, 100000):
    #   randomx = random.randint(left, right)
    #   randomy = random.randint(bottom, top)
    #   self.glVertex(randomx, randomy, WHITE)
    for y in range(bottom, top):
      for x in range(left, right):
        end = 0
        if self.framebuffer[y][x] == color:
          for i in range(x, right):
            #self.framebuffer[y][i] = WHITE
            if self.framebuffer[y][i] != BLACK:
              end = i
        for k in range(x+1, end):
          self.framebuffer[y][k] = color

  def triangle(self, A, B, C, color=None):
    bbox_min, bbox_max = bbox(A, B, C)

    for x in range(bbox_min.x, bbox_max.x + 1):
      for y in range(bbox_min.y, bbox_max.y + 1):
        w, v, u = barycentric(A, B, C, V2(x, y))
        if w < 0 or v < 0 or u < 0:  # 0 is actually a valid value! (it is on the edge)
          continue
        
        self.glVertex(x, y, color)
  
  def glInit(self):
    self.load('./models/pikachu-pokemon-go.obj', [40, 5], [10, 10], PIKACHU)
    # LABORATORIO 1    
    # self.drawPolygon('./polygons/polygon1.txt', PIKACHU)
    # self.drawPolygon('./polygons/polygon2.txt', RED)
    # self.drawPolygon('./polygons/polygon3.txt', AQUA)
    # self.drawPolygon('./polygons/polygon4.txt', PIKACHU)
    # self.drawPolygon('./polygons/polygon5.txt', RED)

    # TRIANGLES
    # self.triangle(V2(10, 70), V2(50, 160), V2(70, 80), RED)
    # self.triangle(V2(180, 50), V2(150, 1), V2(70, 180), PIKACHU)
    # self.triangle(V2(180, 150), V2(120, 160), V2(130, 180), WHITE)
    
    self.glFinish('image.bmp')

renderer = Renderer(1000, 800)
renderer.glInit()
