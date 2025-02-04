#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Produzido por Geodatin - Dados e Geoinformacao
DISTRIBUIDO COM GPLv2
@author: geodatin
"""
import os
import ee
# import gee
import copy
import sys
import pandas as pd
from tqdm import tqdm
import register_parameters as reg_param
import collections
collections.Callable = collections.abc.Callable

from pathlib import Path

pathparent = str(Path(os.getcwd()).parents[0])
sys.path.append(pathparent)
pathparent = str(Path(os.getcwd()).parents[1])
sys.path.append(pathparent)
from configure_account_projects_ee import get_current_account, get_project_from_account
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


param = {
    'asset_rois_grid1': {'id' : 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_merged_Indall'},
    'anoInicial': 2016,
    'anoFinal': 2024,
}


def ask_byGrid_saved( dict_asset, printName): 
    getlstFeat2 = ee.data.getList(dict_asset)
    assetbase = "projects/earthengine-legacy/assets/" + dict_asset['id']
    lstPath2 = [kk for kk in getlstFeat2]
    print(f" we have {len(lstPath2)} featshp of ROIs")
    lstGridFails = []
    # sys.exit()
    lstPathFeat = []
    for idAsset in tqdm(lstPath2):    
        # print(idAsset)     
        path_ = idAsset['id']
        name_feat = path_.replace(assetbase + '/', '')
        if printName:
            print(f" loading {name_feat}")
        feat_tmp = ee.FeatureCollection(path_)
        print(f" distribution for class in Features {feat_tmp.aggregate_histogram('class').getInfo()}")
        print(f" distribution for YEAR in Features {feat_tmp.aggregate_histogram('year').getInfo()}")
        # print("=== class 18 and 33 ==================")
        # print("years of Class 18 >> ", feat_tmp.filter(ee.Filter.eq('class', 18)).aggregate_histogram('year').getInfo())
        # print("years of Class 33 >> ", feat_tmp.filter(ee.Filter.eq('class', 33)).aggregate_histogram('year').getInfo())

    

listaNameBacias = [
    '7754', '7691', '7581', '7625', '7584', '751', '7614', 
    '752', '7616', '745', '7424', '773', '7612', '7613', 
    '7618', '7561', '755', '7617', '7564', '761111', '761112', 
    '7741', '7422', '76116', '7761', '7671', '7615', '7411', 
    '7764', '757', '771', '7712', '766', '7746', '753', '764', 
    '7541', '7721', '772', '7619', '7443', '765', '7544', '7438', 
    '763', '7591', '7592', '7622', '746'
]

ask_byGrid_saved( param['asset_rois_grid1'], True)
