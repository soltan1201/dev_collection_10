
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

param = {      
    'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Merger',
    'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Spatials_all',
    'input_asset_bef' : 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/transitionTest',
    # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Gap-fill',
    # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/TemporalA',
    # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Frequency',
    'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/bacias_hidrografica_caatinga_49_regions',            
    'last_year' : 2024,
    'first_year': 1985,
    'versionOut' : 10,
    'versionInp' : 10,
}

def apply_mixed_asset_export(name_bacia):
    lstnameBaciasV9 = ["7754","773","761112"]
    lstnameBaciasV10 = ["7591","7613","7746","7741","7581","757"]
    nversion = 8
    asset_to_load = param['input_asset_bef']
    if name_bacia in lstnameBaciasV9:
        nversion = 9
        asset_to_load = param['input_asset']
    if name_bacia in lstnameBaciasV10:
        nversion = 10
        asset_to_load = param['input_asset']
    print(f" >>> processing version {nversion} || bacia {name_bacia}")
    geomBacia = (ee.FeatureCollection(param['asset_bacias_buffer'])
                    .filter(ee.Filter.eq('nunivotto4', name_bacia))
        )
    geomBacia = geomBacia.map(lambda f: f.set('id_codigo', 1)).geometry()

    imgClass = (ee.ImageCollection(asset_to_load)
                        .filter(ee.Filter.eq('version', nversion))
                        .filter(ee.Filter.eq('id_bacias', name_bacia ))
                        .first()
                )
    print("processing >>> ", imgClass.get('system:index').getInfo())
    nameExp = f"filterMX_BACIA_{name_bacia}_GTB_V{param['versionOut']}"
    imgClass = (imgClass
                    .set(
                        'version', param['versionOut'], 'biome', 'CAATINGA',
                        'collection', '10.0', 'id_bacias', name_bacia,
                        'sensor', 'Landsat', 'source','geodatin', 
                        'model', 'GTB', 'system:footprint', geomBacia
                    ))
    processoExportar(imgClass,  nameExp, geomBacia)


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
    apply_mixed_asset_export(idbacia)