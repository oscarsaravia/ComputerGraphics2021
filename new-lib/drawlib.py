# Librerias
from numpy.matrixlib.defmatrix import matrix
import operations as op
from obj import Obj, Texture
from figures import Figures
from numpy import *


# V2 = namedtuple('Point2', ['x', 'y'])
# V3 = namedtuple('Point3', ['x', 'y', 'z'])

def operationMatrix(a, b):
  c = []
  for i in range(0, len(a)):
    temp = []
    for j in range(0, len(b[0])):
      s = 0
      for k in range(0, len(a[0])):
        s += a[i][k]*b[k][j]
      temp.append(s)
    c.append(temp)
  return c

# ====== COLORS =================
WHITE = op.color(255, 255, 255)
BLACK = op.color(0, 0, 0)
BLUE = op.color(0, 0, 255)
AQUA = op.color(0, 255, 255)
PIKACHU = op.color(244,220,38)
RED = op.color(255, 0, 0)
COLOR1 = op.color(129, 80, 69)
COLOR2 = op.color(222, 220, 205)
# ===============================

def paintBackground(index):
  if (0 <= index <= 150):
    return COLOR1
  elif (150 < index <= 300):
    return COLOR2
  elif (300 < index <= 450):
    return COLOR1
  elif (450 < index <= 600):
    return COLOR2
  elif (600 < index <= 750):
    return COLOR1
  elif (750 < index <= 900):
    return COLOR2
  elif (900 < index <= 1050):
    return COLOR1
  elif (1050 < index <= 1200):
    return COLOR2
  elif (1200 < index <= 1350):
    return COLOR1
  elif (1350 < index <= 1500):
    return COLOR2


class Renderer(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.current_color = WHITE
    self.current_texture = None
    self.light = op.V3(0, 0, 1)
    self.glCreateWindow()
  
  def glCreateWindow(self):
    self.framebuffer = [
      [paintBackground(x) for x in range(self.width)]
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
        file.write(self.framebuffer[y][x].toBytes())

    file.close()

  def glVertex(self, x, y, color = None):
    try:
      self.framebuffer[y][x] = color or self.current_color
    except:
      pass
  
  def glLine(self, A, B, color):
    x0, y0, x1, y1 = A.x, A.y, B.x, B.y
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

  def transform(self, vertex):
    augmented_vertex = [
      vertex[0],
      vertex[1],
      vertex[2],
      1
    ]

    transformed_vertex = self.Viewport @ self.Projection @ self.View @ self.Model @ augmented_vertex
    transformed_vertex = transformed_vertex.tolist()[0]
    transformed_vertex = [
      transformed_vertex[0] / transformed_vertex[3],
      transformed_vertex[1] / transformed_vertex[3],
      transformed_vertex[2] / transformed_vertex[3],
    ]

    return op.V3(*transformed_vertex)

  
  def load(self, filename, translate=(0, 0, 0), scale=(1, 1, 1), rotate=(0, 0, 0)):
    self.loadModelMatrix(translate, scale, rotate)
    model = Obj(filename)
    vertex_buffer_object = []
    for face in model.faces:
      for v in range(len(face)):
        vertex = self.transform(model.vertices[face[v][0] - 1])
        vertex_buffer_object.append(vertex)
      if self.current_texture:
        for v in range(len(face)):
          tvertex = op.V3(*model.tvertices[face[v][1] - 1])
          vertex_buffer_object.append(tvertex)
      
      for v in range(len(face)):
        normal = op.V3(*model.normals[face[v][2] - 1])
        vertex_buffer_object.append(normal)

    self.active_vertex_array = iter(vertex_buffer_object)
  
  def loadModelMatrix(self, translate=(0, 0, 0), scale=(1, 1, 1), rotation=(0, 0, 0)):
    translate = op.V3(*translate)
    scale = op.V3(*scale)
    rotation = op.V3(*rotation)

    translation_matrix = matrix(
      [[1, 0, 0, translate.x],
      [0, 1, 0, translate.y],
      [0, 0, 1, translate.z],
      [0, 0, 0, 1],]
    )
    angle = rotation.x
    rotation_matrix_x = matrix(
      [[1, 0, 0, 0],
      [0, cos(angle), -sin(angle), 0],
      [0, sin(angle), cos(angle), 0],
      [0, 0, 0, 1],]
    )
    angle = rotation.y
    rotation_matrix_y = matrix(
      [[cos(angle), 0, sin(angle), 0],
      [0, 1, 0, 0],
      [-sin(angle), 0, cos(angle), 0],
      [0, 0, 0, 1],]
    )
    angle = rotation.z
    rotation_matrix_z = matrix(
      [[cos(angle), -sin(angle), 0, 0],
      [sin(angle), cos(angle), 0, 0],
      [0, 0, 1, 0],
      [0, 0, 0, 1],]
    )
    rotation_matrix =rotation_matrix_x @ rotation_matrix_y @ rotation_matrix_z
    scale_matrix = matrix(
      [[scale.x, 0, 0, 0],
      [0, scale.y, 0, 0],
      [0, 0, scale.z, 0],
      [0, 0, 0, 1],]
    )
    self.Model = translation_matrix @ rotation_matrix @ scale_matrix

  def loadViewMatrix(self, x, y, z, center):
    M = matrix([
      [x.x, x.y, x.z, 0],
      [y.x, y.y, y.z, 0],
      [z.x, z.y, z.z, 0],
      [0, 0, 0, 1],
    ])

    O = matrix([
      [1, 0, 0, -center.x],
      [0, 1, 0, -center.y],
      [0, 0, 1, -center.z],
      [0, 0, 0, 1],
    ])

    self.View = M @ O

  def loadProjectionMatrix(self, coeff):
    self.Projection = matrix([
      [1, 0, 0, 0],
      [0, 1, 0, 0],
      [0, 0, 1, 0],
      [0, 0, coeff, 1],
    ])
  
  def loadViewPortMatrix(self, x=0, y=0):
    self.Viewport = matrix([
      [self.width/2, 0, 0, x + self.width/2],
      [0, self.height/2, 0, y + self.height/2],
      [0, 0, 1, 0],
      [0, 0, 0, 1],
    ])

  def lookAt(self, eye, center, up):
    z = op.norm(op.sub(eye, center))
    x = op.norm(op.cross(up, z))
    y = op.norm(op.cross(z, x))
    self.loadViewMatrix(x, y, z, center)
    self.loadProjectionMatrix(-1/op.length(op.sub(eye, center)))
    self.loadViewPortMatrix()

  def draw_arrays(self, polygon):
    if polygon == 'TRIANGLES':
      try:
        while True:
          self.triangle()
      except StopIteration:
        pass
    print('finished')

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
  # def shader(self, x, y):
  #   center_x, center_y = 500, 200
  #   radius = 20
  #   center_x1, center_y1 = 300, 210
  #   radius1 = 5
  #   if (x-center_x)**2 + (y-center_y)**2 < radius**2:
  #     return op.color(156, 125, 96)
  #   elif (x-center_x1)**2 + (y-center_y1)**2 < radius1**2:
  #     return op.color(0, 0, 0)
  #   elif y >= 400:
  #     return op.color(134,124,114)
  #   elif (y >= 380 and y < 400):
  #     return op.color(164, 176, 190)
  #   elif (y >= 365 and y < 380):
  #     return op.color(136, 123, 114)
  #   elif (y >= 345 and y < 365):
  #     return op.color(164, 176, 190)
  #   elif (y >= 310 and y < 345):
  #     return op.color(137, 116, 95)
  #   elif (y >= 260 and y < 310):
  #     return op.color(175, 181, 193)
  #   elif (y >= 225 and y < 260):
  #     return op.color(137, 116, 95)
  #   elif (y >= 205 and y < 225):
  #     return op.color(164, 176, 190)
  #   elif (y >= 175 and y < 205):
  #     return op.color(158, 157, 155)
  #   elif (y >= 150 and y < 175):
  #     return op.color(129, 124, 121)
  #   else :
  #     return op.color(90, 77, 68)
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

    if self.current_texture:
      tA = next(self.active_vertex_array)
      tB = next(self.active_vertex_array)
      tC = next(self.active_vertex_array)

    nA = next(self.active_vertex_array)
    nB = next(self.active_vertex_array)
    nC = next(self.active_vertex_array)

    bbox_min, bbox_max = op.bbox(A, B, C)

    for x in range(bbox_min.x, bbox_max.x + 1):
      for y in range(bbox_min.y, bbox_max.y + 1):
        w, v, u = op.barycentric(A, B, C, op.V2(x, y))
        if w < 0 or v < 0 or u < 0:
          continue

        if self.current_texture:
          tx = tA.x * w + tB.x * v + tC.x * u
          ty = tA.y * w + tB.y * v + tC.y * u
          
          col = self.active_shader(
            self,
            triangle = (A, B, C),
            bar = (w, v, u),
            tex_coords = (tx, ty),
            varying_normals = (nA, nB, nC)
          )
        else:
          col = WHITE * intensity
      
        # col = op.color(255*intensity, 255*intensity, 255*intensity)
        # col = WHITE * intensity

        z = A.z * w + B.z * v + C.z * u

        if x < 0 or y < 0:
          continue

        if x < len(self.zbuffer) and y < len(self.zbuffer[x]) and z > self.zbuffer[x][y]:
          self.glVertex(x, y, col)
          self.zbuffer[x][y] = z

        # if z > self.zbuffer[x][y]:
        #   self.glVertex(x, y, color)
        #   self.zbuffer[x][y] = z

  
  def glInit(self):
    pass
    # self.glLine(op.V3(100, 100), op.V3(200, 200), op.color(255, 0, 0))
    # self.glFinish('t.bmp')


    # self.current_texture = Texture('./models/model.bmp')
    # self.load('./models/model.obj', (1, 1, 1), (300, 300, 300))
    # self.draw_arrays('TRIANGLES')
    # self.glFinish('image.bmp')

renderer = Renderer(800, 600)
renderer.glInit()
