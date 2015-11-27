import os

class DatasetBase:

    def __init__(self,dataBase=None,elistBase=None,sampleDir=None):
        assert os.path.isdir(dataBase)
        self.sampleBase = dataBase + sampleDir
        assert os.path.isdir(self.sampleBase)

        assert os.path.isdir(elistBase)
        self.elistBase = os.path.join(elistBase,os.path.split(os.path.normpath(self.sampleBase))[-1])
        if not os.path.isdir(self.elistBase):
            assert not os.path.exists(self.elistBase)
            os.mkdir(self.elistBase,0744)

                        
    def add(self,sample):
        self.samples.append(sample)
