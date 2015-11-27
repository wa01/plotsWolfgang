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
            self.addVariable("ngenEleFromTau"+flv,5,-0.5,4.5,'b')
            self.addVariable("ngenMuFromTau"+flv,5,-0.5,4.5,'b')
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
            self.addVariable("nVert"+flv,50,-0.5,49.5,'b')
            nr = len(RA40bSelection.regions.keys())
            self.addVariable("CSRs"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("CSRstt"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("CSRstv"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("CSRstooa"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("CSRstineff"+flv,2*nr+1,-nr-0.5,nr+0.5,'b')
            self.addVariable("massDiGenEleFromTau"+flv,500,0.,10.,'b')
            self.addVariable("massDiGenMuFromTau"+flv,500,0.,10.,'b')

            csrCategories = [ "had", "tight", "lt", "mismatch", "tauhad", "tt", "tv", "tOutOfAcc", "tInEff", "other" ]
            self.addCutFlow(csrCategories,nameFlow="DefaultCutFlow"+flv)
            for i in range(13):
                name = "CR"+str(i+1)
                self.addCutFlow(csrCategories,nameFlow=name+flv)
            for i in range(13):
                name = "SR"+str(i+1)
                self.addCutFlow(csrCategories,nameFlow=name+flv)

        curdir.cd()

        self.selection = RA40bSelection()

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
        if ngenTau!=1:
            return
        ngenLepFromTau = eh.get("ngenLepFromTau")
        if ngenLepFromTau>1:
#            print "More than 2 ngenLepFromTau!"
#            print eh.get("genLepFromTau_motherId")
#            print eh.get("genLepFromTau_grandmotherId")
#            print eh.get("genLepFromTau_sourceId")
#            print eh.get("genLepFromTau_charge")
#            print eh.get("genLepFromTau_status")
#            print eh.get("genLepFromTau_pdgId")
#            print eh.get("genLepFromTau_pt")
#            print eh.get("genLepFromTau_eta")
#            print eh.get("genLepFromTau_phi")
##            print eh.get("genLepFromTau_mass")
#            print eh.get("genLepFromTau_motherIndex")
            for i in range(ngenLepFromTau-1):
                pdga = eh.get("genLepFromTau_pdgId")[i]
                if abs(pdga)!=11 and abs(pdga)!=13:
                    continue
                p4a = ROOT.TLorentzVector()
                p4a.SetPtEtaPhiM(eh.get("genLepFromTau_pt")[i],
                                 eh.get("genLepFromTau_eta")[i],
                                 eh.get("genLepFromTau_phi")[i],
                                 eh.get("genLepFromTau_mass")[i])
                for j in range(i+1,ngenLepFromTau):
                    pdgb = eh.get("genLepFromTau_pdgId")[j]
                    if pdgb!=-pdga:
                        continue
                    p4b = ROOT.TLorentzVector()
                    p4b.SetPtEtaPhiM(eh.get("genLepFromTau_pt")[j],
                                     eh.get("genLepFromTau_eta")[j],
                                     eh.get("genLepFromTau_phi")[j],
                                     eh.get("genLepFromTau_mass")[j])
                    print i,j,(p4a+p4b).M()
                    if abs(pdga)==11:
                        self.fill1DByFlavour("massDiGenEleFromTau",pdgLep,(p4a+p4b).M(),w)
                    else:
                        self.fill1DByFlavour("massDiGenMuFromTau",pdgLep,(p4a+p4b).M(),w)
        self.fill1DByFlavour("ngenLep",pdgLep,ngenLep,w)
        self.fill1DByFlavour("ngenTau",pdgLep,ngenTau,w)
        self.fill1DByFlavour("ngenLepFromTau",pdgLep,ngenLepFromTau,w)
        ngenEleFromTau = sum(1 for x in eh.get("genLepFromTau_pdgId") if abs(x)==11)
        self.fill1DByFlavour("ngenEleFromTau",pdgLep,ngenEleFromTau,w)
        ngenMuFromTau = sum(1 for x in eh.get("genLepFromTau_pdgId") if abs(x)==13)
        self.fill1DByFlavour("ngenMuFromTau",pdgLep,ngenMuFromTau,w)
                    
                
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
        metPhi = eh.get("met_phi")

        lepPhis = eh.get("LepGood_phi")
        lepEtas = eh.get("LepGood_eta")
        matchLep = self.closestMatch(lepPhis[tightLeps[0]],lepEtas[tightLeps[0]],
                                     eh.get("genLep_phi"),eh.get("genLep_eta"))
        matchLepFromTau = self.closestMatch(lepPhis[tightLeps[0]],lepEtas[tightLeps[0]],
                                            eh.get("genLepFromTau_phi"),eh.get("genLepFromTau_eta"))
        if matchLep[1]!=None or matchLepFromTau[1]!=None:
            if matchLep[0]<matchLepFromTau[0]:
                self.fill1DByFlavour("typeGenLepMatch",pdgLep,1,w)
                self.fill1DByFlavour("drGenLepMatch",pdgLep,matchLep[0],w)
                ptRatio = lepPt/eh.get("genLep_pt")[matchLep[1]]
                self.fill1DByFlavour("ptrGenLepMatch",pdgLep,ptRatio,w)
            else:
                self.fill1DByFlavour("typeGenLepMatch",pdgLep,2,w)
                self.fill1DByFlavour("drGenLepMatch",pdgLep,matchLepFromTau[0],w)
                ptRatio = lepPt/eh.get("genLepFromTau_pt")[matchLepFromTau[1]]
                self.fill1DByFlavour("ptrGenLepMatch",pdgLep,ptRatio,w)
        else:
            self.fill1DByFlavour("typeGenLepMatch",pdgLep,0,w)



        lt = met + lepPt
        self.fill1DByFlavour("lt",pdgLep,lt,w)
        if lt<250:
            return
        self.passedCutByFlavour("lt",pdgLep,w)

        #
        # match
        #
        self.fill1DByFlavour("matchId",pdgLep,eh.get("LepGood_mcMatchId")[tightLeps[0]],w)

        self.fill1DByFlavour("ptLep",pdgLep,lepPt,w)

        vetoLeps = vetoLeptons(eh)
        nVetoLep = len(vetoLeps)
        self.fill1DByFlavour("nVetoLep",pdgLep,nVetoLep,w)
        if nVetoLep>0:
            return

        cat = "other"
        if ngenTau>ngenLepFromTau:
            cat = "tauhad"
        else:
            if nTightLep==2:
                cat = "tt"
            else:
                if nVetoLep>0:
                    cat = "tv"
                    
        self.passedCutByFlavour(cat,pdgLep,w)
        return

        

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
        
