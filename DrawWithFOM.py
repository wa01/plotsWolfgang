import ROOT
import ctypes
from math import *
import sys

class DrawWithFOM:

    def __init__(self,options):
        self.systematics = 0.05
        if options.fom!=None:
            self.fom = options.fom.lower()
        else:
            self.fom = options.fom
        self.fitRatio = options.fitRatio
        self.luminosity = options.luminosity
        
    def getIntegralWithError(self,h):
        sum = 0.
        esum = 0.
        for i in range(h.GetNbinsX()+1):
            sum += h.GetBinContent(i)
            esum += h.GetBinError(i)**2
        return ( sum, sqrt(esum) )
        
    def getFom(self,h1,h2,scut,syst=0.):
        hr = h1.Clone(h1.GetName()+"R")
        hr.Reset()
        if scut=="u": 
            i1,i2,i3,ioff = 1,h1.GetNbinsX(),1,1
        elif scut=="l": 
            i1,i2,i3,ioff = h1.GetNbinsX()-1,0,-1,0
        elif scut=="b": 
            i1,i2,i3,ioff = 1,h1.GetNbinsX(),1,0
        s, b, es, eb = [ 0 ]*4
        if h2.InheritsFrom(ROOT.THStack.Class()):
            hsum = h2.GetStack().Last().Clone()
        else:
            hsum = h2.Clone()
        lastFOM = None
        show = h1.GetName().find("njet60")>-1
        for i in range(i1,i2,i3):
            if scut=="b":
                s, b, es, eb = [ 0 ]*4
            s += h1.GetBinContent(i)
            es += h1.GetBinError(i)**2
            b += hsum.GetBinContent(i)
            eb += hsum.GetBinError(i)**2
            fom = None
            if b>1.e-9:
                if self.fom=="sob":
                    fom = s/b
                elif self.fom=="sosqrtb":
                    if syst<1.e-9:
                        fom = s/sqrt(b)
                    else:
                        fom = s/sqrt(b+pow(syst*b,2))
            if fom!=None:
                hr.SetBinContent(i+ioff,fom)
                lastFOM = fom
#                hr.SetBinContent(i+ioff,s/b)
#                hr.SetBinError(i+ioff,sqrt(es**2+(eb*s/b)**2)/b)

        btot, ebtot = 0, 0
        stot, estot = 0, 0
        for i in range(h1.GetNbinsX()+2):
            btot += hsum.GetBinContent(i)
            ebtot += hsum.GetBinError(i)**2
            stot += h1.GetBinContent(i)
            estot += h1.GetBinError(i)**2
        ebtot = sqrt(ebtot)
        estot = sqrt(estot)
        line = "*** "+hr.GetName().ljust(20)
#        line += " s,b {0:7.2f} {1:7.2f}".format(h1.GetSumOfWeights(),hsum.GetSumOfWeights())
        line += " s {0:7.2f} +- {1:5.2f}".format(stot,estot)
        line += " b {0:7.2f} +- {1:5.2f}".format(btot,ebtot)
        if lastFOM!=None:
            line += " total "+self.fom+" = {0:7.3f}".format(lastFOM)
        print line
#        print h1.GetSumOfWeights(),hsum.GetSumOfWeights()
        return hr

    def getDoMC(self,h1,h2):
        hr = h1.Clone(h1.GetName()+"DoMC")
        hrmc = h1.Clone(h1.GetName()+"DoMCMC")
        if h2.InheritsFrom(ROOT.THStack.Class()):
            hsum = h2.GetStack().Last().Clone()
        else:
            hsum = h2.Clone()
        hr.Reset()
        hrmc.Reset()
        for i in range(1,hr.GetNbinsX()+1):
            d = h1.GetBinContent(i)
            ed = h1.GetBinError(i)
            b = hsum.GetBinContent(i)
            eb = hsum.GetBinError(i)
            if b>0:
                hr.SetBinContent(i,d/b)
                hr.SetBinError(i,sqrt((ed)**2+(eb*d/b)**2)/b)
                hrmc.SetBinContent(i,1.)
                hrmc.SetBinError(i,eb/b)
        return hr,hrmc


    def drawStack1D(self, samples, histograms, pad=None, sumDict=None):

        if pad!=None:
            pad.cd()

        allEmpty = True

        data = None
        bkgs = None
        sigs = [ ]
        latexs = [ ]
        legend = ROOT.TLegend(0.60,0.75,0.90,0.99)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        for i,s in enumerate(samples):
            h = histograms[i]
            if h.GetSumOfWeights()>1.e-6:
                allEmpty = False
            if s.fill:
                h.SetFillStyle(1001)
                h.SetFillColor(s.color)
                if s.hatch:
                    h.SetFillStyle(s.hatch)
            else:
                h.SetLineColor(s.color)
                h.SetLineStyle(s.line)
                if s.hatch:
                    h.SetFillStyle(s.hatch)
                else:
                    h.SetLineWidth(3)
            hname = h.GetName()
            if s.isBackground():
                if bkgs==None:
#                    print "Defining background ",s.name,hname
                    bkgs = ROOT.THStack()
                    bkgs.SetNameTitle(hname,h.GetTitle())
                opt = "hist "
                if s.fill:
                    opt += "F"
#                print s.name,hname,opt
                bkgs.Add(h,opt)
                integ, einteg = self.getIntegralWithError(h)
                print "   ",hname.ljust(10),s.name.ljust(30),"{0:9.2f} +- {1:7.2f}".format(integ,einteg)
                if sumDict!=None:
                    if not hname in sumDict:
                        sumDict[hname] = { }
                    sumDict[hname][s.name] = ( integ, einteg )
#                print "Adding to background ",s.name,hname,opt
#                if s.name.startswith("W"):
#                    print s.name," contents ",h.GetSumOfWeights()
            elif s.isSignal():
                sigs.append(h)
                integ, einteg = self.getIntegralWithError(h)
                print "   ",hname.ljust(10),s.name.ljust(30),"{0:9.2f} +- {1:7.2f}".format(integ,einteg)
                if sumDict!=None:
                    if not hname in sumDict:
                        sumDict[hname] = { }
                    sumDict[hname][s.name] = ( integ, einteg )
#                print "Adding to signal ",s.name,hname
            elif s.isData():
                data = h
                integ, einteg = self.getIntegralWithError(h)
                print "   ",hname.ljust(10),s.name.ljust(30),"{0:9.2f} +- {1:7.2f}".format(integ,einteg)
                if sumDict!=None:
                    if not hname in sumDict:
                        sumDict[hname] = { }
                    sumDict[hname][s.name] = ( integ, einteg )
                h.SetMarkerStyle(20)
                h.SetLineColor(s.color)
                h.SetMarkerColor(s.color)
                
#                print "Adding to signal ",s.name,h.GetName()
            if s.fill:
                opt = "F"
            else:
                opt = "L"
            if s.isData():
                opt = "P"
            if bkgs!=None:
                bkgs.SetMinimum(0.1)
            legend.AddEntry(h,s.name,opt)       

        integ, einteg = self.getIntegralWithError(bkgs.GetStack().Last())
        print "   ",hname.ljust(10)," ".ljust(30),"{0:9.2f} +- {1:7.2f}".format(integ,einteg)

        if allEmpty:
            return ( None, None, None, None, None )

        opt = ""
        if data and data.GetMaximum()>bkgs.GetStack().Last().GetMaximum():
            if ROOT.gPad.GetLogy()>0:
                data.SetMinimum(0.2)
            data.Draw()
            opt = "same"
        if ROOT.gPad.GetLogy()>0:
            bkgs.SetMinimum(0.2)
        bkgs.Draw(opt)
        bkgs.GetYaxis().SetTitle("Events / bin")
        for s in sigs:
            s.Draw("same hist")
        if data:
            data.Draw("same")
        legend.Draw()
        legend.SetBit(ROOT.kCanDelete)
#        ROOT.gPad.SetLogy(1)

        hdr1 = ROOT.TLatex(0.10,1.01,"CMS preliminary")
        hdr1.SetNDC()
        hdr1.SetTextAlign(11)
        hdr1.SetTextFont(62)
        hdr1.SetTextSize(0.038)
        hdr1.Draw()
        hdr1.SetBit(ROOT.kCanDelete)
        latexs.append(hdr1)

        hdr2 = ROOT.TLatex(0.90,1.01,"{0:d}TeV, {1:4.2f}".format(13,self.luminosity/1000.)+" fb^{-1}")
        hdr2.SetNDC()
        hdr2.SetTextAlign(31)
        hdr2.SetTextFont(62)
        hdr2.SetTextSize(0.038)
        hdr2.Draw()
        hdr2.SetBit(ROOT.kCanDelete)
        latexs.append(hdr2)
        
#        print "Frame",ROOT.gPad.GetXlowNDC(),ROOT.gPad.GetYlowNDC(), \
#            ROOT.gPad.GetWNDC(),ROOT.gPad.GetHNDC()
#        print "  frame",ROOT.gPad.GetLeftMargin(),ROOT.gPad.GetRightMargin(), \
#            ROOT.gPad.GetTopMargin(),ROOT.gPad.GetBottomMargin()
#        print ROOT.gPad.GetXlowNDC()+ROOT.gPad.GetLeftMargin()*ROOT.gPad.GetWNDC()
#        print ROOT.gPad.GetXlowNDC()+(1-ROOT.gPad.GetRightMargin())*ROOT.gPad.GetWNDC()
#        print ROOT.gPad.GetYlowNDC()+(1-ROOT.gPad.GetTopMargin())*ROOT.gPad.GetHNDC()

        if pad!=None:
            pad.Update()

        print data, bkgs, sigs, legend, latexs
        return ( data, bkgs, sigs, legend, latexs )

    def drawStack2D(self, samples, histograms, pad=None):

        if pad!=None:
            currpad = pad
            pad.cd()
        else:
            currpad = ROOT.gPad

        data = None
        bkgs = None
        sigs = [ ]
#        legend = ROOT.TLegend(0.60,0.75,0.90,0.89)
#        legend.SetBorderSize(0)
#        legend.SetFillColor(10)
#        legend.SetFillStyle(0)
        for i,s in enumerate(samples):
            h = histograms[i]
            if s.fill:
                h.SetFillStyle(1001)
                h.SetFillColor(s.color)
            else:
                h.SetLineColor(s.color)
                h.SetLineWidth(3)
            if s.isBackground():
                if bkgs==None:
#                    print "Defining background ",s.name,h.GetName()
                    bkgs = ROOT.THStack()
                    bkgs.SetNameTitle(h.GetName(),h.GetTitle())
                opt = "hist "
                if s.fill:
                    opt += "F"
                bkgs.Add(h,opt)
#                print "Adding bkg histo for ",s.name,h.GetName()
#                legend.SetHeader("Backgrounds")
            elif s.isSignal():
                h.SetLineColor(s.color)
                h.SetLineWidth(1)
                sigs.append(h)
                h.SetTitle(s.name)
#                legend.AddEntry(h,s.name,"L")
                print "Sig histo from ",s.name,h.GetName()
#                print "Adding to signal ",s.name,h.GetName()
#            if s.fill:
#                opt = "F"
#            else:
#                opt = "L"
            elif s.isData():
                data = h
                h.SetTitle("Data")

        nsig = 0
        for s in samples:
            if s.isSignal():  
                nsig += 1
        nsub = int(sqrt(nsig+2))
        if nsub**2<(nsig+2):
            nsub += 1
        currpad.Divide(nsub,nsub)
        latexs = [ ]
        latex = ROOT.TLatex()
        latex.SetNDC(1)
        latex.SetTextSize(0.04)

        currpad.cd(1)
        ROOT.gPad.SetRightMargin(0.15)
        # common maximum (from sum of histograms)
        bkgmax = bkgs.GetStack().Last().GetMaximum()
        bkgs.SetMaximum(bkgmax/0.85)
        bkgs.SetMinimum(0.1)
        for sh in bkgs.GetHists():
            sh.SetMaximum(bkgmax/0.85)
            sh.SetMinimum(0.1)
        for sh in bkgs.GetStack():
            sh.SetMaximum(bkgmax/0.85)
            sh.SetMinimum(0.1)
        # draw all histograms in stack 
        #   (just a workaround to store the individual histograms in the canvas)
        bkgs.Draw("zcol")
        # overwrite with the sum (last histogram in stack)
        bkgs.GetStack().Last().SetFillStyle(0)
        bkgs.GetStack().Last().Draw("zcol same")
        latexs.append(latex.DrawLatex(0.40,0.15,"Backgrounds"))
#        bkgs.GetYaxis().SetTitle("Events / bin")
#        contlist = [ bkgmax/0.85*10**(-i) for i in range(2,5) ]
#        c_contlist = ((ctypes.c_double)*(len(contlist)))(*contlist)
#        legend.Draw()
#        legend.SetBit(ROOT.kCanDelete)
        ROOT.gPad.SetLogz(1)

        if data!=None:
            currpad.cd(2)
            ROOT.gPad.SetRightMargin(0.15)
            data.SetMaximum(bkgmax/0.85)
            data.SetMinimum(0.1)
            data.Draw("zcol")
            print "DataEntries: ",data.GetName(),data.GetTitle(),data.GetEntries()
            latexs.append(latex.DrawLatex(0.40,0.15,"Data"))
            ROOT.gPad.SetLogz(1)

        for i,s in enumerate(sigs):
##            s.SetMaximum(bkgmax/0.85)
##            s.SetMinimum(0.1)
##            s.SetContour(len(contlist),c_contlist)
##            s.SetLineWidth(2)
##            s.Draw("cont3 same")
            currpad.cd(i+3)
            ROOT.gPad.SetRightMargin(0.15)
#            bkgs.DrawClone("zcol")
            s.SetMaximum(bkgmax/0.85)
            s.SetMinimum(0.1)
            s.Draw("zcol")
            latexs.append(latex.DrawLatex(0.40,0.15,s.GetTitle()))
            ROOT.gPad.SetLogz(1)
            print "Drawing signal index ",i,currpad.GetPad(i+2)

        hdr1 = ROOT.TLatex(0.10,1.01,"CMS preliminary")
        hdr1.SetNDC()
        hdr1.SetTextAlign(13)
        hdr1.SetTextFont(62)
        hdr1.SetTextSize(0.038)
        hdr1.Draw()
        hdr1.SetBit(ROOT.kCanDelete)
        latexs.append(hdr1)

        hdr2 = ROOT.TLatex(0.90,1.01,"{0:d}TeV, {1:4.2f}".format(13,self.luminosity/1000.)+" fb^{-1}")
        hdr2.SetNDC()
        hdr2.SetTextAlign(33)
        hdr2.SetTextFont(62)
        hdr2.SetTextSize(0.038)
        hdr2.Draw()
        hdr2.SetBit(ROOT.kCanDelete)
        latexs.append(hdr2)
        
        if pad!=None:
            pad.Update()

        currpad.cd()
        currpad.Update()

        return ( data, bkgs, sigs, latexs )

    def drawFom(self, bkgs, sigs, scut='l', pad=None):

        if self.fom==None:
            return

        assert bkgs!=None

        if pad!=None:
            pad.cd()

        opt = ""
        hrs = [ ]
        hrmax = 0.
        for s in sigs:
            hr = self.getFom(s,bkgs,scut,self.systematics)
#            hrs.append(hr)
            if hr.GetMaximum()>hrmax:
                hrmax = hr.GetMaximum()
            if opt=="":
                hr.GetYaxis().SetTitle("S/B")
                hr.GetYaxis().SetTitleSize(0.08)
            hrs.append(hr.DrawCopy(opt+"hist"))
            opt = "same "
        if len(hrs)>0:
            hrs[0].SetMaximum(hrmax/0.85)

        pad.Update()

    def drawDoMC(self, data, bkgs, otherObjects, pad=None):

        assert data!=None and bkgs!=None

        if pad!=None:
            pad.cd()

        opt = ""
        hr,hrmc = self.getDoMC(data,bkgs)
        print hr,hr.GetBinContent(10),hr.GetBinError(10)
        hrmc.SetMinimum(0.)
        hrmc.SetMaximum(2.)
        hrmc.GetYaxis().SetTitle("data/MC")
        hrmc.GetYaxis().SetTitleSize(0.08)
        hrmc.SetMarkerStyle(1)
        hrmc.SetFillColor(18)
        hrmc.DrawCopy("E2")
        hr.SetMinimum(0.)
        hr.SetMaximum(2.)
        hr.GetYaxis().SetTitle("data/MC")
        hr.GetYaxis().SetTitleSize(0.08)
        hr.SetMarkerStyle(20)
        hr.SetMarkerColor(1)
        hr.SetLineColor(1)
        hr.DrawCopy("same")
        if self.fitRatio and hr.GetNbinsX()>1:
#            hr.Fit("pol1","","0")
            fitGraphs = self.fitRatioHistogram(hr,"pol1")
            if fitGraphs!=None:
                for g in fitGraphs:
                    g.Draw("c")
                    g.SetBit(ROOT.kCanDelete)
                    otherObjects.append(g)
        ROOT.gPad.SetGridx(1)
        ROOT.gPad.SetGridy(1)

        pad.Update()

    def evaluatePol1(self,x,pars,cov):
        return ( pars[0]+x*pars[1], \
                 sqrt(cov(0,0)+2*x*cov(1,0)+x*x*cov(1,1)) )

    def fitEnvelopePol1(self,hr,pars,cov):
        result = ( ROOT.TGraph(), ROOT.TGraph(), ROOT.TGraph() )
        result[1].SetLineStyle(2)
        result[2].SetLineStyle(2)
        axis = hr.GetXaxis()
        for i in range(axis.GetNbins()+1):
            x = axis.GetBinUpEdge(i)
            y,ey = self.evaluatePol1(x,pars,cov)
            result[0].SetPoint(i,x,y)
            result[1].SetPoint(i,x,y-ey)
            result[2].SetPoint(i,x,y+ey)
        return result
            
    def fitRatioHistogram(self,hr,func):
        if func!="pol1":
            return None
        print "Starting fit",hr.GetName()
        sys.stdout.flush()
        fitResult = hr.Fit(func,"SN0")
        print fitResult
        print fitResult.Status(),fitResult.IsValid()
        sys.stdout.flush()
        if fitResult and fitResult.IsValid():
            npars = fitResult.NPar()
            pars = fitResult.Parameters()
            cov = fitResult.GetCovarianceMatrix()
            print pars
            print sqrt(cov(0,0)),cov(1,0),sqrt(cov(1,1))
            print fitResult.ParError(0),fitResult.ParError(1)
            graphs = self.fitEnvelopePol1(hr,pars,cov)
            return graphs
        return None
