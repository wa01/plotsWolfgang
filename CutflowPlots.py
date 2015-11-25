import ROOT
import math
import time
from optparse import OptionParser
from PlotsBase import *
from EventHelper import EventHelper
from LeptonUtilities import *
from KinematicUtilities import deltaR
from PreselectionTools import *

class CutflowPlots(PlotsBase):

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

        if self.options.splitChannels:
            self.flavours = [ "", "Ele", "Mu" ]
        else:
            self.flavours = [ "" ]
        for flv in self.flavours:
            self.addVariable("nTightLep"+flv,10,-0.5,9.5,'u')
            self.addVariable("nVetoLep"+flv,10,-0.5,9.5,'u')
            self.addVariable("nJet30"+flv,20,-0.5,19.5,'l')
            self.addVariable("ptJet1"+flv,100,0.,1000.,'l')
            self.addVariable("ptJet2"+flv,100,0.,1000.,'l')
            self.addVariable("ht"+flv,100,0.,2500.,'l')
            self.addVariable("lt"+flv,100,0.,2500.,'l')
            self.addVariable("nBJet"+flv,10,-0.5,9.5,'b')
            self.addVariable("ptLep"+flv,100,0.,1000.,'b')
            self.addVariable("isoLep"+flv,100,0.,0.2,'u')
            self.addVariable("dxyLep"+flv,100,0.,0.05,'u')
            self.addVariable("dzLep"+flv,100,0.,0.20,'u')
            self.addVariable("sip3dLep"+flv,100,0.,10.,'u')
            self.addVariable("nVert"+flv,50,-0.5,49.5,'b')

            self.addCutFlow(["all","ht500","oneTightLep","noVetoLep","njet5","jet2Pt80", \
                                 "lt250","nb0","nbge1"],"DefaultCutFlow"+flv)
            csrNames = [ ]
            for i in range(13):
                csrNames.append("CR"+str(i+1))
            for i in range(13):
                csrNames.append("SR"+str(i+1))
            self.addCutFlow(csrNames,nameFlow="CSRflow"+flv)

        curdir.cd()

        self.selection = RA40bSelection()

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

        if len(self.flavours)<2:
            pdgLep = None
        else:
            pdgLep = 0
        self.passedCutByFlavour("before",pdgLep,w)

        tightLeps = tightLeptons(eh)
        nTightLep = len(tightLeps)
        self.fill1DByFlavour("nTightLep",pdgLep,nTightLep,w)
        self.fill1DByFlavour("ptLep",pdgLep,eh.get("LepGood_pt")[tightLeps[0]],w)
        self.fill1DByFlavour("isoLep",pdgLep,eh.get("LepGood_miniRelIso")[tightLeps[0]],w)
        self.fill1DByFlavour("dxyLep",pdgLep,eh.get("LepGood_dxy")[tightLeps[0]],w)
        self.fill1DByFlavour("dzLep",pdgLep,eh.get("LepGood_dz")[tightLeps[0]],w)
        self.fill1DByFlavour("sip3dLep",pdgLep,eh.get("LepGood_sip3d")[tightLeps[0]],w)
        if nTightLep!=1:
            return
        self.passedCutByFlavour("oneTightLep",pdgLep,w)

        vetoLeps = vetoLeptons(eh)
        nVetoLep = len(vetoLeps)
        self.fill1DByFlavour("nVetoLep",pdgLep,nVetoLep,w)
        if nVetoLep>0:
            return
        self.passedCutByFlavour("noVetoLep",pdgLep,w)

        # now lepton flavour is defined
        if len(self.flavours)>=2 or self.options.channel!=None:
            pdgLep = eh.get("LepGood_pdgId")[tightLeps[0]]
            if ( self.options.channel=="Ele" and abs(pdgLep)!=11 ) or \
               ( self.options.channel=="Mu" and abs(pdgLep)!=13 ):
                return
        if len(self.flavours)==1:
            pdgLep = None

        goodJs = goodJets(eh)
        nGoodJs = len(goodJs)
        self.fill1DByFlavour("nJet30",pdgLep,nGoodJs,w)
        if nGoodJs<5:
            return
        self.passedCutByFlavour("njet5",pdgLep,w)

        self.fill1DByFlavour("nVert",pdgLep,eh.get("nVert"),w)
        self.fill1DByFlavour("ptJet1",pdgLep,eh.get("Jet_pt")[goodJs[0]],w)
        self.fill1DByFlavour("ptJet2",pdgLep,eh.get("Jet_pt")[goodJs[1]],w)
        if eh.get("Jet_pt")[goodJs[1]]<80.:
            return
        self.passedCutByFlavour("jet2Pt80",pdgLep,w)

        ht = eh.get("htJet30j")
        self.fill1DByFlavour("ht",pdgLep,ht,w)
        if ht<500:
            return
        self.passedCutByFlavour("ht500",pdgLep,w)

        lt = eh.get("met_pt") + eh.get("LepGood_pt")[tightLeps[0]]
        self.fill1DByFlavour("lt",pdgLep,lt,w)
        if lt<250:
            return
        self.passedCutByFlavour("lt250",pdgLep,w)

        nBJets = eh.get("nBJetMedium30")
        self.fill1DByFlavour("nBJet",pdgLep,eh.get("nBJetMedium30"),w)
        if eh.get("nBJetMedium30")==0:
            self.passedCutByFlavour("nb0",pdgLep,w)
        else:
            self.passedCutByFlavour("nbge1",pdgLep,w)


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
        
