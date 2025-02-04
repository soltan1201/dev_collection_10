#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
# SCRIPT DE CLASSIFICACAO POR BACIA
# Produzido por Geodatin - Dados e Geoinformacao
# DISTRIBUIDO COM GPLv2
'''

import ee 
# import gee
import sys
import os
import glob
from pathlib import Path
from tqdm import tqdm
import collections
from pathlib import Path
collections.Callable = collections.abc.Callable

pathparent = str(Path(os.getcwd()).parents[0])
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
# sys.setrecursionlimit(1000000000)

param = {    
    'asset_ROIs_manual': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/cROIsN2manualNN'},
    'asset_ROIs_cluster': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/cROIsN2clusterNN'},
    'asset_ROIs_automatic': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/coletaROIsv1N245'},
    'asset_ROIs_automatic': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/cROIsN5allBND'},
    'asset_ROIs_grades': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/roisGradesgrouped'},
    'asset_ROIS_bacia_grade': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/roisGradesgroupedBuf'},
    'asset_ROIS_joinsBaGr': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/roisJoinsbyBaciaNN'},
    'asset_ROISall_joins': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_merged_IndAll'},
    'anoInicial': 1985,
    'anoFinal': 2022,
    'numeroTask': 6,
    'numeroLimit': 4,
    'conta' : {
        '0': 'solkanGeodatin'              
    },
    'showFilesCSV' : False,
    'showAssetFeat': False
}

#lista de anos
list_anos = [k for k in range(param['anoInicial'],param['anoFinal'] + 1)]
print('lista de anos', list_anos)

#nome das bacias que fazem parte do bioma (38 bacias)
nameBacias = [
    '7754', '7691', '7581', '7625', '7584', '751', '7614', 
    '752', '7616', '745', '7424', '773', '7612', '7613', 
    '7618', '7561', '755', '7617', '7564', '761111','761112', 
    '7741', '7422', '76116', '7761', '7671', '7615', '7411', 
    '7764', '757', '771', '7712', '766', '7746', '753', '764', 
    '7541', '7721', '772', '7619', '7443', '765', '7544', '7438', 
    '763', '7591', '7592', '7622', '746'
]

#========================METODOS=============================
def GetPolygonsfromFolder(dictAsset):
    
    getlistPtos = ee.data.getList(dictAsset)
    ColectionPtos = []
    # print("bacias vizinhas ", nBacias)
    lstROIsAg = [ ]
    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id')        
        ColectionPtos.append(path_) 
        name = path_.split("/")[-1]
        if param['showAssetFeat']:
            print("Reading ", name)
        
    return ColectionPtos


#========================METODOS=============================
# def gerenciador(cont, param):
#     #0, 18, 36, 54]
#     #=====================================#
#     # gerenciador de contas para controlar# 
#     # processos task no gee               #
#     #=====================================#
#     numberofChange = [kk for kk in param['conta'].keys()]

#     if str(cont) in numberofChange:
        
#         gee.switch_user(param['conta'][str(cont)])
#         gee.init()        
#         gee.tasks(n= param['numeroTask'], return_list= True)        
    
#     elif cont > param['numeroLimit']:
#         cont = 0
    
#     cont += 1    
#     return cont

#exporta a imagem classificada para o asset
def processoExportar(ROIsFeat, nameB, nfolder):
    
    optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'folder': nfolder          
        }
    task = ee.batch.Export.table.toDrive(**optExp)
    task.start() 
    print("salvando ... " + nameB + "..!")    

# get dir path of script 
npath = os.getcwd()
# get dir folder before to path scripts 
npath = str(Path(npath).parents[0])
# folder of CSVs ROIs
roisPath = '/dados/Col9_ROIs_grades/'
npath += roisPath
print("path of CSVs Rois is \n ==>",  npath)


lstPathCSV = glob.glob(npath + "*.csv")
lstNameFeat = []
for xpath in tqdm(lstPathCSV):
    nameCSV = xpath.split("/")[-1][:-4]
    if param['showFilesCSV']:
        print(" => " + nameCSV)
    lstNameFeat.append(nameCSV)

cont = 0
# cont = gerenciador(cont, param)
lstNameFeat = []
# sys.exit()
# iterando com cada uma das folders FeatC do asset
# 'asset_ROIs_cluster', 'asset_ROIs_manual', asset_ROIs_grades, asset_ROIS_bacia_grade
# asset_ROIS_joinsBaGr ,asset_ROISall_joins
lstKeysFolder = ['asset_ROISall_joins']   
for assetKey in lstKeysFolder:
    lstAssetFolder = GetPolygonsfromFolder(param[assetKey])
    list_baciaYearFaltan = []
    for cc, assetFeats in enumerate(lstAssetFolder[:]):        
        nameFeat = assetFeats.split("/")[-1]
        if nameFeat not in lstNameFeat:
            print(f" #{cc} loading FeatureCollection => ", assetFeats)
            try: 
                ROIs = ee.FeatureCollection(assetFeats)       
                print(nameFeat, " ", ROIs.size().getInfo())     
                processoExportar(ROIs, nameFeat, "ROIs_Joined_All")              
            except:
                # list_baciaYearFaltan.append(nameFeat)
                # arqFaltante.write(nameFeat + '\n')
                print("faltando ... " + nameFeat)

    # arqFaltante.close()