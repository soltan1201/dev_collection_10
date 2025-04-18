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
// =============== UPDATE =============================
//https://code.earthengine.google.com/7e3bbba61c6ae52e3f6a3856b1fb2886
//https://code.earthengine.google.com/3f81ea74b43ec339d489023abd7df908
var palettes = require('users/mapbiomas/modules:Palettes.js');
var vis = { 
    'mapbiomas': {
        'min': 0, 
        'max': 69,  
        'palette': palettes.get('classification9')
    },
    'points': {
        color: '#FF7803',
    },
    'maskAfloramento': {
        min: 0,
        max: 2,
        palette: ['000FFF','FE9929', 'FF0000']
    },
    'visMosaic': {
        min: 0.0,
        max: 0.4,
        bands: ['red', 'green', 'blue']
    },
    mosaicNorm: {
        bands: ['red', 'green', 'blue'],
        min: 0.02, 
        max: 0.8
    },
    indexRock: {
        min: 0,
        max: 1,
        palette: [
            "41ab5d","78c679","addd8e","d9f0a3","f7fcb9","ffffe5","ffffe5",
            "fff7bc","fee391","fec44f","fe9929","ec7014","cc4c02","8c2d04"
        ]
    },
    indexVeg: {
        min: 0,
        max: 1,
        palette: [
            "ffffe5","f7fcb9","d9f0a3","addd8e","78c679","41ab5d","238443","005a32"
        ]
    },
    indexSlope: {
        min: 0,
        max: 1,
        palette: [
            "252525","525252","737373","969696","bdbdbd","d9d9d9","f0f0f0","ffffff"
        ]
    }
};

// Bare Soil Index 
var agregateBandsIndexBSI = function(img){  
    var bsiImgY = img.expression(
        "float(((b('swir1') - b('red')) - (b('nir') + b('blue'))) / ((b('swir1') + b('red')) + (b('nir') + b('blue'))))")
            .rename(['bsi']).toFloat(); 
    bsiImgY = bsiImgY.add(1).multiply(10000).toUint16();
    return img.addBands(bsiImgY);
}


function agregateBandsIndexEVI(img){
    var eviImgY = img.expression(
        "float(2.4 * (b('nir') - b('red')) / (1 + b('nir') + b('red')))")
            .rename(['evi']).toFloat(); 
    eviImgY = eviImgY.add(1).multiply(10000).toUint16();
    return img.addBands(eviImgY);
}

function agregateBandsIndexNDVI(img){
    var ndviImgY = img.normalizedDifference(['nir', 'red']).rename('ndvi').toFloat();    
    ndviImgY = ndviImgY.add(1).multiply(10000).toUint16();
    return img.addBands(ndviImgY);
}

function agregateBandsIndexGCVI(img){    
    var gcviImgAY = img.expression(
        "float(b('nir')) / (b('green')) - 1")
            .rename(['gcvi']).toFloat();         
    gcviImgAY = gcviImgAY.add(1).multiply(10000).toUint16();
    return img.addBands(gcviImgAY);
}


function agregateBandsIndexMBI(img){    
    var mbiImgAY = img.expression(
        "float(((b('swir1') - b('swir2') - b('nir')) /" + 
                " (b('swir1') + b('swir2') + b('nir'))) + 0.5)")
            .rename(['mbi']).toFloat();         
    mbiImgAY = mbiImgAY.add(1).multiply(10000).toUint16();
    return img.addBands(mbiImgAY);
}


// SAVI OSAVI	Optimized Soil-Adjusted Vegetation Index	vegetation	(N - R) / (N + R + 0.16)
var agregateBandsIndexMSAVI =  function(img){
    var msaviImgY = img.expression(
        "float((2 * b('nir') + 1 - sqrt((2 * b('nir') + 1) * (2 * b('nir') + 1) - 8 * (b('nir') - b('red'))))/2)")
           .toFloat().rename(['msavi']);
    msaviImgY = msaviImgY.add(10).multiply(1000).toUint16();
    return img.addBands(msaviImgY);
}

// Host Rocks - SWIR1/SWIR2
var agregateBandsIndexhostyocks = function(img){    
    var hostRockImgY = img.expression(
        "float(b('swir1')  / b('swir2'))")
           .rename(['HR']).toFloat();
    hostRockImgY = hostRockImgY.add(1).multiply(10000).toUint16();
    return img.addBands(hostRockImgY);
}

// UI	Urban Index	urban
var agregateBandsIndexUI = function(img){
    var uiImgY = img.expression(
        "float((b('swir2') - b('nir')) / (b('swir2') + b('nir')))")
           .rename(['ui']).add(1).multiply(10000).toUint16();
   uiImgY = uiImgY.add(1).multiply(10000).toUint16();
    return img.addBands(uiImgY);
};

// Ferrous Rocks - SWIR1/NIR
var agregateBandsIndexFerrRocks = function(img){
    var ferrRockImgY = img.expression(
        "float(b('swir1')  / b('nir'))")
           .rename(['FR']).add(1).divide(2).toFloat();
    ferrRockImgY = ferrRockImgY.add(1).multiply(10000).toUint16();
    return img.addBands(ferrRockImgY);
};

// Eisenhydroxid-Index - SWIR2/RED
var agregateBandsIndexEisenIndex = function(img){
    var eisenIndexImgY = img.expression(
        "float(b('swir2')  / b('red'))")
           .rename(['EI']).add(1).divide(2).toFloat();       
    eisenIndexImgY = eisenIndexImgY.add(1).multiply(10000).toUint16();           
    return img.addBands(eisenIndexImgY);
};

/// ===== FUNÇÕES =====
var ExportarImgMapstoDriver = function(image_map, name_img, regiao){
   
    var paramExpD = {
        image: image_map, 
        description: name_img + "_img", 
        folder: 'Mapas_Dados', 
        scale: 30, 
        maxPixels: 1e13, 
        fileFormat:  'GeoTIFF',
        priority: 5000,
        region: regiao
    };
    Export.image.toDrive(paramExpD);     
    print("Export all Image to Driver" + name_img + " ....");

};

function processoExportar(ROIsFeat, nameB, assetIdss){
    var optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'folder': "rois_curso_DL"         
        };
    Export.table.toDrive(optExp) ;
    print("salvando ... " + nameB + "..!") ;   
}


function GET_NDFIA(IMAGE){
        
    var lstBands = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'];
    var lstFractions = ['gv', 'shade', 'npv', 'soil', 'cloud'];
    var endmembers = [            
        [0.05, 0.09, 0.04, 0.61, 0.30, 0.10], //*gv*/
        [0.14, 0.17, 0.22, 0.30, 0.55, 0.30], //*npv*/
        [0.20, 0.30, 0.34, 0.58, 0.60, 0.58], //*soil*/
        [0.0 , 0.0,  0.0 , 0.0 , 0.0 , 0.0 ], //*Shade*/
        [0.90, 0.96, 0.80, 0.78, 0.72, 0.65]  //*cloud*/
    ];

    var fractions = ee.Image(IMAGE).select(lstBands).unmix({
                      endmembers: endmembers, 
                      sumToOne: true, 
                      nonNegative: true
                      }).float()
    fractions = fractions.rename(lstFractions)
    // # // print(UNMIXED_IMAGE);
    // # GVshade = GV /(1 - SHADE)
    // # NDFIa = (GVshade - SOIL) / (GVshade + )
    var NDFI_ADJUSTED = fractions.expression(
                            "float(((b('gv') / (1 - b('shade'))) - b('soil')) / ((b('gv') / (1 - b('shade'))) + b('npv') + b('soil')))"
                            ).rename('ndfia')

    var NDFI_ADJUSTED = NDFI_ADJUSTED.add(1).multiply(10000).toUint16()
    var RESULT_IMAGE = (ee.Image(CalculateIndiceAllinOne(IMAGE)) // adicionando indices extras
                                .addBands(fractions.multiply(10000).toUint16())
                                .addBands(NDFI_ADJUSTED))

    return ee.Image(RESULT_IMAGE).toUint16()
};



var CalculateIndiceAllinOne = function(imageW){
    
    imageW = agregateBandsIndexMSAVI(imageW)
    imageW = agregateBandsIndexEVI(imageW)
    imageW = agregateBandsIndexGCVI(imageW)
    imageW = agregateBandsIndexBSI(imageW)
    imageW = agregateBandsIndexNDVI(imageW)
    imageW = agregateBandsIndexMBI(imageW)
    imageW = agregateBandsIndexhostyocks(imageW)
    // imageW = agregateBandsIndexFerrRocks(imageW)
    // imageW = agregateBandsIndexEisenIndex(imageW)
    imageW = agregateBandsIndexUI(imageW)
    
    return imageW
};


var params = {
    asset_collectionId:  'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    asset_areas_afloramento: 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/S2/rois_afloramento_sentinel_2',
    asset_mapbiomas_col90: 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1',
    lstBiomes: ['CERRADO','CAATINGA','MATAATLANTICA'],
    bnd_L: ['blue','green','red','nir','swir1','swir2'],
}

var listCoord = [
        [-45.97399568036865,-12.089862729746187],
        [-44.26699494794678,-12.089862729746187],
        [-44.26699494794678,-11.024284240594122], 
        [-45.97399568036865,-11.024284240594122], 
        [-45.97399568036865,-12.089862729746187]
]
var regionSel = ee.Geometry.Polygon(listCoord)
var mmonth = 1;
var year_mosaic = 2023;
var data_inicial = ee.Date.fromYMD(year_mosaic, mmonth, 1)
var mosaicMonth = ee.ImageCollection(params.asset_collectionId)
                        .filterBounds(regionSel)
                        .filterDate(data_inicial, data_inicial.advance(1, 'year'))
                        .max()
                        .select(params.bnd_L)
                        .clip(regionSel)                       
                    
print("ver os metadados da coleção ", mosaicMonth);

var label_mapbiomas = ee.Image(params.asset_mapbiomas_col90)
                        .select('classification_' + String(year_mosaic))
                        .clip(regionSel);
                        

// var imgScale = img.select(bandMos).divide(10000).toFloat();
//// === calculando indices espectrais e frações Spectral mixed analisys //
//// ===========   CalculateIndiceAllinOne ==============================//
var imgScale = GET_NDFIA(mosaicMonth);
imgScale = imgScale.addBands(label_mapbiomas.rename('class'));
                        
var ptos_coleta =   ee.FeatureCollection.randomPoints({
                                    region:regionSel, 
                                    points: 25000
                                });                  
                        
                                
var ptos_sampled = imgScale.sample({
    region: ptos_coleta.geometry(),
    scale: 30,
    seed: 0, 
    dropNulls: true,
    geometries: true
})
print("revisar informação de pontos coletados ", ptos_sampled);

Map.addLayer(mosaicMonth, vis.visMosaic, 'mosaico');
Map.addLayer(label_mapbiomas, vis.mapbiomas, "mapbiomas");
Map.addLayer(ptos_coleta, {}, "ptos");

var name_ROIsexp = 'dados_classificacao';
processoExportar(ptos_sampled, name_ROIsexp);
    print("Unexpected error:", sys.exc_info()[0])
    raise

##############################################
###     Helper function
###    @param item 
##############################################
def convert2featCollection (item):
    item = ee.Dictionary(item)
    morfol = item.get('class_morfo')
    classesAndAreas = ee.List(item.get('groups'))
    def set_class_layers(classAndArea):
        classAndArea = ee.Dictionary(classAndArea)
        classId = classAndArea.get('classe')
        area = classAndArea.get('sum')
        tableColumns = (ee.Feature(None)
                            .set('class_morfo', morfol)
                            .set('classe', classId)
                            .set('area', area))

        return tableColumns
    # print(classesAndAreas.getInfo())
    tableRows = classesAndAreas.map(lambda feats: set_class_layers(feats))
    # print(tableRows.getInfo())
    return ee.FeatureCollection(tableRows)

#########################################################################
####     Calculate area crossing a cover map (deforestation, mapbiomas)
####     and a region map (states, biomes, municipalites)
####      @param image 
####      @param geometry
#########################################################################
# https://code.earthengine.google.com/5a7c4eaa2e44f77e79f286e030e94695
# https://code.earthengine.google.com/?accept_repo=users%2Fmapbiomas%2Fuser-toolkit&scriptPath=users%2Fmapbiomas%2Fuser-toolkit%3Amapbiomas-user-toolkit-calculate-area.js
def calculateArea (image, morfol, pixelArea, geometry):
    pixelArea = (pixelArea.addBands(image.rename('classe'))
                            .addBands(morfol.rename('class_morfo'))
                            ) # .clip(geometry)
    
    # print(pixelArea.bandNames().getInfo())
    # sys.exit()
    reducer = ee.Reducer.sum().group(1, 'classe').group(1, 'class_morfo')
    optRed = {
        'reducer': reducer,
        'geometry': geometry,
        'scale': param['scale'],
        'bestEffort': True, 
        'maxPixels': 1e13
    }    
    areas = pixelArea.reduceRegion(**optRed)
    # print(areas.getInfo())
    areas = ee.List(areas.get('groups')).map(lambda item: convert2featCollection(item))
    # areas = convert2featCollection(ee.List(areas.get('groups')).get(0))
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
    'asset_semiarido': 'projects/mapbiomas-workspace/AUXILIAR/SemiArido_2024',
    'asset_geomorf': 'projects/mapbiomas-workspace/AUXILIAR/ANALISES/cat33_geomorf_IBGE_3_WGS84_com_IDclass',
    'lstYears': [nyear for nyear in range(1985, 2024)],
    'driverFolder': 'AREA-EXP-SEMIARIDO',
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
dict_colorM ={        
    '0': '#a8a800', 
    '1': '#a8a800', 
    '2': '#e2b9f8', 
    '3': '#e2b9f8', 
    '4': '#fa9d66', 
    '5': '#fa9d66',
    '6': '#ffd37f', 
    '7': '#bee8ff', 
    '8': '#a83800', 
    '9': '#ff73df'
}
def iterandoXanoImCruda(limiteEst, estadoCod):

    areaEstado = ee.FeatureCollection([])
    shpSemiarido = ee.FeatureCollection(param['asset_semiarido']).geometry()
    recorteGeo = shpSemiarido.intersection(limiteEst.geometry())

    masc_recorte = (ee.FeatureCollection([ee.Feature(recorteGeo, {'valor': 1})])
                        .reduceToImage(['valor'], ee.Reducer.first()))
    pixelArea = ee.Image.pixelArea().divide(10000).updateMask(masc_recorte)
    # biomas_raster = ee.Image(param['biomas_250_rasters']).eq(2);

    feat_geom = ee.FeatureCollection(param['asset_geomorf'])#//.updateMask(biomasCaat);
    # print("show geomorfologia ", feat_geom.size().getInfo());
    geomorfologia = feat_geom.reduceToImage(['cd_comp_id'], ee.Reducer.first())
    geomorfologia = geomorfologia.rename('class_morfo').updateMask(masc_recorte)

    for nyear in param['lstYears'][:]:
        print(f" ======== processing year {nyear} for mapbiomas Uso e Cobertura  =====")
        namebanda = 'classification_' + str(nyear) 
        mapa_arr = (
            ee.Image(param['asset_cobertura_col90'])
                    .select(namebanda)
                    .updateMask(masc_recorte)
        )        

        areaTemp = calculateArea (mapa_arr, geomorfologia, pixelArea, recorteGeo)  
        # print(areaTemp.getInfo())
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

shpEstados = ee.FeatureCollection(param['BR_ESTADOS_2022'])
# lstEstCruz = [21,22,23,24,25,26,27,28,29,31,32]
lstEstCruz = ['17','21','22','23','24','25','26','27','28','29','31','32','52']

areaGeral = ee.FeatureCollection([]) 
# print("---- SHOW ALL BANDS FROM MAPBIOKMAS MAPS -------\n ", imgMapp.bandNames().getInfo())
for estadoCod in lstEstCruz[1:]:    
    print(f"processing Estado {dictEst[str(estadoCod)]} with code {estadoCod}")
    shpEstado = shpEstados.filter(ee.Filter.eq('CD_UF', estadoCod))
    areaXestado = iterandoXanoImCruda(shpEstado, estadoCod)
    print("adding area ")
    areaGeral = areaGeral.merge(areaXestado)

print("exportando a área geral ")
processoExportar(areaGeral, 'area_cob_geomorfologico_Semiarido_state')