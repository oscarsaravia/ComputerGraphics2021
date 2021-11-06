from drawlib import *
from operations import *

pi = 3.14

def gorad(render, **kwargs):
  w, v, u = kwargs['bar']
  tx, ty = kwargs['tex_coords']
  nA, nB, nC = kwargs['varying_normals']
  tcolor = render.current_texture.get_color(tx, ty)

  iA, iB, iC = [dot(n, render.light) for n in (nA, nB, nC)]
  intensity = w*iA + v*iB + u*iC

  return tcolor * intensity


r = Renderer(1500, 1500)

# ================= MODELO 1 =================
r.current_texture = Texture('./pmodels/mueble.bmp')
r.lookAt(V3(0, 0, 5), V3(0, 0, 0), V3(0, 1, 0))
r.load('./pmodels/mueble.obj',
  translate=(-0.7, -0.8, 0),
  scale=(1.1, 1.1, 1.1),
  rotate=(0, 0.9, 0)
)
r.active_shader = gorad
r.draw_arrays('TRIANGLES')

# ================= MODELO 2 =================
r.current_texture = Texture('./pmodels/paint.bmp')
r.lookAt(V3(0, 0, 5), V3(0, 0, 0), V3(0, 1, 0))
r.load('./pmodels/paint.obj',
  translate=(0.6, 0.3, 0),
  scale=(1, 1, 1),
  rotate=(0, 0, 0)
)
r.active_shader = gorad
r.draw_arrays('TRIANGLES')

# ================= MODELO 3 =================
r.current_texture = Texture('./pmodels/sofa.bmp')
r.lookAt(V3(0, 0, 5), V3(0, 0, 0), V3(0, 1, 0))
r.load('./pmodels/sofa.obj',
  translate=(0.7, -0.7, 0),
  scale=(0.6, 0.6, 0.6),
  rotate=(0, -0.5, 0)
)
r.active_shader = gorad
r.draw_arrays('TRIANGLES')

# ================= MODELO 4 =================
r.current_texture = Texture('./pmodels/tv.bmp')
r.lookAt(V3(0, 0, 5), V3(0, 0, 0), V3(0, 1, 0))
r.load('./pmodels/tv.obj',
  translate=(-0.7, -0.2, 0),
  scale=(1, 1, 1),
  rotate=(0, 0.5, 0)
)
r.active_shader = gorad
r.draw_arrays('TRIANGLES')

# ================= MODELO 5 =================
r.current_texture = Texture('./pmodels/luz.bmp')
r.lookAt(V3(0, 0, 5), V3(0, 0, 0), V3(0, 1, 0))
r.load('./pmodels/luz.obj',
  translate=(0, 1, 0),
  scale=(0.7, 0.7, 0.7),
  rotate=(0, 0, 0)
)
r.active_shader = gorad
r.draw_arrays('TRIANGLES')

r.glFinish('proyecto1.bmp')
