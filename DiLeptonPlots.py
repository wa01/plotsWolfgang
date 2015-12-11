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
        parser.add_option("--channel", dest="channel", choices=[ "EE", "MuMu", "EMu" ], default=None )
        ( self.options, args ) = parser.parse_args(argv)
        assert len(args)==0

        if self.options.splitChannels:
            self.flavours = [ "", "EE", "MuMu", "EMu" ]
        else:
            self.flavours = [ "" ]

        for flv in self.flavours:
            self.addVariable("flow"+flv,3,-0.5,2.5,'b')
            self.addVariable("ngenLep"+flv,5,-0.5,4.5,'b')
            self.addVariable("ngenLepFromTau"+flv,5,-0.5,4.5,'b')
            self.addVariable("ngenTau"+flv,5,-0.5,4.5,'b')
            self.addVariable("nTightLep"+flv,10,-0.5,9.5,'u')
            self.addVariable("nVetoLep"+flv,10,-0.5,9.5,'u')
            self.addVariable("wrongCharge"+flv,2,-0.5,1.5,'b')
            self.addVariable("flavourCombination"+flv,3,-0.5,2.5,'b')
            self.addVariable("ngenLep2l"+flv,5,-0.5,4.5,'b')
            self.addVariable("ngenLepFromTau2l"+flv,5,-0.5,4.5,'b')
            self.addVariable("ngenTau2l"+flv,5,-0.5,4.5,'b')
            self.addVariable("nTightLep2l"+flv,10,-0.5,9.5,'u')
            self.addVariable("nVetoLep2l"+flv,10,-0.5,9.5,'u')
            self.addVariable("massTT"+flv,60,0.,120.,'b')
            self.addVariable("massTV"+flv,60,0.,120.,'b')
            self.addVariable("IncRegsTT"+flv,2*5+1,-5.5,5.5,'b')
            self.addVariable("IncRegsTV"+flv,2*5+1,-5.5,5.5,'b')
            nr = len(RA40bSelection.regions.keys())
            self.addVariable("wCSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("tt0bCSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("tt1bCSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("tt2bCSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')

            self.addCutFlow(["all", "oneTight", "dilepton", \
                                 "preselection", ],nameFlow="DefaultCutFlow"+flv)

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

        category = None
        self.passedCutByCategory("all",category,w)

        self.selection.set(eh)
        nTight = len(self.selection.tightLeptons)
        nVeto = len(self.selection.vetoLeptons)

        if not sample.isData():
            ngenLep = eh.get("ngenLep")
            ngenTau = eh.get("ngenTau")
            ngenLepFromTau = eh.get("ngenLepFromTau")
                
            self.fill1DByCategory("ngenLep",category,ngenLep,w)
            self.fill1DByCategory("ngenTau",category,ngenTau,w)
            self.fill1DByCategory("ngenLepFromTau",category,ngenLepFromTau,w)
                    
        self.fill1DByCategory("nTightLep",category,nTight,w)
        self.fill1DByCategory("nVetoLep",category,nVeto,w)

        if nTight>0:
            self.passedCutByCategory("oneTight",category,w)

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
        self.fill1DByCategory("wrongCharge",category,wrongCharge,w)
        if idxLep2==None:
            return

        if abs(pdgLep1)==11 and abs(pdgLep2)==11:
            category = "EE"
        elif abs(pdgLep1)==13 and abs(pdgLep2)==13:
            category = "MuMu"
        elif abs(pdgLep1)==11 and abs(pdgLep2)==13:
            category = "EMu"
        elif abs(pdgLep1)==13 and abs(pdgLep2)==11:
            category = "EMu"
        self.fill1DByCategory("flavourCombination",category,self.flavours.index(category)-1,w)
        self.passedCutByCategory("dilepton",category,w)

        if self.options.channel!=None and category!=self.options.channel:
            return

        if not sample.isData():
            self.fill1DByCategory("ngenLep2l",category,ngenLep,w)
            self.fill1DByCategory("ngenTau2l",category,ngenTau,w)
            self.fill1DByCategory("ngenLepFromTau2l",category,ngenLepFromTau,w)
                    
        self.fill1DByCategory("nTightLep2l",category,nTight,w)
        self.fill1DByCategory("nVetoLep2l",category,nVeto,w)
            
        if not self.selection.preselection():
            return

        self.passedCutByCategory("preselection",category,w)

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
        self.fill1DByCategory(hn,category,mll,w)

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
            self.fill1DByCategory(hn,category,incRegSign*ir,w)

        if idxLep2<nTight:
            #
            # W+jets region:
            #
            wRs = self.selection.wRegions()
            for r in wRs:
                assert r[0]=="C" or r[0]=="S"
                if r[0]=="C":
                    self.fill1DByCategory("wCSRs",category,-int(r[2:]),w)
                else:
                    self.fill1DByCategory("wCSRs",category,int(r[2:]),w)
            #
            # ttbar region:
            #
            for ib in [ 0, 1, 2 ]:
                ttRs = self.selection.ttRegions(ib)
                for r in ttRs:
                    assert r[0]=="C" or r[0]=="S"
                    hn = "tt" + str(ib) + "bCSRs"
                    if r[0]=="C":
                        self.fill1DByCategory(hn,category,-int(r[2:]),w)
                    else:
                        self.fill1DByCategory(hn,category,int(r[2:]),w)
            



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
        
