#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

import ee
import os 
import sys
from pathlib import Path
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


spectralBands = ['blue', 'red', 'green', 'nir', 'swir1', 'swir2'];
param = {
    "input_asset": 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Spatials_all',
    "asset_bacias_buffer":  'projects/ee-solkancengine17/assets/shape/bacias_buffer_caatinga_49_regions',
    "asset_afloramento": 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/rockyoutcropcol10',
    "asset_collectionId": 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    "output_asset": 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/extras_yy',
    'versionOut' : 8,
    'versionInp' : 8,
}


#exporta a imagem classificada para o asset
def processoExportar(mapaRF,  nomeDesc, geom_bacia):
    
    idasset =  os.path.join(param['output_asset'], nomeDesc)
    optExp = {
        'image': mapaRF, 
        'description': nomeDesc, 
        'assetId': idasset, 
        'region': geom_bacia,  # .getInfo()['coordinates']
        'scale': 30, 
        'maxPixels': 1e13,
        "pyramidingPolicy":{".default": "mode"}
    }
    task = ee.batch.Export.image.toAsset(**optExp)
    task.start() 
    print("salvando ... " + nomeDesc + "..!")
    # print(task.status())
    for keys, vals in dict(task.status()).items():
        print ( "  {} : {}".format(keys, vals))

def apply_spatialFilterConn(name_bacia):
    
    geomBacia = (ee.FeatureCollection(param['asset_bacias_buffer'])
                    .filter(ee.Filter.eq('nunivotto4', name_bacia))
        )
    geomBacia = geomBacia.map(lambda f: f.set('id_codigo', 1))
    bacia_raster = geomBacia.reduceToImage(['id_codigo'], ee.Reducer.first()).gt(0)            
    geomBacia = geomBacia.geometry()

    imgClass = (ee.ImageCollection(param['input_asset'])
                        .filter(ee.Filter.eq('version', param['versionInp']))
                        .filter(ee.Filter.eq('id_bacias', name_bacia ))
                )
    print(" we load ", imgClass.size().getInfo())
    imgClass = imgClass.first().updateMask(bacia_raster)
    mapSpatial90 = imgClass.select('classification_1990')    
    print('  show metedata imgClass', imgClass.get('system:index').getInfo())

    class_output = ee.Image().byte()
    lst_yy_class = [f'classification_{yy}' for yy in range(1985, 1990)]
    maxVal = 5
    for nyear in range(1985, 1990):
        rasterSpatialYear = imgClass.select(f'classification_{nyear}')
        maskSavana = rasterSpatialYear.eq(4).subtract(mapSpatial90.eq(4)).multiply(maxVal)
        maskSavana = maskSavana.updateMask(maskSavana.neq(0)).rename(f'classification_{nyear}')
        class_output = class_output.addBands(maskSavana)
        maxVal -= 1

    name_exp = f'mascara_savana_ult_anos_{name_bacia}'

    class_output = (class_output.updateMask(bacia_raster)
                .select(lst_yy_class)
                .set(
                    'version', param['versionOut'], 'biome', 'CAATINGA',
                    'collection', '10.0', 'id_bacias', name_bacia,
                    'sensor', 'Landsat', 'source','geodatin', 
                    'model', 'GTB', 
                    'system:footprint', geomBacia
                ))

    processoExportar(class_output,  name_exp, geomBacia)




listaNameBacias = [
    '7691', '7754', '7581', '7625', '7584', '751', '7614', 
    '7616', '745', '7424', '773', '7612', '7613', '752', 
    '7618', '7561', '755', '7617', '7564', '761111','761112', 
    '7741', '7422', '76116', '7761', '7671', '7615', '7411', 
    '7764', '757', '771', '766', '7746', '753', '764', 
    '7541', '7721', '772', '7619', '7443','7544', '7438', 
    '763', '7591', '7592', '746','7712', '7622', '765',     
]


for cc, idbacia in enumerate(listaNameBacias[:]):   
    print("----- PROCESSING BACIA {} -------".format(idbacia))        
    apply_spatialFilterConn(idbacia)