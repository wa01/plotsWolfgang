import ROOT
import math
import time
from optparse import OptionParser
from PlotsBase import *
from EventHelper import EventHelper
from LeptonUtilities import *
from KinematicUtilities import deltaR
from PreselectionTools import *

class DiLeptonPlots(PlotsBase):

    def __init__(self,name,preselection=None,elist=None,elistBase="./elists",rebin=None,argv=[]):
        PlotsBase.__init__(self,name,preselection,elist=elist,elistBase=elistBase,rebin=rebin)
        self.histogramList = { }
        self.cutflowList = { }
        curdir = ROOT.gDirectory
        if not ROOT.gROOT.Get(name):
            ROOT.gROOT.mkdir(name)
        ROOT.gROOT.cd(name)

        parser = OptionParser()
        parser.add_option("--splitChannels", dest="splitChannels", action="store_true", default=False)
        parser.add_option("--channel", dest="channel", choices=[ "Ele", "Mu" ], default=None )
        ( self.options, args ) = parser.parse_args(argv)
        assert len(args)==0

        self.addVariable("ngenLep",5,-0.5,4.5,'b')
        self.addVariable("ngenLepFromTau",5,-0.5,4.5,'b')
        self.addVariable("ngenTau",5,-0.5,4.5,'b')
        self.addVariable("nTightLep",10,-0.5,9.5,'u')
        self.addVariable("nVetoLep",10,-0.5,9.5,'u')
        self.addVariable("wrongCharge",2,-0.5,1.5,'b')
        self.addVariable("flavourCombination",3,-0.5,2.5,'b')
        self.addVariable("ngenLep2l",5,-0.5,4.5,'b')
        self.addVariable("ngenLepFromTau2l",5,-0.5,4.5,'b')
        self.addVariable("ngenTau2l",5,-0.5,4.5,'b')
        self.addVariable("nTightLep2l",10,-0.5,9.5,'u')
        self.addVariable("nVetoLep2l",10,-0.5,9.5,'u')
        self.addVariable("massTTll",60,0.,120.,'b')
        self.addVariable("massTVll",60,0.,120.,'b')
        self.addVariable("massTTemu",60,0.,120.,'b')
        self.addVariable("massTVemu",60,0.,120.,'b')
        self.addVariable("IncRegsTTll",2*5+1,-5.5,5.5,'b')
        self.addVariable("IncRegsTVll",2*5+1,-5.5,5.5,'b')
        self.addVariable("IncRegsTTemu",2*5+1,-5.5,5.5,'b')
        self.addVariable("IncRegsTVemu",2*5+1,-5.5,5.5,'b')

        curdir.cd()

        self.selection = RA40bSelection(reqNTightLep=(1,3),reqNVetoLep=(0,None))

    def fill(self,eh,sample,itree):

        self.timers[0].start()
        if not sample.isData():
#            w = eh.get("weight")*sample.downscale*sample.extweight
#            if self.reweightDY:
#                w *= self.reweightClass.isrWeightDY(zpt)
            w = eh.get("xsec")*sample.baseweights[itree]*sample.downscale*sample.extweight
            if sample.mcReweight:
                w *= sample.mcReweight.weight(eh)
        else:
            w = 1
        self.timers[0].stop()        

        self.selection.set(eh)
        nTight = len(self.selection.tightLeptons)
        nVeto = len(self.selection.vetoLeptons)

        ngenLep = eh.get("ngenLep")
        ngenTau = eh.get("ngenTau")
        ngenLepFromTau = eh.get("ngenLepFromTau")
                
        self.fill1D("ngenLep",ngenLep,w)
        self.fill1D("ngenTau",ngenTau,w)
        self.fill1D("ngenLepFromTau",ngenLepFromTau,w)
                    
        self.fill1D("nTightLep",nTight,w)
        self.fill1D("nVetoLep",nVeto,w)

        pdgs = eh.get("LepGood_pdgId")
        allLeptons = self.selection.tightLeptons + self.selection.vetoLeptons
        idxLep1 = allLeptons[0]
        pdgLep1 = pdgs[idxLep1]
        wrongCharge = 0
        idxLep2 = None
        pdgLep2 = None
        for i in allLeptons[1:]:
            pdg = pdgs[i]
            if pdgLep1*pdg<0:
                idxLep2 = i
                pdgLep2 = pdg
                break
            else:
                wrongCharge = 1
        self.fill1D("wrongCharge",wrongCharge,w)
        if idxLep2==None:
            return

        flavComb = None
        if abs(pdgLep1)==11 and abs(pdgLep2)==11:
            flavComb = 0
        elif abs(pdgLep1)==13 and abs(pdgLep2)==13:
            flavComb = 1
        elif ( abs(pdgLep1)==11 and abs(pdgLep2)==13) or \
             ( abs(pdgLep1)==13 and abs(pdgLep2)==11):
            flavComb = 2
        self.fill1D("flavourCombination",flavComb,w)

        self.fill1D("ngenLep2l",ngenLep,w)
        self.fill1D("ngenTau2l",ngenTau,w)
        self.fill1D("ngenLepFromTau2l",ngenLepFromTau,w)
                    
        self.fill1D("nTightLep2l",nTight,w)
        self.fill1D("nVetoLep2l",nVeto,w)
            
        if not self.selection.preselection():
            return

        lepPts = eh.get("LepGood_pt")
        lepEtas = eh.get("LepGood_eta")
        lepPhis = eh.get("LepGood_phi")
        p4lep1 = ROOT.TLorentzVector()
        p4lep1.SetPtEtaPhiM(lepPts[idxLep1],lepEtas[idxLep1],lepPhis[idxLep1],0.)
        p4lep2 = ROOT.TLorentzVector()
        p4lep2.SetPtEtaPhiM(lepPts[idxLep2],lepEtas[idxLep2],lepPhis[idxLep2],0.)
        mll = (p4lep1+p4lep2).M()
        hn = "massT"
        if idxLep2<nTight:
            hn += "T"
        else:
            hn += "V"
        if flavComb<2:
            hn += "ll"
        elif flavComb==2:
            hn += "emu"
        self.fill1D(hn,mll,w)

        dphi = abs(self.selection.wkin.dPhi())
        nGoodJs = self.selection.nJets
        nBJets = self.selection.nBJets

        incRegSign = -1 if dphi<0.75 else +1
        incRegs = [ 1 ]
        if nGoodJs>=3 and nGoodJs<=4 and nBJets==0:
            incRegs.append(2)
        if nGoodJs>=4 and nGoodJs<=5 and nBJets<3:
            incRegs.append(3+min(nBJets,2))
        for ir in incRegs:
            hn = "IncRegs"
            if idxLep2<nTight:
                hn += "TT"
            else:
                hn += "TV"
            if flavComb<2:
                hn += "ll"
            elif flavComb==2:
                hn += "emu"
            self.fill1D(hn,incRegSign*ir,w)


    def showTimers(self):
        line = ""
        for t in self.timers:
            line += "{0:14.2f}".format(1000000*t.meanTime())
#            line += " " + str(t.meanTime())
        print line
            
    def histograms(self):
        return self.histogramList

    def cutflows(self):
        return self.cutflowList
        
