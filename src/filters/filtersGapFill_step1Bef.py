#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

import ee
import os 
import sys

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


class processo_gapfill(object):

    options = {
            'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fillV2/',
            # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVP/',
            'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVX/',
            'input_asset_prob': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVY/',  # ClassVY
            # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/misto/',
            'inputAsset8': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
            'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',
            # 'asset_bacias_buffer' : 'projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga',
            'classMapB' : [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
            'classNew'  : [3, 4, 3, 3,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33, 21,33,33,21,21,21,21,21,21,21,21,21,21, 4,12,21],
            'year_inic': 1985,
            'year_end': 2023
        }


    def __init__(self, nameBacia, conectarPixels, vers, modelo):
        self.id_bacias = nameBacia
        self.geom_bacia = ee.FeatureCollection(self.options['asset_bacias_buffer']).filter(
                                                    ee.Filter.eq('nunivotto3', nameBacia)).first().geometry()   
        print("geometria ", len(self.geom_bacia.getInfo()['coordinates']))
        self.lstbandNames = ['classification_' + str(yy) for yy in range(self.options['year_inic'], self.options['year_end'] + 1)]
        self.years = [yy for yy in range(self.options['year_end'], self.options['year_inic'] - 1,  -1)]
        # print("lista de years \n ", self.years)
        self.conectarPixels = conectarPixels
        self.version = vers
        self.model = modelo
        # self.name_imgClass = 'BACIA_' + nameBacia + '_GTB_col8'
        # self.name_imgClass = 'BACIA_' + nameBacia + '_RF_col8'
        # BACIA_776_GTB_col9-v9
        self.name_imgClass = 'BACIA_' + nameBacia + '_'+ modelo + '_col9-v' + str(self.version )
        print("processing image ", self.name_imgClass)
        # self.name_imgClass = 'BACIA_corr_mista_' + nameBacia + '_V2'       
        self.imgMap8 = ee.Image(self.options['inputAsset8']).clip(self.geom_bacia)
        if int(self.version) > 6:  # 
            self.imgClass = ee.Image(self.options['input_asset_prob'] + self.name_imgClass)
        else:
            self.imgClass = ee.Image(self.options['input_asset'] + self.name_imgClass)
        
        print("todas as bandas \n === > ", self.imgClass.bandNames().getInfo())
        # sys.exit()
        # self.imgClass = self.imgClass.mask(self.imgClass.neq(0))  
        # o segundo processo de revisão começa na versão 3      
        
        
    def dictionary_bands(self, key, value):
        imgT = ee.Algorithms.If(
                        ee.Number(value).eq(2),
                        self.imgClass.select([key]).byte(),
                        ee.Image().rename([key]).byte().updateMask(self.imgClass.select(0))
                    )
        return ee.Image(imgT)

    def applyGapFill(self):
        lst_band_conn = []
        lstImgMap = None
        previousImage = None        
        ###########  CORREGINDO DE 2023 PARA 1985 ############################
        cc = 0
        for yyear in tqdm(self.years):
            bandActive = 'classification_' + str(yyear)
            # print(f" # {cc}  processing >> {bandActive}")
            if cc > 0:  
                currentImage = self.imgClass.select(bandActive).remap(self.options['classMapB'], 
                                                        self.options['classNew']).rename(bandActive)
                previousImage = ee.Image(previousImage)
                currentImage = currentImage.unmask(previousImage)
                lstImgMap = lstImgMap.addBands(currentImage)
                previousImage = copy.deepcopy(currentImage)              
            else:
                previousImage = self.imgClass.select(bandActive).remap(self.options['classMapB'], 
                                                        self.options['classNew']).rename(bandActive)           
                lstImgMap = copy.deepcopy(previousImage)                
            cc += 1
        imageFilledTnT0 = ee.Image.cat(lstImgMap).select(self.lstbandNames)
        # print(" primeiro passo  ", imageFilledTnT0.bandNames().getInfo())
        previousImage = None
        lstImgMap = None
        ###########  CORREGINDO DE 1985 PARA 2023 ############################
        cc = 0
        for  bandActive in tqdm(self.lstbandNames):    
            # print(f" # {cc}  processing >> {bandActive}")       
            if cc > 0:
                currentImage = imageFilledTnT0.select(bandActive)
                previousImage = ee.Image(previousImage)
                currentImage = currentImage.unmask(previousImage)
                lstImgMap = lstImgMap.addBands(currentImage)
                previousImage = copy.deepcopy(currentImage)
            else:
                previousImage = ee.Image(imageFilledTnT0.select(bandActive))            
                lstImgMap = copy.deepcopy(previousImage) 
            cc += 1
        imageFilledTn = ee.Image.cat(lstImgMap).select(self.lstbandNames)
        # print(" segundo passo  ", imageFilledTn.bandNames().getInfo())
        


        # imageFilledTn = ee.Image.cat(lstImgMap).select(self.lstbandNames)
        if self.conectarPixels:
            lst_band_conn = [bnd + '_conn' for bnd in self.lstbandNames]
            # / add connected pixels bands
            imageFilledTnCon = imageFilledTn.addBands(
                                        imageFilledTn.connectedPixelCount(10, True).rename(lst_band_conn))
            # exportin imagem conectada    
            return imageFilledTnCon
        else:
            # print("banda col 8", imageFilledTn.bandNames().getInfo())
            return imageFilledTn

    def processing_gapfill(self):
        # apply the gap fill
        imageFilled = self.applyGapFill()
        print("passou")
        # print(imageFilled.bandNames().getInfo())

        name_toexport = 'filterGF_BACIA_'+ str(self.id_bacias) + '_' +  self.model + "_V" + str(self.version)
        imageFilled = ee.Image(imageFilled).set(
                            'version', int(self.version), 
                            'biome', 'CAATINGA',
                            'source', 'geodatin',
                            'model', self.model,
                            'type_filter', 'gap_fill',
                            'collection', '9.0',
                            'id_bacia', self.id_bacias,
                            'sensor', 'Landsat',
                            'system:footprint' , self.imgClass.get('system:footprint')
                        )
        
        self.processoExportar(imageFilled, name_toexport)

    #exporta a imagem classificada para o asset
    def processoExportar(self, mapaRF,  nomeDesc):
        
        idasset =  self.options['output_asset'] + nomeDesc
        optExp = {
            'image': mapaRF, 
            'description': nomeDesc, 
            'assetId':idasset, 
            'region':self.geom_bacia.getInfo()['coordinates'],
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
    'bioma': "CAATINGA", #nome do bioma setado nos metadados  
    'numeroTask': 6,
    'numeroLimit': 42,
    'conta' : {
        '0': 'caatinga01',   # 
        '4': 'caatinga02',
        '8': 'caatinga03',
        '12': 'caatinga04',
        '16': 'caatinga05',        
        '20': 'solkan1201',    
        '24': 'solkanGeodatin',
        '28': 'diegoUEFS',
        '32': 'superconta'     
    }
}

#============================================================
#========================METODOS=============================
#============================================================
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
    # '744','741','7422','745','746','7492','751','752','753',
    # '755','759','7621','7622', '763','764','765','766','767', 
    # '771', '772','773','7741','776','7742','775','777', '778',
    # '76116','7612','7613','7615','7616','7617','7618',
    # '7619','754','756','757','758', '7614', '7421', '76111'
    # '752','756','755','758', '76111', 
    '744','754','757','7614','7421'
]
# listaNameBacias = [
#     '754','756','757','758',
# ]

models = "RF"  # "RF", "GTB"
versionMap= 30
cont = 20
for idbacia in listaNameBacias[:]:
    print("-----------------------------------------")
    print("----- PROCESSING BACIA {} -------".format(idbacia))

    cont = gerenciador(cont)
    aplicando_gapfill = processo_gapfill(idbacia, False, versionMap, models) # added band connected is True
    aplicando_gapfill.processing_gapfill()