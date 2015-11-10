import ROOT
from EventHelper import EventHelper


class EventReweighting:

    def __init__(self,variable,histogram):
        self.variable = variable
        self.histogram = histogram
        self.axis = self.histogram.GetXaxis()
        self.nbins = self.axis.GetNbins()

    def weight(self,eh):
        value = eh.get(self.variable)
        ibin = self.axis.FindBin(value)
        if ibin<1 or ibin>self.nbins:
            return 1.
        else:
            return self.histogram.GetBinContent(ibin)

