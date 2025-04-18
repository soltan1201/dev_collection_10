
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Produzido por Geodatin - Dados e Geoinformacao
DISTRIBUIDO COM GPLv2
@author: geodatin
"""

import ee
import os
import copy
import sys
import pandas as pd
import collections
from pathlib import Path
collections.Callable = collections.abc.Callable

pathparent = str(Path(os.getcwd()).parents[0])
sys.path.append(pathparent)
from configure_account_projects_ee import get_current_account, get_project_from_account
from gee_tools import *
projAccount = get_current_account()
print(f"projetos selecionado >>> {projAccount} <<<")

try:
    ee.Initialize(project= projAccount)
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


# https://code.earthengine.google.com/7b0bd298742d1cd823ffee8224081174

param = {
    'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/bacias_hidrografica_caatinga_49_regions',
    'asset_bioma': 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019',
    'asset_input': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_merged_IndAllv3C',
    'asset_output': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_Savana'    
}


def save_ROIs_toAsset(collection, name):
    optExp = {
        'collection': collection,
        'description': name,
        'assetId': param['asset_output'] + "/" + name
    }
    task = ee.batch.Export.table.toAsset(**optExp)
    task.start()
    print("exportando ROIs da bacia $s ...!", name)


shplimitCerr = ee.FeatureCollection(param['asset_bioma']).filter(ee.Filter.eq('CD_Bioma', 3))
shplimitCaat = ee.FeatureCollection(param['asset_bioma']).filter(ee.Filter.eq('CD_Bioma', 2))
# bacias_int = ["7411","7422","7424","745","746","7622","763","764","765","766","7671"]
bacias_int =  ['746', '763', '764', '7671']
lstFails = []
for nbacias in bacias_int[:]:
    print("processing basin >> " + nbacias)
    try:
        path_ROIsbasin = os.path.join(param['asset_input'], f'rois_grade_{nbacias}')
        shpROIs = ee.FeatureCollection(path_ROIsbasin).filter(ee.Filter.eq('class', 4))
        print(shpROIs.aggregate_histogram('class').getInfo())
        shpROIsCerr = shpROIs.filterBounds(shplimitCerr.geometry())
        shpROIsCerr = shpROIsCerr.map(lambda feat : feat.set('classe', 2))
        # print(shpROIsCerr.size().getInfo())
        shpROIsCaat = shpROIs.filterBounds(shplimitCaat.geometry())
        shpROIsCaat = shpROIsCaat.map(lambda feat : feat.set('classe', 1))
        # print(shpROIsCaat.size().getInfo())
        shpROIsav = shpROIsCerr.merge(shpROIsCaat)

        save_ROIs_toAsset(shpROIsav, f'rois_savana_{nbacias}')

    except:
        lstFails.append(nbacias)

print(f" as bacias que falharam são >> {lstFails}")
#as bacias que falharam são >> ['746', '763', '764', '7671']
