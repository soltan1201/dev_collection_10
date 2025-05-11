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


class processo_filterFrequence(object):

    options = {
            'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/FrequencyV3/',
            # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV3',
            'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/TemporalV3',
            # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fillV2',
            'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',            
            'last_year' : 2023,
            'first_year': 1985
        }

    def __init__(self, nameBacia, nmodel):
        self.id_bacias = nameBacia
        self.versoutput = 31
        self.versinput = 31
        self.nmodel = nmodel
        janela = 5
        self.step = 1
        self.geom_bacia = ee.FeatureCollection(self.options['asset_bacias_buffer']).filter(
                                                   ee.Filter.eq('nunivotto3', nameBacia)).first().geometry()   

        # filterSP_BACIA_778_V1     
        if "Spatial" in self.options['input_asset']:
            self.name_imgClass = 'filterSP_BACIA_' + nameBacia + f"_{self.nmodel}_V" + str(self.versinput) + '_step' + str(self.step)
        elif "Gap-fill" in self.options['input_asset']:
            self.name_imgClass = 'filterGF_BACIA_' + nameBacia + "_GTB_V" + str(self.versinput)
        else:
            self.name_imgClass = 'filterTP_BACIA_' + nameBacia+ f"_GTB_J{janela}_V" + str(self.versinput)
        
        print(" ⚠️  Loading " + self.name_imgClass)
        # self.imgClass = ee.Image(self.options['input_asset'] + "/" + self.name_imgClass)   

        self.imgClass = ee.ImageCollection(self.options['input_asset']).filter(
                                    ee.Filter.eq('id_bacia', nameBacia)).filter(
                                        ee.Filter.eq('version',  self.versinput)).filter(
                                            ee.Filter.eq('model', self.nmodel)).first()        
        print(" image class ", self.imgClass.get('system:index').getInfo())

        self.lstbandNames = ['classification_' + str(yy) for yy in range(self.options['first_year'], self.options['last_year'] + 1)]
        self.years = [yy for yy in range(self.options['first_year'], self.options['last_year'] + 1)]

        ##### ////////Calculando frequencias /////////////#####
        #######################################################
        #############  General rule in Years ##################
        exp = '100*((b(0) + b(1) + b(2) + b(3) + b(4) + b(5) + b(6) + b(7) + b(8) + b(9) + b(10) + b(11) + b(12)'
        exp += '+ b(13) + b(14) + b(15) + b(16) + b(17) + b(18) + b(19) + b(20) + b(21) + b(22) + b(23) + b(24)'
        exp += '+ b(25) + b(26) + b(27) + b(28) + b(29) + b(30) + b(31) + b(32) + b(33) + b(34) + b(35) + b(36)'
        exp += '+ b(37)+ b(38))/39)'

        self.florest_frequence = self.imgClass.eq(3).expression(exp)
        self.savana_frequence = self.imgClass.eq(4).expression(exp)
        self.grassland_frequence = self.imgClass.eq(12).expression(exp) 
        # sys.exit()
        # self.maskpropNatural = self.imgClass.eq(3).Or(self.imgClass.eq(4)).Or(self.imgClass.eq(12)).expression(exp)
        
       
    def applyStabilityNaturalClass(self, bandYearCourrent):        

        ############## get frequency   #######################
        mapCourrent = self.imgClass.select(bandYearCourrent)
        maskNatCourrent  = mapCourrent.eq(3).Or(mapCourrent.eq(4)).Or(mapCourrent.eq(12))            
        
        ###########  /////Mapa base////// ############
        # todo o quye esta na
        vegetation_map = ee.Image(0).where(maskNatCourrent.eq(1).And(self.grassland_frequence.gt(80)), 12)
        vegetation_map = vegetation_map.where(maskNatCourrent.eq(1).And(self.florest_frequence.gt(80)), 3)
        vegetation_map = vegetation_map.where(maskNatCourrent.eq(1).And(self.savana_frequence.gte(30)), 4)
                                        

        maskNatCourrent = maskNatCourrent.updateMask(vegetation_map.gt(0))
        img_output = mapCourrent.where(maskNatCourrent, vegetation_map)

        return img_output.clip(self.geom_bacia).rename(bandYearCourrent)

    def iterandoFilterbyYear(self):

        for cc, bandYY in enumerate(self.lstbandNames):            
            imgtempBase = self.applyStabilityNaturalClass(bandYY)
            if cc == 0:
                rasterFinal = imgtempBase
            else:
                rasterFinal = rasterFinal.addBands(imgtempBase)

        rasterFinal = rasterFinal.set(
                            'version',  int(self.versoutput), 
                            'biome', 'CAATINGA',
                            'type_filter', 'frequence',
                            'from', 'Gap-fill',
                            'collection', '9.0',
                            'model', self.nmodel,
                            'step', self.step,
                            'id_bacia', self.id_bacias,
                            'sensor', 'Landsat',
                            'system:footprint' , self.geom_bacia
                        )

        rasterFinal = ee.Image.cat(rasterFinal)
        name_toexport = 'filterFQ_BACIA_'+ str(self.id_bacias) + f"_{self.nmodel}_V" + str(self.versoutput) + '_' + str(self.step)
        self.processoExportar(rasterFinal, name_toexport)    

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
        '0': 'caatinga01',
        '2': 'caatinga02',
        '4': 'caatinga03',
        '6': 'caatinga04',
        '8': 'caatinga05',        
        '10': 'solkan1201',    
        '12': 'solkanGeodatin',
        '14': 'diegoUEFS' ,
        '20': 'superconta'   
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
        return  0
    
    cont += 1    
    return cont


listaNameBacias = [
    '745','741', '7422','744','746','751','752', '7492','7421',
    '753', '754','755','756','757','758','759','7621','7622','763',
    '764','765','766','767','771','772','773', '7741','7742','775',
    '776','76111','76116','7612','7613','7614','7615',  '777','778',
    '7616','7617','7618','7619'
]

# listaNameBacias = [
#     '76111', '756', '757', '758', '754', '7614', '7421'
# ]

# input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/TemporalV3/'
input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/FrequencyV3'
# input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV3'
cont = 0
version = 31
modelo = 'GTB'
# imgtmp = ee.ImageCollection(input_asset).filter(ee.Filter.eq('version', version))
# print(" " ,imgtmp.size().getInfo())
# sys.exit()
knowMapSaved = False
listBacFalta = []

for cc, idbacia in enumerate(listaNameBacias[1:]):
    if knowMapSaved:
        try:
            imgtmp = ee.ImageCollection(input_asset).filter(
                                ee.Filter.eq('id_bacia', idbacia)).filter(
                                    ee.Filter.eq('version', version))
            print(f" {cc} 📢 ", imgtmp.first().get("system:index").getInfo() , " < > ", len(imgtmp.first().bandNames().getInfo()) )
            # print("loading ", nameMap, " ", len(imgtmp.bandNames().getInfo()), "bandas ")
        except:
            listBacFalta.append(idbacia)
    else:
        if idbacia not in listBacFalta:
            print(" ")
            print(f"--------- 📢 #{cc} PROCESSING BACIA {idbacia} ---------")
            print("----------------------------------------------")
            # cont = gerenciador(cont)
            aplicando_FrequenceFilter = processo_filterFrequence(idbacia, modelo)
            aplicando_FrequenceFilter.iterandoFilterbyYear()

if knowMapSaved:
    print("lista de bacias que faltam \n ",listBacFalta)
    print("total ", len(listBacFalta))