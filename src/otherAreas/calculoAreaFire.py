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
# import pandas as pd
# from tqdm import tqdm

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
    'asset_fire_monitor' : 'projects/mapbiomas-public/assets/brazil/fire/monitor/mapbiomas_fire_monthly_burned_v1',
    'asset_fire_anual_cov': 'projects/mapbiomas-public/assets/brazil/fire/collection3_1/mapbiomas_fire_collection31_annual_burned_coverage_v1',
    'asset_matopiba': 'projects/mapbiomas-fogo/assets/territories/matopiba',
    'asset_semiarido': 'projects/mapbiomas-workspace/AUXILIAR/SemiArido_2024',
    "BR_ESTADOS_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_ESTADOS_2022",
    "br_estados_raster": 'projects/mapbiomas-workspace/AUXILIAR/estados-2016-raster',
    "BR_Municipios_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_Municipios_2022",
    "BR_Pais_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_Pais_2022",
    "Im_bioma_250" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/Im_bioma_250",
    'vetor_biomas_250': 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
    'biomas_250_rasters': 'projects/mapbiomas-workspace/AUXILIAR/RASTER/Bioma250mil',
    'lstYears': [2019,2020,2021,2022,2023],
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
    '17': 'TOCANTINS',
    '52': 'GOIÁS'
}


def iterandoXanoImCruda_monitor(limiteEst, estadoCod, cruzMPB):
    areaEstado = ee.FeatureCollection([])
    shpMatopiba = ee.FeatureCollection(param['asset_matopiba']).geometry()
    recorteGeo = shpMatopiba.intersection(limiteEst.geometry())
    pixelArea = ee.Image.pixelArea().divide(10000).clip(recorteGeo)
    biomas_raster = ee.Image(param['biomas_250_rasters']).eq(2);

    for nyear in param['lstYears']:
        print(f" ======== processing year {nyear} for mapbiomas Monitor Fire  =====")
        imgFire = (
            ee.ImageCollection(param['asset_fire_monitor'])
                    .filter(ee.Filter.eq('year', nyear))
                    .reduce(ee.Reducer.sum()).gt(0)
                    .updateMask(biomas_raster)
        )        
        imgFire = imgFire.clip(recorteGeo).selfMask();
        areaTemp = calculateArea (imgFire, pixelArea, recorteGeo)        
        areaTemp = areaTemp.map( lambda feat: feat.set(
                                            'year', nyear, 
                                            'region', 'Matopiba', 
                                            'estado_name', dictEst[str(estadoCod)], # colocar o nome do estado
                                            'estado_codigo', estadoCod
                                        ))
        areaEstado = areaEstado.merge(areaTemp) 

    return areaEstado

def iterandoXanoImCruda_Cover(limiteEst, estadoCod, cruzMPB):
    areaEstado = ee.FeatureCollection([])    
    shpSemiarido = ee.FeatureCollection(param['asset_semiarido']).geometry()
    recorteGeo = shpSemiarido.intersection(limiteEst.geometry())
    if cruzMPB:
        shpMatopiba = ee.FeatureCollection(param['asset_matopiba']).geometry()
        recorteGeo = recorteGeo.intersection(shpMatopiba)

    masc_recorte = (ee.FeatureCollection([ee.Feature(recorteGeo, {'valor': 1})])
                        .reduceToImage(['valor'], ee.Reducer.first()))
    pixelArea = ee.Image.pixelArea().divide(10000).updateMask(masc_recorte)    

    for nyear in range(1985, 2024):
        print(f" ======== processing year {nyear} for mapbiomas Monitor Fire  =====")
        imgFire = (
            ee.Image(param['asset_fire_anual_cov'])
                    .select(f"burned_coverage_{nyear}")
                    .updateMask(masc_recorte)
                    .selfMask()
        )        
        areaTemp = calculateArea (imgFire, pixelArea, recorteGeo)        
        areaTemp = areaTemp.map( lambda feat: feat.set(
                                            'year', nyear, 
                                            'region', 'Semiarido', 
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
calcMatopiba = True

shpEstados = ee.FeatureCollection(param['BR_ESTADOS_2022'])
# lstEstCruz = [21,22,23,24,25,26,27,28,29,31,32]
# lstEstCruz = ['17','21','22','29'];
lstEstCruz = ['17','21','22','23','24','25','26','27','28','29','31','32','52']
areaGeral = ee.FeatureCollection([]) 
# print("---- SHOW ALL BANDS FROM MAPBIOKMAS MAPS -------\n ", imgMapp.bandNames().getInfo())
for estadoCod in lstEstCruz:    
    print(f"processing Estado {dictEst[str(estadoCod)]} with code {estadoCod}")
    shpEstado = shpEstados.filter(ee.Filter.eq('CD_UF', estadoCod))   
    areaXestado = iterandoXanoImCruda_Cover(shpEstado, estadoCod, calcMatopiba)
    print("adding area ")
    try:
        print(areaXestado.size().getInfo())
        areaGeral = areaGeral.merge(areaXestado)
    except:
        print(f"Fail estado {dictEst[str(estadoCod)]}")

print("exportando a área geral ")
if calcMatopiba:
    processoExportar(areaGeral, 'area_anual_fire_state_semiarido_matopiba')
else:
    processoExportar(areaGeral, 'area_anual_fire_state_semiarido')