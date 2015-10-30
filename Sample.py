import ROOT
import os

class Sample:

    def __init__(self,name,base,namelist=None,title=None,type="B",color=1,fill=False,line=1,hatch=None, \
                     downscale=1,filter=None,extension=False,kfactor=1.,baseweights=1.):
        self.name = name
        if namelist==None or namelist==[ ]:
            self.names = [ name ]
            nproc = self.getCmgInputStat(base,name)
            self.baseweights = [ float(baseweights)/nproc ]
        else:
            self.names = namelist
            self.baseweights = [ ]
            bwList = hasattr(baseweights,"__iter__")
            if bwList:
                assert len(namelist)==len(baseweights)
            for i,n in enumerate(namelist):
                nproc = self.getCmgInputStat(base,namelist[i])
                if bwList:
                    self.baseweights.append(float(baseweights[i])/nproc)
                else:
                    self.baseweights.append(float(baseweights)/nproc)
        self.title = title if title!=None else name
        self.base = base
        self.type = type
        self.color = color
        self.fill = fill
        self.line = line
        self.hatch = hatch
        self.downscale = downscale
        self.filter = filter
        self.file = None
        self.fileindex = None
        self.extweight = kfactor
        if extension:
            self.extweight /= len(namelist)
        print "Created sample",name,"with",self.names

    def getCmgInputStat(self,base,name):
        nproc = None
        for l in open(base+"/"+name+"/skimAnalyzerCount/SkimReport.txt"):
            fields = l[:-1].split()
            if len(fields)==5 and fields[0]=="All" and fields[1]=="Events":
                nproc = int(fields[2])
                break
        assert nproc!=None
        return nproc
        
    def fullname(self,name):
        return self.base+"/"+name+"/treeProducerSusySingleLepton/tree.root"

    def getchain(self,ind=0):
        assert ind>=0 and ind<len(self.names)
        if self.fileindex==None or self.fileindex!=ind:
            if self.file!=None:
                self.file.Close()
            n = self.names[ind]
            self.file = ROOT.TFile(self.fullname(n))
        result = self.file.Get("tree")
        return result

#        result = ROOT.TChain("Events")
#        for n in self.names:
#            result.Add(self.base+"/"+n+"/*.root")
#        print self.name," nr. of chains ",result.GetNtrees()
#        return result
    
    def getentries(self,chain):
        return range(0,chain.GetEntries(),self.downscale)
    
    def isBackground(self):
        return len(self.type)>0 and self.type.lower()[0]=="b"

    def isSignal(self):
        return len(self.type)>0 and self.type.lower()[0]=="s"

    def isData(self):
        return len(self.type)>0 and self.type.lower()[0]=="d"

