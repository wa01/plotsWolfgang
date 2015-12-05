import sys
# Based on http://stackoverflow.com/questions/3160699/python-progress-bar
# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
class ProgBar:

    def __init__(self,barLength=60):
        self.barLength = barLength
        self.reset()

    def reset(self):
        self.length = None
        self.pos = None
        self.status = 0
        
    def initialize(self,length=1.,title=None):
        self.reset()
        self.length = length
        self.pos = 0
        if title!=None:
            print title
        self.status = 1

    def halt(self):
        self.update(-1.)

    def increment(self,delta=1):
        self.pos += delta
        self.update(self.pos/float(self.length))
        self.status = 2

    def update(self,progress):
        status = ""
        if isinstance(progress, int):
            progress = float(progress)
        if not isinstance(progress, float):
            progress = 0
            status = "error: progress var must be float\r\n"
        if progress < 0:
            progress = 0
            status = "Halt...\r\n"
            self.status = 3
        if progress >= 1:
            progress = 1
            status = "Done...\r\n"
            self.status = 3
        block = int(round(self.barLength*progress))
        text = "\rPercent: [{0}] {1:7.2%} {2}".format( "#"*block + "-"*(self.barLength-block), progress, status)
        sys.stdout.write(text)
        sys.stdout.flush()

    def isInitialized(self):
        return self.status>=1

    def isActive(self):
        return self.status==2

    def hasTerminated(self):
        return self.status==3
