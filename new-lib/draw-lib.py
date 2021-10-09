# Librerias
import random
import operations as op
from obj import Obj, Texture
from figures import Figures
from collections import namedtuple


# V2 = namedtuple('Point2', ['x', 'y'])
# V3 = namedtuple('Point3', ['x', 'y', 'z'])

# ====== COLORS =================
WHITE = op.color(255, 255, 255)
BLACK = op.color(0, 0, 0)
BLUE = op.color(0, 0, 255)
AQUA = op.color(0, 255, 255)
PIKACHU = op.color(244,220,38)
RED = op.color(255, 0, 0)
# ===============================


class Renderer(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height
    # self.glViewPort(0, 0, width, height)
    self.current_color = WHITE
    self.glCreateWindow()
    self.current_texture = None
    self.light = op.V3(0, 0, 1)
  
  def glCreateWindow(self):
    self.framebuffer = [
      [BLACK for x in range(self.width)]
      for y in range(self.height)
    ]
    self.zbuffer = [
      [-float('inf') for x in range(self.width)]
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
      self.zbuffer = [
      [-float('inf') for x in range(self.width)]
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
    file.write(op.char('B'))
    file.write(op.char('M'))
    file.write(op.dobule_word(54 + 3*(self.width*self.height)))
    file.write(op.dobule_word(0))
    file.write(op.dobule_word(54))

    # Info Header
    file.write(op.dobule_word(40))
    file.write(op.dobule_word(self.width))
    file.write(op.dobule_word(self.height))
    file.write(op.word(1))
    file.write(op.word(24))
    file.write(op.dobule_word(0))
    file.write(op.dobule_word(3*(self.width*self.height)))
    file.write(op.dobule_word(0))
    file.write(op.dobule_word(0))
    file.write(op.dobule_word(0))
    file.write(op.dobule_word(0))

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
    return op.V3(
      round((vertex[0] + translate[0]) * scale[0]),
      round((vertex[1] + translate[1]) * scale[1]),
      round((vertex[2] + translate[2]) * scale[2])
    )
  
  def load(self, filename, translate=(0, 0, 0), scale=(1, 1, 1)):
    model = Obj(filename)
    vertex_buffer_object = []
    for face in model.faces:
      for v in range(len(face)):
        vertex = self.transform(model.vertices[face[v][0] - 1], translate, scale)
        vertex_buffer_object.append(vertex)
    self.active_vertex_array = iter(vertex_buffer_object)
  
  def draw_arrays(self, polygon):
    if polygon == 'TRIANGLES':
      try:
        while True:
          self.triangle()
      except StopIteration:
        pass

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
  def shader(self, x, y):
    center_x, center_y = 500, 200
    radius = 20
    center_x1, center_y1 = 300, 210
    radius1 = 5
    if (x-center_x)**2 + (y-center_y)**2 < radius**2:
      return op.color(156, 125, 96)
    elif (x-center_x1)**2 + (y-center_y1)**2 < radius1**2:
      return op.color(0, 0, 0)
    elif y >= 400:
      return op.color(134,124,114)
    elif (y >= 380 and y < 400):
      return op.color(164, 176, 190)
    elif (y >= 365 and y < 380):
      return op.color(136, 123, 114)
    elif (y >= 345 and y < 365):
      return op.color(164, 176, 190)
    elif (y >= 310 and y < 345):
      return op.color(137, 116, 95)
    elif (y >= 260 and y < 310):
      return op.color(175, 181, 193)
    elif (y >= 225 and y < 260):
      return op.color(137, 116, 95)
    elif (y >= 205 and y < 225):
      return op.color(164, 176, 190)
    elif (y >= 175 and y < 205):
      return op.color(158, 157, 155)
    elif (y >= 150 and y < 175):
      return op.color(129, 124, 121)
    else :
      return op.color(90, 77, 68)
    # else:
    #   choices = [(75,93,133), (46,57,81), (112,137,200)]
    #   random_choice = random.choice(choices)
    #   return op.color(random_choice[0], random_choice[1], random_choice[2])
    # if A.y > 200:
    #   return op.color(255, 0, 200)
    # else:
    #   return op.color(255, 0, 255)

  def triangle(self):
    A = next(self.active_vertex_array)
    B = next(self.active_vertex_array)
    C = next(self.active_vertex_array)
    bbox_min, bbox_max = op.bbox(A, B, C)

    normal = op.norm(op.cross(op.sub(B, A), op.sub(C, A)))
    intensity = op.dot(normal, self.light)
    if intensity < 0:
      return
    for x in range(bbox_min.x, bbox_max.x + 1):
      for y in range(bbox_min.y, bbox_max.y + 1):
        w, v, u = op.barycentric(A, B, C, op.V2(x, y))
        if w < 0 or v < 0 or u < 0:
          continue

        if self.current_texture:
          tA, tB, tC = texture_coords
          tx = tA.x * w + tB.x * v + tC.x * u
          ty = tA.y * w + tB.y * v + tC.y * u
          
          fcolor = self.current_texture.get_color(tx, ty)
          b, g, r = [int(c * intensity) if intensity > 0 else 0 for c in fcolor]
          col = op.color(r, g, b)
      
        # col = op.color(255*intensity, 255*intensity, 255*intensity)
        col = WHITE

        z = A.z * w + B.z * v + C.z * u

        if x < 0 or y < 0:
          continue

        if x < len(self.zbuffer) and y < len(self.zbuffer[x]) and z > self.zbuffer[x][y]:
          self.glVertex(x, y, col)
          self.zbuffer[x][y]

        # if z > self.zbuffer[x][y]:
        #   self.glVertex(x, y, color)
        #   self.zbuffer[x][y] = z

  
  def glInit(self):
    self.load('./models/face.obj', (1, 1, 1), (300, 300, 300))
    self.draw_arrays('TRIANGLES')
    self.glFinish('image.bmp')
    # self.load('./models/face.obj', [1, 1], [1, 1])
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

    # SR4
    # self.load('./models/pikachu-pokemon-go.obj', (35, 5, 0), (15, 15, 15))
    # t = Texture('./models/earth.bmp')
    # self.texture = t
    # self.framebuffer = t.pixels
    # self.load('./models/earth.obj', (800, 600, 0), (0.5, 0.5, 1))
    # self.glFinish('image.bmp')

# renderer = Renderer(4096, 2048)
renderer = Renderer(800, 600)
renderer.glInit()
