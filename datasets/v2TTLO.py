import os
from Sample import *
from SampleFilters import *

class Dataset:

    def __init__(self,dataBase=None,elistBase=None,lumi=1550.,hPU=None,data=False):
        DatasetBase.__init__(self,dataBase=dataBase,elistBase=elistBase, \
                                 sampleDir="tuples_from_Artur/MiniAODv2/")

        self.mcReweight = ("nVert",hPU) if hPU!=None else None
        self.lumi = lumi
        self.data = data

        self.samples = [ ]
        self.add(Sample("TTJets_LO_HT",self.sampleBase,type="B",color=ROOT.kRed,fill=True, \
                            kfactor=1.,filter=GenLepFilter(0,0), \
                            namelist=["TTJets_LO_HT600to800","TTJets_LO_HT800to1200", \
                                          "TTJets_LO_HT1200to2500","TTJets_LO_HT2500toInf"], \
                            baseweights=lumi,mcReweight=self.mcReweight ))
        if self.data:
            self.add(Sample("Data_Run2015D_1p2fb",dataBase+"tuples_from_Artur/JECv6recalibrateMET_eleCBID_1550pb/", \
                                type="D",color=1,fill=False,
                            namelist=[ "SingleMuon_Run2015D_v4", "SingleMuon_Run2015D_05Oct", \
                                           "SingleElectron_Run2015D_v4", "SingleElectron_Run2015D_05Oct" ] ))
