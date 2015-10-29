import ROOT
import sys
from math import *
from EventHelper import EventHelper

def myround (f):
    return int(round(f,0)*1.000001)

def genDaughters (eh,i):
    da1 = myround(eh.get("gpDa1")[i])
    if da1<0:
        return set()
    da2 = myround(eh.get("gpDa2")[i])
    if da2<0:
        da2 = da1
    return set(range(da1,da2+1))
    
def genMothers (eh,i):
    mo1 = myround(eh.get("gpMo1")[i])
    if mo1<0:
        return set()
    mo2 = myround(eh.get("gpMo2")[i])
    if mo2<0:
        mo2 = mo1
    return set(range(mo1,mo2+1))

class GeneratorParticle:
    "A particle in the generator history"
    def __init__(self,eh,i):
        self.index = i
        self.pdg = myround(eh.get("gpPdg")[i])
        self.status = myround(eh.get("gpSta")[i])
        self.mothers = genMothers(eh,i)
        self.daughters = genDaughters(eh,i)
        self.pt = eh.get("gpPt")[i]
        self.phi = eh.get("gpPhi")[i]
        self.eta = eh.get("gpEta")[i]
        self.mass = eh.get("gpM")[i]

    def theta(self):
        return 2*atan(exp(-self.eta))
    
    def px(self):
        return self.pt*cos(self.phi)
    
    def py(self):
        return self.pt*sin(self.phi)

    def pz(self):
        return self.pt*(exp(self.eta)-exp(-self.eta))/2.

    def isDaughter(self,other):
        return other.index in self.daughters

    def isMother(self,other):
        return self.index in others.mothers
    
    def __str__(self):
        result = '{0:5d}{1:5d}{2:8d}'.format(self.index,self.status,self.pdg)
        fmo = '{0:5d}'
        mos = sorted(self.mothers)
        if len(mos)<1:
            result += fmo.format(-1) + fmo.format(-1)
        else:
            result += fmo.format(mos[0])
            if len(mos)<2:
                result += fmo.format(-1)
            else:
                result += fmo.format(mos[-1])

        fdau = '{0:5d}'
        daus = sorted(self.daughters)
        if len(daus)<1:
            result += fdau.format(-1) + fdau.format(-1)
        else:
            result += fdau.format(daus[0])
            if len(daus)<2:
                result += fdau.format(-1)
            else:
                result += fdau.format(daus[-1])

        result += '{0:7.1f}{1:7.1f}{1:7.1f}'.format(self.pt,self.phi,self.eta)
        return result

class GeneratorHistory:
    "Generator history"
    def __init__(self,eh):

        self.particles = [ ]

        self.prologue = set()
        self.signalTree = set()
        self.inProtons = set()
        self.inPartons = set()
        self.signalPartons = set()
        self.isr = set()
        for i in range(eh.get("ngp")):
            particle = GeneratorParticle(eh,i)
            self.particles.append(particle)
            
            if len(self.inProtons)<2:
                assert abs(particle.pdg)==2212
                self.inProtons.add(i)
                self.prologue.add(i)
                continue

            if len(self.inPartons)<2:
                self.prologue.add(i)
                if len(particle.mothers)==1 and list(particle.mothers)[0] in self.inProtons:
                    continue
                self.inPartons.add(i)
                continue

            if len(self.signalPartons)==0:
                inplist = list(self.inPartons)
                assert sorted(self.particles[inplist[0]].daughters)== \
                       sorted(self.particles[inplist[1]].daughters)
                self.signalPartons = self.particles[inplist[0]].daughters

            if i in self.signalPartons:
                self.signalTree.add(i)
                self.signalTree.update(particle.daughters)
            else:
                if i in self.signalTree or len(self.signalTree.intersection(particle.mothers))>0:
                    self.signalTree.add(i)
                    self.signalTree.update(particle.daughters)
                else:
                    self.isr.add(i)


    
    def __str__(self):
        result =  '{0:>5s}{1:>5s}{2:>8s}'.format("idx","sta","pdg")
        result +=  '{0:>5s}{1:>5s}{2:>5s}{3:>5s}'.format("mo1","mo2","da1","da2")
        result +=  '{0:>7s}{1:>7s}{2:>7s}\n'.format("pT","phi","eta")
        for p in self.particles:
            result += p.__str__() + "\n"
        return result[:-1]

def findGenParticle(eh,pdg,useCharge=False):
    result = [ ]
    gpPdgs = eh.get("gpPdg")
    for i in range(eh.get("ngp")):
        p = gpPdgs[i]
        if useCharge:
            p = abs(p)
        if int(p)==pdg:
            result.append(i)
    return result

def findDaughtersByMother(eh,iMo):
    ngp = eh.get("ngp")
    gpMo1s = eh.get("gpMo1")

    result = [ ]
    for i in range(iMo+1,ngp):
        if int(gpMo1s[i])==iMo:
            result.append(i)
    return result
    
def findDaughters(eh,iMo,status=-1,pdg=0):
    ngp = eh.get("ngp")
    gpDa1s = eh.get("gpDa1")
    gpDa2s = eh.get("gpDa2")
    gpStas = eh.get("gpSta")

    gpPdgs = eh.get("gpPdg")
    gpMo1s = eh.get("gpMo1")
#    for i in range(ngp):
#        print "{0:3d}  {1:6d} {2:2d}  {3:3d}  {4:3d} - {5:3d}".format(i,int(gpPdgs[i]),int(gpStas[i]), \
#                                                                          int(gpMo1s[i]), \
#                                                                          int(gpDa1s[i]),int(gpDa2s[i]))

    result = [ ]
    indices = [ iMo ]
    iread = 0
    while len(indices)>iread:
#        print iread,indices
        ind = indices[iread]
        iread += 1
#        print "checking ",ind,gpPdgs[ind],gpStas[ind],gpDa1s[ind],gpDa2s[ind]
        ifrom = int(gpDa1s[ind])
        ito = int(gpDa2s[ind])
        if ifrom<0 or ito<0:
            newIndices = findDaughtersByMother(eh,ind)
#            print " by mother",newIndices
            if not newIndices:
                continue
        else:
#            print " by daughter",ifrom,ito
            assert ito<ngp
            newIndices = range(ifrom,ito+1)
        for i in newIndices:
            if ( status<0 or int(gpStas[i])==status ) and ( pdg==0 or int(gpPdgs[i])==pdg ):
#                print "adding to result ",i 
                result.append(i)
            else:
                indices.append(i)
#        print  iread,indices
#    print "result = ",result
    return result

class IsrReweighting:
    def __init__(self):
        self.ptLimitsWJets = [ 200., 250., 350., 450., 650., 800. ]
        self.wgtsWJets = { 0:  [ 1.008, 1.063, 0.992, 0.847, 0.726, 0.649 ], \
                               -13: [ 1.016, 1.028, 0.991, 0.842, 0.749, 0.704 ], \
                               13: [ 0.997, 1.129, 1.003, 0.870, 0.687, 0.522 ] }

    def isrWeightWJets(self,eh,imu,pdg=0):
        ptw = eh.get("muWPt")[imu]
        for i in range(len(self.ptLimitsWJets)-1,-1,-1):
            if ptw>self.ptLimitsWJets[i]:
                return self.wgtsWJets[pdg][i]
        return 1.

    def ptWeightTT(self,eh):
        gpPt = eh.get("gpPt")
        assert len(gpPt)>=8
        gpPdg = eh.get("gpPdg")
        assert abs(gpPdg[6])==6 and abs(gpPdg[7])==6 and gpPdg[6]*gpPdg[7]<0
        return 1.24*exp(0.156-0.5*0.00137*(gpPt[6]+gpPt[7]))

    def isrWeightDY(self,zpt):
        return exp(6.83960e-02-9.71095e-04*zpt)
