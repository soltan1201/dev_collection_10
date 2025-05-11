#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
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


class processo_filterReshapeFlorest(object):

    options = {
            'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/Reshape/',
            # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/Spatial/',
            'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/Temporal/',
            # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/Frequency/',
            'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',            
            'last_year' : 2022,
            'first_year': 1985,

        }

    def __init__(self, nameBacia):
        self.id_bacias = nameBacia
        self.versionTP = '9'
        self.versionRS = '2'
        self.geom_bacia = ee.FeatureCollection(self.options['asset_bacias_buffer']).filter(
                                                    ee.Filter.eq('nunivotto4', nameBacia)).first().geometry()   

        self.name_imgClass = 'filterTP_BACIA_' + nameBacia + "_V" + self.versionTP

        self.imgClass = ee.Image(self.options['input_asset'] + self.name_imgClass)        
        # print('bandas Year ', self.imgClass.bandNames().getInfo());
        self.lstbandNames = ['classification_' + str(yy) for yy in range(self.options['first_year'], self.options['last_year'] + 1)]
        self.years = [yy for yy in range(self.options['first_year'], self.options['last_year'] + 1)]
        self.limitYear = 5
        
    # https://code.earthengine.google.com/85a553702bd936707b6e9e5aa3321841
    def applyReshapeFlorest(self):

        mapClassCol = ee.Image().byte()        
        maskFlorRec = ee.Image.constant(0);
        contFlorest = ee.Image.constant(0);
        contSavana = ee.Image.constant(0);
        for bandaAct in self.lstbandNames[: self.limitYear]:
            mapFloresttmp = self.imgClass.select(bandaAct)
            maskFlorest = mapFloresttmp.eq(3)
            maskFlorRec = maskFlorRec.add(maskFlorest)

        for cc, bandaAct in enumerate(self.lstbandNames[:]):
            mapYeartmp = copy.deepcopy(self.imgClass.select(bandaAct))
            contFlorest = contFlorest.add(mapYeartmp.eq(3).multiply(maskFlorRec.gt(0)));
            contSavana = contSavana.add(mapYeartmp.eq(4).multiply(maskFlorRec.gt(0)));
          

            if cc + 1 >= self.limitYear:                 
                maskcomparativa = contFlorest.gt(contSavana);  # incluir todos estes pixeis
                # registrando pixels com algum pixel que não é nem Floresta nem Savana
                pixelsExcluidos = maskFlorRec.gt(0).multiply(self.limitYear).subtract(contFlorest.add(contSavana))
                # adicionar pixeis que não sao da classe 3 ou 4 e coloca os de savana maior
                pixelsExcluidos = pixelsExcluidos.add(contSavana.gt(contFlorest)).gt(0); 
                bandaBefore = self.lstbandNames[cc - 1]
                # seleção da floresta dos ultimos 2 anos
                florestUlt2YY = self.imgClass.select(bandaBefore).eq(3).add(mapYeartmp.eq(3))
                florestUlt2YY = florestUlt2YY.eq(2).add(maskcomparativa).gt(0)
                florestUlt2YY = florestUlt2YY.subtract(pixelsExcluidos).gt(0)   

                if cc  < self.limitYear:                    

                    for nbandaAct in self.lstbandNames[: self.limitYear]:
                        print("processing retroactivo band = ", nbandaAct)
                        mapYeartmp = self.imgClass.select(nbandaAct)
                        # incluido floresta 
                        # mapYeartmp = mapYeartmp.where(florestUlt2YY.eq(1), florestUlt2YY.multiply(3))
                        # excluindo floresta e incluindo savana
                        mapYeartmp = mapYeartmp.where(pixelsExcluidos.eq(1), pixelsExcluidos.multiply(4))
                        mapClassCol = mapClassCol.addBands(mapYeartmp.rename([nbandaAct]))

                else:
                    print("processing band = ", bandaAct)
                    
                    mapYeartmp = mapYeartmp.where(florestUlt2YY.eq(1), florestUlt2YY.multiply(3))
                    mapYeartmp = mapYeartmp.where(pixelsExcluidos.eq(1), pixelsExcluidos.multiply(4))
                    mapClassCol = mapClassCol.addBands(mapYeartmp.rename([bandaAct]))
                    # print(mapClassCol.bandNames().getInfo())

        mapClassCol = mapClassCol.select(self.lstbandNames).clip(self.geom_bacia)
        mapClassCol = mapClassCol.set(
                            'version',  self.versionRS, 
                            'biome', 'CAATINGA',
                            'type_filter', 'frequence',
                            'collection', '8.0',
                            'id_bacia', self.id_bacias,
                            'sensor', 'Landsat',
                            'system:footprint' , self.imgClass.get('system:footprint')
                        )
        img_output = ee.Image.cat(mapClassCol)
        name_toexport = 'filterRS_BACIA_'+ str(self.id_bacias) + "_V" + self.versionRS
        self.processoExportar(img_output, name_toexport) 

    def applyReshapeFlorest(self):

        mapClassCol = ee.Image().byte()        
        maskFlorRec = ee.Image.constant(0);
        contFlorest = ee.Image.constant(0);
        contSavana = ee.Image.constant(0);
        for bandaAct in self.lstbandNames[: self.limitYear]:
            mapFloresttmp = self.imgClass.select(bandaAct)
            maskFlorest = mapFloresttmp.eq(3)
            maskFlorRec = maskFlorRec.add(maskFlorest)

        for cc, bandaAct in enumerate(self.lstbandNames[:]):
            mapYeartmp = copy.deepcopy(self.imgClass.select(bandaAct))
            contFlorest = contFlorest.add(mapYeartmp.eq(3).multiply(maskFlorRec.gt(0)));
            contSavana = contSavana.add(mapYeartmp.eq(4).multiply(maskFlorRec.gt(0)));
          

            if cc + 1 >= self.limitYear:                 
                maskcomparativa = contFlorest.gt(contSavana);  # incluir todos estes pixeis
                # registrando pixels com algum pixel que não é nem Floresta nem Savana
                pixelsExcluidos = maskFlorRec.gt(0).multiply(self.limitYear).subtract(contFlorest.add(contSavana))
                # adicionar pixeis que não sao da classe 3 ou 4 e coloca os de savana maior
                pixelsExcluidos = pixelsExcluidos.add(contSavana.gt(contFlorest)).gt(0); 
                bandaBefore = self.lstbandNames[cc - 1]
                # seleção da floresta dos ultimos 2 anos
                florestUlt2YY = self.imgClass.select(bandaBefore).eq(3).add(mapYeartmp.eq(3))
                florestUlt2YY = florestUlt2YY.eq(2).add(maskcomparativa).gt(0)
                florestUlt2YY = florestUlt2YY.subtract(pixelsExcluidos).gt(0)   

                if cc  < self.limitYear:                    

                    for nbandaAct in self.lstbandNames[: self.limitYear]:
                        print("processing retroactivo band = ", nbandaAct)
                        mapYeartmp = self.imgClass.select(nbandaAct)
                        # incluido floresta 
                        # mapYeartmp = mapYeartmp.where(florestUlt2YY.eq(1), florestUlt2YY.multiply(3))
                        # excluindo floresta e incluindo savana
                        mapYeartmp = mapYeartmp.where(pixelsExcluidos.eq(1), pixelsExcluidos.multiply(4))
                        mapClassCol = mapClassCol.addBands(mapYeartmp.rename([nbandaAct]))

                else:
                    print("processing band = ", bandaAct)
                    
                    mapYeartmp = mapYeartmp.where(florestUlt2YY.eq(1), florestUlt2YY.multiply(3))
                    mapYeartmp = mapYeartmp.where(pixelsExcluidos.eq(1), pixelsExcluidos.multiply(4))
                    mapClassCol = mapClassCol.addBands(mapYeartmp.rename([bandaAct]))
                    # print(mapClassCol.bandNames().getInfo())

        mapClassCol = mapClassCol.select(self.lstbandNames).clip(self.geom_bacia)
        mapClassCol = mapClassCol.set(
                            'version',  self.versionRS, 
                            'biome', 'CAATINGA',
                            'type_filter', 'frequence',
                            'collection', '8.0',
                            'id_bacia', self.id_bacias,
                            'sensor', 'Landsat',
                            'system:footprint' , self.imgClass.get('system:footprint')
                        )
        img_output = ee.Image.cat(mapClassCol)
        name_toexport = 'filterRS_BACIA_'+ str(self.id_bacias) + "_V" + self.versionRS
        self.processoExportar(img_output, name_toexport) 


    ##### exporta a imagem classificada para o asset  ###
    def processoExportar(self, mapaRF,  nomeDesc):
        
        idasset =  self.options['output_asset'] + nomeDesc
        optExp = {
            'image': mapaRF, 
            'description': nomeDesc, 
            'assetId':idasset, 
            'region': self.geom_bacia.getInfo()['coordinates'],
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



param = {      
    'numeroTask': 6,
    'numeroLimit': 42,
    'conta' : {
        '0': 'caatinga03',
        '7': 'caatinga02',
        '14': 'caatinga01',
        '21': 'caatinga04',
        '28': 'caatinga05',        
        '32': 'solkan1201',
        # '32': 'rodrigo',
        '37': 'diegoGmail',    
    }
}

#============================================================
#========================METODOS=============================
#============================================================

def gerenciador(cont):

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
    '741','7421','7422','744','745','746','7492','751','752','753',
    '754','755','756','757','758','759','7621','7622','763','764',
    '765','766','767','771','772','773', '7741','7742','775','776',
    '777','778','76111','76116','7612','7613', '7614','7615','7616',
    '7617','7618','7619'
]
# listaNameBacias = ['756','777','778']

input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/Reshape/'
cont = 0
knowMapSaved = False
listBacFalta = []
for idbacia in listaNameBacias[:]:
    if knowMapSaved:
        try:
            nameMap = 'filterRS_BACIA_' + idbacia + "_V1"
            imgtmp = ee.Image(input_asset + nameMap)
            print("loading ", nameMap, " ", len(imgtmp.bandNames().getInfo()), "bandas ")
        except:
            listBacFalta.append(idbacia)
    else:
        print(" ")
        print("--------- PROCESSING BACIA {} ---------".format(idbacia))
        print("-------------------------------------------")
        cont = gerenciador(cont)
        aplicando_ReshapeFilter = processo_filterReshapeFlorest(idbacia)
        aplicando_ReshapeFilter.applyReshapeFlorest()

if knowMapSaved:
    print("lista de bacias que faltam \n ",listBacFalta)
    print("total ", len(listBacFalta))