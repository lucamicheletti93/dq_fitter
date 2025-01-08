from traceback import print_tb
import yaml
import json
import sys
import argparse
from array import array
import os
from os import path
import ROOT
from ROOT import TFile
sys.path.append('../')
from DQFitter_new import DQFitter_new
sys.path.append('../utils')
from utils_library import DoSystematics, CheckVariables

def main():
    print('start')
    parser = argparse.ArgumentParser(description='Arguments to pass')
    parser.add_argument('cfgFileName', metavar='text', default='config.yml', help='config file name')
    #parser.add_argument("--do_fit", help="run the single fit", action="store_true")
    parser.add_argument("--do_fit_fixed_tails", help="run the single fit with tail parameters taken from a root file", action="store_true")
    args = parser.parse_args()
    print(args)
    print('Loading task configuration: ...', end='\r')

    with open(args.cfgFileName, 'r') as jsonCfgFile:
        inputCfg = json.load(jsonCfgFile)
    print('Loading task configuration: Done!')

    """
    if args.do_fit:
        inputFileName  = inputCfg["input"]["input_file_name"]
        outputFileName = inputCfg["output"]["output_file_name"]
        mergedFileName = inputCfg["output"]["output_merged_file_name"]
        histNames      = inputCfg["input"]["input_name"]
        minFitRanges   = inputCfg["input"]["pdf_dictionary"]["fitRangeMin"]
        maxFitRanges   = inputCfg["input"]["pdf_dictionary"]["fitRangeMax"]

        listOfOutputFileNames = [] # list of output file names
        
        if not path.isdir(outputFileName):
            os.system("mkdir -p %s" % (outputFileName))
        for histName in histNames:
            for minFitRange, maxFitRange in zip(minFitRanges, maxFitRanges):
                # Reload configuration file
                with open(args.cfgFileName, 'r') as jsonCfgFile:
                    inputCfg = json.load(jsonCfgFile)
                pdfDictionary  = inputCfg["input"]["pdf_dictionary"]
                print(inputFileName)
                dqFitter = DQFitter(inputFileName, histName, outputFileName, minFitRange, maxFitRange)
                print(inputCfg["input"]["pdf_dictionary"]["parName"])
                dqFitter.SetFitConfig(pdfDictionary)
                dqFitter.SingleFit()
                listOfOutputFileNames.append(dqFitter.GetFileOutName())

        if len(histNames) > 1 or len(minFitRanges) > 1:
            mergedFileName = f'{outputFileName}/{mergedFileName}.root '
            listOfOutputFileNamesToMerge = " ".join(listOfOutputFileNames)
            mergingCommand = mergedFileName + listOfOutputFileNamesToMerge
            print(mergingCommand)
            os.system(f'hadd -f {mergingCommand}')
            # Delete unmerged files
            for listOfOutputFileName in listOfOutputFileNames:
                os.system(f'rm {listOfOutputFileName}')
    """

    if args.do_fit_fixed_tails:
        inputFileName  = inputCfg["input"]["input_file_name"]
        outputFileName = inputCfg["output"]["output_file_name"]
        mergedFileName = inputCfg["output"]["output_merged_file_name"]
        histNames      = inputCfg["input"]["input_name"]
        minFitRanges   = inputCfg["input"]["pdf_dictionary"]["fitRangeMin"]
        maxFitRanges   = inputCfg["input"]["pdf_dictionary"]["fitRangeMax"]

        tailRootFileName = inputCfg["input"]["tailRootFileName"] #NEW
        tailHistName = inputCfg["input"]["tailHistName"] #NEW
        listOfOutputFileNames = [] # list of output file names
        
        if not path.isdir(outputFileName):
            os.system("mkdir -p %s" % (outputFileName))
        for histName in histNames:
            for minFitRange, maxFitRange in zip(minFitRanges, maxFitRanges):
                # Reload configuration file
                with open(args.cfgFileName, 'r') as jsonCfgFile:
                    inputCfg = json.load(jsonCfgFile)
                pdfDictionary  = inputCfg["input"]["pdf_dictionary"]
                print(inputFileName)
                dqFitter = DQFitter_new(inputFileName, histName, outputFileName, minFitRange, maxFitRange)
                print(inputCfg["input"]["pdf_dictionary"]["parName"])
                dqFitter.SetFitConfig(pdfDictionary, tailRootFileName, tailHistName)
                dqFitter.SingleFit()
                listOfOutputFileNames.append(dqFitter.GetFileOutName())

        if len(histNames) > 1 or len(minFitRanges) > 1:
            mergedFileName = f'{outputFileName}/{mergedFileName}.root '
            listOfOutputFileNamesToMerge = " ".join(listOfOutputFileNames)
            mergingCommand = mergedFileName + listOfOutputFileNamesToMerge
            print(mergingCommand)
            os.system(f'hadd -f {mergingCommand}')
            # Delete unmerged files
            for listOfOutputFileName in listOfOutputFileNames:
                os.system(f'rm {listOfOutputFileName}')

if __name__ == '__main__':
    main()
