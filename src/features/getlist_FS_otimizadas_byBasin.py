import os
import glob
import copy
import pandas as pd
import numpy as np
import sys
from pathlib import Path

pathparent = str(Path(os.getcwd()).parents[0])
# sys.path.append(pathparent)
print(pathparent)
pathData = os.path.join(pathparent, 'dados')
pathData = os.path.join(pathData, 'feature_select_col10')
print('we load CSVs from \n >>> ', pathData)

lstFilesFS = glob.glob(pathData + '/*.csv' )
# get first list of basin
lstBasin = []
dictBasinYY = {}

for cc, nfile in enumerate(lstFilesFS):
    print(f" #{cc} >> {nfile.split('/')[-1]}")
    nameBasin =  nfile.split('/')[-1].split("_")[1]
    yyear = nfile.split('/')[-1].split("_")[-1].replace(".csv", "")  

    if nameBasin not in lstBasin:
        lstBasin.append(nameBasin)
        dictBasinYY[nameBasin] = [yyear]
        # print(f'iniciando >> {dictBasinYY[nameBasin]}')
    else:  
        lsttmp = dictBasinYY[nameBasin]
        lsttmp.append(str(yyear))
        dictBasinYY[nameBasin] = copy.deepcopy(lsttmp)
        # print(dictBasinYY[nameBasin])
        
# sys.exit()
print("lista de Basin feitas ", lstBasin)
print(f" {len(lstBasin)} feitas")
for nbasin in lstBasin:
    print(f"  processing  {nbasin}")
    for yyear in dictBasinYY[nameBasin]:
        pathCSV = os.path.join(pathData, f'featuresSelectS2_{nbasin}_{yyear}.csv')
        dftmp = pd.read_csv(pathCSV)
        print(dftmp.head(3))