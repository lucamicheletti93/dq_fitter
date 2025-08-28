#from telnetlib import DO
import os
import re
import ROOT
from ROOT import TCanvas, TFile, TH1F, TPaveText, RooRealVar, RooDataSet, RooWorkspace, RooDataHist, RooArgSet
from ROOT import gPad, gROOT
from utils.plot_library import DoResidualPlot, DoPullPlot, DoCorrMatPlot, DoAlicePlot, LoadStyle
from utils.utils_library import ComputeSigToBkg, ComputeSignificance, ComputeAlpha

class DQFitter:
    def __init__(self, fInName, fInputName, fOutPath, minDatasetRange, maxDatasetRange, ME_norm, tailHistName, fitMethod):
        self.fPdfDict          = {}
        self.tailRootFileName  = "" 
        self.tailHistName      = "" 
        self.fOutPath          = fOutPath
        self.fFileOutName      = "{}/output__{}_{}_{}.root".format(fOutPath, minDatasetRange, maxDatasetRange, ME_norm)
        self.fFileOut          = TFile(self.fFileOutName, "RECREATE")
        self.fFileIn           = TFile.Open(fInName)
        self.fInputName        = fInputName
        self.fInput            = 0
        self.fRooWorkspace     = RooWorkspace('w','workspace')
        self.fParNames         = []
        self.fFitMethod        = fitMethod
        self.fFitRangeMin      = minDatasetRange
        self.fFitRangeMax      = maxDatasetRange
        self.fMe_norm          = ME_norm
        self.fTrialName        = ""
        self.fMinDatasetRange  = minDatasetRange
        self.fMaxDatasetRange  = maxDatasetRange
        self.fRooMass          = RooRealVar("fMass", "#it{M} (GeV/#it{c}^{2})", self.fMinDatasetRange, self.fMaxDatasetRange)
        self.fDoResidualPlot   = False
        self.fDoPullPlot       = False
        self.fDoCorrMatPlot    = False
        self.fFileOutNameNew   = ""

    def GetFileOutName(self):
        return self.fFileOutNameNew
    
    def GetFitResult(self):
        return self.rooFitRes

    def SetFitConfig(self, pdfDict, tailRootFileName, tailHistName):
        '''
        Method set the configuration of the fit
        '''
        self.fPdfDict = pdfDict
        if tailRootFileName is not None and tailHistName is not None:

            self.tailFile = ROOT.TFile(tailRootFileName, "READ") #name of root file used for fixed parameters in the fit (tail parameters)
            self.tailHist = self.tailFile.Get(tailHistName) #name of histogram used for fixed parameters in the fit (tail parameters)

            self.tailFile = ROOT.TFile(tailRootFileName, "READ")
            self.tailHist = self.tailFile.Get(tailHistName)

        else:
            self.tailFile = None
            self.tailHist = None

        # Exception to take into account the case in which AnalysisResults.root is used
        if "analysis-same-event-pairing/output" in self.fInputName:
            hlistIn = self.fFileIn.Get("analysis-same-event-pairing/output")
            listName = self.fInputName.replace("analysis-same-event-pairing/output/", "")
            listIn = hlistIn.FindObject(listName.replace("/Mass", ""))
            self.fInput = listIn.FindObject("Mass")
        else:
            self.fInput = self.fFileIn.Get(self.fInputName)

        if not "TTree" in self.fInput.ClassName():
            self.fInput.Rebin(pdfDict["rebin"])
            self.fInput.Sumw2()
        self.fDoResidualPlot = pdfDict["doResidualPlot"]
        self.fDoPullPlot = pdfDict["doPullPlot"]
        self.fDoCorrMatPlot = pdfDict["doCorrMatPlot"]
        pdfList = []
        for pdf in self.fPdfDict["pdf"][:-1]:
            self.fTrialName = self.fTrialName + pdf + "_"
        #if "analysis-same-event-pairing/output" in self.fInputName:
            #self.fTrialName = listName.replace("/Mass", "") + "_" + self.fTrialName + pdf + "_"
        #else:
            #self.fTrialName = self.fInputName + "_" + self.fTrialName + pdf + "_"
        for i in range(0, len(self.fPdfDict["pdf"])):
            if not self.fPdfDict["pdf"][i] == "SUM":
                gROOT.ProcessLineSync(".x ../fit_library/{}Pdf.cxx+".format(self.fPdfDict["pdf"][i]))
        
        if tailRootFileName is not None and tailHistName is not None:
            fileTails = TFile(tailRootFileName, "READ")
            hTails = fileTails.Get(tailHistName) #this histogram contains all tail parameters from the extraction: 1 and 2 are free, the tails come after

        for i in range(0, len(self.fPdfDict["pdf"])):
        
            parName = self.fPdfDict["parName"][i]
            parVal = [0]*len(parName) #define an array for the parValues of the pdf
            parLimMin = [0]*len(parName)
            parLimMax = [0]*len(parName)

            for j in range(0, len(parName)):
                if not "@" in parName[j]: #if the parameter name does not contain @, then it is free and taken from the configuration file
                    parVal[j]    = self.fPdfDict["parVal"][i][j]
                    parLimMin[j] = self.fPdfDict["parLimMin"][i][j]
                    parLimMax[j] = self.fPdfDict["parLimMax"][i][j]
                    print(j, parVal[j], parLimMin[j], parLimMax[j])

                else:  #if the parameter name contains @, then its value is taken from the root file and ixed (same value for max and min)
                    binNumberRoot = hTails.GetXaxis().FindBin(parName[j].strip("@")) #remove @ from parameter name to correctly retrieve it from root file
                    parVal[j]    = hTails.GetBinContent(binNumberRoot)
                    parLimMin[j] = hTails.GetBinContent(binNumberRoot)
                    parLimMax[j] = hTails.GetBinContent(binNumberRoot)
                    print(j, parVal[j], parLimMin[j], parLimMax[j])

                parName[j] = parName[j].strip("@") #remove @ from all parNames to avoid problems in the next parts of the code

            if not len(parVal) == len(parLimMin) == len(parLimMax) == len(parName):
                print("WARNING! Different size if the input parameters in the configuration")
                print(parVal)
                print(parLimMin)
                print(parLimMax)
                print(parName)
                exit()

            if not self.fPdfDict["pdf"][i] == "SUM":
                # Filling parameter list
                for j in range(0, len(parVal)):
                    if ("sum" in parName[j]) or ("prod" in parName[j]):
                        self.fRooWorkspace.factory("{}".format(parName[j]))
                        parNameOr = parName[j]
                        # Replace the exression of the parameter with the name of the parameter
                        r1 = parName[j].find("::") + 2
                        r2 = parName[j].find("(", r1)
                        parName[j] = parName[j][r1:r2]
                        self.fRooWorkspace.factory("{}[{}]".format(parName[j], parVal[j]))
                        
                        start = parNameOr.find(",") + 1
                        end = parNameOr.find(")", start)
                        val_str = parNameOr[start:end].strip()
                        #val_str = parNameOr[start:end].strip().replace(".", "")

                        if "mean" in parName[j]:
                            self.fMean = val_str
                        elif "width" in parName[j]:
                            self.fWidth = val_str
                
                    else:
                        if (parLimMin[j] == parLimMax[j]):
                            self.fRooWorkspace.factory("{}[{}]".format(parName[j], parVal[j]))
                        else:
                            self.fRooWorkspace.factory("{}[{},{},{}]".format(parName[j], parVal[j], parLimMin[j], parLimMax[j]))

                        self.fParNames.append(parName[j]) # only free parameters will be reported in the histogram of results

                # Define the pdf associating the parametes previously defined
                nameFunc = self.fPdfDict["pdf"][i]
                nameFunc += "Pdf::{}Pdf(fMass[{},{}]".format(self.fPdfDict["pdfName"][i], self.fMinDatasetRange, self.fMaxDatasetRange)
                pdfList.append(self.fPdfDict["pdfName"][i])
                for j in range(0, len(parVal)):
                    nameFunc += ",{}".format(parName[j])
                nameFunc += ")"
                self.fRooWorkspace.factory(nameFunc)
            else:
                nameFunc = self.fPdfDict["pdf"][i]
                nameFunc += "::sum("
                for j in range(0, len(pdfList)):
                    nameFunc += "{}[{},{},{}]*{}Pdf".format(parName[j], parVal[j], parLimMin[j], parLimMax[j], pdfList[j])
                    self.fParNames.append(parName[j])
                    if not j == len(pdfList) - 1:
                        nameFunc += ","
                nameFunc += ")"
                self.fRooWorkspace.factory(nameFunc)


    def CheckSignalTails(self, fitRangeMin, fitRangeMax):
        '''
        Method to plot the signal tail parameters
        '''
        self.fRooWorkspace.Print()
        self.fRooWorkspace.writeToFile("{}_tails.root".format(self.fTrialName))
        ROOT.gDirectory.Add(self.fRooWorkspace)

    def FitInvMassSpectrum(self, fitMethod, fitRangeMin, fitRangeMax, ME_norm, tailRootFileName, tailHistName):
        '''
        Method to perform the fit to the invariant mass spectrum
        '''
        LoadStyle()
        
        trialName = self.fTrialName + f"_{fitRangeMin}_{fitRangeMax}_{self.fMean}_{self.fWidth}"
        if ME_norm is not None:
            trialName += f"_{ME_norm}"

        if "MC" in tailHistName:
            tails = f'MC_tails'
        elif "data" in tailHistName:
            tails = f'data_tails'

        else:
            match = re.search(r"(\d+)MB", tailHistName)
            if match:
                mbName = match.group(0)
                tails = f'_{mbName}'
            else:
                tails = ''

        trialName += f"_{tails}"

        self.fRooWorkspace.Print()
        pdf = self.fRooWorkspace.pdf("sum")
        self.fRooMass.setRange("range", fitRangeMin, fitRangeMax)
        fRooPlot = self.fRooMass.frame(ROOT.RooFit.Title(trialName), ROOT.RooFit.Range("range"))
        fRooPlotExtra = self.fRooMass.frame(ROOT.RooFit.Title(trialName), ROOT.RooFit.Range("range"))
        fRooPlotOff = self.fRooMass.frame(ROOT.RooFit.Title(trialName))
        if "TTree" in self.fInput.ClassName():
            print("########### Perform unbinned fit ###########")
            if self.fPdfDict["sPlot"]["sRun"]:
                sRooVar = RooRealVar(self.fPdfDict["sPlot"]["sVar"], self.fPdfDict["sPlot"]["sVarName"], self.fPdfDict["sPlot"]["sRangeMin"], self.fPdfDict["sPlot"]["sRangeMax"])
                sRooVar.setBins(self.fPdfDict["sPlot"]["sBins"])
            rooDs = RooDataSet("data", "data", RooArgSet(self.fRooMass, sRooVar), ROOT.RooFit.Import(self.fInput))
        else:
            print("########### Perform binned fit ###########")
            rooDs = RooDataHist("data", "data", RooArgSet(self.fRooMass), ROOT.RooFit.Import(self.fInput))

        # Select the fit method
        if fitMethod == "likelyhood":
            print("########### Perform likelyhood fit ###########")
            self.rooFitRes = ROOT.RooFitResult(pdf.fitTo(rooDs, ROOT.RooFit.Range(fitRangeMin,fitRangeMax), ROOT.RooFit.Save()))
        if fitMethod == "chi2":
            print("########### Perform X2 fit ###########")
            self.rooFitRes = ROOT.RooFitResult(pdf.chi2FitTo(rooDs, ROOT.RooFit.Range(fitRangeMin,fitRangeMax),ROOT.RooFit.PrintLevel(-1), ROOT.RooFit.Save()))

        # Code to run sPlot
        if ("TTree" in self.fInput.ClassName()) and self.fPdfDict["sPlot"]["sRun"]:
            sPars = self.fPdfDict["sPlot"]["sPars"]
            sRooPars = []
            for iPar, sPar in enumerate(sPars):
                sRooPars.append(self.fRooWorkspace.var(sPar))

            # TO BE CHECKED: necessary to setConstant the other fit parameters?
            sData = ROOT.RooStats.SPlot("sData", "An SPlot", rooDs, pdf, ROOT.RooArgList(*sRooPars))

            getattr(self.fRooWorkspace, 'import')(rooDs, ROOT.RooFit.Rename("dataWithSWeights"))
            sRooDs = self.fRooWorkspace.data("dataWithSWeights")

            # Create a dataset with sWeights
            dataSw = []
            for iPar, sPar in enumerate(sPars):
                dataSw.append(RooDataSet(sRooDs.GetName(), sRooDs.GetTitle(), sRooDs, sRooDs.get(), "", sPar + "_sw"))

            # Fill histograms with sWeights
            histSw = []
            for iPar, sPar in enumerate(sPars):
                histSw.append(dataSw[iPar].createHistogram(self.fPdfDict["sPlot"]["sVar"]))

            # Write the histograms with sWeights
            self.fFileOut.cd()
            for iPar, sPar in enumerate(sPars):
                histSw[iPar].Write(sPar + "_sw")

        rooDs.plotOn(fRooPlot, ROOT.RooFit.MarkerStyle(20), ROOT.RooFit.MarkerSize(0.6), ROOT.RooFit.Range(fitRangeMin, fitRangeMax))
        pdf.plotOn(fRooPlot, ROOT.RooFit.LineColor(ROOT.kRed+1), ROOT.RooFit.LineWidth(2), ROOT.RooFit.Range(fitRangeMin, fitRangeMax))
        for i in range(0, len(self.fPdfDict["pdf"])):
            if not self.fPdfDict["pdfName"][i] == "SUM":
                pdf.plotOn(fRooPlot, ROOT.RooFit.Components("{}Pdf".format(self.fPdfDict["pdfName"][i])), ROOT.RooFit.LineColor(self.fPdfDict["pdfColor"][i]), ROOT.RooFit.LineStyle(self.fPdfDict["pdfStyle"][i]), ROOT.RooFit.LineWidth(2), ROOT.RooFit.Range(fitRangeMin, fitRangeMax))
        
        reduced_chi2 = 0
        if "TTree" in self.fInput.ClassName():
            # Fit with RooChi2Var
            # To Do : Find a way to get the number of bins differently. The following is a temparary solution.
            # WARNING : The largest fit range has to come first in the config file otherwise it does not work
            # Convert unbinned dataset into binned dataset
            rooDsBinned = RooDataHist("rooDsBinned","binned version of rooDs",RooArgSet(self.fRooMass),rooDs)
            nbinsperGev = rooDsBinned.numEntries() / (self.fPdfDict["fitRangeMax"][0] - self.fPdfDict["fitRangeMin"][0])
            nBins = (fitRangeMax - fitRangeMin) * nbinsperGev
        
            chi2 = ROOT.RooChi2Var("chi2", "chi2", pdf, rooDsBinned, False, ROOT.RooDataHist.SumW2)
            nPars = self.rooFitRes.floatParsFinal().getSize()
            ndof = nBins - nPars
            reduced_chi2 = chi2.getVal() / ndof
        else:
            # Fit with RooChi2Var
            # To Do : Find a way to get the number of bins differently. The following is a temparary solution.
            # WARNING : The largest fit range has to come first in the config file otherwise it does not work
            nbinsperGev = rooDs.numEntries() / (self.fPdfDict["fitRangeMax"][0] - self.fPdfDict["fitRangeMin"][0])
            nBins = (fitRangeMax - fitRangeMin) * nbinsperGev
        
            #chi2 = ROOT.RooChi2Var("chi2", "chi2", pdf, rooDs, False, ROOT.RooDataHist.SumW2)
            #nPars = self.rooFitRes.floatParsFinal().getSize()
            #ndof = nBins - nPars
            #reduced_chi2 = chi2.getVal() / ndof
            reduced_chi2 = 1

        index = 1
        n_extra_bins = 6
        histResults = TH1F("fit_results_{}_{}".format(trialName, self.fInputName), "fit_results_{}_{}".format(trialName, self.fInputName), len(self.fParNames) + n_extra_bins, 0., len(self.fParNames) + n_extra_bins + 1)
        for parName in self.fParNames:
            histResults.GetXaxis().SetBinLabel(index, parName)
            histResults.SetBinContent(index, self.fRooWorkspace.var(parName).getVal())
            histResults.SetBinError(index, self.fRooWorkspace.var(parName).getError())
            index += 1

        histResults.GetXaxis().SetBinLabel(index, "chi2")
        histResults.SetBinContent(index, reduced_chi2)
        index += 1
        extraIndex = index
        print("CHI2: ", reduced_chi2)

        extraText = [] # extra text for "propaganda" plots

        paveText = TPaveText(0.60, 0.45, 0.99, 0.94, "brNDC")
        paveText.SetTextFont(42)
        paveText.SetTextSize(0.025)
        paveText.SetFillColor(ROOT.kWhite)
        for parName in self.fParNames:
            paveText.AddText("{} = {:.4f} #pm {:.4f}".format(parName, self.fRooWorkspace.var(parName).getVal(), self.fRooWorkspace.var(parName).getError()))
            if self.fPdfDict["parForAlicePlot"].count(parName) > 0:
                text = self.fPdfDict["parNameForAlicePlot"][self.fPdfDict["parForAlicePlot"].index(parName)]
                if "sig" in parName:
                    if "Jpsi" in parName:
                        extraText.append("{} = {:.0f} #pm {:.0f}".format(text, self.fRooWorkspace.var(parName).getVal(), self.fRooWorkspace.var(parName).getError()))
                    if "sig_Psi2s" in parName:
                        extraText.append("{} = {:.0f} #pm {:.0f}".format(text, self.fRooWorkspace.function(parName).getVal(), self.fRooWorkspace.function(parName).getError()))
                else:
                    if "Psi2s" in parName:
                        extraText.append("{} = {:.4f} #pm {:.4f}".format(text, self.fRooWorkspace.function(parName).getVal(), self.fRooWorkspace.function(parName).getError()))
                    else:
                        extraText.append("{} = {:.4f} #pm {:.4f}".format(text, self.fRooWorkspace.var(parName).getVal(), self.fRooWorkspace.var(parName).getError()))
            for i in range(0, len(self.fPdfDict["pdfName"])):
                if self.fPdfDict["pdfName"][i] in parName:
                    (paveText.GetListOfLines().Last()).SetTextColor(self.fPdfDict["pdfColor"][i])

        # Add the chiSquare value
        paveText.AddText("n Par = %3.2f" % (nPars)) 
        paveText.AddText("n Bins = %3.2f" % (nBins))
        paveText.AddText("#bf{#chi^{2}/dof = %3.2f}" % reduced_chi2)
      
        fRooPlot.addObject(paveText)
        extraText.append("#chi^{2}/dof = %3.2f" % reduced_chi2)
     
        # Fit plot
        canvasFit = TCanvas("fit_plot_{}_{}".format(trialName, self.fInputName), "fit_plot_{}_{}".format(trialName, self.fInputName), 800, 600)
        canvasFit.SetLeftMargin(0.15)
        gPad.SetLeftMargin(0.15)
        fRooPlot.GetYaxis().SetTitleOffset(1.4)
        fRooPlot.Draw()

        for parName in self.fPdfDict["parForAlicePlot"]:
            if "sOverB_Jpsi" in parName:
                sig_mean = self.fRooWorkspace.var("mean_Jpsi").getVal()
                sig_width = self.fRooWorkspace.var("width_Jpsi").getVal()
                sigForIntegral = self.fRooWorkspace.var("sig_Jpsi").getVal()
                bkgForIntegral = self.fRooWorkspace.var("bkg").getVal()
                min_range = sig_mean - 3. * sig_width
                max_range = sig_mean + 3. * sig_width
                sig_to_bkg = ComputeSigToBkg(canvasFit, "JpsiPdf", "BkgPdf", sigForIntegral, bkgForIntegral, min_range, max_range)
                extraText.append("S/B_{3#sigma, J/#psi} = %5.4f" % sig_to_bkg)
                histResults.GetXaxis().SetBinLabel(extraIndex, "sOverB_Jpsi")
                histResults.SetBinContent(extraIndex, sig_to_bkg)
                extraIndex += 1
            if "sOverB_Psi2s" in parName:
                sig_mean = self.fRooWorkspace.function("mean_Psi2s").getVal()
                sig_width = self.fRooWorkspace.function("width_Psi2s").getVal()
                sigForIntegral = self.fRooWorkspace.var("sig_Psi2s").getVal()
                bkgForIntegral = self.fRooWorkspace.var("bkg").getVal()
                min_range = sig_mean - 3. * sig_width
                max_range = sig_mean + 3. * sig_width
                sig_to_bkg = ComputeSigToBkg(canvasFit, "Psi2sPdf", "BkgPdf", sigForIntegral, bkgForIntegral, min_range, max_range)
                extraText.append("S/B_{3#sigma, #psi(2S)} = %5.4f" % sig_to_bkg)
                histResults.GetXaxis().SetBinLabel(extraIndex, "sOverB_Psi2s")
                histResults.SetBinContent(extraIndex, sig_to_bkg)
                extraIndex += 1
            if "sgnf_Jpsi" in parName:
                sig_mean = self.fRooWorkspace.var("mean_Jpsi").getVal()
                sig_width = self.fRooWorkspace.var("width_Jpsi").getVal()
                sigForIntegral = self.fRooWorkspace.var("sig_Jpsi").getVal()
                bkgForIntegral = self.fRooWorkspace.var("bkg").getVal()
                min_range = sig_mean - 3. * sig_width
                max_range = sig_mean + 3. * sig_width
                significance = ComputeSignificance(canvasFit, "JpsiPdf", "BkgPdf", sigForIntegral, bkgForIntegral, min_range, max_range)
                extraText.append("S/#sqrt{(S+B)}_{3#sigma, J/#psi} = %1.0f" % significance)
                histResults.GetXaxis().SetBinLabel(extraIndex, "sgnf_Jpsi")
                histResults.SetBinContent(extraIndex, significance)
                extraIndex += 1
            if "sgnf_Psi2s" in parName:
                sig_mean = self.fRooWorkspace.function("mean_Psi2s").getVal()
                sig_width = self.fRooWorkspace.function("width_Psi2s").getVal()
                sigForIntegral = self.fRooWorkspace.var("sig_Psi2s").getVal()
                bkgForIntegral = self.fRooWorkspace.var("bkg").getVal()
                min_range = sig_mean - 3. * sig_width
                max_range = sig_mean + 3. * sig_width
                significance = ComputeSignificance(canvasFit, "Psi2sPdf", "BkgPdf", sigForIntegral, bkgForIntegral, min_range, max_range)
                extraText.append("S/#sqrt{(S+B)}_{3#sigma, #psi(2S)} = %1.0f" % significance)
                histResults.GetXaxis().SetBinLabel(extraIndex, "sgnf_Psi2s")
                histResults.SetBinContent(extraIndex, significance)
                extraIndex += 1
            if "alpha_vn_Jpsi" in parName:
                sig_mean = self.fRooWorkspace.var("mean_Jpsi").getVal()
                sig_width = self.fRooWorkspace.var("width_Jpsi").getVal()
                sigForIntegral = self.fRooWorkspace.var("sig_Jpsi").getVal()
                bkgForIntegral = self.fRooWorkspace.var("bkg").getVal()
                min_range = sig_mean - 3. * sig_width
                max_range = sig_mean + 3. * sig_width
                alpha_vn = ComputeAlpha(canvasFit, "JpsiPdf", "BkgPdf", sigForIntegral, bkgForIntegral, min_range, max_range)
                extraText.append("(S/S+B)_{3#sigma} = %5.4f" % alpha_vn)
                histResults.GetXaxis().SetBinLabel(index+3, "alpha_vn")
                histResults.SetBinContent(index+3, alpha_vn)
            if "corrMatrStatus" in parName:
                covMatrixStatus = self.rooFitRes.covQual()
                extraText.append("Cov. matrix status= %i" % covMatrixStatus)
        
        # Print the fit result
        self.rooFitRes.Print()
        
        # Official fit plot
        if self.fPdfDict["doAlicePlot"]:
            cosmetics = self.fPdfDict["cosmeticsForAlicePlot"]
            canvasALICE = DoAlicePlot(rooDs, pdf, fRooPlotOff, self.fPdfDict, self.fInputName, trialName, self.fOutPath, extraText, cosmetics)

        # Save results
        self.fFileOut.cd()
        histResults.Write()
        canvasFit.Write()

        rooDs.plotOn(fRooPlotExtra, ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2), ROOT.RooFit.Range(fitRangeMin, fitRangeMax))
        pdf.plotOn(fRooPlotExtra, ROOT.RooFit.Range(fitRangeMin, fitRangeMax))

        # Residual plot
        if self.fDoResidualPlot:
            print(fRooPlotExtra, self.fRooMass, self.fInputName, self.fOutPath, trialName)
            canvasResidual = DoResidualPlot(fRooPlotExtra, self.fRooMass, self.fInputName, self.fOutPath, trialName)
            canvasResidual.Write()


        # Pull plot
        if self.fDoPullPlot:
            canvasPull = DoPullPlot(fRooPlotExtra, self.fRooMass, self.fInputName, self.fOutPath, trialName)
            canvasPull.Write()

        if self.fPdfDict["doResidualPlotPdf"]:
            canvasResidual.SaveAs("{}/residual_plot_{}_{}.pdf".format(self.fOutPath, self.fInputName, trialName))
        
        if self.fPdfDict["doPullPlotPdf"]:
            canvasPull.SaveAs("{}/pull_plot_{}_{}.pdf".format(self.fOutPath, self.fInputName, trialName))

        # Se entrambi i plot sono stati creati, salviamo un unico PDF combinato
        #if canvasALICE and canvasResidual:
        #SaveCombinedPlot(canvasALICE, canvasPull, self.fOutPath, self.fInputName, trialName)

        # Correlation matrix plot
        if self.fDoCorrMatPlot:
            canvasCorrMat = DoCorrMatPlot(self.rooFitRes, trialName)
            canvasCorrMat.Write()

        del self.fRooWorkspace
        self.fFileIn.Close()


    def SingleFit(self, tailRootFileName, tailHistName):
        '''
        Method to perform a single fit (calling multi-trial from external script)
        '''
        self.FitInvMassSpectrum(self.fFitMethod, self.fFitRangeMin, self.fFitRangeMax, self.fMe_norm, tailRootFileName, tailHistName)
        self.fFileOut.Close()

        me_norm_str = str(self.fMe_norm) if self.fMe_norm is not None else "_"
        if "MC" in tailHistName:
            tails = f'MC_tails'
        elif "data" in tailHistName:
            tails = f'data_tails'
            """ else:
            tails = f'free_tails' """
        else:
            match = re.search(r"(\d+)MB", tailHistName)
            if match:
                mbName = match.group(0)
                tails = f'_{mbName}'
            else:
                tails = ''

        # Update file name
        trialName = f"output__{self.fInputName}_{self.fTrialName}_{self.fFitRangeMin}_{self.fFitRangeMax}_{self.fMean}_{self.fWidth}_{me_norm_str}_{tails}.root"
        oldFileOutName = self.fFileOutName
        newFileOutName = os.path.join(os.path.dirname(oldFileOutName), trialName)

        # Rename file
        os.rename(oldFileOutName, newFileOutName)
        self.fFileOutNameNew = newFileOutName

