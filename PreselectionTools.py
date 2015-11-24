import math
from EventHelper import EventHelper
from KinematicUtilities import *
from LeptonUtilities import *

htMin = 500.
ltMin = 250.
nJetMin = 4
ptJet2Min = 80.
ptLeptonHardMin = 25.
ptLeptonSoftMin = 10.

class RA40bSelection:

    regions = {
        'R1' : ( [ 5, 6 ], [ 250, 350 ], [ 500, None ], 1.00 ), \
        'R2' : ( [ 5, 6 ], [ 350, 450 ], [ 500, None ], 1.00 ), \
        'R3' : ( [ 5, 6 ], [ 450, None ], [ 500, None ], 1.00 ), \
        'R4' : ( [ 6, 8 ], [ 250, 350 ], [ 500, 750 ], 1.00 ), \
        'R5' : ( [ 6, 8 ], [ 250, 350 ], [ 750, None ], 1.00 ), \
        'R6' : ( [ 6, 8 ], [ 350, 450 ], [ 500, 750 ], 1.00 ), \
        'R7' : ( [ 6, 8 ], [ 350, 450 ], [ 750, None ], 1.00 ), \
        'R8' : ( [ 6, 8 ], [ 450, None ], [ 500, 1000 ], 0.75 ), \
        'R9' : ( [ 6, 8 ], [ 450, None ], [ 1000, None ], 0.75 ), \
        'R10' : ( [ 8, None ], [ 250, 350 ], [ 500, 750 ], 1.00 ), \
        'R11' : ( [ 8, None ], [ 250, 350 ], [ 750, None ], 1.00 ), \
        'R12' : ( [ 8, None ], [ 350, 450 ], [ 500, None ], 0.75 ), \
        'R13' : ( [ 8, None ], [ 450, None ], [ 500, None ], 0.75 ) }
    regionLabels = sorted(regions.keys(),key = lambda x: int(x[1:]))

    def __init__(self,reqNTightLep=1,reqTightLepPt=25.,reqNVetoLep=0,reqVetoLepPt=10., \
                     reqHT=500.,reqLT=250.,reqNjet=4,reqJet2Pt=80.):
        self.reqNTightLep = reqNTightLep
        self.reqTightLepPt = reqTightLepPt
        self.reqNVetoLep = reqNVetoLep
        self.reqVetoLepPt = reqVetoLepPt
        self.reqHT = reqHT
        self.reqLT = reqLT
        self.reqNjet = reqNjet
        self.reqJet2Pt = reqJet2Pt
        self.reset()

    def reset(self):
        self.tightLeptons = None
        self.vetoLeptons = None
        self.leptonPt = None
        self.leptonPhi = None
        self.leptonEta = None
        self.leptonPdg = None
        self.met = None
        self.metPhi = None
        self.wkin = None
        self.lt = None
        self.nJets = None
        self.nBJets = None
        self.jet2Pt = None
        self.ht = None
        self.triggers = [ None, None ]
        self.filters = True
        self.region_ = ""

    def set(self,eh,isData=False):
        self.reset()
        self.isData = isData
        if isData:
            self.filename = eh.tree.GetCurrentFile().GetName()
        else:
            self.filename = None
        self.tightLeptons = tightLeptons(eh,ptmin=self.reqTightLepPt)
        if len(self.tightLeptons)>0:
            idx = self.tightLeptons[0]
            self.leptonPt = eh.get("LepGood_pt")[idx]
            self.leptonPhi = eh.get("LepGood_phi")[idx]
            self.leptonEta = eh.get("LepGood_eta")[idx]
            self.leptonPdg = eh.get("LepGood_pdgId")[idx]
        self.vetoLeptons = vetoLeptons(eh,ptmin=self.reqVetoLepPt,pttight=self.reqTightLepPt)
        self.met = eh.get("met_pt")
        self.metPhi = eh.get("met_phi")
        if self.leptonPt!=None:
            self.wkin = LepNuSystem(self.met,self.metPhi, \
                                    self.leptonPt,self.leptonPhi,self.leptonEta,self.leptonPdg)
            self.lt = self.wkin.lt()

        jets = goodJets(eh)
        self.nJets = len(jets)
        if self.nJets>1:
            self.jet2Pt = eh.get("Jet_pt")[jets[1]]
        else:
            self.jet2Pt = 0.
        self.nBJets = eh.get("nBJetMedium30")
        self.ht = eh.get("htJet30j")
        if self.isData:
            self.triggers = [ eh.get("HLT_EleHT350")>0.5, eh.get("HLT_MuHT350")>0.5 ]
            self.filters = eh.get("nVert")>0 and eh.get("Flag_CSCTightHaloFilter")>0.5 and \
                eh.get("Flag_eeBadScFilter")>0.5 and eh.get("Flag_HBHENoiseFilter_fix")>0.5 and \
                eh.get("Flag_HBHENoiseIsoFilter")>0.5
#            if not self.filters:
#                print "*** Rejected"

                        
    def inBin(self,x,rng):
        if rng[0]!=None and x<rng[0]:
            return False
        if rng[1]!=None and x>=rng[1]:
            return False
        return True
        
    def preselection(self):
        if len(self.tightLeptons)!=self.reqNTightLep:
            return False

        if not self.filters:
            return False

        if self.isData:
            if abs(self.leptonPdg)==11:
                if not self.triggers[0] or self.filename.find("SingleElectron")<0:
                    return False
            elif abs(self.leptonPdg)==13:
                if not self.triggers[1] or self.filename.find("SingleMuon")<0:
                    return False

        if len(self.vetoLeptons)>self.reqNVetoLep:
            return False

        if self.nJets<self.reqNjet:
            return False

        if self.jet2Pt<self.reqJet2Pt:
            return False

        if self.ht<self.reqHT:
            return False

        if self.lt<self.reqLT:
            return False

        return True

    def matchRegions(self,njets=None,lt=None,ht=None):
        result = [ ]
        for r,cuts in RA40bSelection.regions.iteritems():
            if ( njets==None or self.inBin(njets,cuts[0]) ) and \
               ( lt==None or self.inBin(lt,cuts[1]) ) and \
               ( ht==None or self.inBin(ht,cuts[2]) ):
                result.append(r)
        return result

    def region(self):
        if self.region_!="":
            return self.region_
        self.region_ = None

        if not self.preselection():
            return None

        if self.nBJets>0:
            return None

        matched = self.matchRegions(self.nJets,self.lt,self.ht)
        assert len(matched)<2
        if len(matched)==0:
            return None
        result = matched[0]

#        result = None
#        for r in RA40bSelection.regions:
#            if self.inBin(self.nJets,RA40bSelection.regions[r][0]) and \
#               self.inBin(self.lt,RA40bSelection.regions[r][1]) and \
#               self.inBin(self.ht,RA40bSelection.regions[r][2]):
#                assert result==None
#                result = r
#
#        if result==None:
#            return None

        dphi = abs(self.wkin.dPhi())
        if dphi<RA40bSelection.regions[result][3]:
            result = "C" + result
        else:
            result = "S" + result

        self.region_ = result
        return result

    def isSignalRegion(self):
        r = self.region()
        return r!=None and r.startswith("S")

    def isControlRegion(self):
        r = self.region()
        return r!=None and r.startswith("C")

    def wRegions(self):
        if not self.preselection():
            return [ ]

        if self.nBJets>0:
            return [ ]

        if self.nJets<3 or self.nJets>4:
            return [ ]

        matched = self.matchRegions(None,self.lt,self.ht)

        dphi = abs(self.wkin.dPhi())
        result = [ ]
        for r in matched:
            if dphi<RA40bSelection.regions[r][3]:
                result.append("C"+r)
            else:
                result.append("S"+r)

        return result

    def ttRegions(self,nb):

        if not self.preselection():
            return [ ]

        if self.nBJets!=nb:
            return [ ]

        if self.nJets<4 or self.nJets>5:
            return [ ]

        matched = self.matchRegions(None,self.lt,self.ht)

        dphi = abs(self.wkin.dPhi())
        result = [ ]
        for r in matched:
            if dphi<RA40bSelection.regions[r][3]:
                result.append("C"+r)
            else:
                result.append("S"+r)

        return result

    def isBlinded(self):
        if not self.preselection():
            return False

        if self.nBJets==0 and abs(self.wkin.dPhi())>0.5 and self.nJets>4:
            return True
        if self.nBJets>0 and self.nJets>5:
            return True

        return False

