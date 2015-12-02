import ROOT
import math
import time
from optparse import OptionParser
from PlotsBase import *
from EventHelper import EventHelper
from LeptonUtilities import *
from KinematicUtilities import deltaR
from PreselectionTools import *

class LostLeptonPlots(PlotsBase):

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
            self.addVariable("ngenLep"+flv,5,-0.5,4.5,'b')
            self.addVariable("ngenLepFromTau"+flv,5,-0.5,4.5,'b')
            self.addVariable("ngenTau"+flv,5,-0.5,4.5,'b')
            self.addVariable("nTightLep"+flv,10,-0.5,9.5,'u')
            self.addVariable("nVetoLep"+flv,10,-0.5,9.5,'u')
            self.addVariable("matchId"+flv,61,-30.5,30.5,'b')
            self.addVariable("typeGenLepMatch"+flv,3,-0.5,2.5,'b')
            self.addVariable("drGenLepMatch"+flv,100,0.,10.,'b')
            self.addVariable("ptrGenLepMatch"+flv,100,0.,2.5,'b')
            self.addVariable("nJet30"+flv,20,-0.5,19.5,'l')
            self.addVariable("ptJet1"+flv,100,0.,1000.,'l')
            self.addVariable("ptJet2"+flv,100,0.,1000.,'l')
            self.addVariable("ht"+flv,100,0.,2500.,'l')
            self.addVariable("lt"+flv,100,0.,2500.,'l')
            self.addVariable("ptLep"+flv,100,0.,1000.,'b')
            nr = len(RA40bSelection.regions.keys())
            self.addVariable("CSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')

            csrCategories = [ "had", "tight", "lt", "matched", "tauhad", "tt", "tv", "tInEff", "tOutOfAcc", "other" ]
            self.addCutFlow(csrCategories,nameFlow="DefaultCutFlow"+flv)
            for i in range(nr):
                name = "CR"+str(i+1)
                self.addCutFlow(csrCategories,nameFlow=name+flv)
            for i in range(nr):
                name = "SR"+str(i+1)
                self.addCutFlow(csrCategories,nameFlow=name+flv)

        curdir.cd()

        self.selection = RA40bSelection(reqNVetoLep=(0,None))

    def closestMatch(self,phiRef,etaRef,phis,etas):
        minDr = 999999.
        minIdx = None
        for i in range(len(phis)):
            dr = deltaR(phiRef,etaRef,phis[i],etas[i])
            if dr<minDr:
                minDr = dr
                minIdx = i
        return (minDr, minIdx)

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

        ngenLep = eh.get("ngenLep")
        ngenTau = eh.get("ngenTau")
        if (ngenLep+ngenTau)!=2:
            return
        ngenLepFromTau = eh.get("ngenLepFromTau")
                
        ht = eh.get("htJet30j")
        if ht<500:
            return

        goodJs = goodJets(eh)
        nGoodJs = len(goodJs)
        if nGoodJs<4:
            return

        jet2Pt = eh.get("Jet_pt")[goodJs[1]]
        if jet2Pt<80.:
            return
        jet1Pt = eh.get("Jet_pt")[goodJs[0]]
 
        self.passedCutByFlavour("had",pdgLep,w)

        self.fill1DByFlavour("ht",pdgLep,ht,w)
        self.fill1DByFlavour("nJet30",pdgLep,nGoodJs,w)
        self.fill1DByFlavour("ptJet1",pdgLep,jet1Pt,w)
        self.fill1DByFlavour("ptJet2",pdgLep,jet2Pt,w)

        tightLeps = tightLeptons(eh)
        nTightLep = len(tightLeps)
        self.fill1DByFlavour("nTightLep",pdgLep,nTightLep,w)
        if nTightLep==0 or nTightLep>2:
            return

        # now lepton flavour is defined
        if len(self.flavours)>=2 or self.options.channel!=None:
            pdgLep = eh.get("LepGood_pdgId")[tightLeps[0]]
            if ( self.options.channel=="Ele" and abs(pdgLep)!=11 ) or \
               ( self.options.channel=="Mu" and abs(pdgLep)!=13 ):
                return
        if len(self.flavours)==1:
            pdgLep = None
        self.passedCutByFlavour("tight",pdgLep,w)


        lepPt = eh.get("LepGood_pt")[tightLeps[0]]
        met = eh.get("met_pt")
        lt = met + lepPt
        self.fill1DByFlavour("lt",pdgLep,lt,w)
        if lt<250:
            return
        self.passedCutByFlavour("lt",pdgLep,w)

        self.fill1DByFlavour("ngenLep",pdgLep,ngenLep,w)
        self.fill1DByFlavour("ngenTau",pdgLep,ngenTau,w)
        self.fill1DByFlavour("ngenLepFromTau",pdgLep,ngenLepFromTau,w)
                    
        #
        # match
        #

        lepPhis = eh.get("LepGood_phi")
        lepEtas = eh.get("LepGood_eta")
        genLepPhis = eh.get("genLep_phi")
        genLepEtas = eh.get("genLep_eta")
        matchLep = self.closestMatch(lepPhis[tightLeps[0]],lepEtas[tightLeps[0]],genLepPhis,genLepEtas)
        genLepFromTauPhis = eh.get("genLepFromTau_phi")
        genLepFromTauEtas = eh.get("genLepFromTau_eta")
        matchLepFromTau = self.closestMatch(lepPhis[tightLeps[0]],lepEtas[tightLeps[0]],
                                            genLepFromTauPhis,genLepFromTauEtas)
        matchCollection = None
        matchIndex = None
        if matchLep[1]!=None or matchLepFromTau[1]!=None:
            if matchLep[0]<matchLepFromTau[0]:
                self.fill1DByFlavour("drGenLepMatch",pdgLep,matchLep[0],w)
                if matchLep[0]<0.3:
                    self.fill1DByFlavour("typeGenLepMatch",pdgLep,1,w)
                    ptRatio = lepPt/eh.get("genLep_pt")[matchLep[1]]
                    self.fill1DByFlavour("ptrGenLepMatch",pdgLep,ptRatio,w)
                    matchCollection = "genLep"
                    matchIndex = matchLep[1]
            else:
                self.fill1DByFlavour("drGenLepMatch",pdgLep,matchLepFromTau[0],w)
                if matchLepFromTau[0]<0.3:
                    self.fill1DByFlavour("typeGenLepMatch",pdgLep,2,w)
                    ptRatio = lepPt/eh.get("genLepFromTau_pt")[matchLepFromTau[1]]
                    self.fill1DByFlavour("ptrGenLepMatch",pdgLep,ptRatio,w)
                    matchCollection = "genLepFromTau"
                    matchIndex = matchLepFromTau[1]
        if matchCollection==None:
            self.fill1DByFlavour("typeGenLepMatch",pdgLep,0,w)
            return
        self.passedCutByFlavour("matched",pdgLep,w)
        self.fill1DByFlavour("matchId",pdgLep,eh.get("LepGood_mcMatchId")[tightLeps[0]],w)

        self.fill1DByFlavour("ptLep",pdgLep,lepPt,w)

        vetoLeps = vetoLeptons(eh)
        nVetoLep = len(vetoLeps)
        self.fill1DByFlavour("nVetoLep",pdgLep,nVetoLep,w)

        cat = None
        if ngenTau>ngenLepFromTau:
            cat = "tauhad"
        elif nTightLep==2:
            cat = "tt"
        elif nVetoLep>0:
            cat = "tv"
        else:
            genLepInAcc = False
            genLepOutOfAcc = False
            mIdx = matchIndex if matchCollection=="genLep" else None
            genLepPts = eh.get("genLep_pt")
            for i in range(ngenLep):
                if mIdx==None or not i==mIdx:
                    if genLepPts[i]>25. and abs(genLepEtas[i])<2.4:
                        genLepInAcc = True
                    else:
                        genLepOutOfAcc = True
            mIdx = matchIndex if matchCollection=="genLepFromTau" else None
            genLepFromTauPts = eh.get("genLepFromTau_pt")
            for i in range(ngenLepFromTau):
                if mIdx==None or not i==mIdx:
                    if genLepFromTauPts[i]>25. and abs(genLepFromTauEtas[i])<2.4:
                        genLepInAcc = True
                    else:
                        genLepOutOfAcc = True
            if genLepInAcc:
                cat = "tInEff"
            elif genLepOutOfAcc:
                cat = "tOutOfAcc"
            else:
                cat = "other"
#                print "Category: other"
#                print "  Tight leptons (pdgId,pt,eta,phi,matchId):"
#                print "     matchCollection = ",matchCollection," index = ",matchIndex
#                for i in tightLeps:
#                    print "    {0:3d} {1:6.1f} {2:6.2f} {3:6.2f} {4:3d}".format(eh.get("LepGood_pdgId")[i], \
#                                                                             eh.get("LepGood_pt")[i], \
#                                                                             eh.get("LepGood_eta")[i], \
#                                                                             eh.get("LepGood_phi")[i], \
#                                                                             eh.get("LepGood_mcMatchId")[i])
#                print "  Veto leptons (pdgId,pt,eta,phi,matchId):"
#                for i in vetoLeps:
#                    print "    {0:3d} {1:6.1f} {2:6.2f} {3:6.2f} {4:3d}".format(eh.get("LepGood_pdgId")[i], \
#                                                                             eh.get("LepGood_pt")[i], \
#                                                                             eh.get("LepGood_eta")[i], \
#                                                                             eh.get("LepGood_phi")[i], \
#                                                                             eh.get("LepGood_mcMatchId")[i])
#                print "  #genLep, genLepFromTau, genTau = ",ngenLep,ngenLepFromTau,ngenTau
#                print "  genLep (pdgId,pt,eta,phi):"
#                for i in range(ngenLep):
#                    print "    {0:3d} {1:6.1f} {2:6.2f} {3:6.2f}".format(eh.get("genLep_pdgId")[i], \
#                                                                             eh.get("genLep_pt")[i], \
#                                                                             eh.get("genLep_eta")[i], \
#                                                                             eh.get("genLep_phi")[i])
#                print "  genLepFromTau (pdgId,pt,eta,phi):"
#                for i in range(ngenLepFromTau):
#                    print "    {0:3d} {1:6.1f} {2:6.2f} {3:6.2f}".format(eh.get("genLepFromTau_pdgId")[i], \
#                                                                             eh.get("genLepFromTau_pt")[i], \
#                                                                             eh.get("genLepFromTau_eta")[i], \
#                                                                             eh.get("genLepFromTau_phi")[i])
        self.selection.set(eh)
        region = self.selection.region()
        if region!=None:
            assert region[0]=="C" or region[0]=="S"
            ir = int(region[2:])
#            if region[0]=="C":
#                self.fill1DByFlavour("CSRs",pdgLep,-ir,w)
#            else:
#                self.fill1DByFlavour("CSRs",pdgLep,ir,w)
            self.passedCutByFlavour(cat,pdgLep,w,nameFlow=region)
            

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
        
