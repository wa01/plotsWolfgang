#!/usr/bin/env python

import ROOT
import os,sys,string,math
from fnmatch import fnmatch
from Sample import *
#from drawWithFOM import *
#from drawSoB import *
from optparse import OptionParser
from SampleFilters import *

parser = OptionParser()
parser.add_option("--preselection", "-p", dest="preselection",  help="preselection", default=None)
parser.add_option("--draw", "-d", dest="drawClass",  help="draw class", default="DrawWithFOM.py")
parser.add_option("--elist", "-e", dest="elist",  help="event list mode", choices=[ "w", "r", "a" ], default=None )
parser.add_option("--fom", dest="fom",  help="fom to be used", choices=[ "sob", "sosqrtb", "dataovermc", "None" ], default="sosqrtb" )
parser.add_option("--elistBase", dest="elistBase",  help="base directory for event lists", default="./elists")
parser.add_option("-s", dest="save",  help="directory for saved plots", default=None)
parser.add_option("-b", dest="batch",  help="batch mode", action="store_true", default=False)
parser.add_option("--fomByBin", dest="fomByBin",  help="calculate fom by bin", action="store_true", default=False)
parser.add_option("--rebin", dest="rebin",  help="rebin factor", type=int, default=1)
parser.add_option("--dset", dest="dset", help="dataset", choices=[ "met", "singleMu", "diMu", "diEle", "isrDiMu", "isrDiNu" ], default="met" )
parser.add_option("--data", dest="data", help="show data", action="store_true", default=False)
parser.add_option("--overwrite", "-o", dest="overwrite", help="overwrite output directory", action="store_true", default=False)
parser.add_option("--canvasNames",dest="canvasNames",help="(comma-separated list) of canvases to show",default=None)
parser.add_option("--writeSums", dest="writeSums",  help="write pickle file with histogram counts", action="store_false", default=True)
(options, args) = parser.parse_args()
assert len(args)>0
if options.fom=="None":
    options.fom = None
assert options.rebin>0
selectedCanvasNames = [ ]
if options.canvasNames!=None:
    for cnvname in  options.canvasNames.split(","):
        selectedCanvasNames.append(cnvname)
    print selectedCanvasNames
if options.writeSums:
    import cPickle
    sumDict = { }
else:
    sumDict = None

savedir = None
if options.save:
    savedir = "".join(s for s in options.save if s in string.letters+string.digits+"_-")
    savedir = "/afs/cern.ch/user/a/adamwo/www/cms/ra4/plots_"+savedir+"/"
    if os.path.isdir(savedir):
        if not options.overwrite:
            print "Output directory ",savedir," exists - terminating"
            sys.exit(1)
        else:
            print "Output directory ",savedir," will be overwritten !!!!"

plotGlobals = {}
execfile(args[0],plotGlobals)
plotClassName = os.path.splitext(os.path.basename(args[0]))[0]
plotClass = plotGlobals[plotClassName]
plotClassArguments = [] if len(args)<2 else args[1:]

drawGlobals = {}
execfile(options.drawClass,drawGlobals)
drawClassName = os.path.splitext(os.path.basename(options.drawClass))[0]
drawClass = drawGlobals[drawClassName](options)

presel = None
if options.preselection!=None:
    preselGlobals = {}
    execfile(options.preselection,preselGlobals)
    preselClassName = os.path.splitext(os.path.basename(options.preselection))[0]
    preselClass = preselGlobals[preselClassName]
    presel = preselClass()
    setattr(presel,"sourcefile",options.preselection)

#dataBase = "/home/adamwo/data/"
dataBase = "/media/Seagate/adamwo/data/cmgTuples/"
sampleBase = dataBase+"tuples_from_Artur/"
if options.dset=="singleMu":
    sampleBase += "copyMu/"
elif options.dset=="diMu":
    sampleBase = dataBase+"tuples_from_Artur/copyDiMu/"
elif options.dset=="diEle":
    sampleBase = dataBase+"tuples_from_Artur/copyDiEle/"
elif options.dset.startswith("isr"):
    sampleBase = dataBase+"tuples_from_Artur/copyIsr/"
else:
    pass
#    sampleBase += "copy/"
assert os.path.isdir(options.elistBase)
elistbase = os.path.join(options.elistBase,os.path.split(os.path.normpath(sampleBase))[-1])
if not os.path.isdir(elistbase):
    assert not os.path.exists(elistbase)
    os.mkdir(elistbase,0744)

samples = []
lumi = 3000.
if options.dset=="singleMu":
    pass
else:
#    samples.append(Sample("QCD",sampleBase,type="B",color=7,fill=True, \
#                              namelist=[ "QCD20to600", "QCD600to1000", "QCD1000" ]))
#    samples.append(Sample("VV",sampleBase,type="B",color=6,fill=True, \
#                              namelist=[ "WW", "WZ", "ZZ"]))
#    samples.append(Sample("DYJetsToLL",sampleBase,type="B",color=3,fill=True, \
#                              namelist=[ "8TeV-DYJetsToLL_PtZ-50_TuneZ2star_8TeV_ext-madgraph-tarball" ], \
#                              kfactor=1.20))
##                              namelist=["8TeV-DYJetsToLL_PtZ-50_TuneZ2star_8TeV_ext-madgraph-tarball"]))
##    samples.append(Sample("ZJetsInv",dataBase+"monoJetTuples_v8/copy/",type="B",color=9,fill=True))
#    samples.append(Sample("ZJetsToNuNu",sampleBase,type="B",color=9,fill=True, \
#                              namelist=[ "8TeV-ZJetsToNuNu_50_TuneZ2Star_8TeV_madgraph_ext" ]))
#    samples.append(Sample("singleTop",sampleBase,type="B",color=4,fill=True))
#    samples.append(Sample("TTJetsPowHeg",sampleBase,type="B",color=2,fill=True))
#    samples.append(Sample("WJetsHT150v2Tau",sampleBase,type="B",color=8,fill=True, \
#                              namelist=["WJetsHT150v2"],filter=LeptonFilter(16),kfactor=1.19))
#    samples.append(Sample("WJetsHT150v2NoTau",sampleBase,type="B",color=5,fill=True, \
#                              namelist=["WJetsHT150v2"],filter=InvertedSampleFilter(LeptonFilter(16)), \
#                              kfactor=1.19))
#    samples.append(Sample("T2DegStop_300_270",sampleBase,type="S",color=1,line=2,fill=False))
#    samples.append(Sample("T2DegStop_300_240",sampleBase,type="S",color=1,line=4,fill=False))

    samples.append(Sample("QCD",sampleBase,type="B",color=8,fill=True,kfactor=1., \
                              namelist=["QCD_HT200to300", \
                                            "QCD_HT300to500", \
                                            "QCD_HT500to700", \
                                            "QCD_HT700to1000", \
                                            "QCD_HT1000to1500", \
                                            "QCD_HT1500to2000", \
                                            "QCD_HT2000toInf" ], \
                              baseweights=lumi ))
    samples.append(Sample("DYJetsToLL",sampleBase,type="B",color=5,fill=True, \
                              kfactor=1., \
                              namelist=["DYJetsToLL_M50_HT100to200", \
                                        "DYJetsToLL_M50_HT200to400", \
                                        "DYJetsToLL_M50_HT400to600", \
                                        "DYJetsToLL_M50_HT600toInf" ], \
                              baseweights=[lumi, lumi, lumi, lumi] ))
    samples.append(Sample("TTV",sampleBase,type="B",color=6,fill=True, \
                              kfactor=1., \
                              namelist=["TTWJetsToQQ_25ns","TTZToLLNuNu_25ns","TTZToQQ_25ns"], \
                              baseweights=3*[lumi] ))
    samples.append(Sample("singleTop",sampleBase,type="B",color=ROOT.kRed-7,fill=True,kfactor=1., \
                              namelist=["TToLeptons_sch", \
                                            "TToLeptons_tch", \
                                            "T_tWch", \
                                            "TBar_tWch" ], \
                              baseweights=lumi ))
    samples.append(Sample("TTJets_LO_25ns",sampleBase,type="B",color=ROOT.kRed,fill=True, \
                              kfactor=1.,baseweights=lumi ))
    samples.append(Sample("WJetsToLNu",sampleBase,type="B",color=4,fill=True, \
                              kfactor=1., \
                              namelist=["WJetsToLNu_HT100to200", \
                                        "WJetsToLNu_HT200to400", \
                                        "WJetsToLNu_HT400to600", \
                                        "WJetsToLNu_HT600to800", \
                                        "WJetsToLNu_HT800to1200", \
                                        "WJetsToLNu_HT1200to2500", \
                                        "WJetsToLNu_HT2500toInf" ], \
                              baseweights=7*[lumi] ))
    if options.data:
        samples.append(Sample("data",sampleBase,type="D",color=1,fill=False))


ROOT.TH1.SetDefaultSumw2()

allplots = [ ]
variables = { }
cutflows = { }
for s in samples:
    plots = plotClass(s.name,presel,elist=options.elist,elistBase=elistbase,rebin=options.rebin,argv=plotClassArguments)
    if options.fomByBin:
        for v in plots.getVariables1D():
            v.scut = 'b'
    allplots.append(plots)
    plots.fillall(s)
    if len(variables)==0:
        variableNames = plots.getVariables()
        for varname in variableNames:
            variables[varname] = ( plots.getVariables()[varname] , [ ] )
    for varname in variables:
        variables[varname][1].append(plots.histograms()[varname])
#    print s.name," : ",plots.hdr.GetSumOfWeights()
    if len(cutflows)==0:
        cutflowNames = plots.getCutFlows()
        for cfname in cutflowNames:
            cutflows[cfname] = ( plots.getCutFlows()[cfname] , [ ] )
    for cfname in cutflowNames:
        cutflows[cfname][1].append( plots.cutflows()[cfname])

ROOT.gROOT.cd()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

if savedir!=None:
    if not os.path.isdir(savedir):
        os.mkdir(savedir)
    else:
        os.system("rm "+savedir+"*.png "+savedir+"*.root "+savedir+"*.pkl "+savedir+"*.log "+savedir+"*.php")
    if os.path.exists(savedir+"../my_index.php") and os.path.islink(savedir+"../my_index.php"):
        target = os.readlink(savedir+"../my_index.php")
        os.symlink(target,savedir+"index.php")

canvases = [ ]
pads = [ ]
allobjects = [ ]
definedPalette = False
oldstdout = None
if savedir:
    oldstdout = sys.stdout
    sys.stdout = open(savedir+"summary.log","w")
    print " ".join(sys.argv)
    print " "

for varname in variables:

    showCanvas = False if selectedCanvasNames else True
    for cnvname in selectedCanvasNames:
        if fnmatch(varname,cnvname):
            showCanvas = True
            break
    if not showCanvas:
        continue

    variable, histograms = variables[varname]


#    cnv = ROOT.TCanvas(bkgs.GetName(),bkgs.GetName(),700,700)
    cnv = ROOT.TCanvas("cnv","cnv",700,700)

#    drawClass = DrawWithFOM(fom=options.fom)

    data = None
    if variable.is2D():
        cnv.SetRightMargin(0.15)
        if not definedPalette:
            ROOT.gROOT.ProcessLine(".L ../../HEPHYPythonTools/scripts/root/useNiceColorPalette.C")
            ROOT.useNiceColorPalette()
            definedPalette = True
        data, bkgs, sigs, legend = drawClass.drawStack2D(samples,histograms,cnv)
        if variable.uselog:
            cnv.SetLogz(1)

    else:
        if options.fom!=None:
            p1 = ROOT.TPad("p1","", 0, 0.28, 1, 0.95)
            p1.SetTopMargin(1e-7)
            p1.Draw()
            p2 = ROOT.TPad("p2","", 0, 0, 1, 0.3)
            p2.SetTopMargin(1e-7)
            p2.Draw()
            if not options.batch:
                pads.append(p1)
                pads.append(p2)
        else:
            p1 = ROOT.TPad("p1","", 0, 0., 1, 0.95)
            p1.SetTopMargin(1e-7)
            p1.Draw()
            if not options.batch:
                pads.append(p1)

        if variable.uselog:
            p1.SetLogy(1)
        data, bkgs, sigs, legend = drawClass.drawStack1D(samples,histograms,pad=p1,sumDict=sumDict)
        if data==None and bkgs==None and sigs==None and legend==None:
            continue
#        if variable.uselog:
#            p1.SetLogy(1)

    if not options.batch:
        canvases.append(cnv)

    ROOT.SetOwnership(bkgs,False)
    cnv.SetName(bkgs.GetName())
    cnv.SetTitle(bkgs.GetName())
    if not options.batch:
        if data!=None:
            allobjects.append(data)
        if bkgs!=None:
            allobjects.append(bkgs)
        if legend!=None:
            allobjects.append(legend)
        if len(sigs)>0:
            allobjects.extend(sigs)
    if not variable.is2D() and bkgs!=None and options.fom!=None:
#        drawClass.drawSoB(bkgs,sigs,variable.scut,pad=p2)
        if data!=None and options.fom=="dataovermc":
            drawClass.drawDoMC(data,bkgs,pad=p2)
        elif variable.scut!=None:
            drawClass.drawFom(bkgs,sigs,variable.scut,pad=p2)
    cnv.Update()
    if savedir!=None:
        cnv.SaveAs(savedir+cnv.GetName()+".png")
        cnv.SaveAs(savedir+cnv.GetName()+".root")
    if options.batch:
        del cnv

allCutFlowsByLabels = { }
for cfname,cf in cutflows.iteritems():
    allCutFlowsByLabels[cfname] = [ ]
    print " "
    print "Cut flow ",cfname
    cfByLabels = [ ]
    line = " ".ljust(15)
    cfByLabels.append("")
    for s in samples:
        line += 2*" " + s.name[:13].rjust(13)
        cfByLabels.append(s.name)
    line += 2*" " + "Total"[:13].rjust(13)
    print line
    allCutFlowsByLabels[cfname].append(cfByLabels)
    axis = cf[1][0].GetXaxis()
    nbins = axis.GetNbins()
    labels = [ axis.GetBinLabel(i+1) for i in range(nbins) ]
    cs = len(samples)*[ 0. ]
    es = len(samples)*[ 0. ]
    for i,label in enumerate(labels):
        cfByLabels = [ label ]
        line1 = label[:15].ljust(15)
        line2 = " ".ljust(15)
        csum = 0.
        esum = 0.
        for j,s in enumerate(samples):
            cs[j] = cf[1][j].GetBinContent(i+1)
            csum += cs[j]
            es[j] = cf[1][j].GetBinError(i+1)
            esum += es[j]**2
            line1 += "{0:15.2f}".format(cs[j])
            line2 += ("  +- "+"{0:8.2f}".format(es[j]).strip()).rjust(15)
            cfByLabels.append( ( cs[j], es[j] ) )
        line1 += "{0:15.2f}".format(csum)
        line2 += ("  +- "+"{0:8.2f}".format(math.sqrt(esum)).strip()).rjust(15)
        print line1
        print line2
        allCutFlowsByLabels[cfname].append(cfByLabels)
        if csum<1.e-6:
            csum = 1.
        line1 = " ".ljust(15)
        for j in range(len(cs)):
            line1 += "{0:7.1f} +-{1:5.1%}".format(100*cs[j]/csum,es[j]/csum)
        print line1

if oldstdout!=None:
    log = sys.stdout
    sys.stdout = oldstdout
    log.close()

if sumDict and savedir:
    fsum = open(savedir+"summary.pkl","wb")
    cPickle.dump(args[1:],fsum)
    cPickle.dump(sumDict,fsum)
    cPickle.dump(allCutFlowsByLabels,fsum)
    fsum.close()

if not options.batch:
    raw_input("Press enter")
#if options.save:
#    savedir = "".join(s for s in options.save if s in string.letters+string.digits+"_-")
#    savedir = "plots_"+savedir+"/"
#    if not os.path.isdir(savedir):
#        os.mkdir(savedir)
#    else:
#        os.system("rm "+savedir+"*.png")
#        os.system("rm "+savedir+"*.root")
#    for c in canvases:
#        c.SaveAs(savedir+c.GetName()+".png")
#        c.SaveAs(savedir+c.GetName()+".root")
print "continuing"
