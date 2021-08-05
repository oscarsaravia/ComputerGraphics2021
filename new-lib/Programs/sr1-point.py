# Librerias
import struct

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
    x = int( (x + 1) * (self.vpw / 2) + self.vpx )
    y = int( (y + 1) * (self.vph / 2) + self.vpy)
    self.framebuffer[y][x] = color
    print(x, y)
      


  def glInit(self):
    self.glVertex(0, 0, WHITE)
    self.glFinish('image.bmp')

renderer = Renderer(1024, 768)
renderer.glInit()

