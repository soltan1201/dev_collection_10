#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
# SCRIPT DE CLASSIFICACAO POR BACIA
# Produzido por Geodatin - Dados e Geoinformacao
# DISTRIBUIDO COM GPLv2
'''

import ee 
import sys
import glob
import copy
import collections
collections.Callable = collections.abc.Callable

try:
    ee.Initialize(project= 'geo-data-s')    
    # ee.Initialize(project= 'mapbiomas-caatinga-cloud05')
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


params = {

    'asset_col9' : "projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1",
    'asset_classifier': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVY',
    'asset_gapfill': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fillV2',
    'asset_frequency': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/FrequencyV3',
    'asset_spatial': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV3',
    'asset_temporal': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/TemporalV3',
    'asset_biomas_raster': 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019-raster',
    'asset_sphBiomas': "projects/mapbiomas-workspace/AUXILIAR/biomas-2019",
    'assetOutput': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/aggrements',
    "br_estados_raster": 'projects/mapbiomas-workspace/AUXILIAR/estados-2016-raster',
    "BR_ESTADOS_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_ESTADOS_2022",
    'vetor_biomas_250': 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
    'classMapB': [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,39,40,41,46,47,48,49,50,62],
    'classNew':  [3, 4, 3, 3,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33,21,21,21,21,21,21,21, 3,12,21],
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
        'classe', item.get('classe'),"area", item.get('sum'))
        
    return feature

#########################################################################
####     Calculate area crossing a cover map (deforestation, mapbiomas)
####     and a region map (states, biomes, municipalites)
####      @param image 
####      @param geometry
#########################################################################
# https://code.earthengine.google.com/5a7c4eaa2e44f77e79f286e030e94695
def calculateArea (image, pixelArea, reg_geom):

    pixelArea = pixelArea.addBands(image.rename('classe'))
    reducer = ee.Reducer.sum().group(1, 'classe')
    optRed = {
        'reducer': reducer,
        'geometry': reg_geom,
        'scale': 30,
        'bestEffort': True, 
        'maxPixels': 1e13
    }    
    areas = pixelArea.reduceRegion(**optRed)

    areas = ee.List(areas.get('groups')).map(lambda item: convert2featCollection(item))
    areas = ee.FeatureCollection(areas)    
    return areas

def iterandoXanoImCruda(imgAreaRef, imgMapp, nyear, nameLayer):
    CD_Bioma = 2
    estados_raster = ee.Image(params["br_estados_raster"])
    lstEstCruz = [22,23,24,25,26,27,28,29,31]
    
    limitGeometria = ee.FeatureCollection(params["vetor_biomas_250"])
    limitGeometria = limitGeometria.filter(ee.Filter.eq("CD_Bioma", CD_Bioma))
    rasterCaat = ee.Image(params['asset_biomas_raster']).eq(5);


    areaGeral = ee.FeatureCollection([]) 
    for estadoCod in lstEstCruz:        
        # print(f"processing Estado {dictEst[str(estadoCod)]} with code {estadoCod}")
        maskRasterEstBioma = estados_raster.eq(estadoCod).multiply(rasterCaat)
        rasterMapEstado = imgMapp.updateMask(maskRasterEstBioma)
        imgAreaEst = imgAreaRef.updateMask(maskRasterEstBioma)
        regEst = (
            ee.FeatureCollection(params['BR_ESTADOS_2022'])
            .filter(ee.Filter.eq("CD_UF", str(estadoCod)))
            .geometry().intersection(limitGeometria.geometry())            
        )

        areaTemp = calculateArea (rasterMapEstado, imgAreaEst, regEst)        
        areaTemp = areaTemp.map( lambda feat: feat.set(
                                            'year', nyear, 
                                            'layer', nameLayer,                                            
                                            'estado_codigo', estadoCod,
                                            'area_est', regEst.area().divide(10000)
                                        ))
        areaGeral = areaGeral.merge(areaTemp)

    return areaGeral


def processoExportar(areaFeat, nameT):      
    optExp = {
          'collection': areaFeat, 
          'description': nameT, 
          'folder': 'mudanzas_filtersXClass'        
        }    
    task = ee.batch.Export.table.toDrive(**optExp)
    task.start() 
    print("salvando ... " + nameT + "..!")    

# bioma =  'Caatinga'; 
pixelArea = ee.Image.pixelArea().divide(10000)
class_col90 = ee.Image(params['asset_col9'])

#Map.addLayer(ee.Image.constant(1), {min: 0, max: 1}, 'base');
classification = (
    ee.ImageCollection(params['asset_classifier'])
        .filter(ee.Filter.eq('version', 31))
            .max()              
)
# print(classification.bandNames().getInfo())
gap = (
    ee.ImageCollection(params['asset_gapfill'])
        .filter(ee.Filter.eq('model', 'GTB'))
            .filter(ee.Filter.eq('version', 30))
                .max()
)

spatial = (
    ee.ImageCollection(params['asset_spatial'])
        .filter(ee.Filter.eq('version', 41))
            .max()
)

frequency = (
    ee.ImageCollection(params['asset_frequency'])
        .filter(ee.Filter.eq('version', 31))
            .max()
)

temporal = (
    ee.ImageCollection(params['asset_temporal'])
        .filter(ee.Filter.eq('version', 39))
            .max()
)
por_estado = False
dictMaps = {
    'classification': classification,
    'gap_filter': gap,
    'spatial_filter': spatial,
    'frequency_filter': frequency,
    'temporal_filter': temporal,
    'class_col90': class_col90    
}
lst_raster = [
    'classification', 'gap_filter', 'spatial_filter', 
    'frequency_filter', 'temporal_filter', 'class_col90'
]
mapa_prev = None
if por_estado:
    for cc, key_raster in enumerate(lst_raster[:]):
        print(f'Calculando área de para layer >> {key_raster}')
        raster_tmp = ee.Image(dictMaps[key_raster])
        print(f" {key_raster} >> ", raster_tmp.bandNames().getInfo())
        # sys.exit()
        featColMap = ee.FeatureCollection([])
        for year_j in range(1985, 2024):
            # para cada ano  
            print("processing year >> ", year_j)
            year_j = str(year_j)
            band_select = 'classification_'+ year_j
            # processamento a fazer 
            raster_tmpYY = raster_tmp.select(band_select)
            if cc > 0:
                mapa_prevYY = mapa_prev.select(band_select)
                # desde a camada Gap Fill já o mapa está reclassificado
                if cc == 1:
                    mapa_prevYY = mapa_prevYY.remap(params['classMapB'], params['classNew'])

                raster_tmpYY = (
                    ee.Image.constant(0)
                        .where(raster_tmpYY.neq(mapa_prevYY), ee.Image.constant(1))
                )
            else:
                print(" ---- primeira camada de calculo de área ----")
                mapa_prevYY = ee.Image.constant(1)
                raster_tmpYY = raster_tmpYY.unmask(0).eq(0)
                # sys.exit()
            
            areaCC = iterandoXanoImCruda(pixelArea, raster_tmpYY, year_j, key_raster);
            featColMap = featColMap.merge(areaCC)
        print(f" copiando o mapa {key_raster}")
        mapa_prev = copy.deepcopy(raster_tmp)
        print("============================================================")
        nameSHP = f'mudanza_pixels_{key_raster}'
        processoExportar(featColMap, nameSHP)
        # sys.exit()

else:
    for cc, key_raster in enumerate(lst_raster[:]):
        print(f'Calculando área de para layer >> {key_raster}')
        raster_tmp = ee.Image(dictMaps[key_raster])
        print(raster_tmp.bandNames().getInfo())
        # sys.exit()
        featColMap = ee.FeatureCollection([])
        for cclass in [3, 4, 12, 21]:
            print(f" ============ classe {cclass} =============")
            for year_j in range(1985, 2024):
                # para cada ano  
                print("processing year >> ", year_j)
                year_j = str(year_j)
                band_select = 'classification_'+ year_j
                # processamento a fazer 
                raster_tmpYY = raster_tmp.select(band_select)
                maskCC = raster_tmpYY.eq(cclass)
                # mascarando pela classe
                # raster_tmpYYM = raster_tmpYY.updateMask(maskCC)

                if cc > 0:
                    mapa_prevYY = mapa_prev.select(band_select)
                    if cc == 1:
                        mapa_prevYY = mapa_prevYY.remap(params['classMapB'], params['classNew'])

                    # todas as mudanças 1 para 0 serão registradas como 1
                    raster_tmpYY = (
                        ee.Image.constant(0)
                            .where(maskCC.neq(mapa_prevYY.eq(cclass)), ee.Image.constant(1))
                    )
                else:
                    print(" ---- primeira camada de calculo de área ----")
                    mapa_prevYY = ee.Image.constant(1)
                    raster_tmpYY = raster_tmpYY.unmask(0).eq(0)
                    # sys.exit()
                
                areaCC = iterandoXanoImCruda(pixelArea, raster_tmpYY, year_j, key_raster);
                areaCC = areaCC.map(lambda x: x.set('cobertura', cclass))
                featColMap = featColMap.merge(areaCC)
        
        print(f" copiando o mapa {key_raster}")
        mapa_prev = copy.deepcopy(raster_tmp)
        print("============================================================")
        nameSHP = f'mudanza_pixels_{key_raster}_byClassCover'
        processoExportar(featColMap, nameSHP)
  