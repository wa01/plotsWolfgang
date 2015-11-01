import ROOT
import math
from EventHelper import EventHelper
from KinematicUtilities import *
from LeptonUtilities import *
import PreselectionTools as PreTools
        
class PreselStd:

    def __init__(self):
        self.preselection = PreTools.RA40bSelection()

    def accept(self,eh,sample):

        self.preselection.set(eh)
        return self.preselection.preselection()

        return True

