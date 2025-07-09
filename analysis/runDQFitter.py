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
from DQFitter import DQFitter
sys.path.append('../utils')
from utils_library import DoSystematics, CheckVariables

def main():
    print('start')
    parser = argparse.ArgumentParser(description='Arguments to pass')
    parser.add_argument('cfgFileName', metavar='text', default='config.yml', help='config file name')
    parser.add_argument("--do_fit", help="run the single fit", action="store_true")
    args = parser.parse_args()
    print(args)
    print('Loading task configuration: ...', end='\r')

    with open(args.cfgFileName, 'r') as jsonCfgFile:
        inputCfg = json.load(jsonCfgFile)
    print('Loading task configuration: Done!')
    
    if args.do_fit:
        inputFileName  = inputCfg["input"]["input_file_name"]
        outputFileName = inputCfg["output"]["output_file_name"]
        mergedFileName = inputCfg["output"]["output_merged_file_name"]
        histNames      = inputCfg["input"]["input_name"]
        minFitRanges   = inputCfg["input"]["pdf_dictionary"]["fitRangeMin"]
        maxFitRanges   = inputCfg["input"]["pdf_dictionary"]["fitRangeMax"]
        fitMethod      = inputCfg["input"]["pdf_dictionary"]["fitMethod"]
        mean   = inputCfg["input"]["pdf_dictionary"]["mean_Psi2s"]
        width   = inputCfg["input"]["pdf_dictionary"]["width_Psi2s"]
        ME_norm   = inputCfg["input"]["pdf_dictionary"]["ME_norm"]
        dataset   = inputCfg["input"]["pdf_dictionary"]["dataset"]

        if "tailRootFileName" in inputCfg["input"] and "tailHistNames" in inputCfg["input"]:
            tailRootFileName = inputCfg["input"]["tailRootFileName"] 
            tailHistNames = inputCfg["input"]["tailHistNames"] 
        else:
            tailRootFileName = None
            tailHistNames = [None]
        
        if not path.isdir(outputFileName):
            os.system("mkdir -p %s" % (outputFileName))
        
        if tailRootFileName is not None:
            tailRootFileName = inputCfg["input"]["tailRootFileName"] 
            tailHistNames = inputCfg["input"]["tailHistNames"] 
            for histName in histNames:
                for tailHistName in tailHistNames: #looping over different histograms contaoining different sets of tail parameters
                    listOfOutputFileNames = [] # list of output file names
                    for minFitRange, maxFitRange in zip(minFitRanges, maxFitRanges):
                        # Reload configuration file
                        with open(args.cfgFileName, 'r') as jsonCfgFile:
                            inputCfg = json.load(jsonCfgFile)
                        pdfDictionary  = inputCfg["input"]["pdf_dictionary"]
                        print("PDF Dictionary content:", pdfDictionary)
                        print(inputFileName)
                        dqFitter = DQFitter(inputFileName, histName, outputFileName, minFitRange, maxFitRange, mean, width, ME_norm, dataset, tailHistName, fitMethod)
                        print(inputCfg["input"]["pdf_dictionary"]["parName"])
                        dqFitter.SetFitConfig(pdfDictionary, tailRootFileName, tailHistName) #using each tail set at a time
                        dqFitter.SingleFit(tailRootFileName, tailHistName)
                        listOfOutputFileNames.append(dqFitter.GetFileOutName())
                    
                    #Creating a different merged file for each set of tails for a given histogram, containing the 3 fit types
                    #if len(histNames) > 1 or len(minFitRanges) > 1:
                    if len(minFitRanges) > 1: 
                        if "MC" in tailHistName:
                            mergedFileName_full = f'{outputFileName}/{mergedFileName}_MC_tails.root '
                        if "data" in tailHistName:
                            mergedFileName_full = f'{outputFileName}/{mergedFileName}_data_tails.root '
                        else:
                            mergedFileName_full = f'{outputFileName}/{mergedFileName}_free_tails.root '
                        listOfOutputFileNamesToMerge = " ".join(listOfOutputFileNames)
                        mergingCommand = mergedFileName_full + listOfOutputFileNamesToMerge
                        print(mergingCommand)
                        os.system(f'hadd -f {mergingCommand}') # -f option to overwrite merged file when rerunning the code
                        # Delete unmerged files
                        for listOfOutputFileName in listOfOutputFileNames:
                            os.system(f'rm {listOfOutputFileName}')

        #If "tailRootFileName": null, "tailHistNames": [null] in jsonCfgFile, the fit is peformed for one set of tails
        else:
            listOfOutputFileNames = [] # list of output file names
            for histName in histNames:
                for minFitRange, maxFitRange in zip(minFitRanges, maxFitRanges):
                    # Reload configuration file
                    with open(args.cfgFileName, 'r') as jsonCfgFile:
                        inputCfg = json.load(jsonCfgFile)
                    pdfDictionary  = inputCfg["input"]["pdf_dictionary"]
                    print(inputFileName)
                    dqFitter = DQFitter(inputFileName, histName, outputFileName, minFitRange, maxFitRange, mean, width, ME_norm, dataset, tailHistName, fitMethod)
                    #dqFitter = DQFitter(inputFileName, histName, outputFileName, minFitRange, maxFitRange, fitMethod)
                    print(inputCfg["input"]["pdf_dictionary"]["parName"])
                    dqFitter.SetFitConfig(pdfDictionary, tailRootFileName, None)
                    dqFitter.SingleFit(tailRootFileName, tailHistName)
                    listOfOutputFileNames.append(dqFitter.GetFileOutName())
            if len(histNames) > 1 or len(minFitRanges) > 1:
                mergedFileName = f'{outputFileName}/{mergedFileName}.root '
                listOfOutputFileNamesToMerge = " ".join(listOfOutputFileNames)
                mergingCommand = mergedFileName + listOfOutputFileNamesToMerge
                print(mergingCommand)
                os.system(f'hadd -f {mergingCommand}') # -f option to overwrite merged file when rerunning the code
                # Delete unmerged files
                for listOfOutputFileName in listOfOutputFileNames:
                    os.system(f'rm {listOfOutputFileName}')
            


if __name__ == '__main__':
    main()
