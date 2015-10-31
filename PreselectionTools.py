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

    def __init__(self):
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
        self.goodJets = None
        self.ht = None

    def set(self,eh):
        self.tightLeptons = tightLeptons(eh,ptmin=25.)
        if len(self.tightLeptons)>0:
            idx = self.tightLeptons[0]
            self.leptonPt = eh.get("LepGood_pt")[idx]
            self.leptonPhi = eh.get("LepGood_phi")[idx]
            self.leptonEta = eh.get("LepGood_eta")[idx]
            self.leptonPdg = eh.get("LepGood_pdgId")[idx]
        self.vetoLeptons = vetoLeptons(eh,ptmin=10.,pttight=25.)
        self.met = eh.get("met_pt")
        self.metPhi = eh.get("met_phi")
        if self.leptonPt!=None:
            self.wkin = LepNuSystem(self.met,self.metPhi,self.leptonPt,self.leptonPhi,self.leptonEta,self.leptonPdg)
            self.lt = self.wkin.lt()

        self.goodJets = goodJets(eh)
        self.ht = eh.get("htJet30j")
                        
    def inBin(self,x,rng):
        if rng[0]!=None and x<rng[0]:
            return False
        if rng[1]!=None and x>=rng[1]:
            return False
        return True
        
    def preselection(self):
        if len(self.tightLeptons)!=1:
            return False

        if len(self.vetoLeptons)>0:
            return False

        if len(self.goodJets)<4:
            return False

        if self.ht<500.:
            return False

        if self.lt<250:
            return False

        return True

    def region(self):
        if not self.preselection():
            return None

        result = None
        for r in RA40bSelection.regions:
            if self.inBin(len(self.goodJets),RA40bSelection.regions[r][0]) and \
               self.inBin(self.lt,RA40bSelection.regions[r][1]) and \
               self.inBin(self.ht,RA40bSelection.regions[r][2]):
                assert result==None
                result = r

        if result==None:
            return None

        dphi = self.wkin.dPhi()
        if dphi<RA40bSelection.regions[r][3]:
            result = "C" + result
        else:
            result = "S" + result

        return result

