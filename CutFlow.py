import ROOT
from math import sqrt
from array import array

class CutFlow:

  def __init__(self,name,labels):
    assert name.isalnum()
    self.name = name
    self.nbins = None
    self.xmin = None
    self.xmax = None
    self.labels = [ ]
    for l in labels:
      self.labels.append(l)
    self.histogram = None

  def createHistogram(self):
    h = ROOT.TH1D(self.name,self.name,len(self.labels),-0.5,len(self.labels)-1)
    axis = h.GetXaxis()
    for i,l in enumerate(self.labels):
      axis.SetBinLabel(i+1,l)
    return h

  def index(self,label):
    return self.labels.index(label)
