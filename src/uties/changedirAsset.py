#-*- coding utf-8 -*-
import ee
import os
import sys
import json
from tqdm import tqdm
import random
from datetime import date
import pandas as pd
import collections
from pathlib import Path
collections.Callable = collections.abc.Callable

pathparent = str(Path(os.getcwd()).parents[0])
sys.path.append(pathparent)
from configure_account_projects_ee import get_current_account, get_project_from_account
projAccount = get_current_account()
print(f"projetos selecionado >>> {projAccount} <<<")

try:
    ee.Initialize(project= projAccount) # project='ee-cartassol'
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise



def sendFilenewAsset(idSource, idTarget):
    # moving file from repository Arida to Nextgenmap
    ee.data.renameAsset(idSource, idTarget)

listaNameBacias = [
    '7754', '7691', '7581', '7625', '7584', '751', '7614', 
    '752', '7616', '745', '7424', '773', '7612', '7613', 
    '7618', '7561', '755', '7617', '7564', '761111', '761112', 
    '7741', '7422', '76116', '7761', '7671', '7615', '7411', 
    '7764', '757', '771', '7712', '766', '7746', '753', '764', 
    '7541', '7721', '772', '7619', '7443', '765', '7544', '7438', 
    '763', '7591', '7592', '7622', '746'
]
print(f" here we have {len(listaNameBacias)} basin")
# ee.data.renameAsset(sourceId, destinationId, callback)
asset_output = 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Temporal'
# asset_input = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fills'
asset_input = 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Frequency'
# asset_output = 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/ClassifyVA'
# asset_input = 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/ClassifV1'
changeConta = False
fromImgCol = True
versionMapping = 10
# sys.exit()

if fromImgCol:
    imgCol = ee.ImageCollection(asset_input).filter(ee.Filter.eq('version', versionMapping))
    lstIds = imgCol.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()

    for cc, masset in enumerate(lstIds):
        print(cc, ' => move ', masset, " to ImageCollection in NEXGENTMAP")
        sendFilenewAsset(asset_input + '/' + masset, asset_output + '/' + masset)

else:
    lstFails = []
    for cc, nbacia in enumerate(listaNameBacias):
        # BACIA_7411_GTB_col10-v1
        nameImage = f'BACIA_{nbacia}_GTB_col10-v1'
        namedestino = f'BACIA_{nbacia}_GTB_col10-v2'
                
        try:
            # imgtmp = ee.Image(asset_input + '/' + nameImage)
            # print(" list name bands ", imgtmp.bandNames().getInfo())
            sendFilenewAsset(asset_input + '/' + nameImage, asset_output + '/' + namedestino) # .replace("Gap-fill", "")
            print(cc, ' => move ', nameImage, f" to ImageCollection in {asset_output}")
        except:
            print(cc, ' => FAILS move  ', nameImage, f" to ImageCollection in {asset_output}")
            lstFails.append(nbacia)

    if len(lstFails):
        print(f" we added the basin {len(lstFails)} to list fails ")
        print(lstFails)
    else:
        print(" ----- We don´t have basin in list fails --------")

print('========================================')
print("            finish process              ")