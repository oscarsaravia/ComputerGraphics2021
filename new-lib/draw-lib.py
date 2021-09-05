# Librerias
import random
import operations as op
from obj import Obj, Texture
from figures import Figures
from collections import namedtuple


V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])

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
    self.glCreateWindow(self.width, self.height)
    self.glViewPort(0, 0, width, height)
  
  def glCreateWindow(self, width, height):
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

        normal = op.norm(op.cross(op.sub(b, a), op.sub(c, a)))
        intensity = op.dot(normal, light)

        if not self.texture:
          grey = round(255 * intensity)
          if grey < 0:
            continue 
          self.triangle(a, b, c, color=op.color(grey, grey, grey))
        else:
          f1 = face[0][0] - 1
          f2 = face[1][0] - 1
          f3 = face[2][0] - 1

          tA = op.V3(*model.tvertices[f1])
          tB = op.V3(*model.tvertices[f2])
          tC = op.V3(*model.tvertices[f3])
          self.triangle(a, b, c, texture_coords=(tA, tB, tC), intensity=intensity)

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

        normal = op.norm(op.cross(op.sub(vertices[0], vertices[1]), op.sub(vertices[1], vertices[2])))
        intensity = op.dot(normal, light)
        grey = round(255 * intensity)
        A, B, C, D = vertices 

        if not self.texture:
          grey = round(255 * intensity)
          if grey < 0:
            continue 
          self.triangle(A, B, C, op.color(grey, grey, grey))
          self.triangle(A, C, D, op.color(grey, grey, grey))
        else:
          f1 = face[0][0] - 1
          f2 = face[1][0] - 1
          f3 = face[2][0] - 1
          f4 = face[3][0] - 1

          tA = op.V3(*model.tvertices[f1])
          tB = op.V3(*model.tvertices[f2])
          tC = op.V3(*model.tvertices[f3])
          tD = op.V3(*model.tvertices[f4])
          self.triangle(A, B, C, texture_coords=(tA, tB, tC), intensity=intensity)
          self.triangle(A, C, D, texture_coords=(tA, tC, tD), intensity=intensity)

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
  def shader(self, x, y):
    if y < 150:
      choices = [(64,78,111), (109,133,191)]
      selected = random.choice(choices)
      return op.color(selected[0], selected[1], selected[2])
    else:
      return op.color(109,133,191)
    # center_x, center_y = 400, 400
    # radius = 50
    # if (x-center_x)**2 + (y-center_y)**2 < radius**2:
    #   return op.color(107,131,199)
    # else:
    #   choices = [(75,93,133), (46,57,81), (112,137,200)]
    #   random_choice = random.choice(choices)
    #   return op.color(random_choice[0], random_choice[1], random_choice[2])
    # if A.y > 200:
    #   return op.color(255, 0, 200)
    # else:
    #   return op.color(255, 0, 255)

  def triangle(self, A, B, C, col=None, texture_coords=None, intensity=1):
    bbox_min, bbox_max = op.bbox(A, B, C)

    for x in range(bbox_min.x, bbox_max.x + 1):
      for y in range(bbox_min.y, bbox_max.y + 1):
        w, v, u = op.barycentric(A, B, C, V2(x, y))
        if w < 0 or v < 0 or u < 0:
          continue

        if self.texture:
          tA, tB, tC = texture_coords
          tx = tA.x * w + tB.x * v + tC.x * u
          ty = tA.y * w + tB.y * v + tC.y * u
          
          fcolor = self.texture.get_color(tx, ty)
          b, g, r = [int(c * intensity) if intensity > 0 else 0 for c in fcolor]
          col = op.color(r, g, b)
      
        col = self.shader(x, y)

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
    t = Texture('./models/earth.bmp')
    self.texture = t
    # self.framebuffer = t.pixels
    self.load('./models/earth.obj', (800, 600, 0), (0.5, 0.5, 1))
    self.glFinish('image.bmp')

# renderer = Renderer(4096, 2048)
renderer = Renderer(800, 600)
renderer.glInit()
