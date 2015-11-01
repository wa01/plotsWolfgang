import ROOT
import math
from EventHelper import EventHelper
from KinematicUtilities import *
from LeptonUtilities import *
import PreselectionTools as PreTools
        
class PreselHTSkim:

    def __init__(self):
        self.htMin = 500
        self.leptonTightPtMin = 25
        self.leptonLoosePtMin = 10
        self.electronEtaMax = 2.5
        self.muonEtaMax = 2.4

    def accept(self,eh,sample):

        ht = eh.get("htJet30j")
        if ht<350.:
            return False

##        isrJetPt = eh.get("isrJetPt")
##        if math.isnan(isrJetPt) or isrJetPt<110.:
##            return False

#        if eh.get("nHardElectrons")>0 or eh.get("nHardTaus")>0:
#            return False

#        if sample.isData():
#            if eh.get("HLTMu24")==0 and eh.get("HLTIsoMu24")==0 and eh.get("HLTIsoMu24eta2p1")==0:
#                return False

        return True

