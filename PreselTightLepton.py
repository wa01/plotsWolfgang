import ROOT
import math
from EventHelper import EventHelper
from KinematicUtilities import *
from LeptonUtilities import *
import PreselectionTools as PreTools
        
class PreselTightLepton:

    def __init__(self):
#        self.htMin = 500
        self.leptonTightPtMin = 10
#        self.leptonLoosePtMin = 10
#        self.electronEtaMax = 2.5
#        self.muonEtaMax = 2.4

    def accept(self,eh,sample):

        if len(tightLeptons(eh,ptmin=10.))==0:
            return False


#        if sample.isData():
#            if eh.get("HLTMu24")==0 and eh.get("HLTIsoMu24")==0 and eh.get("HLTIsoMu24eta2p1")==0:
#                return False

        return True

