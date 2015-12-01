import ROOT
import math
from EventHelper import EventHelper
from KinematicUtilities import *
from LeptonUtilities import *
import PreselectionTools as PreTools
        
class PreselDiLepton:

    def __init__(self):
        self.preselection = PreTools.RA40bSelection(reqNTightLep=(1,3),reqNVetoLep=(0,None))

    def accept(self,eh,sample):

        self.preselection.set(eh,sample.isData())
        presel = self.preselection.preselection()
        if not presel:
            return False
        if len(self.preselection.tightLeptons)+len(self.preselection.vetoLeptons)<2:
            return False

        return True

