class LeptonFilter:

  def __init__(self,leptonPdg):
    self.leptonPdg = abs(leptonPdg)

  def accept(self,eh):
    ngp = int(eh.get("ngp"))
    pdgs = eh.get("gpPdg")
    for pdg in pdgs[:ngp]:
      if abs(pdg)==self.leptonPdg:
        return True
    return False

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
