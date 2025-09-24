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
    print("Inizio do_systematics")

    pathNamePt = inputCfg["inputs"]["pathPtDep"]
    ptMin = inputCfg["inputs"]["ptMin"]
    ptMax = inputCfg["inputs"]["ptMax"]
    varNames = inputCfg["inputs"]["varNames"]
    varIndex = inputCfg["inputs"]["varIndex"]
    fileNames = inputCfg["inputs"]["fileNames"]
    #file_types = ["multi_trial", "output"]

    print("Parametri caricati")
    print(f"path: {pathNamePt}")
    print(f"ptMin: {ptMin}")
    print(f"ptMax: {ptMax}")
    print(f"varNames: {varNames}")
    print(f"fileNames: {fileNames}")

    for varName in varNames:
        print(f"Processing variable: {varName}")
        with open(f"{pathNamePt}/systematic_{varName}.txt", 'w') as fOut:
            fOut.write("x_min x_max val stat syst \n")
            for iPt in range(len(ptMin)):
                outdir = f"{pathNamePt}/Pt_{ptMin[iPt]:.1f}_{ptMax[iPt]:.1f}/systematics"
                print(f"Creating directory (if not exists): {outdir}")
                if not os.path.exists(outdir):
                    os.makedirs(outdir)

                DoSystematics(f"{pathNamePt}/Pt_{ptMin[iPt]:.1f}_{ptMax[iPt]:.1f}", fileNames, varName, varIndex, fOut)

def main():
    print('start')
    parser = argparse.ArgumentParser(description='Arguments to pass')
    parser.add_argument('cfgFileName', metavar='text', default='config.yml', help='config file name')
    parser.add_argument("--run", help="run the single fit", action="store_true")
    parser.add_argument("--do_check_variables", help="run the single fit", action="store_true")
    args = parser.parse_args()
    print(args)
    print('Loading task configuration: ...', end='\r')

    print('Loading task configuration: ...', end='\r')
    with open(args.cfgFileName, 'r') as ymlCfgFile:
        inputCfg = yaml.load(ymlCfgFile, yaml.FullLoader)
    print('Loading task configuration: Done!')
    
    if args.run:
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