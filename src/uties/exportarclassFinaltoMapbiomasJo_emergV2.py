#!/usr/bin/env python2
# -*- coding: utf-8 -*-

##########################################################
## CRIPT DE EXPORTAÇÃO DO RESULTADO FINAL PARA O ASSET  ##
## DE mAPBIOMAS                                         ##
## Produzido por Geodatin - Dados e Geoinformação       ##
##  DISTRIBUIDO COM GPLv2                               ##
#########################################################

import ee 
import sys
import collections
collections.Callable = collections.abc.Callable

try:
    ee.Initialize(project='mapbiomas-brazil')
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise



param = {
    'asset_caat_buffer': 'users/CartasSol/shapes/caatinga_buffer5km',
    'outputAsset': 'projects/mapbiomas-brazil/assets/LAND-COVER/COLLECTION-10/GENERAL/classification-caa', 
    'inputAsset': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/MergerV5',   
    'biome': 'CAATINGA', #configure como null se for tema transversal
    'version': 1,
    'collection': 10.0,
    'source': 'geodatin',
    'setUniqueCount': True,
    'theme': None, 
    'numeroTask': 0,
    'numeroLimit': 39,
    'conta' : {
        '0': 'caatinga01',   # 
        '5': 'caatinga02',
        '10': 'caatinga03',
        '15': 'caatinga04',
        '20': 'caatinga05',        
        '25': 'solkan1201',    
        '30': 'solkanGeodatin',
        '35': 'diegoUEFS',
        # '16': 'superconta' 
    }

}
classMapB = [ 0, 3, 4, 5, 6, 9,11,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62]
classNew =  [27, 4, 4, 4, 4, 4,12,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33,21,33,33,21,21,21,21,21,21,21,21,21,21,49,50,21]

countFix = 0
# countFix = gerenciador(countFix, param) 
processExport = True
metadados = {}
bioma5kbuf = ee.FeatureCollection(param['asset_caat_buffer'])
bioma5kbuf = bioma5kbuf.map(lambda f: f.set('id_codigo', 1))
bioma5k_raster = bioma5kbuf.reduceToImage(['id_codigo'], ee.Reducer.first()).gt(0) 
bioma5kbuf = bioma5kbuf.geometry()
layerFloresta = None
imgColExp = ee.ImageCollection(param['inputAsset'])
print("lista de bandas da imagem min \n ", imgColExp.size().getInfo())

for ii, year in enumerate(range(1985, 2025)):  #        
    bandaAct = 'classification_' + str(year) 
    name = param['biome'] + '-' + str(year) + '-' + str(param['version'])
    imgExtraBnd = imgColExp.select(bandaAct).min()
    print("layer  ", imgExtraBnd.bandNames().getInfo() )
    # sys.exit()
    
    imgYear = (imgExtraBnd.updateMask(bioma5k_raster)
                    .set('biome', param['biome'])
                    .set('year', year)
                    .set('version', str(param['version']))
                    .set('collection', param['collection'])
                    .set('source', param['source'])
                    .set('theme',None)
                    .set('system:footprint', bioma5kbuf)    
            )

    
    name = param['biome'] + '-' + str(year) + '-' + str(param['version'])
    if processExport:
        optExp = {   
            'image': imgYear.byte(), 
            'description': name, 
            'assetId': param['outputAsset'] + '/' + name, 
            'region': bioma5kbuf, #.getInfo()['coordinates']
            'scale': 30, 
            'maxPixels': 1e13,
            "pyramidingPolicy": {".default": "mode"}
        }
        task = ee.batch.Export.image.toAsset(**optExp)
        task.start() 
        print("salvando ... banda  " + name + "..!")
    else:
        print(f"verficando => {name} >> {imgYear.bandNames().getInfo()}")
        
        # sys.exit()