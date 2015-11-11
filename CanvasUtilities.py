import ROOT

def getObjectsFromCanvas(canvas,type,name=None):
  result = [ ]
  for obj in canvas.GetListOfPrimitives():
    if obj.InheritsFrom(type):
      if name==None or obj.GetName()==name:
        result.append(obj)
  return result

def getObjectsFromDirectory(dir,type,name=None):
  result = [ ]
  ROOT.gROOT.cd()
  for key in dir.GetListOfKeys():
    obj = key.ReadObj()
    if obj.InheritsFrom(type):
      if name==None or obj.GetName()==name:
        result.append(obj)
  return result

