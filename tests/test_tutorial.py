from traceback import print_tb
import yaml
import json
import sys
import argparse
from array import array
import os
from os import path
import ROOT
from ROOT import TFile, TF1, TH1F, TTree
from ROOT import gRandom
sys.path.append('../')
from DQFitter import DQFitter

def main():
    with open("../tutorial/config_tutorial_fit.json", 'r') as jsonCfgFile:
        inputCfg = json.load(jsonCfgFile)
    print('Loading task configuration: Done!')

    print('start')
    inputFileName  = inputCfg["input"]["input_file_name"]
    outputFileName = inputCfg["output"]["output_file_name"]
    histNames      = inputCfg["input"]["input_name"]
    minFitRanges   = inputCfg["input"]["pdf_dictionary"]["fitRangeMin"]
    maxFitRanges   = inputCfg["input"]["pdf_dictionary"]["fitRangeMax"]
    ME_norm        = inputCfg["input"]["pdf_dictionary"]["ME_norm"]
    fitMethod      = inputCfg["input"]["pdf_dictionary"]["fitMethod"]

    tailRootFileName = None
    tailHistNames = ["Data"]
        
    if not path.isdir(outputFileName):
        os.system("mkdir -p %s" % (outputFileName))
    for histName in histNames:
        for minFitRange, maxFitRange in zip(minFitRanges, maxFitRanges):
            # Reload configuration file
            with open("../tutorial/config_tutorial_fit.json", 'r') as jsonCfgFile:
                inputCfg = json.load(jsonCfgFile)
            pdfDictionary  = inputCfg["input"]["pdf_dictionary"]
            dqFitter = DQFitter(inputFileName, histName, outputFileName, minFitRange, maxFitRange, ME_norm, tailHistNames[0], fitMethod)
            dqFitter.SetFitConfig(pdfDictionary, tailRootFileName, tailHistNames[0])
            dqFitter.SingleFit(tailRootFileName, tailHistNames[0])


if __name__ == '__main__':
    main()