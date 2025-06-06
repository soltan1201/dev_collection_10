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
    'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/transition',
    'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Merger',
    'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/bacias_hidrografica_caatinga_49_regions',      
    'classMapB': [3, 4, 5, 6, 9, 11, 12, 13, 15, 18, 19, 20, 21, 22, 23, 24, 25, 26, 29, 30, 31, 32, 33, 35, 36, 39, 40, 41, 46, 47, 48, 49, 50, 62],
    'classNew':  [3, 4, 4, 4, 4, 12, 12, 12, 21, 21, 21, 21, 21, 22, 22, 22, 22, 33, 29, 22, 33, 12, 33, 21, 21, 21, 21, 21, 21, 21, 21, 12,  4, 21], 
    'classNat':  [1, 1, 1, 1, 1,  1,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  0],       
    'last_year' : 2024,
    'first_year': 1985,
    'janela': 5,
    'step': 1,
    'versionOut' : 10,
    'versionInp' : 10,
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


def reclass_natural_Antropic(raster_maps, listYYbnd):
    mapstemporal = ee.Image().byte()
    lstRemap = []
    for mm, bnd_year in enumerate(listYYbnd):
        tmp_raster = raster_maps.select(bnd_year).remap(param['classMapB'], param['classNat'])
        mapstemporal = mapstemporal.addBands(tmp_raster)
        if mm == 0:
            lstRemap.append('remapped')
        else:
            lstRemap.append(f'remapped_{mm}')
    
    return mapstemporal.select(lstRemap).rename(listYYbnd)

def corrigir_transicoes_com_mascara_iterativa(name_bacia):
    """
    Corrige transições espúrias iterativamente para cada ano alvo, comparando-o
    com múltiplos anos de referência anteriores, e retorna a imagem corrigida
    mais uma máscara com os pixels revertidos.

    Para cada ano alvo, a sua banda é comparada sequencialmente com N anos anteriores
    (definido por 'janela_referencia_anos'), atualizando-se a cada passo.

    Retorna:
    - imagem_corrigida: ee.Image com bandas classification_YYYY corrigidas.
    - mapa_corrigido: ee.Image com 1 (nat→ant revertido), 2 (ant→nat revertido), 0 (sem mudança).
                      Reflete a última correção aplicada ao pixel.
    """
    lst_bands_years = ['classification_' + str(yy) for yy in range(param['last_year'], param['first_year'] - 1,  -1)]
    print("lista de anos ", lst_bands_years)

    geomBacia = (ee.FeatureCollection(param['asset_bacias_buffer'])
                    .filter(ee.Filter.eq('nunivotto4', name_bacia))
        )
    geomBacia = geomBacia.map(lambda f: f.set('id_codigo', 1))
    bacia_raster = geomBacia.reduceToImage(['id_codigo'], ee.Reducer.first()).gt(0)            
    geomBacia = geomBacia.geometry()

    imgClass = (ee.ImageCollection(param['input_asset'])
                        .filter(ee.Filter.eq('version', param['versionInp']))
                        .filter(ee.Filter.eq('id_bacias', name_bacia ))
                )
    print(" we load ", imgClass.size().getInfo())
    imgClass = imgClass.first()

    corrigida_final = ee.Image()
    limite_pixels = 44

    for cc, bnd_activa in enumerate(lst_bands_years):
        if cc < 2:
            limite_pixels -=  11
        raster_year_activo = imgClass.select(bnd_activa)

        if cc < len(lst_bands_years) - 1:             
            raster_year_before = imgClass.select(lst_bands_years[cc + 1])
            # print(janela_4)
            raster_year_activo_nat_ant = raster_year_activo.remap(param['classMapB'], param['classNat'])
            raster_year_before_nat_ant = raster_year_before.remap(param['classMapB'], param['classNat'])
            # print(anos_ref_para_iteracao.bandNames().getInfo())
            
            # ano activo sendo antropico ano anterior na serie com classe natural
            transicao_nat_para_ant_iter = raster_year_activo_nat_ant.eq(0).And(raster_year_before_nat_ant.eq(1))
            transicao_ant_para_nat_iter = raster_year_activo_nat_ant.eq(1).And(raster_year_before_nat_ant.eq(0))

            # Checar conectividade das transições identificadas
            conect_nat_para_ant_iter = transicao_nat_para_ant_iter.connectedPixelCount(100, True).lte(limite_pixels)
            conect_ant_para_nat_iter = transicao_ant_para_nat_iter.connectedPixelCount(100, True).lte(limite_pixels)


            # Aplicar correção à banda_sendo_processada, revertendo para o valor da banda_ref_iteracao
            banda_sendo_processada = (raster_year_activo 
                                            .where(conect_nat_para_ant_iter, raster_year_before) 
                                            .where(conect_ant_para_nat_iter, raster_year_before)
                                            .rename(bnd_activa)
                                    )
            corrigida_final = corrigida_final.addBands(banda_sendo_processada)
        else:
            corrigida_final = corrigida_final.addBands(raster_year_activo)

    
    class_output = ee.Image().byte()
    lst_bands_years = [f'classification_{yyear}' for yyear in range(param['first_year'], param['last_year'] + 1)]
    for yyear in range(param['first_year'], param['last_year'] + 1):
        class_output = class_output.addBands(corrigida_final.select(f'classification_{yyear}'))

    nameExp = f"filterTS_BACIA_{name_bacia}_GTB_V{param['versionOut']}"
    # class_output = class_output.set('version', param['versionSP'])
    class_output = (class_output.updateMask(bacia_raster)
                    .select(lst_bands_years)
                    .set(
                        'version', param['versionOut'], 'biome', 'CAATINGA',
                        'collection', '10.0', 'id_bacias', name_bacia,
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
        
    



listaNameBacias = [
    '7691', '7754', '7581', '7625', '7584', '751', '7614', 
    '7616', '745', '7424', '773', '7612', '7613', '752', 
    '7618', '7561', '755', '7617', '7564', '761111','761112', 
    '7741', '7422', '76116', '7761', '7671', '7615', '7411', 
    '7764', '757', '771', '766', '7746', '753', '764', 
    '7541', '7721', '772', '7619', '7443','7544', '7438', 
    '763', '7591', '7592', '746','7712', '7622', '765',     
]

version = 10
input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Spatials_int'
listBacFalta = []
knowMapSaved = False
for cc, idbacia in enumerate(listaNameBacias[:]):   
    if knowMapSaved:
        try:
            imgtmp = (ee.ImageCollection(input_asset)
                            .filter(ee.Filter.eq('version', version))
                            .filter(ee.Filter.eq('id_bacias', idbacia ))
                            .first()
                )
            # print("know how many images exist ", imgtmp.get('system:index').getInfo())
            print(f" 👀> {cc} loading {imgtmp.get('system:index').getInfo()}", len(imgtmp.bandNames().getInfo()), "bandas ✅ ")
        except:
            listBacFalta.append(idbacia)
    else: 
        if idbacia not in listBacFalta:
            # cont = gerenciador(cont)            
            print("----- PROCESSING BACIA {} -------".format(idbacia))        
            corrigir_transicoes_com_mascara_iterativa(idbacia)

if knowMapSaved:
    print("lista de bacias que faltam \n ",listBacFalta)
    print("total ", len(listBacFalta))