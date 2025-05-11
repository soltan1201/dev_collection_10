#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
# https://code.earthengine.google.com/0c432999045898bb6e40c1fb7238d32f
'''

import ee
import os 
import gee
import json
import csv
import copy
import sys
import math
import arqParametros as arqParams 
import collections
collections.Callable = collections.abc.Callable
try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

param = {      
    'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV3/',
    'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV2',
    # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/TemporalV2',
    # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fillV2/',
    # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/Spatial/',
    'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',            
    'last_year' : 2023,
    'first_year': 1985,
    'janela': 3,
    'step': 1,
    'versionOut' : 18,
    # 'versionSP' : '7',
    'versionSP' : 13,
    'numeroTask': 6,
    'numeroLimit': 42,
    'conta' : {
        '0': 'caatinga01',
        '5': 'caatinga02',
        '10': 'caatinga03',
        '16': 'caatinga04',
        '22': 'caatinga05',        
        '27': 'solkan1201',    
        '32': 'solkanGeodatin',
        '37': 'diegoUEFS'   
    }
}
def processoExportar(mapaRF,  nomeDesc, geom_bacia):
    
    idasset =  param['output_asset'] + nomeDesc
    optExp = {
        'image': mapaRF, 
        'description': nomeDesc, 
        'assetId':idasset, 
        'region': geom_bacia.getInfo()['coordinates'],
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



def apply_spatialCopy(name_bacia, nmodel):
    geomBacia = ee.FeatureCollection(param['asset_bacias_buffer']).filter(
                ee.Filter.eq('nunivotto3', name_bacia)).first().geometry()
    imgClass = ee.ImageCollection(param['input_asset']).filter(
                            ee.Filter.eq('version', param['versionSP'])).filter(
                                    ee.Filter.eq('id_bacia', name_bacia )).first()

    print('  show metedata imgClass', imgClass.get('system:index').getInfo())

    nameExp = 'filterSP_BACIA_'+ str(name_bacia) + "_" + nmodel + "_V" + str(param['versionOut']) + '_step' + str(param['step'])
    imgClass = imgClass.set(
                        'version', param['versionOut'], 'biome', 'CAATINGA',
                        'collection', '9.0', 'id_bacia', name_bacia,
                        'sensor', 'Landsat', 'source','geodatin', 
                        'model', nmodel, 'step', param['step'], 
                        'system:footprint', geomBacia# imgClass.get('system:footprint')
                    )
    # print(nameExp)
    processoExportar(imgClass,  nameExp, geomBacia)

def gerenciador(cont):
    #0, 18, 36, 54]
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
    numberofChange = [kk for kk in param['conta'].keys()]    
    if str(cont) in numberofChange:
        print("conta ativa >> {} <<".format(param['conta'][str(cont)]))        
        gee.switch_user(param['conta'][str(cont)])
        gee.init()        
        gee.tasks(n= param['numeroTask'], return_list= True)        
    
    elif cont > param['numeroLimit']:
        cont = 0
    
    cont += 1    
    return cont


listaNameBacias = [
    '744','741','7422','745','746','7492','751','752','753',
    '755','759','7621','7622', '763','764','765','766',
    '767', '771', '772','773','7741','776','7742','775', 
    '777', '778','76111','76116','7612','7613','7615','7616',
    '7617','7618','7619','756','757','758','754', '7614', '7421'
]

listBacias = [
    '752', '766', '753', '776', '764', '765', '7621', '744', 
    '756','757','758','754','7614', '7421'
]
cont = 12
version = 15
modelo = 'GTB'

for cc, idbacia in enumerate(listaNameBacias[:]):      
    if idbacia not in listBacias:            
        print("----- PROCESSING BACIA {} -------".format(idbacia))        
        apply_spatialCopy(idbacia, modelo)
        # cont = gerenciador(cont)












