import ROOT
import math
import time
from optparse import OptionParser
from PlotsBase import *
from EventHelper import EventHelper
from LeptonUtilities import *
from KinematicUtilities import deltaR


class BaselinePlots(PlotsBase):

    def __init__(self,name,preselection=None,elist=None,elistBase="./elists",rebin=None,argv=[]):
        PlotsBase.__init__(self,name,preselection,elist=elist,elistBase=elistBase,rebin=rebin)
        self.histogramList = { }
        curdir = ROOT.gDirectory
        if not ROOT.gROOT.Get(name):
            ROOT.gROOT.mkdir(name)
        ROOT.gROOT.cd(name)

        parser = OptionParser()
#        parser.add_option("--channel", dest="channel",  help="channel", choices=[ "mu", "el" ], default="mu")
#        parser.add_option("--metht", dest="metht",  help="MET/HT cut", type=float, default=150.)
#        parser.add_option("--isrPt", dest="isrPt",  help="isrJetPt cut", type=float, default=None)
#        parser.add_option("--dm", dest="dm",  help="1/2 width of Z mass window", type=float, default=15.)
#        parser.add_option("--isoCut", dest="isoCut",  help="abs iso cut", type=float, default=None)
#        parser.add_option("--jetPt", dest="jetPt",  help="leading jet pt cut", type=float, default=None)
#        parser.add_option("--dyReweighting", dest="dyReweighting", help="DY ISR reweighting", type="int", default=0)
#        parser.add_option("--bWeights", dest="bWeights", help="b-tag reweighting", choices=[ "count", "MC", "SF", "mixed" ], default=None)
        ( self.options, args ) = parser.parse_args(argv)
        assert len(args)==0

        # self.flavours = [ "" ]
        self.flavours = [ "Ele", "Mu" ]
        for flv in self.flavours:
            self.addVariable("before"+flv,1,0.5,1.5,'b')
            self.addVariable("nTightLep"+flv,10,-0.5,9.5,'u')
            self.addVariable("nVetoLep"+flv,10,-0.5,9.5,'u')
            self.addVariable("nJet30"+flv,20,-0.5,19.5,'l')
            self.addVariable("ptJet1"+flv,100,0.,1000.,'l')
            self.addVariable("ptJet2"+flv,100,0.,1000.,'l')
            self.addVariable("ht"+flv,100,0.,2500.,'l')
            self.addVariable("lt"+flv,100,0.,2500.,'l')
            self.addVariable("after"+flv,1,0.5,1.5,'b')

#        self.charges = [ "Minus", "Plus" ]
#        self.charges = [ "" ]
#        for sign in self.charges:
#            self.addVariable("isrJetPt"+sign,100,0.,1000.,'l')
#            self.addVariable("isrJetEta"+sign,50,0.,5.,'u')
#            self.addVariable("jet1Pt"+sign,100,0.,1000.,'u')
#            self.addVariable("jet1Eta"+sign,50,0.,5.,'u')
#            self.addVariable("jet1BTag"+sign,100,-1.,1.,'u')
#            self.addVariable("jet2Pt"+sign,100,0.,1000.,'u')
#            self.addVariable("jet2Eta"+sign,50,0.,5.,'u')
#            self.addVariable("jet2BTag"+sign,100,-1.,1.,'u')
#            self.addVariable("jetPtRatio"+sign,50,0.,1.,'u')
#            self.addVariable("njet60"+sign,10,-0.5,9.5,'u')
#            self.addVariable("njet"+sign,20,-0.5,19.5,'u')
#            self.addVariable("nbMedium"+sign,20,-0.5,19.5,'u')
#            self.addVariable("nbMedium60"+sign,20,-0.5,19.5,'u')
#            self.addVariable("nbLoose"+sign,20,-0.5,19.5,'u')
#            self.addVariable("nbLoose60"+sign,20,-0.5,19.5,'u')
#            self.addVariable("nmu"+sign,10,-0.5,9.5,'u')
#            self.addVariable("met"+sign,100,0.,1000.,'l')
#            self.addVariable("metParZ"+sign,100,-100.,100.,'b')
#            self.addVariable("metPerpZ"+sign,100,-100.,100.,'b')
#            self.addVariable("metParJet"+sign,100,-100.,100.,'b')
#            self.addVariable("metPerpJet"+sign,100,-100.,100.,'b')
#            self.addVariable("ht"+sign,100,0.,1000.,'l')
#            self.addVariable("zm"+sign,100,0.,500.,'b')
#            self.addVariable("zpt"+sign,200,0.,1000.,'b')
#            self.addVariable("zptmod"+sign,200,0.,1000.,'b')
#            self.addVariable("zeta"+sign,50,0.,5.,'b')
#            self.addVariable("zptmodht"+sign,24,0.,1000.,'b',
#                             binEdges=range(0,100,10)+range(100,300,25)+range(300,450,50)+[450,550,650,1000])
#            self.addVariable("mt"+sign,50,0.,200.,'u')
#            self.addVariable("qq"+sign,3,-1.,1.,'b')
#            for i in range(2):
#                self.addVariable("hard"+self.leptonPrefixCap+str(i)+"Pt"+sign,100,0.,500.,'b')
#                self.addVariable("hard"+self.leptonPrefixCap+str(i)+"Eta"+sign,60,0.,3.,'b')
#                self.addVariable("hard"+self.leptonPrefixCap+str(i)+"RelIso"+sign,100,0.,0.25,'b')
#                self.addVariable("hard"+self.leptonPrefixCap+str(i)+"Log10Dxy"+sign,150,-4.,-1.,'b')
#                self.addVariable("hard"+self.leptonPrefixCap+str(i)+"Log10Dz"+sign,100,-4.,0.,'b')
##                self.addVariable("hard"+self.leptonPrefixCap+str(i)+"Idx"+sign,10,0.,10.,'b')
#            self.addVariable("softMuPt"+sign,20,0.,50.,'u')
#            self.addVariable("softMuEta"+sign,60,0.,3.,'u')
#            self.addVariable("softMuRelIso"+sign,100,0.,10.,'u')
#            self.addVariable("softMuIso"+sign,100,0.,250.,'u')
#            self.addVariable("softMuLog10Dxy"+sign,150,-4.,-1.,'u')
#            self.addVariable("softMuLog10Dz"+sign,100,-4.,0.,'u')
#            self.addVariable("softMuQ"+sign,2,-20.,20.,'u')
#            self.addVariable("softMuDRjet"+sign,100,0.,10.,'u')
#            self.addVariable("softMuDRjetPt"+sign,100,0.,1000.,'u')
#            self.addVariable("softMuDRjetBTag"+sign,50,-1.,1.,'u')
#            self.addVariable("zmSoftMu"+sign,100,0.,500.,'b')
#            self.addVariable("zptSoftMu"+sign,200,0.,1000.,'b')
#            self.addVariable("zptmodSoftMu"+sign,200,0.,1000.,'b')
#            self.addVariable("zetaSoftMu"+sign,50,0.,5.,'b')
#            self.addVariable("zptmodhtSoftMu"+sign,24,0.,1000.,'b',
#                             binEdges=range(0,100,10)+range(100,300,25)+range(300,450,50)+[450,550,650,1000])
#            self.addVariable("isrJetPtSoftMu"+sign,100,0.,1000.,'l')
#            self.addVariable("jet1PtSoftMu"+sign,100,0.,1000.,'u')
#            self.addVariable("jet1EtaSoftMu"+sign,50,0.,5.,'u')
#            self.addVariable("jet1BTagSoftMu"+sign,100,-1.,1.,'u')
#            self.addVariable("njet60SoftMu"+sign,10,-0.5,9.5,'u')
#            self.addVariable("njetSoftMu"+sign,20,-0.5,19.5,'u')
#            self.addVariable("nbMediumSoftMu"+sign,20,-0.5,19.5,'u')
#            self.addVariable("nbMedium60SoftMu"+sign,20,-0.5,19.5,'u')
#            self.addVariable("nbLooseSoftMu"+sign,20,-0.5,19.5,'u')
#            self.addVariable("nbLoose60SoftMu"+sign,20,-0.5,19.5,'u')
#            self.addVariable("nmuSoftMu"+sign,10,-0.5,9.5,'u')
#            self.addVariable("metSoftMu"+sign,100,0.,1000.,'l')


#            self.addVariablePair("zptmod",50,0.,1000.,"ht",50,0.,1000.,suffix=sign)
#            self.addVariablePair("zptmodht",50,0.,1000.,"softMuIso",50,0.,250.,suffix=sign)

#            self.addVariablePair("isrJetPt",50,0.,1000.,"thirdMuon",2,-0.5,1.5,suffix=sign)
#            self.addVariablePair("njet60",10,-0.5,9.5,"thirdMuon",2,-0.5,1.5,suffix=sign)
#            self.addVariablePair("njet",20,-0.5,19.5,"thirdMuon",2,-0.5,1.5,suffix=sign)
#            self.addVariablePair("zptmod",50,0.,1000.,"thirdMuon",2,-0.5,1.5,suffix=sign)
#            self.addVariablePair("zptmodht",50,0.,1000.,"thirdMuon",2,-0.5,1.5,suffix=sign)

#            self.addVariablePair("softMuIso",50,0.,100.,"softMuPt",15,5.,20.,suffix=sign)

#        self.addVariable("softDiMuM",150,0.,150.,'b')
        curdir.cd()

    def fill(self,eh,sample,itree):


        self.timers[0].start()
        if self.name!="data":
#            w = eh.get("weight")*sample.downscale*sample.extweight
#            if self.reweightDY:
#                w *= self.reweightClass.isrWeightDY(zpt)
            w = eh.get("xsec")*sample.baseweights[itree]*sample.downscale*sample.extweight
        else:
            w = 1
        self.timers[0].stop()        

        if len(self.flavours)<2:
            pdgLep = None
        else:
            pdgLep = 0
        self.fill1DByFlavour("before",pdgLep,1,w)

        ht = eh.get("htJet30j")
        self.fill1DByFlavour("ht",pdgLep,ht,w)
        if ht<500:
            return

        tightLeps = tightLeptons(eh)
        nTightLep = len(tightLeps)
        self.fill1DByFlavour("nTightLep",pdgLep,nTightLep,w)
        if nTightLep!=1:
            return

        # now lepton flavour is defined
        if len(self.flavours)==2:
            pdgLep = eh.get("LepGood_pdgId")[tightLeps[0]]

        vetoLeps = vetoLeptons(eh)
        nVetoLep = len(vetoLeps)
        self.fill1DByFlavour("nVetoLep",pdgLep,nVetoLep,w)
        if nVetoLep>0:
            return

        goodJs = goodJets(eh)
        nGoodJs = len(goodJs)
        self.fill1DByFlavour("nJet30",pdgLep,nGoodJs,w)
        if nGoodJs<4:
            return

        self.fill1DByFlavour("ptJet1",pdgLep,eh.get("Jet_pt")[goodJs[0]],w)
        self.fill1DByFlavour("ptJet2",pdgLep,eh.get("Jet_pt")[goodJs[1]],w)
        if eh.get("Jet_pt")[goodJs[1]]<80.:
            return

        lt = eh.get("met_pt") + eh.get("LepGood_pt")[tightLeps[0]]
        self.fill1DByFlavour("lt",pdgLep,lt,w)
        if lt<250:
            return
        
        self.fill1DByFlavour("after",pdgLep,1,w)

    def showTimers(self):
        line = ""
        for t in self.timers:
            line += "{0:14.2f}".format(1000000*t.meanTime())
#            line += " " + str(t.meanTime())
        print line
            
    def histograms(self):
        return self.histogramList
        
