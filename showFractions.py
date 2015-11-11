import ROOT
import sys
from math import sqrt
from fnmatch import fnmatch
from CanvasUtilities import *

canvases = [ ]

#def getObjectsFromCanvas(canvas,type,name=None):
#  result = [ ]
#  for obj in canvas.GetListOfPrimitives():
#    if obj.InheritsFrom(type):
#      if name==None or obj.GetName()==name:
#        result.append(obj)
#  return result

#def getObjectsFromDirectory(dir,type,name=None):
#  result = [ ]
#  ROOT.gROOT.cd()
#  for key in dir.GetListOfKeys():
#    obj = key.ReadObj()
#    if obj.InheritsFrom(type):
#      if name==None or obj.GetName()==name:
#        result.append(obj)
#  return result

def getYield(hist,ibin):
  return ( hist.GetBinContent(ibin), hist.GetBinError(ibin) )

def getYields(hists,ibin):
  result = [ ]
  for h in hists:
    result.append( getYield(h,ibin) )
  return result

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--showcolors", dest="showcolors", action="store_true", default=False)
parser.add_option("--color", "-c", dest="color", type="int", default=None)
parser.add_option("--sample", "-s", dest="sample", default=None)
(options, args) = parser.parse_args()

tf = ROOT.TFile(args[0])
cnv = getObjectsFromDirectory(tf,ROOT.TCanvas.Class())[0]
cnv.Draw()
pad = getObjectsFromCanvas(cnv,ROOT.TPad.Class(),"p1")[0]
stack = getObjectsFromCanvas(pad,ROOT.THStack.Class())[0]

htot = stack.GetStack().Last()
nbins = htot.GetNbinsX()
assert nbins%2==1
nreg = (nbins-1)/2

ROOT.gROOT.cd()
allObjects = [ ]
for sgn in [ -1, 1 ]:

  rname = "CR" if sgn<0 else "SR"

  hRs = [ ]
  for ih,h in enumerate(stack.GetHists()):
    hRs.append(ROOT.TH1D("h"+rname+str(ih),"h"+rname+str(ih),nreg,0.5,nreg+0.5))
    hRs[-1].SetLineColor(h.GetFillColor())
    hRs[-1].SetMarkerStyle(20)
    hRs[-1].SetMarkerColor(h.GetFillColor())
    allObjects.append(hRs[-1])

  for ir in range(nreg):
    ctotal = getYield(htot,sgn*(ir+1)+nreg+1)
    csamples = getYields(stack.GetHists(),sgn*(ir+1)+nreg+1)

    sv = 0.
    se2 = 0.
    for c in csamples:
      sv += c[0]
      se2 += c[1]**2
    if ctotal[0]>1e-6:
      assert abs(ctotal[0]-sv)/ctotal[0]<1.e-4
    if ctotal[1]>1e-6:
      assert abs(ctotal[1]**2-se2)/ctotal[1]**2<1.e-4

    for ih,h in enumerate(stack.GetHists()):
      c = csamples[ih][0]
      if ctotal[0]>1.e-4:
        f = c / ctotal[0]
        ef = ctotal[0]*(ctotal[0]-2*c)*csamples[ih][1]**2 + (c*ctotal[1])**2
        ef = sqrt(ef) / ctotal[0]**2
        hRs[ih].SetBinContent(ir+1,f)
        hRs[ih].SetBinError(ir+1,ef)
        
      
  for ih,h in enumerate(stack.GetHists()):
        
    if ih==0:
      cnv = ROOT.TCanvas(rname,rname)
      allObjects.append(cnv)
      hRs[ih].SetMaximum(1.05)
      hRs[ih].Draw()
      hRs[ih].Draw("same hist")
    else:
      hRs[ih].Draw("same")
      hRs[ih].Draw("same hist")

  cnv.Update()

