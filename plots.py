import ROOT
import sys

class Histograms:
    def __init__(self):
        self.names = [ ]
        self.histograms = { }

    def addHistogram(self,name):
        assert not name in self.names
        self.names.append(name)
        self.histograms[name] = ROOT.TH1D("h_"+name,"h_"+name,1,0.5,1.5)

def isTightLepton(e,idx):
    pdgId = abs(e.LepGood_pdgId[idx])
    assert pdgId==11 or pdgId==13
    pt = e.LepGood_pt[idx]
    if pt<25:
        return False
    eta = e.LepGood_eta[idx]
    if pdgId==11:
        return abs(eta)<2.5 and e.LepGood_miniRelIso[idx]<0.1 and e.LepGood_SPRING15_25ns_v1[idx]==4
    else:
        return abs(eta)<2.4 and e.LepGood_miniRelIso[idx]<0.2 and e.LepGood_mediumMuonId[idx]==1 and e.LepGood_sip3d[idx]<4.

def isVetoLepton(e,idx):
    if isTightLepton(e,idx):
        return False

    pdgId = abs(e.LepGood_pdgId[idx])
    assert pdgId==11 or pdgId==13

    pt = e.LepGood_pt[idx]
    if pt<10:
        return False
    eta = e.LepGood_eta[idx]
    if pdgId==11:
        return abs(eta)<2.5
    else:
        return abs(eta)<2.4

def isGoodJet(e,idx):
    return e.Jet_pt[idx]>30 and abs(e.Jet_eta[idx])<2.4

def createCountHistogram(hCounts,name):
    assert not name in [ x[0] for x in hCounts ]
    hCounts.append( ( name, ROOT.TH1D("h_"+name,"h_"+name,1,0.5,1.5) ) )
    
datadir = "/media/Seagate/adamwo/data/cmgTuples/tuples_from_Artur"
samples = { "TTJets_LO" : [ ( "TTJets_LO_25ns", 831.76 ) ], \
                "DY" : [ ( "DYJetsToLL_M50_HT100to200", 1.23*139.4 ), \
                         ( "DYJetsToLL_M50_HT200to400", 1.23*42.75 ), \
                         ( "DYJetsToLL_M50_HT400to600", 1.23*5.497 ), \
                         ( "DYJetsToLL_M50_HT600toInf", 1.23*2.21 ) ]
                }

#infilename = "/media/Seagate/adamwo/data/cmgTuples/tuples_from_Artur/TTJets_LO_25ns/treeProducerSusySingleLepton/tree.root"
#if len(sys.argv)>1:
#    infilename = sys.argv[1]
#if len(sys.argv)<2:
#    sys.argv.append("/media/Seagate/adamwo/data/cmgTuples/tuples_from_Artur/TTJets_LO_25ns/treeProducerSusySingleLepton/tree.root")

ROOT.gStyle.SetOptStat(111111)
ROOT.TH1.SetDefaultSumw2(1)

#hCounts = [ ]
#createCountHistogram(hCounts,"skim")
#createCountHistogram(hCounts,"ht")
#createCountHistogram(hCounts,"tight-lepton")
#createCountHistogram(hCounts,"lepton-veto")
#createCountHistogram(hCounts,"njet")
#createCountHistogram(hCounts,"ptj2")

hCounts = Histograms()
hCounts.addHistogram("skim")
hCounts.addHistogram("tight-lepton")
hCounts.addHistogram("lepton-veto")
hCounts.addHistogram("njet")
hCounts.addHistogram("ptj2")
hCounts.addHistogram("ht")
hCounts.addHistogram("lt")

sample = samples[sys.argv[1]]
for d,xs in sample:

    nproc = None
    for l in open(datadir+"/"+d+"/skimAnalyzerCount/SkimReport.txt"):
        fields = l[:-1].split()
        if len(fields)==5 and fields[0]=="All" and fields[1]=="Events":
            nproc = int(fields[2])
            break
    assert nproc!=None
#    wgt = 3000./(nproc/xs)
    w = 3000./nproc
    print "Processing ",d,"with weight",w

    tree = ROOT.TChain("tree")
    tree.Add(datadir+"/"+d+"/treeProducerSusySingleLepton/tree.root")
    #infile = ROOT.TFile(infilename)
    #tree = infile.Get("tree")

    for ie,e in enumerate(tree):

        if ie%10000==0:
            print "At event ",ie

        wgt = w*e.xsec
        hCounts.histograms["skim"].Fill(1,wgt)

        tightLeptons = [ i for i in range(len(e.LepGood_pt)) if isTightLepton(e,i) ]
        if len(tightLeptons)!=1:
            continue
        hCounts.histograms["tight-lepton"].Fill(1,wgt)

        vetoLeptons = [ i for i in range(len(e.LepGood_pt)) if isVetoLepton(e,i) ]
        if len(vetoLeptons)>0:
            continue
        hCounts.histograms["lepton-veto"].Fill(1,wgt)
#        print "Selected:",d,ie,e.run,e.lumi,e.evt

        centralJets = [ i for i in range(len(e.Jet_pt)) if isGoodJet(e,i) ]
        if len(centralJets)<5:
            continue
        hCounts.histograms["njet"].Fill(1,wgt)

        if e.Jet_pt[centralJets[1]]<80:
            continue
        hCounts.histograms["ptj2"].Fill(1,wgt)

        if e.htJet30j<500:
            continue
        hCounts.histograms["ht"].Fill(1,wgt)

        met = e.met_pt
        lidx = tightLeptons[0]
        lpt = e.LepGood_pt[lidx]
        lt = met + lpt
        if lt<250:
            continue
        hCounts.histograms["lt"].Fill(1,wgt)
        
    #    print len(e.LepGood_pt),len(tightLeptons),len(vetoLeptons)
    #    if ie>=10:
    #        break

for n in hCounts.names:
    h = hCounts.histograms[n]
    print "{0:20s} {1:10.1f}".format(n,h.GetSumOfWeights())
