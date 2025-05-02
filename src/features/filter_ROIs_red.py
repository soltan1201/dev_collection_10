#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

import ee
import os 
import sys
import json
from pathlib import Path
import arqParametros as arqParams 
import collections
collections.Callable = collections.abc.Callable

pathparent = str(Path(os.getcwd()).parents[0])
sys.path.append(pathparent)
print("parents ", pathparent)
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
# sys.setrecursionlimit(1000000000)


param = {    
    'bioma': "CAATINGA", #nome do bioma setado nos metadados
    'biomas': ["CAATINGA","CERRADO", "MATAATLANTICA"],
    'asset_bacias': "projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga49div",
    'asset_bacias_buffer' : 'projects/ee-solkancengine17/assets/shape/bacias_buffer_caatinga_49_regions',
    'asset_IBGE': 'users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas',
    # 'assetOutMB': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/Classify_fromMMBV2',
    'assetOut': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_cleaned_DS_v4CC',
    'asset_joinsGrBa': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_cleaned_downsamplesv4C',    
    'asset_joinsGrBaMB': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_cleaned_MB_V4C',
    'outAssetROIs': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/roisJoinedBaGrNN', 
    'asset_mosaic': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',
    'asset_collectionId': 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    'bnd_L': ['blue','green','red','nir','swir1','swir2'],
    'version': 4,
    'yearInicial': 1985,
    'yearFinal': 2024,
    'sufix': "_01",    
    'lsBandasMap': [],
    'dict_classChangeBa': arqParams.dictClassRepre
}
dictRemap = {
    '3': [[3,4,12], [1,0,0]],
    '4': [[3,4,12], [0,1,0]],
    '12': [[3,4,12], [0,0,1]],
    '15': [[15,18,21], [1,0,0]],
    '18': [[15,18,21], [0,1,0]],
    '21': [[15,18,21], [0,0,1]],
}
dictQtLimit = {
    '3': 2000,
    '4': 4000,
    '12': 1200,
    '15': 3000,
    '18': 2000,
    '21': 2500,
    '22': 2000,
    '25': 2000,
    '29': 1000,
    '33': 1000
}
dictGroup = {
    'vegetation' : [3,4,12],
    'agropecuaria': [15,18,21],
    'outros': [22,25,33,29]
} # 
make_complex = False
def getPathCSV (nfolder):
    # get dir path of script 
    mpath = os.getcwd()
    # get dir folder before to path scripts 
    pathparent = str(Path(mpath).parents[0])
    # folder of CSVs ROIs
    roisPath = '/dados/' + nfolder
    mpath = pathparent + roisPath
    print("path of CSVs Rois is \n ==>",  mpath)
    return mpath

def downsamplesFC(dfOneClass, num_limit):
    lstNameProp = dfOneClass.first().propertyNames()
    dfOneClass = dfOneClass.randomColumn('random')
    dfOneClass = dfOneClass.filter(ee.Filter.lt('random', num_limit))
    return dfOneClass.select(lstNameProp)

#exporta a imagem classificada para o asset
def processoExportar(ROIsFeat, IdAssetnameB):
    # id_asset = "projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_cleaned_downsamplesv4C"   
    nameB = IdAssetnameB.split("/")[-1]
    optExp = {
        'collection': ROIsFeat, 
        'description': nameB, 
        'assetId': IdAssetnameB          
        }
    task = ee.batch.Export.table.toAsset(**optExp)
    task.start() 
    print("salvando ... " + nameB + "..!")    

# print(param.keys())
print("vai exportar em ", param['assetOut'])
listYears = [k for k in range(param['yearInicial'], param['yearFinal'] + 1)]
pathFSJson = getPathCSV("FS_col10_json/")
rate_learn = 0.1
max_leaf_node = 50
pmtros_GTB= {
    'numberOfTrees': int(max_leaf_node), 
    'shrinkage': float(rate_learn),         
    'samplingRate': 0.8, 
    'loss': "LeastSquares",#'Huber',#'LeastAbsoluteDeviation', 
    'seed': int(0)
}

nameBacias = [
    '7754', '7691', '7581', '7625', '7584', '751', '7614', 
    '752', '7616', '745', '7424', '773', '7612', '7613', 
    '7618', '7561', '755', '7617', '7564', '761111','761112', 
    '7741', '7422', '76116', '7761', '7671', '7615', '7411', 
    '7764', '757', '771', '7712', '766', '7746', '753', '764', 
    '7541', '7721', '772', '7619', '7443', '765', '7544', '7438', 
    '763', '7591', '7592', '7622', '746'
]
nameBaciasLST = ['7541', '7544', '7592', '7612', '7615',  '7712', '7721', '7741', '7746']
lst_bacias_proc = [item for item in nameBacias if item not in nameBaciasLST]

asset_rois = param['asset_joinsGrBa']
tesauroBasin = arqParams.tesauroBasin
for _nbacia in lst_bacias_proc[30:30]:
    path_ptrosFS = os.path.join(pathFSJson, f"feat_sel_{_nbacia}.json")
    print("load features json ", path_ptrosFS)

    # Open the JSON file for reading
    bandas_fromFS = None
    with open(path_ptrosFS, 'r') as file:
        # Load the JSON data
        bandas_fromFS = json.load(file)
    # lista de classe por bacia 
    lstClassesUn = param['dict_classChangeBa'][tesauroBasin[_nbacia]]    
    print(" lista de classes ", lstClassesUn)
    
    # sys.exit()
    for cc, nyear in enumerate(listYears[:]):  
        nameFeatROIs =  f"{_nbacia}_{nyear}_cd"  
        print("loading Rois JOINS = ", nameFeatROIs)
        lstbandas_import = bandas_fromFS[f"{_nbacia}_{nyear}"]['features']
        bandas_imports = [bnd for bnd in lstbandas_import if 'stdDev' not in bnd]
        if 'solpe' in bandas_imports:
            bandas_imports.remove('solpe')        
        if 'slope' not in bandas_imports:
            bandas_imports += ['slope']
        if 'hillshade' not in bandas_imports:
            bandas_imports += ['hillshade']
        print(f" numero de bandas selecionadas {len(bandas_imports)} ") 

        try:
            ROIs_toTrain = ee.FeatureCollection( os.path.join(param['assetOut'], nameFeatROIs))
            print('  >>>> ', ROIs_toTrain.aggregate_histogram('class').getInfo())        
        except:
            ROIs_toTrain = (
                ee.FeatureCollection( os.path.join(asset_rois, nameFeatROIs)) 
                            # .filter(ee.Filter.eq("year", nyear))  
                            .filter(ee.Filter.inList('class', lstClassesUn))  
                            .select(bandas_imports + ['class'])
            )
            print('  >>>> ', ROIs_toTrain.aggregate_histogram('class').getInfo())
            feaReSamples = ee.FeatureCollection([])
            if make_complex:                
                for tipo in list(dictGroup.keys()):
                    print(f"------ grupo {tipo} -----------------")
                    fcYYtipo = ROIs_toTrain.filter(ee.Filter.inList('class', dictGroup[tipo]))
                    if tipo in ['vegetation', 'agropecuaria']:
                        dict_Class = ee.Dictionary(fcYYtipo.aggregate_histogram('class')).getInfo()
                        for nclass in list(dict_Class.keys()):
                            nclass =  int(float(nclass))
                            print("filter by class == ", nclass)
                            fcYYbyClass = fcYYtipo.remap(dictRemap[str(nclass)][0], dictRemap[str(nclass)][1], 'class') 
                            # treinamdo para amostras de duas classes 
                            classifierGTB = (ee.Classifier.smileGradientTreeBoost(**pmtros_GTB)
                                            .train(fcYYbyClass, 'class', bandas_imports)
                                            .setOutputMode('PROBABILITY'))
                            # classificando para a classe de valor 1
                            classROIsGTB = (fcYYbyClass.filter(ee.Filter.eq('class', 1))
                                                .classify(classifierGTB, 'label'))

                            step = 5
                            for ii in range(70, 100, 5):
                                frac_inic = ii/100
                                frac_end = (ii + step)/100 
                                classROIsGTBf = (classROIsGTB.filter(
                                                    ee.Filter.And(
                                                        ee.Filter.gt('label', frac_inic),
                                                        ee.Filter.lte('label', frac_end)
                                                    )
                                                ))
                                sizeFilt = classROIsGTBf.size()# .getInfo()
                                num_limite = ee.Number(dictQtLimit[str(nclass)]).divide(ee.Number(sizeFilt))
                                
                                # if sizeFilt > self.dictQtLimit[str(nclass)]:                                
                                classROIsGTBf = ee.Algorithms.If(
                                                ee.Algorithms.IsEqual(ee.Number(sizeFilt).gt(dictQtLimit[str(nclass)]), 1),
                                                downsamplesFC(classROIsGTBf, num_limite), classROIsGTBf
                                            )                            
                                
                                classROIsGTBf = ee.FeatureCollection(classROIsGTBf).remap([1], [nclass], 'class')
                                feaReSamples = feaReSamples.merge(classROIsGTBf)

            else:
                # feaReSamples = ee.FeatureCollection([]) 
                for nclass in [4, 15, 21]:
                    nclass =  int(float(nclass))                    
                    classROIs = ROIs_toTrain.filter(ee.Filter.eq('class', nclass))
                    sizeFilt = classROIs.size().getInfo()
                    # print(classROIs.propertyNames().getInfo())
                    print(f"filter by class == {nclass}  with {sizeFilt}" )
                    if sizeFilt > 5:                        
                        num_limite = ee.Number(dictQtLimit[str(nclass)]).divide(ee.Number(sizeFilt))
                        classROIsSel = downsamplesFC(classROIs, num_limite)
                        # print(classROIsSel.propertyNames().getInfo())
                        classROIsSel = classROIsSel.filter(ee.Filter.notNull(bandas_imports[:2]))
                        # print(classROIsSel.first().propertyNames().getInfo())
                        feaReSamples = feaReSamples.merge(ee.FeatureCollection(classROIsSel))

                classROIsSel = ROIs_toTrain.filter(ee.Filter.inList('class', [4, 15, 21]).Not())
                # print(feaReSamples.propertyNames().getInfo())
                feaReSamples = feaReSamples.merge(ee.FeatureCollection(classROIsSel))              

                    # self.processoExportar(feaReSamples, idAssetOut)
            
            idAssetOut = os.path.join(param['assetOut'], nameFeatROIs)
            processoExportar(feaReSamples, idAssetOut )