#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

import ee 
import sys
import glob
import collections
collections.Callable = collections.abc.Callable

try:
    # ee.Initialize(project= 'geo-data-s')    
    ee.Initialize(project= 'mapbiomas-caatinga-cloud05')
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


params = {
    'asset_Col6' : 'projects/mapbiomas-public/assets/brazil/lulc/collection6/mapbiomas_collection60_integration_v1',
    'asset_Col71' : 'projects/mapbiomas-public/assets/brazil/lulc/collection7_1/mapbiomas_collection71_integration_v1',
    'asset_Col8' : 'projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_integration_v1',
    'asset_col9' : "projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1",
    'asset_biomas': 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019-raster',
    'asset_sphBiomas': "projects/mapbiomas-workspace/AUXILIAR/biomas-2019",
    'assetOutput': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/aggrements',
    "br_estados_raster": 'projects/mapbiomas-workspace/AUXILIAR/estados-2016-raster',
    "BR_ESTADOS_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_ESTADOS_2022",
    'vetor_biomas_250': 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
}

"""
//   var ano = 2021
//   AZUL somente na col 8
//   VERMELHO somente col7.1
//   CINZA mapeado nos 2 
//   listar anos para poerformar a análise
//   years = [2021];
"""
dictEst = {
    '21': 'MARANHÃO',
    '22': 'PIAUÍ',
    '23': 'CEARÁ',
    '24': 'RIO GRANDE DO NORTE',
    '25': 'PARAÍBA',
    '26': 'PERNAMBUCO',
    '27': 'ALAGOAS',
    '28': 'SERGIPE',
    '29': 'BAHIA',
    '31': 'MINAS GERAIS',
    '32': 'ESPÍRITO SANTO'
}

##############################################
###     Helper function
###    @param item 
##############################################
def convert2featCollection (item):
    item = ee.Dictionary(item)
    feature = ee.Feature(ee.Geometry.Point([0, 0])).set(
        'conc', item.get('conc'),"area", item.get('sum'))
        
    return feature

#########################################################################
####     Calculate area crossing a cover map (deforestation, mapbiomas)
####     and a region map (states, biomes, municipalites)
####      @param image 
####      @param geometry
#########################################################################
# https://code.earthengine.google.com/5a7c4eaa2e44f77e79f286e030e94695
def calculateArea (image, pixelArea, geometry):

    pixelArea = pixelArea.addBands(image.rename('conc')).clip(geometry)#.addBands(
                                # ee.Image.constant(yyear).rename('year'))
    reducer = ee.Reducer.sum().group(1, 'conc')
    optRed = {
        'reducer': reducer,
        'geometry': geometry,
        'scale': 30,
        'bestEffort': True, 
        'maxPixels': 1e13
    }    
    areas = pixelArea.reduceRegion(**optRed)

    areas = ee.List(areas.get('groups')).map(lambda item: convert2featCollection(item))
    areas = ee.FeatureCollection(areas)    
    return areas

def iterandoXanoImCruda(imgAreaRef, imgMapp, limite, nclass, nyear):
    CD_Bioma = 2
    estados_raster = ee.Image(params["br_estados_raster"])
    lstEstCruz = [22,23,24,25,26,27,28,29,31]
    areaGeral = ee.FeatureCollection([]) 
    limitGeometria = ee.FeatureCollection(params["vetor_biomas_250"])
    limitGeometria = limitGeometria.filter(ee.Filter.eq("CD_Bioma", CD_Bioma))

    for estadoCod in lstEstCruz:        
        print(f"processing Estado {dictEst[str(estadoCod)]} with code {estadoCod}")
        maskRasterEstado = estados_raster.eq(estadoCod)
        rasterMapEstado = imgMapp.updateMask(maskRasterEstado)
        imgAreaEst = imgAreaRef.updateMask(maskRasterEstado)
        regEst = (
            ee.FeatureCollection(params['BR_ESTADOS_2022'])
            .filter(ee.Filter.eq("CD_UF", str(estadoCod)))
            .geometry().intersection(limitGeometria.geometry())            
        )

        areaTemp = calculateArea (rasterMapEstado, imgAreaEst, regEst)        
        areaTemp = areaTemp.map( lambda feat: feat.set(
                                            'year', nyear, 
                                            'classe', nclass,                                            
                                            'estado_codigo', estadoCod
                                        ))
        areaGeral = areaGeral.merge(areaTemp)

    return areaGeral


def processoExportar(areaFeat, nameT):      
    optExp = {
          'collection': areaFeat, 
          'description': nameT, 
          'folder': 'areas_aggrements'        
        }    
    task = ee.batch.Export.table.toDrive(**optExp)
    task.start() 
    print("salvando ... " + nameT + "..!")    

#//exporta a imagem classificada para o asset
def processoExportarImage (imageMap, nameB, idAssetF, regionB):
    idasset =  idAssetF + "/" + nameB
    print("saving ")
    optExp = {
            'image': imageMap, 
            'description': nameB, 
            'assetId': idasset, 
            'region': regionB.getInfo()['coordinates'], #//['coordinates']
            'scale': 30, 
            'maxPixels': 1e13,
            "pyramidingPolicy":{".default": "mode"}
        }
        
    task = ee.batch.Export.image.toAsset(**optExp)
    task.start() 
    print("salvando mapa ... " + nameB + "..!");


bioma =  'Caatinga'; 
biomes = ee.Image(params['asset_biomas']).eq(5).selfMask();
limitBioma = ee.FeatureCollection(params['asset_sphBiomas']).filter(ee.Filter.eq("Bioma", bioma));

pixelArea = ee.Image.pixelArea().divide(10000).updateMask(biomes)
class_col80 = ee.Image(params['asset_Col8']).updateMask(biomes);
class_col90 = ee.Image(params['asset_col9']).updateMask(biomes);
#Map.addLayer(ee.Image.constant(1), {min: 0, max: 1}, 'base');
    
cont = 2      
#// listar classes para performar a análise 
lst_classes = [3,4,12,29,15,18,21,22,25,33];
for year_j in range(1985, 2024):
    # // para cada classe 
    # // para cada ano  
    print("processing year >> ", year_j)
    year_j = str(year_j)
    col8_j = class_col80.select('classification_'+ year_j);
    col9_j = class_col90.select('classification_'+year_j);
    featColCC = ee.FeatureCollection([])
    for class_i in lst_classes:
        print(f"select class {class_i} in aggrements ")
        images = ee.Image(0);
        #// selecionar a classificação do ano j        
        #// calcular concordância
        conc = ee.Image(0).where(col8_j.eq(class_i).And(col9_j.eq(class_i)), 1).where(   #// [1]: Concordância
                            col9_j.eq(class_i).And(col8_j.neq(class_i)), 2).where(  #// [2]: Apenas col8
                            col9_j.neq(class_i).And(col8_j.eq(class_i)), 3)  #// [3]: Apenas Col7.1
                            #//.updateMask(biomes.eq(4));
        
        conc = conc.updateMask(conc.neq(0)).rename('territory_' + year_j);
        areaCC = iterandoXanoImCruda(pixelArea, conc, limitBioma, class_i, year_j);
        featColCC = featColCC.merge(areaCC)
    
    nameSHP = f'Agreement_{year_j}'
    processoExportar(featColCC, nameSHP)
    
  