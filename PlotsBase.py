import ROOT
import time
import os
from EventHelper import EventHelper
from Variable import *
from CutFlow import *

class MyTimer:
    def __init__(self):
        self.active = False
        self.paused = False
        self.start_ = 0.
        self.stop_ = 0.
        self.entries = 0
        self.sum = 0.

    def resume(self):
        assert self.active and self.paused
        self.paused = False
        self.start_ = time.clock()

    def start(self,paused=False):
        assert not self.active
        self.active = True
        self.paused = True
        if not paused:
            self.resume()

    def pause(self):
        self.stop_ = time.clock()
        assert self.active and not self.paused
        self.sum += self.stop_ - self.start_
        self.start_ = 0.
        self.stop_ = 0.
        self.paused = True

    def stop(self):
        if not self.paused:
            self.pause()
        self.entries += 1
        self.active = False

    def meanTime(self):
        if self.entries==0:
            return 0.
        return self.sum/self.entries
        
class PlotsBase:

    variables = { }
    cutflows = { }

    def getVariables(self):
        return PlotsBase.variables

    def getVariables1D(self):
        return [ v for v in PlotsBase.variables.values() if not v.is2D() ]

    def getVariables2D(self):
        return [ v for v in PlotsBase.variables.values() if v.is2D() ]

    def addVariable(self,name,nbins,xmin,xmax,scut='l',uselog=True,binEdges=None):
        assert name.isalnum()
        assert not name in self.histogramList
        if not name in PlotsBase.variables:
            nb = nbins if binEdges else nbins/self.rebin
            PlotsBase.variables[name] = Variable(name,nb,xmin,xmax,scut,uselog)
        h1d = PlotsBase.variables[name].createHistogram(binEdges)
        self.histogramList[name] = h1d
        setattr(self,"h"+name,h1d)

    def getCutFlows(self):
        return PlotsBase.cutflows

    def addCutFlow(self,labels,nameFlow="DefaultCutFlow"):
        assert nameFlow.isalnum()
        assert not nameFlow in self.cutflowList
        if not nameFlow in PlotsBase.cutflows:
            PlotsBase.cutflows[nameFlow] = CutFlow(nameFlow,labels)
        h = PlotsBase.cutflows[nameFlow].createHistogram()
        self.cutflowList[nameFlow] = h
        setattr(self,"c"+nameFlow,h)

    def addVariablePair(self,xname,nbinsx,xmin,xmax,yname,nbinsy,ymin,ymax,uselog=True,suffix=None):
        varPair = VariablePair(xname,nbinsx/self.rebin,xmin,xmax,yname,nbinsy/self.rebin,ymin,ymax, \
                                   uselog,suffix)
        assert not varPair.name in self.histogramList
        if not varPair.name in PlotsBase.variables:
            PlotsBase.variables[varPair.name] = varPair
        h2d = varPair.createHistogram()
        self.histogramList[varPair.name] = h2d
        setattr(self,"h"+varPair.name,h2d)

    def __init__(self,name,preselection=None,elist=None,elistBase="./elists",rebin=1):
        self.name = name
        self.preselection = preselection
        self.elist = elist
        if elist!=None:
            self.elist = elist.lower()[0]
        self.elistBase = elistBase
        assert os.path.isdir(elistBase)
        self.timers = [ ]
        for i in range(10):
            self.timers.append(MyTimer())
        self.writeElist = False
        self.readElist = False
        if self.preselection!=None and self.elist!=None:
            self.preselName = self.preselection.__class__.__name__
            if self.elist=="w" or self.elist=="a":
                self.writeElist = True
            elif self.elist=="r" or self.elist=="a":
                self.readElist = True
        if self.writeElist or self.readElist:
            self.preselDirName = os.path.join(self.elistBase,self.preselName)
            if not os.path.isdir(self.preselDirName):
                os.mkdir(self.preselDirName,0744)
        self.rebin = rebin
         
    def showTimers(self):
        line = ""
        for t in self.timers:
            line += "{0:14.2f}".format(1000000*t.meanTime())
#            line += " " + str(t.meanTime())
        print line

    def prepareElist(self,sample,subSampleName):
        elist = None
        elistFile = None
        if self.readElist or self.writeElist:
            dirName = os.path.join(self.preselDirName,sample.name)
            if not os.path.isdir(dirName):
                os.mkdir(dirName,0744)
            elistFileName = os.path.join(dirName,subSampleName+"_elist.root")
            if self.elist=="a":
                self.writeElist = False
                self.readElist = False
                if not os.path.exists(elistFileName):
                    self.writeElist = True
                else:
                    elistTime = os.path.getmtime(elistFileName)
                    if elistTime<=os.path.getmtime(self.preselection.sourcefile):
                        self.writeElist = True
                    if elistTime<=os.path.getmtime(sample.fullname(subSampleName)):
                        self.writeElist = True
                self.readElist = not self.writeElist
            if self.writeElist:
                print "(Re)creating elist for ",sample.name,subSampleName
            if self.writeElist:
                print "Reading elist for ",sample.name,subSampleName
            opt = "recreate" if self.writeElist else "read"
            elistFile = ROOT.TFile(elistFileName,opt)
            objarr = ROOT.TObjArray()
            if self.writeElist:
                objstr = ROOT.TObjString()
                objstr.SetString(sample.name)
                objarr.Add(objstr.Clone())
                objstr.SetString(subSampleName)
                objarr.Add(objstr.Clone())
                objstr.SetString(str(sample.downscale))
                objarr.Add(objstr.Clone())
                objarr.Write("file",ROOT.TObject.kSingleKey)
                elist = ROOT.TEventList("elist",self.preselName+" / "+sample.name+" / "+subSampleName)
            else:
                objarr = elistFile.Get("file")
                assert objarr[0].GetString().Data()==sample.name
                assert objarr[1].GetString().Data()==subSampleName
                assert objarr[2].GetString().Data()==str(sample.downscale)
                elist = elistFile.Get("elist")
        return ( elist, elistFile )

    def createGenerator(self,end,downscale=1):
        i = downscale - 1
        while i<end:
            yield i
            i += downscale


    def fillall(self,sample):
        for itree in range(len(sample.names)):
            tree = sample.getchain(itree)            
#            print sample.name,itree
#            print tree.GetEntries()
            nentries = tree.GetEntries()
            downscale = sample.downscale
            iterator = self.createGenerator(tree.GetEntries(),sample.downscale)
            if self.readElist or self.writeElist:
                elist, elistFile = self.prepareElist(sample,sample.names[itree])
                if self.readElist:
                    iterator = self.createGenerator(elist.GetN())
            self.timers[6].start()
            eh = EventHelper(tree)
            self.timers[6].stop()
#        for iev in range(tree.GetEntries()):
            nall = 0
            nsel = 0
            self.timers[7].start(paused=True)
            self.timers[8].start(paused=True)
            for iev in iterator:
#            for iev in sample.getentries(tree):
#            if sample.downscale==1 or (iev%sample.downscale)==0:
                jev = iev if not self.readElist else elist.GetEntry(iev)
                self.timers[8].resume()
                eh.getEntry(jev)
                self.timers[8].pause()
                nall += 1
                if self.readElist or ( \
                    ( self.preselection==None or self.preselection.accept(eh,sample) ) and \
                    ( sample.filter==None or sample.filter.accept(eh) ) ):
#                    if sample.name.startswith("TTJets"):
#                        print "Accepted for ",sample.name,":",eh.get("run"),eh.get("lumi"),eh.get("evt")                        
                    self.timers[7].resume()
                    self.fill(eh,sample,itree)
                    self.timers[7].pause()
                    for timer in self.timers[:7]:
                        if timer.active:
                            timer.stop()
                    if self.writeElist:
                        elist.Enter(iev)
                    nsel += 1
#            print "Ntot for ",sample.name,sample.names[itree]," = ",nall,nsel
#        for ev in tree:
#            self.fill(ev)
            self.timers[7].stop()
            self.timers[8].stop()
            if self.writeElist:
                elist.Write()
            if self.writeElist or self.readElist:
                elistFile.Close()
        # handle under- & overflows
        for n,v in PlotsBase.variables.iteritems():
            v.moveUnderOverFlow(self.histogramList[n])
        self.showTimers()
            
        
    def fill1DBySign(self,name,pdg,value,weight):
        fullname = name
        if pdg>0:
            fullname += "Minus"
        elif pdg<0:
            fullname += "Plus"
        self.histogramList[fullname].Fill(value,weight)

    def fill1DByFlavour(self,name,pdg,value,weight):
        self.histogramList[name].Fill(value,weight)
        if pdg!=None:
            if pdg==0 or abs(pdg)==11:
                self.histogramList[name+"Ele"].Fill(value,weight)        
            if pdg==0 or abs(pdg)==13:
                self.histogramList[name+"Mu"].Fill(value,weight)        

    def fill1D(self,name,value,weight):
        self.fill1DBySign(name,0,value,weight)

    def fill2DBySign(self,name,pdg,xvalue,yvalue,weight):
        fullname = name + "_"
        if pdg>0:
            fullname += "Minus"
        elif pdg<0:
            fullname += "Plus"
        self.histogramList[fullname].Fill(xvalue,yvalue,weight)

    def fill2D(self,name,xvalue,yvalue,weight):
        self.fill2DBySign(name,0,xvalue,yvalue,weight)

    def passedCut(self,label,w,nameFlow="DefaultCutFlow"):
        flow = PlotsBase.cutflows[nameFlow]
        self.cutflowList[nameFlow].Fill(flow.index(label),w)

    def passedCutByFlavour(self,label,pdg,w,nameFlow="DefaultCutFlow"):
        flow = PlotsBase.cutflows[nameFlow]
        self.cutflowList[nameFlow].Fill(flow.index(label),w)
        if pdg!=None:
            if pdg==0 or abs(pdg)==11:
                flow = PlotsBase.cutflows[nameFlow+"Ele"]
                self.cutflowList[nameFlow+"Ele"].Fill(flow.index(label),w)
            if pdg==0 or abs(pdg)==13:
                flow = PlotsBase.cutflows[nameFlow+"Mu"]
                self.cutflowList[nameFlow+"Mu"].Fill(flow.index(label),w)
