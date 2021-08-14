# Librerias
import struct
import random
from obj import Obj
from figures import Figures

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
  
  def load(self, filename, translate, scale):
    model = Obj(filename)
    for face in model.faces:
      # print(face)
      vcount = len(face)
      for j in range(vcount):
        f1 = face[j][0]
        f2 = face[(j + 1) % vcount][0]

        v1 = model.vertices[f1 - 1]
        v2 = model.vertices[f2 - 1]

        x1 = round((v1[0] + translate[0]) * scale[0])
        y1 = round((v1[1] + translate[1]) * scale[1])
        x2 = round((v2[0] + translate[0]) * scale[0])
        y2 = round((v2[1] + translate[1]) * scale[1])

        self.glLine(x1, y1, x2, y2)

  def glInit(self):
    # self.load('./models/pikachu-pokemon-go.obj', [40, 5], [10, 10])
    
    self.drawPolygon('./polygons/polygon1.txt', PIKACHU)
    self.drawPolygon('./polygons/polygon2.txt', RED)
    self.drawPolygon('./polygons/polygon3.txt', AQUA)
    self.drawPolygon('./polygons/polygon4.txt', PIKACHU)
    self.drawPolygon('./polygons/polygon5.txt', RED)
    self.glFinish('image.bmp')

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


          



      

renderer = Renderer(800, 600)
renderer.glInit()
