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
except ee.EEException as projects/mapbiomas-brazil/assets/LAND-COVER/COLLECTION-10/GENERAL/classification-caae:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


spectralBands = ['blue', 'red', 'green', 'nir', 'swir1', 'swir2'];
param = {
    'input_asset':'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/transitionTest',
    'asset_polygon': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/poligons_corretores',
    'asset_painel_sol': 'projects/mapbiomas-arida/energias/solar-panel-br-30m',
    "asset_bacias_buffer":  'projects/ee-solkancengine17/assets/shape/bacias_buffer_caatinga_49_regions',
    "asset_afloramento": 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/rockyoutcropcol10',
    'asset_restinga': 'projects/mapbiomas-arida/restinga_ibge_2014',
    "asset_collectionId": 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    "output_asset": 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/MergerV6',
    'versionOut' : 8,
    'versionInp' : 8,
    'last_year' : 2024,
    'first_year': 1985,
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
    listCoor = [
        [-56.44604894060301,-31.07051878963668],
        [-32.18823644060301,-31.07051878963668],
        [-32.18823644060301,-0.10841888037947958],
        [-56.44604894060301,-0.10841888037947958],
        [-56.44604894060301,-31.07051878963668]
    ]
    limiteBox = ee.Geometry.Polygon(listCoor)
    imgClass = (ee.ImageCollection(param['input_asset'])
                        .filter(ee.Filter.eq('version', param['versionInp']))
                        .filter(ee.Filter.eq('id_bacias', name_bacia ))
                )
    print(" we load ", imgClass.size().getInfo())
    imgClass = imgClass.first().updateMask(bacia_raster)
    print('  show metedata imgClass', imgClass.get('system:index').getInfo())

    shp_restinga = (ee.FeatureCollection(param['asset_restinga'])
                        .map(lambda feat : feat.set('id_codigo', 1)))
    raster_restinga = shp_restinga.reduceToImage(['id_codigo'], ee.Reducer.first()).gt(0)
    raster_afloramento = ee.Image(param["asset_afloramento"]).selfMask().multiply(29)
    raster_FV = ee.Image(param['asset_painel_sol']).set('system:footprint', limiteBox)
    # raster_FV = raster_FV
    print("know the bands FotoVoltaicas ", raster_FV.bandNames().getInfo())

    shp_pol_correct = ee.FeatureCollection(param['asset_polygon'])
    lstLabel = shp_pol_correct.reduceColumns(ee.Reducer.toList(), ['label']).get('list')
    lstLabel = ee.List(lstLabel).distinct().getInfo()


    class_output = ee.Image().byte()    
    lstyear = [yy for yy in range(param['first_year'], param['last_year'] + 1)]
    lst_yy_class = [f'classification_{yy}' for yy in lstyear]
    for nyear in lstyear:
        banda_activa = f'classification_{nyear}'
        rasterSpatialYear = imgClass.select(banda_activa)        
        rasterSpatialYear = rasterSpatialYear.where(raster_afloramento)
        maskRest = rasterSpatialYear.updateMask(raster_restinga).lt(22).multiply(50)
        rasterSpatialYear = rasterSpatialYear.where(maskRest)
        if nyear > 2014:
            rasterFV_YY = raster_FV.select(f"Panel_{nyear}") #.multiply(22).selfMask()
            # rasterSpatialYear = rasterSpatialYear.blend(rasterFV_YY)
            rasterSpatialYear = rasterSpatialYear.where(rasterFV_YY.eq(1), 22)

        for label in lstLabel:
            tmpSHP = shp_pol_correct.filter(ee.Filter.eq('label', label))
            maskPolyTo = tmpSHP.reduceToImage(['para'], ee.Reducer.first())
            maskPolyCC = tmpSHP.reduceToImage(['class'], ee.Reducer.first())
            if label == 'x21vira29':
                print('processing ' + label)
                mask21v29 = rasterSpatialYear.eq(21).multiply(maskPolyCC.eq(21)).multiply(maskPolyTo)
                rasterSpatialYear = rasterSpatialYear.where(mask21v29.selfMask())

            if label == 'x22vira29':
                mask22v29 = rasterSpatialYear.eq(22).multiply(maskPolyCC.eq(22)).multiply(maskPolyTo)
                rasterSpatialYear = rasterSpatialYear.blend(mask22v29.selfMask())

            if label == 'x22vira21':
                mask22v21 = rasterSpatialYear.eq(22).multiply(maskPolyCC.eq(22)).multiply(maskPolyTo)
                rasterSpatialYear = rasterSpatialYear.blend(mask22v21.selfMask())

            if label == 'x29vira22':
                mask29v22 = rasterSpatialYear.eq(29).multiply(maskPolyCC.eq(29)).multiply(maskPolyTo)
                rasterSpatialYear = rasterSpatialYear.blend(mask29v22.selfMask())

            if label == 'x33vira29':
                mask33v29 = rasterSpatialYear.eq(33).multiply(maskPolyCC.eq(33)).multiply(maskPolyTo)
                rasterSpatialYear = rasterSpatialYear.blend(mask33v29.selfMask())

            if label == 'x33vira3':
                mask33v3 = rasterSpatialYear.eq(33).multiply(maskPolyCC.eq(33)).multiply(maskPolyTo)
                rasterSpatialYear = rasterSpatialYear.blend(mask33v3.selfMask())

            if label == 'x33vira21':
                mask33v21 = rasterSpatialYear.eq(33).multiply(maskPolyCC.eq(33)).multiply(maskPolyTo)
                rasterSpatialYear = rasterSpatialYear.blend(mask33v21.selfMask())

        class_output = class_output.addBands(rasterSpatialYear.rename(banda_activa))  


    name_exp = f"filterMG_BACIA_{name_bacia}_GTB_V{param['versionOut']}"
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
    # sys.exit()

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