import ROOT
from EventHelper import EventHelper

def isTightLepton(eh,idx,ptmin=25.):
    pdgId = abs(eh.get("LepGood_pdgId")[idx])
    assert pdgId==11 or pdgId==13
    pt = eh.get("LepGood_pt")[idx]
    if pt<ptmin:
        return False
    eta = eh.get("LepGood_eta")[idx]
    miniRelIso = eh.get("LepGood_miniRelIso")[idx]
    if pdgId==11:
        return abs(eta)<2.5 and miniRelIso<0.1 and eh.get("LepGood_SPRING15_25ns_v1")[idx]==4
    else:
        return abs(eta)<2.4 and miniRelIso<0.2 and eh.get("LepGood_mediumMuonId")[idx]==1 and eh.get("LepGood_sip3d")[idx]<4.

def isVetoLepton(eh,idx,ptmin=10.):

    if isTightLepton(eh,idx):
        return False

    pdgId = abs(eh.get("LepGood_pdgId")[idx])
    assert pdgId==11 or pdgId==13

    pt = eh.get("LepGood_pt")[idx]
    if pt<10:
        return False
    eta = eh.get("LepGood_eta")[idx]
    if pdgId==11:
        return abs(eta)<2.5
    else:
        return abs(eta)<2.4

def tightLeptons(eh,ptmin=25.):
  return [ i for i in range(len(eh.get("LepGood_pdgId"))) if isTightLepton(eh,i,ptmin) ]

def vetoLeptons(eh,ptmin=10.):
  return [ i for i in range(len(eh.get("LepGood_pdgId"))) if isVetoLepton(eh,i,ptmin) ]

def isolatedMuons(eh,ptmin=5.,etamax=1.5,wp="medium"):
  imus = [ ]
  nmu = int(eh.get("nmuCount")+0.5)
  mupts = eh.get("muPt")
  assert len(mupts)==nmu
  muetas = eh.get("muEta")
  murelisos = eh.get("muRelIso")
  mudxys = eh.get("muDxy")

  relabstransition = 25.
  if wp.lower().startswith("loose"):
    relisomax = 0.4
  elif wp.lower().startswith("medium"):
    relisomax = 0.2
  elif wp.lower().startswith("tight"):
    relisomax = 0.12
  else:
    raise ValueError("unknown working point "+wp)

  for i in range(nmu):
    if mupts[i]<ptmin:
      continue
    if abs(muetas[i])>etamax:
      continue
    if abs(mudxys[i])>0.02:
      continue
    absiso = murelisos[i]*mupts[i]
#    absisomax = reliso
    if mupts[i]<relabstransition:
      absisomax = relisomax*relabstransition
    else:
      absisomax = relisomax*mupts[i]
    if int(eh.get("run"))==194429 and int(eh.get("lumi"))==824 and eh.get("event")==723391041:
      print "Muon ",i,mupts[i],murelisos[i],absiso,absisomax
    if absiso<absisomax:
      imus.append(i)
  if int(eh.get("run"))==194429 and int(eh.get("lumi"))==824 and eh.get("event")==723391041:
    print "Muons ",imus
  return imus

def hardestIsolatedMuon(eh,ptmin=5.,etamax=1.5,wp="medium"):
  imus = isolatedMuons(eh,ptmin,etamax,wp)
  if len(imus)>0:
    return imus[0]
  return None

def isolatedElectrons(eh,ptmin=7.,etamax=1.5,wp="medium"):
  ieles = [ ]
  nele = int(eh.get("nelCount")+0.5)
  elepts = eh.get("elPt")
  assert len(elepts)==nele
  eleetas = eh.get("elEta")
  elerelisos = eh.get("elRelIso")

  relabstransition = 25.
  if wp.lower().startswith("loose"):
    relisomax = 0.30
  elif wp.lower().startswith("medium"):
    relisomax = 0.15
  elif wp.lower().startswith("tight"):
    relisomax = 0.10
  else:
    raise ValueError("unknown working point "+wp)

  for i in range(nele):
    if elepts[i]<ptmin:
      continue
    if abs(eleetas[i])>etamax:
      continue
    absiso = elerelisos[i]*elepts[i]
#    absisomax = reliso
    if elepts[i]<relabstransition:
      absisomax = relisomax*relabstransition
    else:
      absisomax = relisomax*elepts[i]
    if absiso<absisomax:
      ieles.append(i)
  return ieles

def hardestIsolatedElectron(eh,ptmin=7.,etamax=1.5,wp="medium"):
  ieles = isolatedElectrons(eh,ptmin,etamax,wp)
  if len(ieles)>0:
    return ieles[0]
  return None

def diLepton(eh,prefix="mu",veto3rd=False): 
  ileps = [ ]
#  nmu = int(eh.get("nmuCount")+0.5)
#  if nmu<2:
#    return [ ]
  leppts = eh.get(prefix+"Pt")
  if len(leppts)<2:
    return [ ]
  ileps1 = filter(lambda i: leppts[i]>20, range(len(leppts)))
  if len(ileps1)<2:
    return [ ]

  lepetas = eh.get(prefix+"Eta")
  ileps2 = filter(lambda i: abs(lepetas[i])<2.1, ileps1)
  if len(ileps2)<2:
    return [ ]
  
  leprelisos = eh.get(prefix+"RelIso")
  ptcut = 25.
  for i in ileps2:
    if leppts[i]>ptcut and leprelisos[i]<0.12:
      ptcut = 20.
      ileps.append(i)
  if len(ileps)<2 or ( veto3rd and len(ileps)>2 ):
    return [ ]
  return ileps

def diMuon(eh,veto3rd=False): 
  return diLepton(eh,"mu",veto3rd)

def diMuonOnia(eh,veto3rd=False): 
  imus = [ ]
  nmu = int(eh.get("nmuCount")+0.5)
  if nmu<2:
    return ( None, None )
  mupts = eh.get("muPt")
  muetas = eh.get("muEta")
  murelisos = eh.get("muRelIso")
  mupdgs = eh.get("muPdg")
  for i in range(nmu):
    if not imus:
      if mupts[i]>25. and abs(muetas[i])<2.1 and murelisos[i]<0.12:
        pdg = mupdgs[i]
        imus.append(i)
    else:
      if mupts[i]>5. and abs(muetas[i])<1.5 and mupdgs[i]==-pdg:
        imus.append(i)

  if len(imus)<2 or ( veto3rd and len(imus)>2 ):
    return ( None, None )
  return ( imus[0], imus[1] )

class DiLepVV:

    def __init__(self,pdg):
        self.pdg = abs(pdg)
        assert pdg==11 or pdg==13
        if pdg==11:
          self.prefix = "el"
        else:
          self.prefix = "mu"
        self.p4cache = [ ]
        self.p4z = ROOT.TLorentzVector()

    def resetP4s(self):
        for p in self.p4cache:
            p[0] = False
            
    def p4(self,ind,ileps,pts,etas,phis):
        if ind>=len(self.p4cache):
            for _ in range(ind-len(self.p4cache)+1):
                self.p4cache.append( [ False, ROOT.TLorentzVector() ] )

        if not self.p4cache[ind][0]:
            self.p4cache[ind][0] = True
            indlep = ileps[ind]
            self.p4cache[ind][1].SetPtEtaPhiM(pts[indlep],etas[indlep],phis[indlep],0.105)

        return self.p4cache[ind][1]
        
    def diLeptonVV(self,eh,minM=55.,minPt=75.):

        ileps = diLepton(eh,self.prefix)
        if not ileps:
            return [ ]

        leppts = eh.get(self.prefix+"Pt")
        if leppts[ileps[0]]<25.:
            return [ ]

        lepetas = eh.get(self.prefix+"Eta")
        lepphis = eh.get(self.prefix+"Phi")

        self.resetP4s()
        p4done = len(ileps)*[ False ]
        for i in range(len(ileps)-1):
            if leppts[ileps[i]]<25.:
                continue
            p4a = self.p4(i,ileps,leppts,lepetas,lepphis)
            for j in range(i+1,len(ileps)):
                p4b = self.p4(j,ileps,leppts,lepetas,lepphis)
                self.p4z = p4a + p4b
                if self.p4z.M()>minM and self.p4z.Pt()>minPt:
                    return [ ileps[i], ileps[j] ]

        return [ ]


def isGoodJet(eh,idx):
  return eh.get("Jet_pt")[idx]>25 and abs(eh.get("Jet_eta")[idx])<2.4

def goodJets(eh):
  return [ i for i in range(len(eh.get("Jet_pt"))) if isGoodJet(eh,i) ]
