class Figures(object):
  def __init__(self, filename):
    with open(filename) as f:
      self.lines = f.read().splitlines()
      self.draws = []
    
    self.read()

  def read(self):
    for line in self.lines:
      secondLine = line.replace('(','').replace(')','').replace(' ', '')
      self.draws.append(secondLine.split(','))
