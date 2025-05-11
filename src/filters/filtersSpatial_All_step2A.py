#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

import ee
import os 
import copy
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
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

param = {      
    'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Spatial',
    # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/FrequencyV3',
    'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Gap-fill',
    # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Temporal',
    'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/bacias_hidrografica_caatinga_49_regions',            
    'last_year' : 2024,
    'first_year': 1985,
    'janela': 3,
    'step': 1,
    'versionOut' : 4,
    'versionInp' : 4,
    'numeroTask': 6,
    'numeroLimit': 50,
    'conta' : {
        '0': 'caatinga01',   # 
        '6': 'caatinga02',
        '14': 'caatinga03',
        '21': 'caatinga04',
        '28': 'caatinga05',        
        '35': 'solkan1201',    
        '42': 'solkanGeodatin',
        # '14': 'diegoUEFS',
        '16': 'superconta'     
    }
}
lst_bands_years = ['classification_' + str(yy) for yy in range(param['first_year'], param['last_year'] + 1)]

def buildingLayerconnectado(imgClasse):
    lst_band_conn = ['classification_' + str(yy) + '_conn' for yy in range(param['first_year'], param['last_year'] + 1)]
    # / add connected pixels bands
    maxNumbPixels = 10
    bandaConectados = imgClasse.connectedPixelCount(
                                            maxSize= maxNumbPixels, 
                                            eightConnected= True
                                        ).rename(lst_band_conn)
    imageFilledConnected = imgClasse.addBands(bandaConectados)

    return imageFilledConnected


def apply_spatialFilterConn (name_bacia):
    frequencyNat = False
    # no scripts do gapFill estava com 10
    min_connect_pixel = 10
    geomBacia = (ee.FeatureCollection(param['asset_bacias_buffer'])
                    .filter(ee.Filter.eq('nunivotto4', name_bacia))
        )
    geomBacia = geomBacia.map(lambda f: f.set('id_codigo', 1))
    bacia_raster = geomBacia.reduceToImage(['id_codigo'], ee.Reducer.first()).gt(0)            
    geomBacia = geomBacia.geometry()

    if 'Temporal' in param['input_asset']:
        #filterTP_BACIA_7754_GTB_J3_V4
        name_imgClass = f"filterTP_BACIA_{name_bacia}_GTB_J{param['janela']}_V{param['versionInp']}"
    elif "Frequenc" in param['input_asset']:
        name_imgClass = 'filterFQ_BACIA_'+ name_bacia + "_V" + str(param['versionInp'])
    elif 'Gap-fill' in param['input_asset']:
        # filterGF_BACIA_745_GTB_V30
        pass
    
    if frequencyNat:
        print("carregando frequency Natural ")
        frecuencia = 'frequence'
    else:
        frecuencia = 'frequence_natUso'

    imgClass = (ee.ImageCollection(param['input_asset'])
                        # .filter(ee.Filter.eq('version', param['versionInp']))
                        .filter(ee.Filter.eq('id_bacia', name_bacia ))
                )
    print(" we load ", imgClass.size().getInfo())
    if "Temporal" in param['input_asset']:
        imgClass = (imgClass.filter(ee.Filter.eq('step', 1))
                            .filter(ee.Filter.eq('janela', 3)))
    
    imgClass = imgClass.first().updateMask(bacia_raster)
    print('  show metedata imgClass', imgClass.get('system:index').getInfo())
    # print(imgClass.aggregate_histogram('system:index').getInfo())
    # sys.exit()
    numBands = len(imgClass.bandNames().getInfo())
    print(' numero de bandas ', numBands)
    if numBands <= 49:
        imgClass = buildingLayerconnectado(imgClass)
    

    class_output = ee.Image().byte()

    # https://code.earthengine.google.com/b24c36d4d749a00d619eee4d4cbdde58
    for cc, yband_name in enumerate(lst_bands_years[:]):
        maskConn = imgClass.select(f'{yband_name}_conn').lt(min_connect_pixel).selfMask()
        ### // Define o tamanho da janela do filtro (3x3 neste caso)   ///
        ###  // var kernel = ee.Kernel.square(1); ### // Raio de 1 pixel (janela 3x3) //
        kernel = ee.Kernel.square(2) ####// Raio de 2 pixels (janela 5x5)
        # // Aplica o filtro da maioria colocando o valor da moda
        filteredImage = (imgClass.select(yband_name)
                                .reduceNeighborhood(
                                    reducer= ee.Reducer.mode(),
                                    kernel= kernel
                                )
                        )
        # ficando com os pixels da moda 
        filteredImage = filteredImage.updateMask(maskConn)
        # moda_kernel = imgClass.select(yband_name).focal_mode(2 , 'square', 'pixels')
        # moda_kernel = moda_kernel.updateMask()
        rasterMap = imgClass.select(yband_name).blend(filteredImage).rename(yband_name)
        class_output = class_output.addBands(rasterMap)
    
    nameExp = f"filterSP_BACIA_{name_bacia}_GTB_V{param['versionOut']}_step{param['step']}"
    # class_output = class_output.set('version', param['versionSP'])
    class_output = (class_output.updateMask(bacia_raster)
                    .select(lst_bands_years)
                    .set(
                        'version', param['versionOut'], 'biome', 'CAATINGA',
                        'collection', '10.0', 'id_bacia', name_bacia,
                        'sensor', 'Landsat', 'source','geodatin', 
                        'model', 'GTB', 'step', param['step'], 
                        'system:footprint', geomBacia
                    ))
    processoExportar(class_output,  nameExp, geomBacia)

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


relatorios = open("relatorioTaskXContas.txt", 'a+')
#============================================================
#========================METODOS=============================
#============================================================
def gerenciador(cont):    
    #=====================================
    # gerenciador de contas para controlar 
    # processos task no gee   
    #=====================================
    numberofChange = [kk for kk in param['conta'].keys()]
    print(numberofChange)
    
    if str(cont) in numberofChange:
        
        switch_user(param['conta'][str(cont)])
        projAccount = get_project_from_account(param['conta'][str(cont)])
        try:
            ee.Initialize(project= projAccount) # project='ee-cartassol'
            print('The Earth Engine package initialized successfully!')
        except ee.EEException as e:
            print('The Earth Engine package failed to initialize!') 

        # tasks(n= param['numeroTask'], return_list= True) 
        relatorios.write("Conta de: " + param['conta'][str(cont)] + '\n')

        tarefas = tasks(
            n= param['numeroTask'],
            return_list= True)
        
        for lin in tarefas:            
            relatorios.write(str(lin) + '\n')
    
    elif cont > param['numeroLimit']:
        return 0
    cont += 1    
    return cont


listaNameBacias = [
    '7691', '7754', '7581', '7625', '7584', '751', '7614', 
    '7616', '745', '7424', '773', '7612', '7613', 
    '7618', '7561', '755', '7617', '7564', '761111','761112', 
    '7741', '7422', '76116', '7761', '7671', '7615', '7411', 
    '7764', '757', '771', '766', '7746', '753', '764', 
    '7541', '7721', '772', '7619', '7443','7544', '7438', 
    '763', '7591', '7592', '746','7712', '7622', '765', 
    #'752', 
]

lstBacias = []
changeAcount = False
lstqFalta =  []
cont = 16
# input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Estavel'
# input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fillV2'
input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Gap-fill'
if changeAcount:
    cont = gerenciador(cont)
version = 4
modelo = 'GTB'
listBacFalta = []
knowMapSaved = False
for cc, idbacia in enumerate(listaNameBacias[:]):   
    if knowMapSaved:
        try:
            nameMap = f"filterGF_BACIA_{idbacia}_GTB_V{version}"
            # # nameMap = 'filterSP_BACIA_'+ str(idbacia) + "_V" + str(version)
            # print(nameMap)
            # imgtmp = ee.Image(input_asset + nameMap)
            imgtmp = (ee.ImageCollection(input_asset)
                            # .filter(ee.Filter.eq('version', version))
                            .filter(ee.Filter.eq('id_bacia', idbacia ))
                            .first()
                )
            # print("know how many images exist ", imgtmp.size().getInfo())
            print(f" 👀> {cc} loading {imgtmp.get('system:index').getInfo()}", len(imgtmp.bandNames().getInfo()), "bandas ✅ ")
        except:
            listBacFalta.append(idbacia)
    else: 
        if idbacia not in lstBacias:
            # cont = gerenciador(cont)            
            print("----- PROCESSING BACIA {} -------".format(idbacia))        
            apply_spatialFilterConn(idbacia)
            


if knowMapSaved:
    print("lista de bacias que faltam \n ",listBacFalta)
    print("total ", len(listBacFalta))