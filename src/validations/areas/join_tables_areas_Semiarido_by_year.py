#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import os 
import glob
import copy
import pandas as pd


showlstGerral = False
filesAreaCSV = glob.glob('areasPrioritaYear/*.csv')
print("==================================================================================")
print("========== LISTA DE CSVs  NO FOLDER areasPrioritCSV ==============================")
if showlstGerral:
    for cc, namFile in enumerate(filesAreaCSV):
        print(f" #{cc}  >>  {namFile}")

    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print("==================================================================================")

lstLayer = [
    # 'water_Semiarido',
    # 'limite_Semiarido',
    # 'desf_veg_secundaria',
    # 'queimadas_Semiarido',
    'class_irrigated'
]
dictLayer = {
    'water_Semiarido': 'water',
    'limite_Semiarido': 'cobertura',
    'desf_veg_secundaria': 'veg secundaria',
    'queimadas_Semiarido': 'queimadas',
    'class_irrigated': 'áreas_irrigated'
}

for nlayer in lstLayer:
    print(f" ====== processing {nlayer} ========")
    lstDF = []
    nameexport = ''
    for namFile in filesAreaCSV:
        if nlayer in namFile:
            print(f"----loading >> {namFile} -----")
            dftmp = pd.read_csv(namFile)

            dftmp = dftmp[(dftmp['classe'] != 0) & (dftmp['classe'] != 29)]
            dftmp = dftmp.drop(['system:index', '.geo'], axis='columns')
            dftmp['layer'] = [dictLayer[nlayer]] * dftmp.shape[0]
            lstDF.append(dftmp)
            nameexport = copy.deepcopy(namFile)
    print(dftmp.head(2))
    ndfArea = pd.concat(lstDF, ignore_index= True)
    print("columna ", ndfArea.columns)
    ndfArea = ndfArea.sort_values(by='year')
    print(ndfArea.head())
    print(nameexport)
    nameexport = nameexport.replace("areasPrioritaYear", "statistic_layers")
    ultimoYY = nameexport.split("_")[-1].replace(".csv","")
    nameexport = nameexport.replace(ultimoYY, 'Serie')
    print("we going to export with name => ", nameexport)
    ndfArea.to_csv(nameexport)
    print(" -------- DONE ! --------------")
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print("==================================================================================")