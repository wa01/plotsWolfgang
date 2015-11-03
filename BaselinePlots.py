import ROOT
import math
import time
from optparse import OptionParser
from PlotsBase import *
from EventHelper import EventHelper
from LeptonUtilities import *
from KinematicUtilities import deltaR
from PreselectionTools import *

class BaselinePlots(PlotsBase):

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

        if self.options.splitChannels:
            self.flavours = [ "", "Ele", "Mu" ]
        else:
            self.flavours = [ "" ]
        for flv in self.flavours:
            self.addVariable("before"+flv,1,0.5,1.5,'b')
            self.addVariable("nTightLep"+flv,10,-0.5,9.5,'u')
            self.addVariable("nVetoLep"+flv,10,-0.5,9.5,'u')
            self.addVariable("nJet30"+flv,20,-0.5,19.5,'l')
            self.addVariable("ptJet1"+flv,100,0.,1000.,'l')
            self.addVariable("ptJet2"+flv,100,0.,1000.,'l')
            self.addVariable("ht"+flv,100,0.,2500.,'l')
            self.addVariable("lt"+flv,100,0.,2500.,'l')
            self.addVariable("nBJet"+flv,10,-0.5,9.5,'b')
            self.addVariable("dPhi"+flv,63,0.,3.15,'l')
            self.addVariable("ptLep"+flv,100,0.,1000.,'b')
            self.addVariable("isoLep"+flv,100,0.,0.2,'u')
            self.addVariable("dxyLep"+flv,100,0.,0.05,'u')
            self.addVariable("dzLep"+flv,100,0.,0.20,'u')
            self.addVariable("sip3dLep"+flv,100,0.,10.,'u')
            self.addVariable("jet1DRLep"+flv,120,0.,6.,'u')
            self.addVariable("jet2DRLep"+flv,120,0.,6.,'u')
            self.addVariable("met"+flv,100,0.,1000.,'b')
            self.addVariable("metPhi"+flv,90,-math.pi,math.pi,'b')
            self.addVariable("dPhiMetJet1"+flv,63,0.,3.15,'l')
            self.addVariable("dPhiMetJet2"+flv,63,0.,3.15,'l')
            nr = len(RA40bSelection.regions.keys())
            self.addVariable("wCSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("tt0bCSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("tt1bCSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("tt2bCSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("CSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("after"+flv,1,0.5,1.5,'b')

            self.addCutFlow(["all","ht500","oneTightLep","noVetoLep","njet4","jet2Pt80", \
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
        self.passedCutByFlavour("all",pdgLep,w)

        ht = eh.get("htJet30j")
        self.fill1DByFlavour("ht",pdgLep,ht,w)
        if ht<500:
            return
        self.passedCutByFlavour("ht500",pdgLep,w)

        tightLeps = tightLeptons(eh)
        nTightLep = len(tightLeps)
        self.fill1DByFlavour("nTightLep",pdgLep,nTightLep,w)
        if nTightLep!=1:
            return
        self.passedCutByFlavour("oneTightLep",pdgLep,w)

        # now lepton flavour is defined
        if len(self.flavours)>=2:
            pdgLep = eh.get("LepGood_pdgId")[tightLeps[0]]

        vetoLeps = vetoLeptons(eh)
        nVetoLep = len(vetoLeps)
        self.fill1DByFlavour("nVetoLep",pdgLep,nVetoLep,w)
        if nVetoLep>0:
            return
        self.passedCutByFlavour("noVetoLep",pdgLep,w)

        goodJs = goodJets(eh)
        nGoodJs = len(goodJs)
        self.fill1DByFlavour("nJet30",pdgLep,nGoodJs,w)
        if nGoodJs<4:
            return
        self.passedCutByFlavour("njet4",pdgLep,w)

        self.fill1DByFlavour("ptJet1",pdgLep,eh.get("Jet_pt")[goodJs[0]],w)
        self.fill1DByFlavour("ptJet2",pdgLep,eh.get("Jet_pt")[goodJs[1]],w)
        if eh.get("Jet_pt")[goodJs[1]]<80.:
            return
        self.passedCutByFlavour("jet2Pt80",pdgLep,w)

        lt = eh.get("met_pt") + eh.get("LepGood_pt")[tightLeps[0]]
        self.fill1DByFlavour("lt",pdgLep,lt,w)
        if lt<250:
            return
        self.passedCutByFlavour("lt250",pdgLep,w)

        if eh.get("nBJetMedium30")==0:
            self.passedCutByFlavour("nb0",pdgLep,w)
        else:
            self.passedCutByFlavour("nbge1",pdgLep,w)

        self.selection.set(eh)
        lt2 = self.selection.wkin.lt()
        assert abs(lt2-lt)/lt<0.00001
        dphi = abs(self.selection.wkin.dPhi())
        self.fill1DByFlavour("dPhi",pdgLep,abs(dphi),w)

        if nGoodJs<5:
            return

        self.fill1DByFlavour("nBJet",pdgLep,eh.get("nBJetMedium30"),w)
        self.fill1DByFlavour("ptLep",pdgLep,eh.get("LepGood_pt")[tightLeps[0]],w)
        self.fill1DByFlavour("isoLep",pdgLep,eh.get("LepGood_miniRelIso")[tightLeps[0]],w)
        self.fill1DByFlavour("dxyLep",pdgLep,eh.get("LepGood_dxy")[tightLeps[0]],w)
        self.fill1DByFlavour("dzLep",pdgLep,eh.get("LepGood_dz")[tightLeps[0]],w)
        self.fill1DByFlavour("sip3dLep",pdgLep,eh.get("LepGood_sip3d")[tightLeps[0]],w)
        jetDRLep = deltaR(eh.get("Jet_phi")[goodJs[0]],eh.get("Jet_eta")[goodJs[0]],
                          eh.get("LepGood_phi")[tightLeps[0]],eh.get("LepGood_eta")[tightLeps[0]])
        self.fill1DByFlavour("jet1DRLep",pdgLep,jetDRLep,w)
        jetDRLep = deltaR(eh.get("Jet_phi")[goodJs[1]],eh.get("Jet_eta")[goodJs[1]],
                          eh.get("LepGood_phi")[tightLeps[0]],eh.get("LepGood_eta")[tightLeps[0]])
        self.fill1DByFlavour("jet2DRLep",pdgLep,jetDRLep,w)
        self.fill1DByFlavour("met",pdgLep,eh.get("met_pt"),w)
        self.fill1DByFlavour("metPhi",pdgLep,eh.get("met_phi"),w)
        jetPhi = eh.get("Jet_phi")[goodJs[0]]
        self.fill1DByFlavour("dPhiMetJet1",pdgLep,abs(deltaPhi(eh.get("met_phi"),jetPhi)),w)
        jetPhi = eh.get("Jet_phi")[goodJs[1]]
        self.fill1DByFlavour("dPhiMetJet2",pdgLep,abs(deltaPhi(eh.get("met_phi"),jetPhi)),w)
#        assert eh.get("nBJetMedium30")==self.selection.nBJets
#        if eh.get("nBJetMedium30")>0:
#            return
#        assert self.selection.preselection()
        #
        # W+jets region:
        #
        wRs = self.selection.wRegions()
        for r in wRs:
            assert r[0]=="C" or r[0]=="S"
            if r[0]=="C":
                self.fill1DByFlavour("wCSRs",pdgLep,-int(r[2:]),w)
            else:
                self.fill1DByFlavour("wCSRs",pdgLep,int(r[2:]),w)
        #
        # ttbar region:
        #
        for ib in [ 0, 1, 2 ]:
            ttRs = self.selection.ttRegions(ib)
            for r in ttRs:
                assert r[0]=="C" or r[0]=="S"
                hn = "tt" + str(ib) + "bCSRs"
                if r[0]=="C":
                    self.fill1DByFlavour(hn,pdgLep,-int(r[2:]),w)
                else:
                    self.fill1DByFlavour(hn,pdgLep,int(r[2:]),w)
            
            
        region = self.selection.region()
#        if region==None:
#            self.fill1DByFlavour("CSRs",pdgLep,0.,w)
#            print "*Rejected: ",eh.get("nBJetMedium30"),self.selection.preselection(),self.selection.__dict__
        if region!=None:
            assert region[0]=="C" or region[0]=="S"
            if region[0]=="C":
                self.fill1DByFlavour("CSRs",pdgLep,-int(region[2:]),w)
            else:
                self.fill1DByFlavour("CSRs",pdgLep,int(region[2:]),w)
            self.passedCutByFlavour(region,pdgLep,w,nameFlow="CSRflow")
            
        self.fill1DByFlavour("after",pdgLep,1,w)

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
        
