#!/usr/bin/env python3.12
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

##############################################
###     Helper function
###    @param item 
##############################################
def convert2featCollection (item):
    item = ee.Dictionary(item)
    feature = ee.Feature(ee.Geometry.Point([0, 0])).set(
        'classe', item.get('classe'),"area", item.get('sum'))
        
    return feature

#########################################################################
####     Calculate area crossing a cover map (deforestation, mapbiomas)
####     and a region map (states, biomes, municipalites)
####      @param image 
####      @param geometry
#########################################################################
# https://code.earthengine.google.com/5a7c4eaa2e44f77e79f286e030e94695
# https://code.earthengine.google.com/?accept_repo=users%2Fmapbiomas%2Fuser-toolkit&scriptPath=users%2Fmapbiomas%2Fuser-toolkit%3Amapbiomas-user-toolkit-calculate-area.js
def calculateArea (image, pixelArea, geometry):

    pixelArea = pixelArea.addBands(image.rename('classe')).clip(geometry)#.addBands(
                                # ee.Image.constant(yyear).rename('year'))
    reducer = ee.Reducer.sum().group(1, 'classe')
    optRed = {
        'reducer': reducer,
        'geometry': geometry,
        'scale': param['scale'],
        'bestEffort': True, 
        'maxPixels': 1e13
    }    
    areas = pixelArea.reduceRegion(**optRed)

    areas = ee.List(areas.get('groups')).map(lambda item: convert2featCollection(item))
    areas = ee.FeatureCollection(areas)    
    return areas

param = {
    'asset_cobertura_col90': "projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1",
    'asset_matopiba': 'projects/mapbiomas-fogo/assets/territories/matopiba',
    "BR_ESTADOS_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_ESTADOS_2022",
    "br_estados_raster": 'projects/mapbiomas-workspace/AUXILIAR/estados-2016-raster',
    "BR_Municipios_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_Municipios_2022",
    "BR_Pais_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_Pais_2022",
    "Im_bioma_250" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/Im_bioma_250",
    'vetor_biomas_250': 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
    'biomas_250_rasters': 'projects/mapbiomas-workspace/AUXILIAR/RASTER/Bioma250mil',
    'classMapB': [3, 4, 5, 9, 12, 13, 15, 18, 18, 20, 21, 22, 23, 24, 25, 26, 29, 30, 31, 32, 33,
                      36, 39, 40, 41, 46, 47, 48, 49, 50, 62],
    'classNew':  [4, 4, 4, 4,  4,  4, 15, 18, 18, 18, 15, 22, 22, 22, 22, 33,  4, 22, 33, 4, 33,
                      18, 18, 18, 18, 18, 18, 18,  4,  12, 18],
    'lstYears': [nyear for nyear in range(1985, 2024)],
    'driverFolder': 'AREA-EXP-fireMATOPIBA',
    'scale': 30
}
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
    '32': 'ESPÍRITO SANTO',
    '17': 'Tocantins',
}


def iterandoXanoImCruda(limiteEst, estadoCod):
    

    est_raster = ee.Image(param["br_estados_raster"]).eq(int(estadoCod))
    biomas_raster = ee.Image(param['biomas_250_rasters']).eq(2);
    maskunico = est_raster.updateMask(biomas_raster)
    pixelArea = ee.Image.pixelArea().updateMask(maskunico).divide(10000)
    
    shpBioma = (
        ee.FeatureCollection(param['vetor_biomas_250'])
                .filter(ee.Filter.eq('CD_Bioma', 2))
    ).geometry()
    recorteGeo = shpBioma.intersection(limiteEst.geometry())
    areaEstado = ee.FeatureCollection([])
    imgDynamica = ee.Image.constant(0)

    for nyear in param['lstYears'][1:]:
        nbandaCou = 'classification_' + str(nyear) 
        nbandaBef = 'classification_' + str(nyear - 1) 
        
        imgCobCou = (
            ee.Image(param['asset_cobertura_col90'])
                    .select(nbandaCou)
                    .remap(param['classMapB'], param['classNew'])
                    .updateMask(maskunico)
        ) 
        imgCobBef = (
            ee.Image(param['asset_cobertura_col90'])
                    .select(nbandaBef)
                    .remap(param['classMapB'], param['classNew'])
                    .updateMask(maskunico)

        )         
        imgDynamica = (
            imgDynamica
                .where(imgCobBef.eq(4).And( imgCobCou.eq(15)), 1)    # Desmatamento to pasture
                .where(imgCobBef.eq(4).And( imgCobCou.eq(18)), 2)    # Desmatamento to agriculture
                .where(imgCobBef.eq(4).And( imgCobCou.eq(21)), 3)    # Desmatamento to Mosaic of uses
                .where(imgCobBef.eq(18).And(imgCobCou.eq(15)), 4)    # agriculture to pasture
                .where(imgCobBef.eq(18).And(imgCobCou.eq(21)), 5)    # agriculture to Mosaic of uses
                .where(imgCobBef.eq(18).And(imgCobCou.eq(4) ), 6)      # agriculture to Regeneration
                .where(imgCobBef.eq(15).And(imgCobCou.eq(18)), 7)      # Pasture to agriculture
                .where(imgCobBef.eq(15).And(imgCobCou.eq(21)), 8)      # Pasture to Mosaic of uses
                .where(imgCobBef.eq(15).And(imgCobCou.eq(4) ), 9)      # Pasture to Regeneration
                .where(imgCobBef.eq(21).And(imgCobCou.eq(15)), 10)     # Mosaic of uses to pasture
                .where(imgCobBef.eq(21).And(imgCobCou.eq(18)), 11)     # Mosaic of uses to agriculture
                .where(imgCobBef.eq(21).And(imgCobCou.eq(4) ), 12)     # Mosaic of uses to Regeneration
                .where(imgDynamica.eq(2).And(imgCobCou.eq(15)), 13)    # Desmatamento to agriculture to pasture
                .where(imgDynamica.eq(2).And(imgCobCou.eq(21)), 14)    # Desmatamento to agriculture to Mosaic of uses
                .where(imgDynamica.eq(2).And(imgCobCou.eq(4) ), 15)    # Desmatamento to agriculture to Regeneration
                .where(imgDynamica.eq(3).And(imgCobCou.eq(18)), 16)    # Desmatamento to Mosaic of uses to agriculture 
                .where(imgDynamica.eq(3).And(imgCobCou.eq(15)), 17)    # Desmatamento to Mosaic of uses to pasture 
                .where(imgDynamica.eq(3).And(imgCobCou.eq(4) ), 18)    # Desmatamento to Mosaic of uses to Regeneration 
                .where(imgDynamica.eq(1).And(imgCobCou.eq(21)), 19)    # Desmatamento to pasture to Mosaic of uses
                .where(imgDynamica.eq(1).And(imgCobCou.eq(18)), 20)    # Desmatamento to pasture to agriculture 
                .where(imgDynamica.eq(1).And(imgCobCou.eq(4) ), 21)    # Desmatamento to pasture to Regeneration                 
                .where(imgDynamica.eq(11).And(imgCobCou.eq(15)), 22)   # Mosaic of uses to agriculture to pasture
                .where(imgDynamica.eq(10).And(imgCobCou.eq(18)), 23)   # Mosaic of uses to pasture to agriculture 
                .where(imgDynamica.eq(7).And(imgCobCou.eq(15) ), 24)   # pasture to agriculture to pasture              
                .where(imgDynamica.eq(4).And(imgCobCou.eq(18) ), 25)   # agriculture to pasture to agriculture                 
                # .rename('dynamica_' + str(nyear))
            )
    imgDynamica = imgDynamica.rename('classe')

    areaTemp = calculateArea (imgDynamica.selfMask(), pixelArea, recorteGeo)        
    areaTemp = areaTemp.map( lambda feat: feat.set(
                                        'year', nyear, 
                                        'region', 'Caatinga', 
                                        'estado_name', dictEst[str(estadoCod)], # colocar o nome do estado
                                        'estado_codigo', estadoCod
                                    ))
    areaEstado = areaEstado.merge(areaTemp) 

    return areaEstado

#exporta a imagem classificada para o asset
def processoExportar(areaFeat, nameT):      
    optExp = {
          'collection': areaFeat, 
          'description': nameT, 
          'folder': param["driverFolder"]        
        }    
    task = ee.batch.Export.table.toDrive(**optExp)
    task.start() 
    print("salvando ... " + nameT + "..!")   

# bioma = 'Caatinga'
# rasterLimit = ee.Image(param['biomas_250_rasters']).eq(2)

shpEstados = ee.FeatureCollection(param['BR_ESTADOS_2022'])
lstEstCruz = ['22','23','24','25','26','27','28','29','31','32']
# lstEstCruz = ['17','21','22','29'];

areaGeral = ee.FeatureCollection([]) 
# print("---- SHOW ALL BANDS FROM MAPBIOKMAS MAPS -------\n ", imgMapp.bandNames().getInfo())
for estadoCod in lstEstCruz[:]:    
    print(f"processing Estado {dictEst[str(estadoCod)]} with code {estadoCod}")
    shpEstado = shpEstados.filter(ee.Filter.eq('CD_UF', estadoCod))
    areaXestado = iterandoXanoImCruda(shpEstado, estadoCod)
    print("adding area ")
    # areaGeral = areaGeral.merge(areaXestado)

    print("exportando a área geral ")
    processoExportar(areaXestado, f'area_cobertura_col90_state_caatinga_{estadoCod}')