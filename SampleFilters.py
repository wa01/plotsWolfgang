class LeptonFilter:

  verboseCounter = 100

  def expandPdgs(self,pdgs):
    if hasattr(pdgs,"__getitem__"):
      return [ abs(x) for x in pdgs ]
    else:
      return [ abs(pdgs) ]

  def __init__(self,minLeptons=1,leptonPdgs=[11,13,15],motherPdgs=None,grandMotherPdgs=None, \
                 collections=["Lep","Tau"]):
    self.minLeptons = minLeptons
    self.leptonPdgs = self.expandPdgs(leptonPdgs)
    if motherPdgs==None:
      self.motherPdgs = None
    else:
      self.motherPdgs = self.expandPdgs(motherPdgs)
    if grandMotherPdgs==None:
      self.grandMotherPdgs = None
    else:
      self.grandMotherPdgs = self.expandPdgs(grandMotherPdgs)
    self.collections = collections

  def getSpecificLeptons(self,eh,prefix,reqIds,reqMotherIds,reqGrandMotherIds):
    result = [ ]
    if reqMotherIds!=None:
      motherIds = eh.get(prefix+"_motherId")
    if reqGrandMotherIds!=None:
      grandmotherIds = eh.get(prefix+"_grandmotherId")
    for i,pdg in enumerate(eh.get(prefix+"_pdgId")):
      if abs(pdg) in reqIds:
        if reqMotherIds==None or ( abs(motherIds[i]) in reqMotherIds ):
          if reqGrandMotherIds==None or ( abs(grandmotherIds[i]) in reqGrandMotherIds ):
            result.append(i)
    return result
    
  def getLeptons(self,eh):
    result = [ ]

    if "Lep" in self.collections:
      reqIds = [ x for x in self.leptonPdgs if ( x==11 or x==13 ) ]
      if reqIds != [ ]:
        result.append(self.getSpecificLeptons(eh,"genLep",reqIds,self.motherPdgs,self.grandMotherPdgs))
      else:
        result.append([ ])

    if "LepFromTau" in self.collections:
      reqIds = [ x for x in self.leptonPdgs if ( x==11 or x==13 ) ]
      if reqIds != [ ]:
        result.append(self.getSpecificLeptons(eh,"genLepFromTau",reqIds,None,self.motherPdgs))
      else:
        result.append([ ])

    if "Tau" in self.collections:
      reqIds = [ x for x in self.leptonPdgs if x==15 ]
      if reqIds != [ ]:
        result.append(self.getSpecificLeptons(eh,"genTau",reqIds,self.motherPdgs,self.grandMotherPdgs))
      else:
        result.append([ ])

    return result

  def accept(self,eh):
    allLeptons = self.getLeptons(eh)
    if LeptonFilter.verboseCounter>0:
      print allLeptons
      LeptonFilter.verboseCounter -= 1
    return len(allLeptons[0])+len(allLeptons[1])>=self.minLeptons

class QuarkFilter:

  def __init__(self,quarkPdg):
    self.quarkPdg = abs(quarkPdg)

  def accept(self,eh):
    ngp = int(eh.get("ngp"))
    if ngp<4:
      return False
    pdgs = eh.get("gpPdg")
    assert ngp==len(pdgs)
    for pdg in pdgs[4:ngp]:
      if abs(pdg)==self.quarkPdg:
        return True
    return False

  

class InvertedSampleFilter:

  def __init__(self,other):
    self.filter = other

  def accept(self,eh):
    return not self.filter.accept(eh)
