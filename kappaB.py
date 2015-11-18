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

def getRcs(histo,name):
    nr = (histo.GetNbinsX()-1)/2
    result = ROOT.TH1D(name,name,nr,0.5,nr+0.5)
    for i in range(nr):
        icr = nr - i
        ccr = histo.GetBinContent(icr)
        ecr = histo.GetBinError(icr)
        isr = nr + i + 2
        csr = histo.GetBinContent(isr)
        esr = histo.GetBinError(isr)
        if ccr>0.:
            rcs = csr/ccr
            if csr>0.:
                ercs = sqrt((ecr/ccr)**2+(esr/csr)**2)*rcs
            else:
                ercs = 0.
        else:
            rcs = 0.
            ercs = 0.
        result.SetBinContent(i+1,rcs)
        result.SetBinError(i+1,ercs)
        result.GetXaxis().SetBinLabel(i+1,histo.GetXaxis().GetBinLabel(i+1))
    return result

def getByColor(stack,color):
    result = None
    for h in stack.GetHists():
      if h.GetFillColor()==color:
        assert result==None
        result = h
    return result

def getByIndices(stack,indices=None):
  if indices==None:
    return stack.GetStack().Last()

  if len(indices)==1:
    return stack.GetHists()[indices[0]]

  result = None
  for i in indices:
    if result==None:
      result = stack.GetHists()[i].Clone()
    else:
      result.Add(stack.GetHists()[i])
  return result
  
def getRcsRatios(stack0,stack1,indices=None):
#    if color==None:
#      h0 = stack0.GetStack().Last()
#      h1 = stack1.GetStack().Last()
#    else:
#      h0 = getByColor(stack0,color)
#      h1 = getByColor(stack1,color)
    h0 = getByIndices(stack0,indices)
    h1 = getByIndices(stack1,indices)

    hrcs0 = getRcs(h0,stack0.GetName())
    hrcs0.SetFillStyle(0)
    hrcs0.SetLineWidth(2)
    hrcs0.SetLineColor(4)
    hrcs0.SetMarkerStyle(22)
    hrcs0.SetMarkerColor(4)
        
    hrcs1 = getRcs(h1,stack1.GetName())
    hrcs1.SetFillStyle(0)
    hrcs1.SetLineWidth(2)
    hrcs1.SetLineColor(2)
    hrcs1.SetMarkerStyle(22)
    hrcs1.SetMarkerColor(2)
        
    cnv1 = ROOT.TCanvas("c"+stack0.GetName()+stack1.GetName()+"Rcs",
                        "c"+stack0.GetName()+stack1.GetName()+"Rcs")
    canvases.append(cnv1)
    hrcs0.Draw()
    hrcs1.Draw("same")
    cnv1.Modified(1)
    cnv1.SetLogy(1)
    cnv1.Update()

    hrcsRatio = hrcs0.Clone("ratio")
    hrcsRatio.Divide(hrcs1)
    hrcsRatio.SetLineColor(1)
    hrcsRatio.SetMarkerStyle(20)
    hrcsRatio.SetMarkerColor(1)

    cnv2 = ROOT.TCanvas("c"+stack0.GetName()+stack1.GetName()+"RcsRatio",
                        "c"+stack0.GetName()+stack1.GetName()+"RcsRatio")
    canvases.append(cnv2)
    hrcsRatio.Draw()
    cnv2.Modified(1)
#    cnv2.SetLogy(1)
    cnv2.Update()

#    raw_input("Enter")

    return hrcsRatio

def getLegend(pad):
  """Get lists of legend entries for data and bkg MC histograms.
  """
  legends = getObjectsFromCanvas(pad,ROOT.TLegend.Class())
  assert len(legends)==1

  result = { 'Data' : None, 'MC' : [ ] }
  for le in legends[0].GetListOfPrimitives():
    obj = le.GetObject()
    # data histogram uses markers and no fill color
    if obj.GetMarkerStyle()>1 or obj.GetFillColor()==0:
      assert le.GetLabel().lower().find("data")>=0
      assert result["Data"]==None
      result["Data"] = le
    # MC background histograms use no markers and a fill color
    elif obj.GetFillColor()>0:
      assert le.GetLabel().lower().find("data")<0
      result["MC"].append(le)

  return result

def getLegendLabels(legendEntries):
  """Get data and bkg MC labels from result of getLegend().
  """
  result = { 'Data' : None, 'MC' : [ ] }
  leData = legendEntries['Data']
  if leData!=None:
    result['Data'] = leData.GetLabel()
  for le in legendEntries['MC']:
    result['MC'].append(le.GetLabel())
  return result

def getLegendObjects(legendEntries):
  """Get data and bkg MC objects from result of getLegend().
  """
  result = { 'Data' : None, 'MC' : [ ] }
  leData = legendEntries['Data']
  if leData!=None:
    result['Data'] = leData.GetObject()
  for le in legendEntries['MC']:
    result['MC'].append(le.GetObject())
  return result

def getDataHistogram(pad):
  """Get data histogram from canvas.
  """
  histos = getObjectsFromCanvas(pad,ROOT.TH1.Class())

  result = None
  for h in histos:
    if h.GetMarkerStyle()>1 and h.GetFillColor()==0:
      assert result==None
      result = h

  return result

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--showcolors", dest="showcolors", action="store_true", default=False)
parser.add_option("--color", "-c", dest="color", type="int", default=None)
parser.add_option("--sample", "-s", dest="sample", default=None)
parser.add_option("--sample", "-s", dest="sample", default=None)
parser.add_option("--data", "-d", dest="data", action="store_true", default=False)
(options, args) = parser.parse_args()

tfs = [ ]
stacks = [ ]
hdatas = [ ]
sampleIndices = { 'Data' : None, 'MC' : None }
if options.data:
  sampleIndices['Data'] = -1
allLegends = [ ]
allLabels = None
for ib in [ 0, 1, 2 ]:
    cnvName = "tt"+str(ib)+"bCSRs"
    tfs.append(ROOT.TFile(args[0]+"/"+cnvName+".root"))
    cnv = tfs[-1].Get(cnvName)
    cnv.Draw()
    pad = getObjectsFromCanvas(cnv,ROOT.TPad.Class(),"p1")[0]
    allLegends.append(getLegend(pad))
    if allLabels==None:
      allLabels = getLegendLabels(allLegends[-1])
    else:
      assert allLabels==getLegendLabels(allLegends[-1])
    if allLabels["Data"]!=None:
      hdatas.append(getDataHistogram(pad))
    stack = getObjectsFromCanvas(pad,ROOT.THStack.Class())[0]
    if options.showcolors:
      for h in stack.GetHists():
        print h,h.GetFillColor()
      leg = getObjectsFromCanvas(pad,ROOT.TLegend.Class())[0]
      for o in leg.GetListOfPrimitives():
        print o,o.GetObject(),o.GetLabel()
      print allLabels
      sys.exit(0)
    if options.sample!=None and sampleIndices['MC']==None:
      sampleIndices['MC'] = [ ]
      for il,l in enumerate(allLabels['MC']):
        if fnmatch(l,options.sample):
          o = allLegends[-1]['MC'][il].GetObject()
          h = stack.GetHists()[il]
          print il,l,o.GetFillColor(),h.GetFillColor(),o.GetMarkerStyle(),h.GetMarkerStyle()
          assert o.GetFillColor()==h.GetFillColor() and o.GetMarkerStyle()==h.GetMarkerStyle()
          sampleIndices['MC'].append(il)
      assert len(sampleIndices)>0
#      leg = getObjectsFromCanvas(pad,ROOT.TLegend.Class())[0]
#      for io,o in enumerate(leg.GetListOfPrimitives()):
#        print o,o.GetObject(),o.GetLabel()
#        if not fnmatch(o.GetLabel(),options.sample):
#          continue
#        assert o.GetObject().GetFillColor()==stack.GetHists()[io].GetFillColor() and \
#            o.GetObject().GetMarkerStyle()==stack.GetHists()[io].GetMarkerStyle()
#        sampleIndices.append(io)
#      assert len(sampleIndices)>0
    stacks.append(stack)

print stacks
ROOT.gROOT.cd()
#h01 = getRcsRatios(stacks[0],stacks[1],color=options.color)
#h12 = getRcsRatios(stacks[1],stacks[2],color=options.color)
h01 = getRcsRatios(stacks[0],stacks[1],indices=sampleIndices['MC'])
h12 = getRcsRatios(stacks[1],stacks[2],indices=sampleIndices['MC'])

cnv = ROOT.TCanvas("cDoubleRatio","cDoubleRatio")
canvases.append(cnv)
h01.SetLineColor(4)
h01.SetMarkerColor(4)
h01.SetMaximum(1.)
h01.Draw()
h01.Fit("pol0","","same")
h01.GetFunction("pol0").SetLineStyle(2)
h01.GetFunction("pol0").SetLineColor(4)
h12.SetLineColor(2)
h12.SetMarkerColor(2)
h12.Draw("same")
h12.Fit("pol0","","same")
h12.GetFunction("pol0").SetLineStyle(2)
h12.GetFunction("pol0").SetLineColor(2)
ROOT.gPad.Update()
raw_input("Enter")
