import os
from DatasetBase import *
from Sample import *
from SampleFilters import *

class Dataset(DatasetBase):

    def __init__(self,dataBase=None,elistBase=None,lumi=1550.,hPU=None,data=False):
        DatasetBase.__init__(self,dataBase=dataBase,elistBase=elistBase, \
                                 sampleDir="tuples_from_Artur/MiniAODv2/")

        self.mcReweight = ("nVert",hPU) if hPU!=None else None
        self.lumi = lumi
        self.data = data

        self.samples = [ ]
        self.add(Sample("TTJets_LO_DiLepton",self.sampleBase,type="B",color=ROOT.kBlue-3,fill=True, \
                            kfactor=1.059, \
                            namelist=["TTJets_DiLepton_full"], \
                            baseweights=lumi,mcReweight=self.mcReweight ))
