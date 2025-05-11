#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#  SCRIPT DE CALCULO DE AREA POR AREAS PRIORITARIAS DA CAATINGA
#  Produzido por Geodatin - Dados e Geoinformacao
#  DISTRIBUIDO COM GPLv2

#   Relação de camadas para destaques:
#   limite bioma Caatinga 
#   Novo limite do semiarido 2024
#   Camadas Raster:
#       Fogo
#       Agua
#       Alertas
#       Vegetação secundaria 

'''


import ee 
import sys
import collections
collections.Callable = collections.abc.Callable

try:
    ee.Initialize(project= 'mapbiomas-caatinga-cloud')
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


param = {
    'asset_Cover_Col8': 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1',  
    'asset_transicao': 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_transitions_v1',
    'asset_annual_water': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_water_collection2_annual_water_coverage_v1',
    'asset_desf_vegsec': 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_deforestation_secondary_vegetation_v1',
    'asset_vegsec_age': ' projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_secondary_vegetation_age_v1',
    'asset_irrigate_agro': 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_irrigated_agriculture_v1',
    "asset_semiarido2024": 'projects/mapbiomas-workspace/AUXILIAR/SemiArido_2024',
    "asset_biomas_250" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/Im_bioma_250",
    "asset_biomas_raster" : 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41',
    'asset_fire_annual': 'projects/mapbiomas-public/assets/brazil/fire/collection3/mapbiomas_fire_collection3_annual_burned_coverage_v1',
    'asset_fire_acumulado': 'projects/mapbiomas-public/assets/brazil/fire/collection3/mapbiomas_fire_collection3_accumulated_burned_v1',
    'asset_vigor_pastagem': 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_pasture_quality_v1',
    "br_estados_raster": 'projects/mapbiomas-workspace/AUXILIAR/estados-2016-raster',
    "br_estados_vector": 'projects/mapbiomas-workspace/AUXILIAR/estados-2016',
    'scale': 30,
    # 'driverFolder': 'AREA-EXP-SEMIARIDO-24',
    'driverFolder': 'AREA-EXP-CAATINGA-24',
}

lst_nameAsset = [    
    # 'asset_annual_water',
    # 'asset_desf_vegsec',
    # 'asset_irrigate_agro',
    # 'asset_fire_annual',
    'asset_fire_acumulado'
    # 'asset_vegsec_age',
    # 'asset_vigor_pastagem'
]
dict_CD_Bioma = {
    '1': '',
    '2': '_Caatinga',
    '3': '',
    '4': '',
    '5': '',
    '6': '',
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

# pixelArea, imgMapa, bioma250mil
# pixelArea, imgWater, limitGeometria, pref_bnd, nomegeometria, byYears, nameCSV
def iterandoXanoImCruda(imgAreaRef, mapaDelimitado, limite, preficoBnd, nameregion, porAno, nameExport, SiglaEst, idEstado):
    
    imgAreaRef = imgAreaRef
    areaGeral = ee.FeatureCollection([])      
    print("Loadding image Cobertura Coleção 9 " )
    imgMapp = ee.Image(mapaDelimitado)
    # print("---- SHOW ALL BANDS FROM MAPBIOKMAS MAPS -------\n ", imgMapp.bandNames().getInfo())
    dateInit = 1985
    dateEnd = 2023
    if "_desf_veg_" in nameExport:
        dateInit = 1986
    elif 'water' in nameExport:
        dateEnd = 2022

    for year in range(dateInit, dateEnd + 1):          
        bandAct = preficoBnd + str(year)
        print(f" ========  🫵 processing year {year} for mapbiomas map ===== {bandAct}")
        newimgMap = imgMapp.select(bandAct)
        areaTemp = calculateArea (newimgMap, imgAreaRef, limite)        
        areaTemp = areaTemp.map( lambda feat: feat.set(
                                            'year', year, 
                                            'camada', preficoBnd[:-2],
                                            'region', nameregion, 
                                            'estado', SiglaEst,
                                            'id_estado', idEstado                                               
                                        ))
        if porAno:
            nameCSV = nameExport + "_" + str(year)
            processoExportar(areaTemp, nameCSV)       

        areaGeral = areaGeral.merge(areaTemp)      
       
    nExport = True
    if porAno:
        nExport = False     
    
    return areaGeral, nExport


# pixelArea, imgWater, limitGeometria, pref_bnd, nomegeometria, byYears, nameCSV
def anoImCruda(imgAreaRef, mapaDelimitado, limite, preficoBnd, nameregion, nameExport, SiglaEst, idEstado):
    
    imgAreaRef = imgAreaRef.clip(limite)
    areaGeral = ee.FeatureCollection([])      
    print("Loadding image Cobertura Coleção 8 " )
    bandActive = ''
    intervalo = ''
    imgMapp = ee.Image(mapaDelimitado).clip(limite)
    if 'queimadas_accumalada' in nameExport:
        bandActive = "fire_accumulated_1986_2023"
        intervalo = '1986_2023'

    imgMapp = imgMapp.select(bandActive)  
    # print("---- SHOW ALL BANDS FROM MAPBIOKMAS MAPS -------\n ", imgMapp.bandNames().getInfo())

    areaTemp = calculateArea (imgMapp, imgAreaRef, limite)        
    areaTemp = areaTemp.map( lambda feat: feat.set(
                                        'year', 'intervalo', 
                                        'camada', preficoBnd[:-2],
                                        'region', nameregion                                               
                                    ))

    nameCSV = "stat_" + nameExport
    processoExportar(areaTemp, nameCSV)       



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


raster_base = ee.Image(param["asset_biomas_raster"])
select_Caatinga = True
sobreNomeGeom = "_Semiarido"
nomegeometria = 'semiarido'
CD_Bioma = 2
if select_Caatinga:
    limitGeometria = ee.FeatureCollection(param["asset_biomas_250"])
    if CD_Bioma == None:
        sobreNomeGeom = '_Brasil'
    else:
        print('         limite caatinga carregado ')
        limitGeometria = limitGeometria.filter(ee.Filter.eq("CD_Bioma", int(CD_Bioma)))
        sobreNomeGeom = dict_CD_Bioma[str(CD_Bioma)]
        nomegeometria = 'Caatinga'
        raster_base = raster_base.eq(5);
else:
    limitGeometria = ee.FeatureCollection(param["asset_semiarido2024"])

print(f"=============== limite a Macro Selecionado com {limitGeometria.size().getInfo()} shape========== ")
dictEstSigla = {
    '21': 'MA',
    '22': 'PI',
    '23': 'CE',
    '24': 'RN',
    '25': 'PB',
    '26': 'PE',
    '27': 'AL',
    '28': 'SE',
    '29': 'BA',
    '31': 'MG',
    '32': 'ES'
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
    '32': 'ESPÍRITO SANTO'
}
lstEstCruz = [21,22,23,24,25,26,27,28,29,31,32];
limitGeometria = limitGeometria.geometry()
pixelArea = ee.Image.pixelArea().divide(10000).updateMask(raster_base)
imgWater = ee.Image(param["asset_annual_water"]).updateMask(raster_base)
mapsdesfVegSec = ee.Image(param["asset_desf_vegsec"]).updateMask(raster_base)
mapsIrrigate = ee.Image(param["asset_irrigate_agro"]).updateMask(raster_base)
mapsFire = ee.Image(param["asset_fire_annual"]).updateMask(raster_base)
mapsFireAcc = ee.Image(param["asset_fire_acumulado"]).updateMask(raster_base)
estados_raster = ee.Image(param["br_estados_raster"])
estados_shp = ee.FeatureCollection(param["br_estados_vector"])

exportar = False
byYears = False
# iterandoXanoImCruda(imgAreaRef, mapaDelimitado, limite, preficoBnd, nameregion):
for assetName in lst_nameAsset:
    for id_est in lstEstCruz:
        print("---- PROCESSING MAPS ", assetName, " - ESTADO ", id_est,"  ",dictEst[str(id_est)])
        baseEstado = estados_raster.eq(id_est)
        limitEst = estados_shp.filter(ee.Filter.eq('CD_GEOCUF', str(id_est)))
        # print("quantidade de estados ", limitEst.size().getInfo())
        limitEst = limitEst.geometry().intersection(limitGeometria)
        # print("ver geometria ", limitEst.getInfo())
        pixelAreaEst = pixelArea.updateMask(baseEstado) 
        # sys.exit()
        if assetName == 'asset_annual_water':
            print("---- PROCESSING MAPS WATER ---------------")
            pref_bnd = "annual_water_coverage_"  
            nameCSV = "area_class_water_" + dictEstSigla[str(id_est)] + '_' + sobreNomeGeom            
            imgWaterEst = imgWater.updateMask(baseEstado)
            csv_table, exportar = iterandoXanoImCruda(pixelAreaEst, imgWaterEst, limitEst, pref_bnd, nomegeometria, 
                                                        byYears, nameCSV, dictEstSigla[str(id_est)], id_est)        

        elif assetName == 'asset_desf_vegsec':
            print("---- PROCESSING MAPS VEGETAÇÃO SECUNDARIA  ---------------")
            pref_bnd = "classification_"
            nameCSV = "area_class_desf_veg_secundaria" + dictEstSigla[str(id_est)] + '_' + sobreNomeGeom
            mapsdesfVegSecEst = mapsdesfVegSec.updateMask(baseEstado)
            csv_table, exportar = iterandoXanoImCruda(pixelAreaEst, mapsdesfVegSec, limitEst, pref_bnd, nomegeometria, 
                                                        byYears, nameCSV, dictEstSigla[str(id_est)], id_est)

        elif assetName == 'asset_irrigate_agro':
            print("---- PROCESSING MAPS AREAS IRRIGADAS ---------------")
            pref_bnd = "irrigated_agriculture_"
            nameCSV = "area_class_irrigated_" + dictEstSigla[str(id_est)] + '_' + sobreNomeGeom
            mapsIrrigateEst = mapsIrrigate.updateMask(baseEstado)
            csv_table, exportar = iterandoXanoImCruda(pixelAreaEst, mapsIrrigateEst, limitGeometria, pref_bnd, nomegeometria, 
                                                        byYears, nameCSV, dictEstSigla[str(id_est)], id_est)

        elif assetName == 'asset_fire_annual':
            print("---- PROCESSING MAPS AREAS QUEIMADAS ---------------")
            pref_bnd = "burned_area_"
            nameCSV = "area_class_queimadas" + dictEstSigla[str(id_est)] + '_' + sobreNomeGeom
            mapsFireEst = mapsFire.updateMask(baseEstado)
            csv_table, exportar = iterandoXanoImCruda(pixelAreaEst, mapsFireEst, limitGeometria, pref_bnd, nomegeometria, 
                                                        byYears, nameCSV, dictEstSigla[str(id_est)], id_est)

        elif assetName == 'asset_fire_acumulado':
            print("---- PROCESSING MAPS AREAS QUEIMADAS ---------------")
            pref_bnd = "burned_area_acc"
            nameCSV = "area_class_queimadas_accumalada" + dictEstSigla[str(id_est)] + '_' + sobreNomeGeom
            mapsFireAccEst = mapsFireAcc.updateMask(baseEstado)
            anoImCruda(pixelAreaEst, mapsFireAccEst, limitGeometria, pref_bnd, nomegeometria, 
                                                        nameCSV, dictEstSigla[str(id_est)], id_est)

        elif assetName == 'asset_vegsec_age':
            print("---- PROCESSING MAPS AREAS QUEIMADAS ---------------")
            pref_bnd = "vegsec_age"
            nameCSV = "area_class_vegsec_age" + dictEstSigla[str(id_est)] + '_' + sobreNomeGeom
            mapsFireAccEst = mapsFireAcc.updateMask(baseEstado)
            anoImCruda(pixelAreaEst, mapsFireAccEst, limitGeometria, pref_bnd, nomegeometria, nameCSV)

        if exportar:
            processoExportar(csv_table, nameCSV)