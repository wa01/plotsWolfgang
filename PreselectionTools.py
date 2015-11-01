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
        self.nJets = None
        self.nBJets = None
        self.jet2Pt = None
        self.ht = None

    def set(self,eh):
        self.reset()
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

        jets = goodJets(eh)
        self.nJets = len(jets)
        if self.nJets>1:
            self.jet2Pt = eh.get("Jet_pt")[jets[1]]
        else:
            self.jet2Pt = 0.
        self.nBJets = eh.get("nBJetMedium30")
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

        if self.nJets<4:
            return False

        if self.jet2Pt<80.:
            return False

        if self.ht<500.:
            return False

        if self.lt<250:
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

        dphi = self.wkin.dPhi()
        if dphi<RA40bSelection.regions[result][3]:
            result = "C" + result
        else:
            result = "S" + result

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

        if self.nJets<2 or self.nJets>3:
            return [ ]

        matched = self.matchRegions(None,self.lt,self.ht)

        dphi = self.wkin.dPhi()
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

        dphi = self.wkin.dPhi()
        result = [ ]
        for r in matched:
            if dphi<RA40bSelection.regions[r][3]:
                result.append("C"+r)
            else:
                result.append("S"+r)

        return result
