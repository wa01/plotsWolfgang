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
        parser.add_option("--channel", dest="channel", choices=[ "Ele", "Mu" ], default=None )
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
            self.addVariable("lp"+flv,100,-5,5,'b')
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
            self.addVariable("nVert"+flv,50,-0.5,49.5,'b')
            nr = len(RA40bSelection.regions.keys())
            self.addVariable("wCSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("tt0bCSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("tt1bCSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("tt2bCSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("CSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("InclusiveRegs"+flv,2*5+1,-5.5,5.5,'b')
            for i in range(5):
                dPhiMin = 0.75
                dPhiEdges = [ 0. ]
                ddPhi = 0.125
                while (dPhiEdges[-1]+ddPhi-dPhiMin)<0.001:
                    dPhiEdges.append(dPhiEdges[-1]+ddPhi)
                ddPhi = 0.25
                while (dPhiEdges[-1]+ddPhi-1.)<0.001:
                    dPhiEdges.append(dPhiEdges[-1]+ddPhi)
                ddPhi = 0.70
                while (dPhiEdges[-1]+ddPhi-3.15)<0.001:
                    dPhiEdges.append(dPhiEdges[-1]+ddPhi)
                self.addVariable("dPhiIncReg"+str(i+1)+flv,len(dPhiEdges)-1, \
                                     dPhiEdges[0],dPhiEdges[-1],'l',binEdges=dPhiEdges)
#                self.addVariable("dPhiIncReg"+str(i+1)+flv,63,0.,3.15,'b')
                self.addVariable("metIncReg"+str(i+1)+flv,50,0.,1000.,'b')
                self.addVariable("dPhiJet1MetIncReg"+str(i+1)+flv,16,0.,3.2,'b')
                self.addVariable("ptLepIncReg"+str(i+1)+flv,50,0.,1000.,'b')
                self.addVariable("isoLepIncReg"+str(i+1)+flv,40,0.,0.2,'b')
                self.addVariable("lpIncReg"+str(i+1)+flv,40,-2.,2.,'b')
            for i in range(nr):
#                rname = 'R{0:02d}'.format(i+1)
                dPhiMin = RA40bSelection.regions["R"+str(i+1)][-1]
                dPhiEdges = [ 0. ]
                ddPhi = 0.125
                while (dPhiEdges[-1]+ddPhi-dPhiMin)<0.001:
                    dPhiEdges.append(dPhiEdges[-1]+ddPhi)
                ddPhi = 0.25
                while (dPhiEdges[-1]+ddPhi-1.)<0.001:
                    dPhiEdges.append(dPhiEdges[-1]+ddPhi)
                ddPhi = 0.70
                while (dPhiEdges[-1]+ddPhi-3.15)<0.001:
                    dPhiEdges.append(dPhiEdges[-1]+ddPhi)
#                print dPhiEdges
#                dPhiEdges = [ j/10. for j in range(10) ]
#                dPhiEdges.extend([ 1.35, 1.80, 2.25, 2.70, 3.15 ])
                self.addVariable("dPhiR"+"{0:02d}".format(i+1)+flv,len(dPhiEdges)-1, \
                                     dPhiEdges[0],dPhiEdges[-1],'l', \
                                     binEdges=dPhiEdges)
            self.addVariable("after"+flv,1,0.5,1.5,'b')

            self.addCutFlow(["all","ht500","oneTightLep","noVetoLep","njet4","jet2Pt80", \
                                 "lt250","nb0","nbge1"],nameFlow="DefaultCutFlow"+flv)
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
        if len(self.flavours)>=2 or self.options.channel!=None:
            pdgLep = eh.get("LepGood_pdgId")[tightLeps[0]]
            if ( self.options.channel=="Ele" and abs(pdgLep)!=11 ) or \
               ( self.options.channel=="Mu" and abs(pdgLep)!=13 ):
                return
        if len(self.flavours)==1:
            pdgLep = None
        lepPt = eh.get("LepGood_pt")[tightLeps[0]]

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

        jet1Pt = eh.get("Jet_pt")[goodJs[0]]
        jet2Pt = eh.get("Jet_pt")[goodJs[1]]

        self.fill1DByFlavour("nVert",pdgLep,eh.get("nVert"),w)
        self.fill1DByFlavour("ptJet1",pdgLep,jet1Pt,w)
        self.fill1DByFlavour("ptJet2",pdgLep,jet2Pt,w)
        if jet2Pt<80.:
            return
        self.passedCutByFlavour("jet2Pt80",pdgLep,w)

        met = eh.get("met_pt")
        metPhi = eh.get("met_phi")

        lt = met + lepPt
        self.fill1DByFlavour("lt",pdgLep,lt,w)
        if lt<250:
            return
        self.passedCutByFlavour("lt250",pdgLep,w)

        nBJets = eh.get("nBJetMedium30")
        if nBJets==0:
            self.passedCutByFlavour("nb0",pdgLep,w)
        else:
            self.passedCutByFlavour("nbge1",pdgLep,w)

        self.selection.set(eh)
        lt2 = self.selection.wkin.lt()
        assert abs(lt2-lt)/lt<0.00001
        dphi = abs(self.selection.wkin.dPhi())
        self.fill1DByFlavour("dPhi",pdgLep,abs(dphi),w)
        self.fill1DByFlavour("lp",pdgLep,self.selection.wkin.lp(),w)

        incRegSign = -1 if dphi<0.75 else +1
        incRegs = [ 1 ]
#        self.fill1DByFlavour("InclusiveRegs",pdgLep,incRegSign*1,w)
#        self.fill1DByFlavour("dPhiIncReg1",pdgLep,dphi,w)
        if nGoodJs>=3 and nGoodJs<=4 and nBJets==0:
            incRegs.append(2)
#            self.fill1DByFlavour("InclusiveRegs",pdgLep,incRegSign*2,w)
#            self.fill1DByFlavour("dPhiIncReg2",pdgLep,dphi,w)
        if nGoodJs>=4 and nGoodJs<=5 and nBJets<3:
            incRegs.append(3+min(nBJets,2))
#            self.fill1DByFlavour("InclusiveRegs",pdgLep,incRegSign*(3+min(nBJets,2)),w)
#            self.fill1DByFlavour("dPhiIncReg"+str(min(nBJets,2)+3),pdgLep,dphi,w)
        for ir in incRegs:
            self.fill1DByFlavour("InclusiveRegs",pdgLep,incRegSign*ir,w)
            self.fill1DByFlavour("dPhiIncReg"+str(ir),pdgLep,dphi,w)
            self.fill1DByFlavour("metIncReg"+str(ir),pdgLep,met,w)
            jetPhi = eh.get("Jet_phi")[goodJs[0]]
            self.fill1DByFlavour("dPhiJet1MetIncReg"+str(ir),pdgLep,abs(deltaPhi(metPhi,jetPhi)),w)
            self.fill1DByFlavour("ptLepIncReg"+str(ir),pdgLep,lepPt,w)
            self.fill1DByFlavour("isoLepIncReg"+str(ir),pdgLep,eh.get("LepGood_miniRelIso")[tightLeps[0]],w)
            self.fill1DByFlavour("lpIncReg"+str(ir),pdgLep,self.selection.wkin.lp(),w)

#        if nGoodJs<5:
#            return

        self.fill1DByFlavour("nBJet",pdgLep,nBJets,w)
        self.fill1DByFlavour("ptLep",pdgLep,lepPt,w)
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
        self.fill1DByFlavour("metPhi",pdgLep,metPhi,w)
        jetPhi = eh.get("Jet_phi")[goodJs[0]]
        self.fill1DByFlavour("dPhiMetJet1",pdgLep,abs(deltaPhi(metPhi,jetPhi)),w)
        jetPhi = eh.get("Jet_phi")[goodJs[1]]
        self.fill1DByFlavour("dPhiMetJet2",pdgLep,abs(deltaPhi(metPhi,jetPhi)),w)
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
            ir = int(region[2:])
            if region[0]=="C":
                self.fill1DByFlavour("CSRs",pdgLep,-ir,w)
            else:
                self.fill1DByFlavour("CSRs",pdgLep,ir,w)
            self.fill1DByFlavour("dPhiR"+"{0:02d}".format(ir),pdgLep,abs(dphi),w)
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
        
