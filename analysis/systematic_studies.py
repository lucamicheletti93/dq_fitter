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

def do_systematics(inputCfg):
    """
    function to compute the systematics on variables evaluated with the DQFitter
    """
    pathNamePt = inputCfg["inputs"]["pathPtDep"]
    ptMin = inputCfg["inputs"]["ptMin"]
    ptMax = inputCfg["inputs"]["ptMax"]
    varNames = inputCfg["inputs"]["varNames"]
    varIndex = inputCfg["inputs"]["varIndex"]

    for varName in varNames:
        with open("{}/systematic_{}.txt".format(pathNamePt, varName), 'w') as fOut:
            fOut.write("x_min x_max val stat syst \n")
            for iPt in range(0, len(ptMin)):
                if not os.path.exists("{}/Pt_{:2.1f}_{:2.1f}/systematics".format(pathNamePt, ptMin[iPt], ptMax[iPt])):
                    os.makedirs("{}/Pt_{:2.1f}_{:2.1f}/systematics".format(pathNamePt, ptMin[iPt], ptMax[iPt]))
                DoSystematics("{}/Pt_{:2.1f}_{:2.1f}".format(pathNamePt, ptMin[iPt], ptMax[iPt]), "multi_trial", varName, varIndex, fOut)
            fOut.close()
        
    #pathNameRap = "/Users/lucamicheletti/GITHUB/dq_fitter/analysis/LHC23_pass3_full/y_dependence"
    #rapMin = [2.50, 2.75, 3.00, 3.25, 3.50, 3.75]
    #rapMax = [2.75, 3.00, 3.25, 3.50, 3.75, 4.00]

    #for varName in varNames:
        #with open("{}/systematic_{}.txt".format(pathNameRap, varName), 'w') as fOut:
            #fOut.write("x_min x_max val stat syst \n")
            #for iRap in range(0, len(rapMin)):
                #if not os.path.exists("{}/Rap_{:3.2f}_{:3.2f}/systematics".format(pathNameRap, rapMin[iRap], rapMax[iRap])):
                    #os.makedirs("{}/Rap_{:3.2f}_{:3.2f}/systematics".format(pathNameRap, rapMin[iRap], rapMax[iRap]))
                #DoSystematics("{}/Rap_{:3.2f}_{:3.2f}".format(pathNameRap, rapMin[iRap], rapMax[iRap]), "multi_trial", varName, fOut)
            #fOut.close()

def main():
    print('start')
    parser = argparse.ArgumentParser(description='Arguments to pass')
    parser.add_argument('cfgFileName', metavar='text', default='config.yml', help='config file name')
    parser.add_argument("--do_systematics", help="run the single fit", action="store_true")
    parser.add_argument("--do_check_variables", help="run the single fit", action="store_true")
    args = parser.parse_args()
    print(args)
    print('Loading task configuration: ...', end='\r')

    print('Loading task configuration: ...', end='\r')
    with open(args.cfgFileName, 'r') as ymlCfgFile:
        inputCfg = yaml.load(ymlCfgFile, yaml.FullLoader)
    print('Loading task configuration: Done!')
    
    if args.do_systematics:
        do_systematics(inputCfg)
    

    if args.do_check_variables:
        #fInNames = ["/Users/lucamicheletti/GITHUB/dq_fitter/analysis/LHC24e5/standard_association/multi_trial/multi_trial_CB2.root"]
        fInNames = ["/Users/lucamicheletti/GITHUB/dq_fitter/analysis/LHC22o_pass6_minBias/time_association/MC_tails/multi_trial_CB2_VWG.root"]
        parNames = ["sig_Jpsi", "sig_Psi2s", "width_Jpsi", "mean_Jpsi"]
        xMin = [0, 1, 2, 3, 4, 5, 7, 10]
        xMax = [1, 2, 3, 4, 5, 7, 10, 20]
        #fOutName = "/Users/lucamicheletti/GITHUB/dq_fitter/analysis/LHC24e5/standard_association/multi_trial"
        fOutName = "/Users/lucamicheletti/GITHUB/dq_fitter/analysis/LHC22o_pass6_minBias/time_association/MC_tails"
        obs = "signal_extraction_CB2"
        CheckVariables(fInNames, parNames, xMin, xMax, fOutName, obs)

if __name__ == '__main__':
    main()