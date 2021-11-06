from numpy import *
from drawlib import *
from operations import *

r = Renderer(1000, 1000)
WHITE = color(255, 255, 255)

points = [
  [200, 200],
  [400, 200],
  [400, 400],
  [200, 400]
]

center = V3(300, 300)

a = 3.14 / 4

move_to_origin = matrix([
  [1, 0, -center.x],
  [0, 1, -center.y],
  [0, 0, 1]
])

move_back = matrix([
  [1, 0, center.x],
  [0, 1, center.y],
  [0, 0, 1]
])

rotation_matrix = matrix([
  [cos(a), -sin(a), 0],
  [sin(a), cos(a), 0],
  [0, 0, 1]
])

identity_matrix = matrix([
  [1, 0, 0],
  [0, 1, 0],
  [0.01, 0, 1]
])

scale_matrix = matrix([
  [1.2, 0, 0],
  [0, 1.2, 0],
  [0, 0, 1]
])

transform_matrix = move_back @ identity_matrix @ scale_matrix @ rotation_matrix @ move_to_origin

transformed_points = []

for point in points:
  point = V3(*point)
  tpoint = transform_matrix @ [ point.x, point.y, 1]
  tpoint = tpoint.tolist()[0]
  tpoint2D = V3(
    int(tpoint[0]/tpoint[2]),
    int(tpoint[1]/tpoint[2])
  )
  transformed_points.append(tpoint2D)

point = transformed_points[-1]
prev_point = V3(point[0], point[1])

for point in transformed_points:
  r.glLine(prev_point, point, WHITE)
  prev_point = point

r.glFinish('t.bmp')