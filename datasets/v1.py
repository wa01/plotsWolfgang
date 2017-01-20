import os
from DatasetBase import *
from Sample import *
from SampleFilters import *

class Dataset(DatasetBase):

    def __init__(self,dataBase=None,elistBase=None,lumi=36500.,hPU=None,data=False):
        DatasetBase.__init__(self,dataBase=dataBase,elistBase=elistBase,sampleDir=".")

        self.mcReweight = ("nVert",hPU) if hPU!=None else None
        self.lumi = lumi
        self.data = data
        
        mcSampleDir = "postProcessing_Data_Moriond2017_v6/HT350"
        mcSampleBase = dataBase + mcSampleDir

        self.samples = [ ]
        self.add(Sample("QCD",mcSampleBase,type="B",color=8,fill=True,kfactor=1., \
                            namelist=[    "QCD_HT300to500", \
                                          "QCD_HT500to700", \
                                          "QCD_HT700to1000", \
                                          "QCD_HT1000to1500", \
                                          "QCD_HT1500to2000", \
                                          "QCD_HT2000toInf" ], \
                            baseweights=lumi,mcReweight=self.mcReweight ))
        self.add(Sample("DYJetsToLL",mcSampleBase,type="B",color=5,fill=True, \
                            kfactor=1., \
                            namelist=["DYJetsToLL_M50_HT100to200", \
                                          "DYJetsToLL_M50_HT200to400", \
                                          "DYJetsToLL_M50_HT400to600", \
                                          "DYJetsToLL_M50_HT600toInf" ], \
                            baseweights=[lumi, lumi, lumi, lumi],mcReweight=self.mcReweight ))
#        self.add(Sample("TTV",mcSampleBase,type="B",color=6,fill=True, \
#                            kfactor=1., \
#                            namelist=["TTWJetsToQQ_25ns","TTZToLLNuNu_25ns","TTZToQQ_25ns"], \
#                            baseweights=3*[lumi],mcReweight=self.mcReweight ))
        self.add(Sample("singleTop",mcSampleBase,type="B",color=ROOT.kOrange,fill=True,kfactor=1., \
                            namelist=["ST_s_channel_4f_leptonDecays", \
                                          "ST_t_channel_antitop_4f_leptonDecays", \
                                          "ST_t_channel_top_4f_leptonDecays", \
                                          "ST_tW_antitop_5f_NoFullyHadronicDecays", \
                                          "ST_tW_top_5f_NoFullyHadronicDecays" ], \
                            baseweights=lumi,mcReweight=self.mcReweight ))
        ttJetsDiLeptonFilter = LeptonFilter(motherPdgs=24,grandMotherPdgs=6,minLeptons=2)
        self.add(Sample("TTJets_SingleLepton",mcSampleBase,type="B",color=ROOT.kRed-3,fill=True, \
                            kfactor=1.,namelist=["TTJets_SingleLeptonFromT", \
                                                     "TTJets_SingleLeptonFromTbar" ], \
#                            filter=ttJetsDiLeptonFilter, \
                            baseweights=lumi,mcReweight=self.mcReweight ))
        self.add(Sample("TTJets_DiLepton",mcSampleBase,type="B",color=ROOT.kRed+3,fill=True, \
                            kfactor=1.,namelist=["TTJets_DiLepton"], \
#                            filter=InvertedSampleFilter(ttJetsDiLeptonFilter), \
                            baseweights=lumi,mcReweight=self.mcReweight ))
#    ttJetsDiLeptonFilter = LeptonFilter(motherPdgs=24,grandMotherPdgs=6,minLeptons=2, \
#                                            collections=["Lep","LepFromTau"])
#    self.add(Sample("TTJets_LO_25ns_diEleMu",sampleBase,type="B",color=ROOT.kRed-3,fill=True, \
#                              kfactor=1.,namelist=["TTJets_LO_25ns"], \
#                              filter=ttJetsDiLeptonFilter, \
#                              baseweights=[lumi],mcReweight=self.mcReweight ))
#    self.add(Sample("TTJets_LO_25ns_other1",sampleBase,type="B",color=ROOT.kRed+3,fill=True, \
#                              kfactor=1.,namelist=["TTJets_LO_25ns"], \
#                              filter=InvertedSampleFilter(ttJetsDiLeptonFilter), \
#                              baseweights=[lumi],mcReweight=self.mcReweight ))
        self.add(Sample("WJetsToLNu",mcSampleBase,type="B",color=4,fill=True, \
                            kfactor=1., \
                            namelist=["WJetsToLNu_HT100to200", \
                                          "WJetsToLNu_HT200to400", \
                                          "WJetsToLNu_HT400to600", \
                                          "WJetsToLNu_HT600to800", \
                                          "WJetsToLNu_HT800to1200", \
                                          "WJetsToLNu_HT1200to2500", \
                                          "WJetsToLNu_HT2500toInf" ], \
                            baseweights=7*[lumi],mcReweight=self.mcReweight ))
        if self.data:
#        self.add(Sample("SingleMuon_Run2015D",sampleBase,type="D",color=1,fill=False))
#        self.add(Sample("SingleMuon_Run2015D_1p2fb",sampleBase,type="D",color=1,fill=False,
#                              namelist=[ "SingleMuon_Run2015D_v4", "SingleMuon_Run2015D_05Oct"] ))
            dataSampleDir = "postProcessing_Data_Moriond2017_v9_Trigskimmed/HT350"
            dataSampleBase = dataBase + dataSampleDir
            self.add(Sample("Data_Run2015D_1p2fb",dataSampleBase,type="D",color=1,fill=False,
                            namelist=[ "SingleMuon_Run2016B_23Sep2016", \
                                           "SingleMuon_Run2016C_23Sep2016_v1", \
                                           "SingleMuon_Run2016D_23Sep2016_v1", \
                                           "SingleMuon_Run2016E_23Sep2016_v1", \
                                           "SingleMuon_Run2016F_23Sep2016_v1", \
                                           "SingleMuon_Run2016G_23Sep2016_v1", \
                                           "SingleMuon_Run2016H_23Sep2016_v2", \
                                           "SingleMuon_Run2016H_23Sep2016_v3" ] ))
                        
    def add(self,sample):
        self.samples.append(sample)
