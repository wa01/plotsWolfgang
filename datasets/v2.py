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
        self.add(Sample("QCD",self.sampleBase,type="B",color=8,fill=True,kfactor=1., \
                            namelist=["QCD_HT300to500", \
                                          "QCD_HT500to700", \
                                          "QCD_HT700to1000", \
                                          "QCD_HT1000to1500", \
                                          "QCD_HT1500to2000", \
                                          "QCD_HT2000toInf" ], \
                            baseweights=lumi,mcReweight=self.mcReweight ))
        self.add(Sample("DYJetsToLL",self.sampleBase,type="B",color=5,fill=True, \
                            kfactor=1., \
                            namelist=["DYJetsToLL_M50_HT100to200", \
                                          "DYJetsToLL_M50_HT200to400", \
                                          "DYJetsToLL_M50_HT400to600", \
                                          "DYJetsToLL_M50_HT600toInf" ], \
                            baseweights=[lumi, lumi, lumi, lumi],mcReweight=self.mcReweight ))
        self.add(Sample("TTV",self.sampleBase,type="B",color=6,fill=True, \
                            kfactor=1., \
                            namelist=["TTWToQQ","TTWToLNu","TTZToQQ","TTZToLLNuNu"], \
                            baseweights=lumi,mcReweight=self.mcReweight ))
        self.add(Sample("singleTop",self.sampleBase,type="B",color=ROOT.kOrange,fill=True,kfactor=1., \
                            namelist=["TToLeptons_sch", \
#                                            "TToLeptons_tch", \
                                          "T_tWch" ], \
#                                           "T_tWch", \
#                                            "TBar_tWch" ], \
                            baseweights=lumi,mcReweight=self.mcReweight ))
        self.add(Sample("TTJets_LO_HT",self.sampleBase,type="B",color=ROOT.kRed,fill=True, \
                            kfactor=1.,filter=GenLepFilter(0,0), \
                            namelist=["TTJets_LO_HT600to800","TTJets_LO_HT800to1200", \
                                          "TTJets_LO_HT1200to2500","TTJets_LO_HT2500toInf"], \
                            baseweights=lumi,mcReweight=self.mcReweight ))
        self.add(Sample("TTJets_LO",self.sampleBase,type="B",color=ROOT.kRed,fill=True, \
                            kfactor=1., \
                            filter=SampleFilterAND(LheHtFilter(maxHt=600.),GenLepFilter(0,0)), \
                            baseweights=lumi,mcReweight=self.mcReweight ))
        self.add(Sample("TTJets_LO_DiLepton",self.sampleBase,type="B",color=ROOT.kBlue-3,fill=True, \
                            kfactor=1.059, \
                            namelist=["TTJets_DiLepton_full"], \
                            baseweights=lumi,mcReweight=self.mcReweight ))
        self.add(Sample("TTJets_LO_SingleLepton",self.sampleBase,type="B",color=ROOT.kRed,fill=True, \
                            kfactor=1.023, \
                            namelist=["TTJets_SingleLeptonFromT_full","TTJets_SingleLeptonFromTbar_full"], \
                            baseweights=lumi,mcReweight=self.mcReweight ))
        self.add(Sample("WJetsToLNu",self.sampleBase,type="B",color=4,fill=True, \
                            kfactor=1., \
                            namelist=["WJetsToLNu_HT100to200", \
                                          "WJetsToLNu_HT200to400", \
                                          "WJetsToLNu_HT400to600", \
                                          "WJetsToLNu_HT600to800", \
                                          "WJetsToLNu_HT800to1200", \
                                          "WJetsToLNu_HT1200to2500", \
                                          "WJetsToLNu_HT2500toInf" ], \
                            baseweights=lumi,mcReweight=self.mcReweight ))
        if self.data:
            self.add(Sample("Data_Run2015D_1p2fb",dataBase+"tuples_from_Artur/JECv6recalibrateMET_eleCBID_1550pb/", \
                                type="D",color=1,fill=False,
                            namelist=[ "SingleMuon_Run2015D_v4", "SingleMuon_Run2015D_05Oct", \
                                           "SingleElectron_Run2015D_v4", "SingleElectron_Run2015D_05Oct" ] ))
