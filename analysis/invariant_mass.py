import yaml
import json
import sys
import argparse
from array import array
import os
import math 
from os import path
import numpy as np
import pandas as pd
import ROOT
from ROOT import TCanvas, TH1F, TH2F, TGraphErrors, TLegend
sys.path.append('../utils')
from plot_library import LoadStyle, SetGraStat, SetGraSyst, SetLegend

ROOT.gROOT.ProcessLineSync(".x ../fit_library/VWGPdf.cxx+")
ROOT.gROOT.ProcessLineSync(".x ../fit_library/CB2Pdf.cxx+")

def inv_mass_plot(inputCfg):
    LoadStyle()
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetHatchesSpacing(0.3)
    #gStyle.SetHatchesLineWidth(2)

    fIn = ROOT.TFile(inputCfg["inputs"]["fIn"], "READ")
    canvasInvMass = fIn.Get(inputCfg["inputs"]["invMass"])
    canvasPull = fIn.Get(inputCfg["inputs"]["pull"])
    listOfPrimsInvMass = canvasInvMass.GetListOfPrimitives()
    listOfPrimsPull = canvasPull.GetListOfPrimitives()

    #print(list(listOfPrimsInvMass))
    #print(list(listOfPrimsPull))

    xMin = inputCfg["inputs"]["xMin"]
    xMax = inputCfg["inputs"]["xMax"]
    yMin = inputCfg["inputs"]["yMin"]
    yMax = inputCfg["inputs"]["yMax"]

    frame1 = ROOT.TH2D("histGrid1", "", 100, xMin, xMax, 100, yMin, yMax)

    # Histograms
    histData = listOfPrimsInvMass.At(1)
    histData.SetMarkerStyle(20)
    histData.SetMarkerColor(ROOT.kBlack)

    # PDFs
    pdfNames = inputCfg["inputs"]["pdfNames"]
    pdfLegendNames = inputCfg["inputs"]["pdfLegendNames"]
    pdfs = []
    index = 0

    for pdfName in pdfNames:
        for i, listOfPrimInvMass in enumerate(listOfPrimsInvMass):
            if pdfName in listOfPrimInvMass.GetName():
                index = i
        pdfs.append(listOfPrimsInvMass.At(index))
        index = 0

    canvasOut = TCanvas("canvasOut", "canvasOut", 800, 800)
    ROOT.gStyle.SetCanvasPreferGL(0)

    canvasOut.cd()
    canvasOut.SetTickx(1)
    canvasOut.SetTicky(1)
    ROOT.gPad.SetLogy(1)
    frame1.Draw()
    histData.Draw("EP")
    for pdf in pdfs:
        pdf.Draw("SAME")

    legXmin = inputCfg["inputs"]["legXmin"]
    legYmin = inputCfg["inputs"]["legYmin"]
    legXmax = inputCfg["inputs"]["legXmax"]
    legYmax = inputCfg["inputs"]["legYmax"]

    legend = TLegend(legXmin, legYmin, legXmax, legYmax, " ", "brNDC")
    SetLegend(legend)
    legend.SetTextSize(0.04)
    legend.AddEntry(histData,"Data", "PL")
    for i, pdfLegendName in enumerate(pdfLegendNames):
        legend.AddEntry(pdfs[i], pdfLegendName, "L")
    legend.Draw()

    letexTitle = ROOT.TLatex()
    letexTitle.SetTextSize(0.045)
    letexTitle.SetNDC()
    letexTitle.SetTextFont(42)
    letexTitle.DrawLatex(0.18, 0.88, inputCfg["inputs"]["textTitle"])
    letexTitle.DrawLatex(0.18, 0.82, inputCfg["inputs"]["textSyst"])
    letexTitle.DrawLatex(0.18, 0.76, inputCfg["inputs"]["textKine"])

    letexY1Axis = ROOT.TLatex()
    letexY1Axis.SetTextAngle(90)
    letexY1Axis.SetTextSize(0.045)
    letexY1Axis.SetNDC()
    letexY1Axis.SetTextFont(42)
    letexY1Axis.DrawLatex(0.05, 0.60, "d#it{N}/d#it{m}_{#mu#mu} (GeV/#it{c}^{2})")

    letexX2Axis = ROOT.TLatex()
    letexX2Axis.SetTextSize(0.045)
    letexX2Axis.SetNDC()
    letexX2Axis.SetTextFont(42)
    letexX2Axis.DrawLatex(0.70, 0.05, "#it{m}_{#mu#mu} (GeV/#it{c}^{2})")

    canvasOut.Update()
    canvasOut.SaveAs(inputCfg["outputs"]["pdfOut"])



def pull_plot(inputCfg):
    LoadStyle()
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetHatchesSpacing(0.3)
    #gStyle.SetHatchesLineWidth(2)

    fIn = ROOT.TFile(inputCfg["inputs"]["fIn"], "READ")
    canvasInvMass = fIn.Get(inputCfg["inputs"]["invMass"])
    canvasPull = fIn.Get(inputCfg["inputs"]["pull"])
    listOfPrimsInvMass = canvasInvMass.GetListOfPrimitives()
    listOfPrimsPull = canvasPull.GetListOfPrimitives()

    #print(list(listOfPrimsInvMass))
    #print(list(listOfPrimsPull))

    xMin = inputCfg["inputs"]["xMin"]
    xMax = inputCfg["inputs"]["xMax"]
    yMin = inputCfg["inputs"]["yMin"]
    yMax = inputCfg["inputs"]["yMax"]

    frame1 = ROOT.TH2D("histGrid1", "", 100, xMin, xMax, 100, yMin, yMax)
    frame2 = ROOT.TH2D("histGrid2", "", 100, xMin, xMax, 100, -5, 5)
    frame2.GetXaxis().SetLabelSize(0.15)
    frame2.GetYaxis().SetLabelSize(0.15)
    frame2.GetYaxis().SetNdivisions(5)
    frame2.GetXaxis().SetTitleSize(0.15)
    frame2.GetXaxis().SetTitleOffset(0.85)

    # Histograms
    histData = listOfPrimsInvMass.At(1)
    histData.SetMarkerStyle(20)
    histData.SetMarkerColor(ROOT.kBlack)

    histPull = listOfPrimsPull.At(1)
    histPull.SetMarkerStyle(20)
    histPull.SetMarkerColor(ROOT.kBlack)

    for i in range(histPull.GetN()):
        histPull.SetPointEXlow(i, 0)
        histPull.SetPointEXhigh(i, 0)
        histPull.SetPointEYlow(i, 0)
        histPull.SetPointEYhigh(i, 0)


    # PDFs
    pdfNames = inputCfg["inputs"]["pdfNames"]
    pdfLegendNames = inputCfg["inputs"]["pdfLegendNames"]
    pdfs = []
    index = 0

    for pdfName in pdfNames:
        for i, listOfPrimInvMass in enumerate(listOfPrimsInvMass):
            if pdfName in listOfPrimInvMass.GetName():
                index = i
        pdfs.append(listOfPrimsInvMass.At(index))
        index = 0

    canvasOut = TCanvas("canvasOut", "canvasOut", 800, 800)

    canvasOut.cd()
    pad1 = ROOT.TPad("pad1", "pad1", 0.005, 0.3, 0.995, 0.95)
    pad1.SetBottomMargin(0.01)
    pad1.SetTopMargin(0.05)
    pad1.Draw()
    pad1.cd()
    #canvasOut.SetTickx(1)
    #canvasOut.SetTicky(1)
    ROOT.gPad.SetLogy(1)
    frame1.Draw()
    histData.Draw("EP")
    for pdf in pdfs:
        pdf.Draw("SAME")

    legend = TLegend(0.75, 0.52, 0.92, 0.87, " ", "brNDC")
    SetLegend(legend)
    legend.SetTextSize(0.04)
    legend.AddEntry(histData,"Data", "P")
    for i, pdfLegendName in enumerate(pdfLegendNames):
        legend.AddEntry(pdfs[i], pdfLegendName, "L")
    legend.Draw()

    letexTitle = ROOT.TLatex()
    letexTitle.SetTextSize(0.055)
    letexTitle.SetNDC()
    letexTitle.SetTextFont(42)
    letexTitle.DrawLatex(0.18, 0.88, inputCfg["inputs"]["textTitle"])
    letexTitle.DrawLatex(0.18, 0.81, inputCfg["inputs"]["textKine"])

    canvasOut.cd()
    pad2 = ROOT.TPad("pad2", "pad2", 0.005, 0.1, 0.995, 0.30)
    pad2.SetBottomMargin(0.12)
    pad2.SetTopMargin(0.07)
    pad2.Draw()
    pad2.cd()
    frame2.Draw()
    histPull.Draw("P")

    lineZero = ROOT.TLine(xMin, 0, xMax, 0)
    lineZero.Draw()

    line2SigmaUp = ROOT.TLine(xMin, 2, xMax, 2)
    line2SigmaUp.SetLineStyle(ROOT.kDashed)
    line2SigmaUp.Draw()
    
    line2SigmaDown = ROOT.TLine(xMin, -2, xMax, -2)
    line2SigmaDown.SetLineStyle(ROOT.kDashed)
    line2SigmaDown.Draw()

    canvasOut.cd()

    letexY1Axis = ROOT.TLatex()
    letexY1Axis.SetTextAngle(90)
    letexY1Axis.SetTextSize(0.035)
    letexY1Axis.SetNDC()
    letexY1Axis.SetTextFont(42)
    letexY1Axis.DrawLatex(0.05, 0.60, "dN/d#it{m}_{#mu#mu} (GeV/#it{c}^{2})")

    letexY2Axis = ROOT.TLatex()
    letexY2Axis.SetTextAngle(90)
    letexY2Axis.SetTextSize(0.035)
    letexY2Axis.SetNDC()
    letexY2Axis.SetTextFont(42)
    letexY2Axis.DrawLatex(0.05, 0.20, "Pull")

    letexX2Axis = ROOT.TLatex()
    letexX2Axis.SetTextSize(0.035)
    letexX2Axis.SetNDC()
    letexX2Axis.SetTextFont(42)
    letexX2Axis.DrawLatex(0.80, 0.05, "#it{m}_{#mu#mu} (GeV/#it{c}^{2})")

    canvasOut.Update()

    input()

    canvasOut.SaveAs(inputCfg["outputs"]["pdfOut"])

def main():
    print('start')
    parser = argparse.ArgumentParser(description='Arguments to pass')
    parser.add_argument('cfgFileName', metavar='text', default='config.yml', help='config file name')
    parser.add_argument("--run", help="run the single fit", action="store_true")
    parser.add_argument("--do_pull_plot", help="run the single fit + pull plot", action="store_true")
    args = parser.parse_args()
    print(args)
    print('Loading task configuration: ...', end='\r')
    with open(args.cfgFileName, 'r') as ymlCfgFile:
        inputCfg = yaml.load(ymlCfgFile, yaml.FullLoader)
    print('Loading task configuration: Done!')
    
    if args.run:
        inv_mass_plot(inputCfg)
    if args.do_pull_plot:
        pull_plot(inputCfg)

if __name__ == '__main__':
    main()