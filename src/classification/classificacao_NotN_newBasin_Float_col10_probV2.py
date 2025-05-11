#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

import ee
import os 
import glob
import json
import csv
import copy
import sys
import math
import pandas as pd
from pathlib import Path
import arqParametros as arqParams 
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
# sys.setrecursionlimit(1000000000)

#============================================================
#============== FUNCTIONS FO SPECTRAL INDEX =================
#region Bloco de functions de calculos de Indices 
# Ratio Vegetation Index
def agregateBandsIndexRATIO(img):

    ratioImgY = img.expression("float(b('nir_median') / b('red_median'))")\
                            .rename(['ratio_median']).toFloat()

    ratioImgwet = img.expression("float(b('nir_median_wet') / b('red_median_wet'))")\
                            .rename(['ratio_median_wet']).toFloat()  

    ratioImgdry = img.expression("float(b('nir_median_dry') / b('red_median_dry'))")\
                            .rename(['ratio_median_dry']).toFloat()        

    return img.addBands(ratioImgY).addBands(ratioImgwet).addBands(ratioImgdry)

# Ratio Vegetation Index
def agregateBandsIndexRVI(img):

    rviImgY = img.expression("float(b('red_median') / b('nir_median'))")\
                            .rename(['rvi_median']).toFloat() 
    
    rviImgWet = img.expression("float(b('red_median_wet') / b('nir_median_wet'))")\
                            .rename(['rvi_median_wet']).toFloat() 

    rviImgDry = img.expression("float(b('red_median_dry') / b('nir_median_dry'))")\
                            .rename(['rvi_median']).toFloat()       

    return img.addBands(rviImgY).addBands(rviImgWet).addBands(rviImgDry)


def agregateBandsIndexNDVI(img):

    ndviImgY = img.expression("float(b('nir_median') - b('red_median')) / (b('nir_median') + b('red_median'))")\
                            .rename(['ndvi_median']).toFloat()    

    ndviImgWet = img.expression("float(b('nir_median_wet') - b('red_median_wet')) / (b('nir_median_wet') + b('red_median_wet'))")\
                            .rename(['ndvi_median_wet']).toFloat()  

    ndviImgDry = img.expression("float(b('nir_median_dry') - b('red_median_dry')) / (b('nir_median_dry') + b('red_median_dry'))")\
                            .rename(['ndvi_median_dry']).toFloat()     

    return img.addBands(ndviImgY).addBands(ndviImgWet).addBands(ndviImgDry)


def  agregateBandsIndexNDWI(img):

    ndwiImgY = img.expression("float(b('nir_median') - b('swir2_median')) / (b('nir_median') + b('swir2_median'))")\
                            .rename(['ndwi_median']).toFloat()       

    ndwiImgWet = img.expression("float(b('nir_median_wet') - b('swir2_median_wet')) / (b('nir_median_wet') + b('swir2_median_wet'))")\
                            .rename(['ndwi_median_wet']).toFloat()   

    ndwiImgDry = img.expression("float(b('nir_median_dry') - b('swir2_median_dry')) / (b('nir_median_dry') + b('swir2_median_dry'))")\
                            .rename(['ndwi_median_dry']).toFloat()   

    return img.addBands(ndwiImgY).addBands(ndwiImgWet).addBands(ndwiImgDry)


def AutomatedWaterExtractionIndex(img):    
    aweiY = img.expression(
                        "float(4 * (b('green_median') - b('swir2_median')) - (0.25 * b('nir_median') + 2.75 * b('swir1_median')))"
                    ).rename("awei_median").toFloat() 

    aweiWet = img.expression(
                        "float(4 * (b('green_median_wet') - b('swir2_median_wet')) - (0.25 * b('nir_median_wet') + 2.75 * b('swir1_median_wet')))"
                    ).rename("awei_median_wet").toFloat() 

    aweiDry = img.expression(
                        "float(4 * (b('green_median_dry') - b('swir2_median_dry')) - (0.25 * b('nir_median_dry') + 2.75 * b('swir1_median_dry')))"
                    ).rename("awei_median_dry").toFloat()          
    
    return img.addBands(aweiY).addBands(aweiWet).addBands(aweiDry)


def IndiceIndicadorAgua(img):    
    iiaImgY = img.expression(
                        "float((b('green_median') - 4 *  b('nir_median')) / (b('green_median') + 4 *  b('nir_median')))"
                    ).rename("iia_median").toFloat()
    
    iiaImgWet = img.expression(
                        "float((b('green_median_wet') - 4 *  b('nir_median_wet')) / (b('green_median_wet') + 4 *  b('nir_median_wet')))"
                    ).rename("iia_median_wet").toFloat()

    iiaImgDry = img.expression(
                        "float((b('green_median_dry') - 4 *  b('nir_median_dry')) / (b('green_median_dry') + 4 *  b('nir_median_dry')))"
                    ).rename("iia_median_dry").toFloat()
    
    return img.addBands(iiaImgY).addBands(iiaImgWet).addBands(iiaImgDry)


def agregateBandsIndexEVI(img):
        
    eviImgY = (img.expression(
        "float(2.4 * (b('nir_median') - b('red_median')) / (1 + b('nir_median') + b('red_median')))")
            .rename(['evi_median']).toFloat() )

    eviImgWet = (img.expression(
        "float(2.4 * (b('nir_median_wet') - b('red_median_wet')) / (1 + b('nir_median_wet') + b('red_median_wet')))")
            .rename(['evi_median_wet']).toFloat()   )

    eviImgDry = (img.expression(
        "float(2.4 * (b('nir_median_dry') - b('red_median_dry')) / (1 + b('nir_median_dry') + b('red_median_dry')))")\
            .rename(['evi_median_dry']).toFloat()   )
    
    return img.addBands(eviImgY).addBands(eviImgWet).addBands(eviImgDry)

def calculateBandsIndexEVI(img):
    
    eviImgY = img.expression(
        "float(2.4 * (b('nir') - b('red')) / (1 + b('nir') + b('red')))")\
            .rename(['evi']).toFloat() 

    return img.addBands(eviImgY)


def agregateBandsIndexGVMI(img):
    
    gvmiImgY = img.expression(
                    "float ((b('nir_median')  + 0.1) - (b('swir1_median') + 0.02)) / ((b('nir_median') + 0.1) + (b('swir1_median') + 0.02))" 
                ).rename(['gvmi_median']).toFloat()   

    gvmiImgWet = img.expression(
                    "float ((b('nir_median_wet')  + 0.1) - (b('swir1_median_wet') + 0.02)) / ((b('nir_median_wet') + 0.1) + (b('swir1_median_wet') + 0.02))" 
                ).rename(['gvmi_median_wet']).toFloat()

    gvmiImgDry = img.expression(
                    "float ((b('nir_median_dry')  + 0.1) - (b('swir1_median_dry') + 0.02)) / ((b('nir_median_dry') + 0.1) + (b('swir1_median_dry') + 0.02))" 
                ).rename(['gvmi_median_dry']).toFloat()  

    return img.addBands(gvmiImgY).addBands(gvmiImgWet).addBands(gvmiImgDry)

def agregateBandsIndexLAI(img):
    laiImgY = img.expression(
        "float(3.618 * (b('evi_median') - 0.118))")\
            .rename(['lai_median']).toFloat()

    return img.addBands(laiImgY)    

def agregateBandsIndexGCVI(img):    
    gcviImgAY = img.expression(
        "float(b('nir_median')) / (b('green_median')) - 1")\
            .rename(['gcvi_median']).toFloat()   

    gcviImgAWet = img.expression(
        "float(b('nir_median_wet')) / (b('green_median_wet')) - 1")\
            .rename(['gcvi_median_wet']).toFloat() 
            
    gcviImgADry = img.expression(
        "float(b('nir_median_dry')) / (b('green_median_dry')) - 1")\
            .rename(['gcvi_median_dry']).toFloat()      
    
    return img.addBands(gcviImgAY).addBands(gcviImgAWet).addBands(gcviImgADry)

# Global Environment Monitoring Index GEMI 
def agregateBandsIndexGEMI(img):    
    # "( 2 * ( NIR ^2 - RED ^2) + 1.5 * NIR + 0.5 * RED ) / ( NIR + RED + 0.5 )"
    gemiImgAY = img.expression(
        "float((2 * (b('nir_median') * b('nir_median') - b('red_median') * b('red_median')) + 1.5 * b('nir_median')" +
        " + 0.5 * b('red_median')) / (b('nir_median') + b('green_median') + 0.5) )")\
            .rename(['gemi_median']).toFloat()    

    gemiImgAWet = img.expression(
        "float((2 * (b('nir_median_wet') * b('nir_median_wet') - b('red_median_wet') * b('red_median_wet')) + 1.5 * b('nir_median_wet')" +
        " + 0.5 * b('red_median_wet')) / (b('nir_median_wet') + b('green_median_wet') + 0.5) )")\
            .rename(['gemi_median_wet']).toFloat() 

    gemiImgADry = img.expression(
        "float((2 * (b('nir_median_dry') * b('nir_median_dry') - b('red_median_dry') * b('red_median_dry')) + 1.5 * b('nir_median_dry')" +
        " + 0.5 * b('red_median_dry')) / (b('nir_median_dry') + b('green_median_dry') + 0.5) )")\
            .rename(['gemi_median_dry']).toFloat()     
    
    return img.addBands(gemiImgAY).addBands(gemiImgAWet).addBands(gemiImgADry)

# Chlorophyll vegetation index CVI
def agregateBandsIndexCVI(img):    
    cviImgAY = img.expression(
        "float(b('nir_median') * (b('green_median') / (b('blue_median') * b('blue_median'))))")\
            .rename(['cvi_median']).toFloat()  

    cviImgAWet = img.expression(
        "float(b('nir_median_wet') * (b('green_median_wet') / (b('blue_median_wet') * b('blue_median_wet'))))")\
            .rename(['cvi_median_wet']).toFloat()

    cviImgADry = img.expression(
        "float(b('nir_median_dry') * (b('green_median_dry') / (b('blue_median_dry') * b('blue_median_dry'))))")\
            .rename(['cvi_median_dry']).toFloat()      
    
    return img.addBands(cviImgAY).addBands(cviImgAWet).addBands(cviImgADry)

# Green leaf index  GLI
def agregateBandsIndexGLI(img):    
    gliImgY = img.expression(
        "float((2 * b('green_median') - b('red_median') - b('blue_median')) / (2 * b('green_median') + b('red_median') + b('blue_median')))")\
            .rename(['gli_median']).toFloat()    

    gliImgWet = img.expression(
        "float((2 * b('green_median_wet') - b('red_median_wet') - b('blue_median_wet')) / (2 * b('green_median_wet') + b('red_median_wet') + b('blue_median_wet')))")\
            .rename(['gli_median_wet']).toFloat()   

    gliImgDry = img.expression(
        "float((2 * b('green_median_dry') - b('red_median_dry') - b('blue_median_dry')) / (2 * b('green_median_dry') + b('red_median_dry') + b('blue_median_dry')))")\
            .rename(['gli_median_dry']).toFloat()       
    
    return img.addBands(gliImgY).addBands(gliImgWet).addBands(gliImgDry)

# Shape Index  IF 
def agregateBandsIndexShapeI(img):    
    shapeImgAY = img.expression(
        "float((2 * b('red_median') - b('green_median') - b('blue_median')) / (b('green_median') - b('blue_median')))")\
            .rename(['shape_median']).toFloat()  

    shapeImgAWet = img.expression(
        "float((2 * b('red_median_wet') - b('green_median_wet') - b('blue_median_wet')) / (b('green_median_wet') - b('blue_median_wet')))")\
            .rename(['shape_median_wet']).toFloat() 

    shapeImgADry = img.expression(
        "float((2 * b('red_median_dry') - b('green_median_dry') - b('blue_median_dry')) / (b('green_median_dry') - b('blue_median_dry')))")\
            .rename(['shape_median_dry']).toFloat()      
    
    return img.addBands(shapeImgAY).addBands(shapeImgAWet).addBands(shapeImgADry)

# Aerosol Free Vegetation Index (2100 nm) 
def agregateBandsIndexAFVI(img):    
    afviImgAY = img.expression(
        "float((b('nir_median') - 0.5 * b('swir2_median')) / (b('nir_median') + 0.5 * b('swir2_median')))")\
            .rename(['afvi_median']).toFloat()  

    afviImgAWet = img.expression(
        "float((b('nir_median_wet') - 0.5 * b('swir2_median_wet')) / (b('nir_median_wet') + 0.5 * b('swir2_median_wet')))")\
            .rename(['afvi_median_wet']).toFloat()

    afviImgADry = img.expression(
        "float((b('nir_median_dry') - 0.5 * b('swir2_median_dry')) / (b('nir_median_dry') + 0.5 * b('swir2_median_dry')))")\
            .rename(['afvi_median_dry']).toFloat()      
    
    return img.addBands(afviImgAY).addBands(afviImgAWet).addBands(afviImgADry)

# Advanced Vegetation Index 
def agregateBandsIndexAVI(img):    
    aviImgAY = img.expression(
        "float((b('nir_median')* (1.0 - b('red_median')) * (b('nir_median') - b('red_median'))) ** 1/3)")\
            .rename(['avi_median']).toFloat()   

    aviImgAWet = img.expression(
        "float((b('nir_median_wet')* (1.0 - b('red_median_wet')) * (b('nir_median_wet') - b('red_median_wet'))) ** 1/3)")\
            .rename(['avi_median_wet']).toFloat()

    aviImgADry = img.expression(
        "float((b('nir_median_dry')* (1.0 - b('red_median_dry')) * (b('nir_median_dry') - b('red_median_dry'))) ** 1/3)")\
            .rename(['avi_median_dry']).toFloat()     
    
    return img.addBands(aviImgAY).addBands(aviImgAWet).addBands(aviImgADry)

#  NDDI Normalized Differenece Drought Index
def agregateBandsIndexNDDI(img):
    nddiImg = img.expression(
        "float((b('ndvi_median') - b('ndwi_median')) / (b('ndvi_median') + b('ndwi_median')))"
    ).rename(['nddi_median']).toFloat() 
    
    nddiImgWet = img.expression(
        "float((b('ndvi_median_wet') - b('ndwi_median_wet')) / (b('ndvi_median_wet') + b('ndwi_median_wet')))"
    ).rename(['nddi_median_wet']).toFloat()  
    
    nddiImgDry = img.expression(
        "float((b('ndvi_median_dry') - b('ndwi_median_dry')) / (b('ndvi_median_dry') + b('ndwi_median_dry')))"
    ).rename(['nddi_median_dry']).toFloat()  

    return img.addBands(nddiImg).addBands(nddiImgWet).addBands(nddiImgDry)


# Bare Soil Index 
def agregateBandsIndexBSI(img):    
    bsiImgY = img.expression(
        "float(((b('swir1_median') - b('red_median')) - (b('nir_median') + b('blue_median'))) / " + 
            "((b('swir1_median') + b('red_median')) + (b('nir_median') + b('blue_median'))))")\
            .rename(['bsi_median']).toFloat()  

    bsiImgWet = img.expression(
        "float(((b('swir1_median') - b('red_median')) - (b('nir_median') + b('blue_median'))) / " + 
            "((b('swir1_median') + b('red_median')) + (b('nir_median') + b('blue_median'))))")\
            .rename(['bsi_median']).toFloat()

    bsiImgDry = img.expression(
        "float(((b('swir1_median') - b('red_median')) - (b('nir_median') + b('blue_median'))) / " + 
            "((b('swir1_median') + b('red_median')) + (b('nir_median') + b('blue_median'))))")\
            .rename(['bsi_median']).toFloat()      
    
    return img.addBands(bsiImgY).addBands(bsiImgWet).addBands(bsiImgDry)

# BRBA	Band Ratio for Built-up Area  
def agregateBandsIndexBRBA(img):    
    brbaImgY = img.expression(
        "float(b('red_median') / b('swir1_median'))")\
            .rename(['brba_median']).toFloat()   

    brbaImgWet = img.expression(
        "float(b('red_median_wet') / b('swir1_median_wet'))")\
            .rename(['brba_median_wet']).toFloat()

    brbaImgDry = img.expression(
        "float(b('red_median_dry') / b('swir1_median_dry'))")\
            .rename(['brba_median_dry']).toFloat()     
    
    return img.addBands(brbaImgY).addBands(brbaImgWet).addBands(brbaImgDry)

# DSWI5	Disease-Water Stress Index 5
def agregateBandsIndexDSWI5(img):    
    dswi5ImgY = img.expression(
        "float((b('nir_median') + b('green_median')) / (b('swir1_median') + b('red_median')))")\
            .rename(['dswi5_median']).toFloat() 

    dswi5ImgWet = img.expression(
        "float((b('nir_median_wet') + b('green_median_wet')) / (b('swir1_median_wet') + b('red_median_wet')))")\
            .rename(['dswi5_median_wet']).toFloat() 

    dswi5ImgDry = img.expression(
        "float((b('nir_median_dry') + b('green_median_dry')) / (b('swir1_median_dry') + b('red_median_dry')))")\
            .rename(['dswi5_median_dry']).toFloat() 

    return img.addBands(dswi5ImgY).addBands(dswi5ImgWet).addBands(dswi5ImgDry)

# LSWI	Land Surface Water Index
def agregateBandsIndexLSWI(img):    
    lswiImgY = img.expression(
        "float((b('nir_median') - b('swir1_median')) / (b('nir_median') + b('swir1_median')))")\
            .rename(['lswi_median']).toFloat()  

    lswiImgWet = img.expression(
        "float((b('nir_median_wet') - b('swir1_median_wet')) / (b('nir_median_wet') + b('swir1_median_wet')))")\
            .rename(['lswi_median_wet']).toFloat()

    lswiImgDry = img.expression(
        "float((b('nir_median_dry') - b('swir1_median_dry')) / (b('nir_median_dry') + b('swir1_median_dry')))")\
            .rename(['lswi_median_dry']).toFloat()      
    
    return img.addBands(lswiImgY).addBands(lswiImgWet).addBands(lswiImgDry)

# MBI	Modified Bare Soil Index
def agregateBandsIndexMBI(img):    
    mbiImgY = img.expression(
        "float(((b('swir1_median') - b('swir2_median') - b('nir_median')) /" + 
            " (b('swir1_median') + b('swir2_median') + b('nir_median'))) + 0.5)")\
                .rename(['mbi_median']).toFloat() 

    mbiImgWet = img.expression(
        "float(((b('swir1_median_wet') - b('swir2_median_wet') - b('nir_median_wet')) /" + 
            " (b('swir1_median_wet') + b('swir2_median_wet') + b('nir_median_wet'))) + 0.5)")\
                .rename(['mbi_median_wet']).toFloat() 

    mbiImgDry = img.expression(
        "float(((b('swir1_median_dry') - b('swir2_median_dry') - b('nir_median_dry')) /" + 
            " (b('swir1_median_dry') + b('swir2_median_dry') + b('nir_median_dry'))) + 0.5)")\
                .rename(['mbi_median_dry']).toFloat()       
    
    return img.addBands(mbiImgY).addBands(mbiImgWet).addBands(mbiImgDry)

# UI	Urban Index	urban
def agregateBandsIndexUI(img):    
    uiImgY = img.expression(
        "float((b('swir2_median') - b('nir_median')) / (b('swir2_median') + b('nir_median')))")\
            .rename(['ui_median']).toFloat()  

    uiImgWet = img.expression(
        "float((b('swir2_median_wet') - b('nir_median_wet')) / (b('swir2_median_wet') + b('nir_median_wet')))")\
            .rename(['ui_median_wet']).toFloat() 

    uiImgDry = img.expression(
        "float((b('swir2_median_dry') - b('nir_median_dry')) / (b('swir2_median_dry') + b('nir_median_dry')))")\
            .rename(['ui_median_dry']).toFloat()       
    
    return img.addBands(uiImgY).addBands(uiImgWet).addBands(uiImgDry)

# OSAVI	Optimized Soil-Adjusted Vegetation Index
def agregateBandsIndexOSAVI(img):    
    osaviImgY = img.expression(
        "float(b('nir_median') - b('red_median')) / (0.16 + b('nir_median') + b('red_median'))")\
            .rename(['osavi_median']).toFloat() 

    osaviImgWet = img.expression(
        "float(b('nir_median_wet') - b('red_median_wet')) / (0.16 + b('nir_median_wet') + b('red_median_wet'))")\
            .rename(['osavi_median_wet']).toFloat() 

    osaviImgDry = img.expression(
        "float(b('nir_median_dry') - b('red_median_dry')) / (0.16 + b('nir_median_dry') + b('red_median_dry'))")\
            .rename(['osavi_median_dry']).toFloat()        
    
    return img.addBands(osaviImgY).addBands(osaviImgWet).addBands(osaviImgDry)

# Normalized Difference Red/Green Redness Index  RI
def agregateBandsIndexRI(img):        
    riImgY = img.expression(
        "float(b('nir_median') - b('green_median')) / (b('nir_median') + b('green_median'))")\
            .rename(['ri_median']).toFloat()   

    riImgWet = img.expression(
        "float(b('nir_median_wet') - b('green_median_wet')) / (b('nir_median_wet') + b('green_median_wet'))")\
            .rename(['ri_median_wet']).toFloat()

    riImgDry = img.expression(
        "float(b('nir_median_dry') - b('green_median_dry')) / (b('nir_median_dry') + b('green_median_dry'))")\
            .rename(['ri_median_dry']).toFloat()    
    
    return img.addBands(riImgY).addBands(riImgWet).addBands(riImgDry)    

# Tasselled Cap - brightness 
def agregateBandsIndexBrightness(img):    
    tasselledCapImgY = img.expression(
        "float(0.3037 * b('blue_median') + 0.2793 * b('green_median') + 0.4743 * b('red_median')  " + 
            "+ 0.5585 * b('nir_median') + 0.5082 * b('swir1_median') +  0.1863 * b('swir2_median'))")\
                .rename(['brightness_median']).toFloat()

    tasselledCapImgWet = img.expression(
        "float(0.3037 * b('blue_median_wet') + 0.2793 * b('green_median_wet') + 0.4743 * b('red_median_wet')  " + 
            "+ 0.5585 * b('nir_median_wet') + 0.5082 * b('swir1_median_wet') +  0.1863 * b('swir2_median_wet'))")\
                .rename(['brightness_median_wet']).toFloat()

    tasselledCapImgDry = img.expression(
        "float(0.3037 * b('blue_median_dry') + 0.2793 * b('green_median_dry') + 0.4743 * b('red_median_dry')  " + 
            "+ 0.5585 * b('nir_median_dry') + 0.5082 * b('swir1_median_dry') +  0.1863 * b('swir2_median_dry'))")\
                .rename(['brightness_median_dry']).toFloat() 
    
    return img.addBands(tasselledCapImgY).addBands(tasselledCapImgWet).addBands(tasselledCapImgDry)

# Tasselled Cap - wetness 
def agregateBandsIndexwetness(img): 

    tasselledCapImgY = img.expression(
        "float(0.1509 * b('blue_median') + 0.1973 * b('green_median') + 0.3279 * b('red_median')  " + 
            "+ 0.3406 * b('nir_median') + 0.7112 * b('swir1_median') +  0.4572 * b('swir2_median'))")\
                .rename(['wetness_median']).toFloat() 
    
    tasselledCapImgWet = img.expression(
        "float(0.1509 * b('blue_median_wet') + 0.1973 * b('green_median_wet') + 0.3279 * b('red_median_wet')  " + 
            "+ 0.3406 * b('nir_median_wet') + 0.7112 * b('swir1_median_wet') +  0.4572 * b('swir2_median_wet'))")\
                .rename(['wetness_median_wet']).toFloat() 
    
    tasselledCapImgDry = img.expression(
        "float(0.1509 * b('blue_median_dry') + 0.1973 * b('green_median_dry') + 0.3279 * b('red_median_dry')  " + 
            "+ 0.3406 * b('nir_median_dry') + 0.7112 * b('swir1_median_dry') +  0.4572 * b('swir2_median_dry'))")\
                .rename(['wetness_median_dry']).toFloat() 
    
    return img.addBands(tasselledCapImgY).addBands(tasselledCapImgWet).addBands(tasselledCapImgDry)

# Moisture Stress Index (MSI)
def agregateBandsIndexMSI(img):    
    msiImgY = img.expression(
        "float( b('nir_median') / b('swir1_median'))")\
            .rename(['msi_median']).toFloat() 
    
    msiImgWet = img.expression(
        "float( b('nir_median_wet') / b('swir1_median_wet'))")\
            .rename(['msi_median_wet']).toFloat() 

    msiImgDry = img.expression(
        "float( b('nir_median_dry') / b('swir1_median_dry'))")\
            .rename(['msi_median_dry']).toFloat() 
    
    return img.addBands(msiImgY).addBands(msiImgWet).addBands(msiImgDry)


def agregateBandsIndexGVMI(img):        
    gvmiImgY = img.expression(
                    "float ((b('nir_median')  + 0.1) - (b('swir1_median') + 0.02)) " + 
                        "/ ((b('nir_median') + 0.1) + (b('swir1_median') + 0.02))" 
                    ).rename(['gvmi_median']).toFloat()  

    gvmiImgWet = img.expression(
                    "float ((b('nir_median_wet')  + 0.1) - (b('swir1_median_wet') + 0.02)) " + 
                        "/ ((b('nir_median_wet') + 0.1) + (b('swir1_median_wet') + 0.02))" 
                    ).rename(['gvmi_median_wet']).toFloat()

    gvmiImgDry = img.expression(
                    "float ((b('nir_median_dry')  + 0.1) - (b('swir1_median_dry') + 0.02)) " + 
                        "/ ((b('nir_median_dry') + 0.1) + (b('swir1_median_dry') + 0.02))" 
                    ).rename(['gvmi_median_dry']).toFloat()   

    return img.addBands(gvmiImgY).addBands(gvmiImgWet).addBands(gvmiImgDry) 


def agregateBandsIndexsPRI(img):        
    priImgY = img.expression(
                            "float((b('green_median') - b('blue_median')) / (b('green_median') + b('blue_median')))"
                        ).rename(['pri_median'])   
    spriImgY =   priImgY.expression(
                            "float((b('pri_median') + 1) / 2)").rename(['spri_median']).toFloat()  

    priImgWet = img.expression(
                            "float((b('green_median_wet') - b('blue_median_wet')) / (b('green_median_wet') + b('blue_median_wet')))"
                        ).rename(['pri_median_wet'])   
    spriImgWet =   priImgWet.expression(
                            "float((b('pri_median_wet') + 1) / 2)").rename(['spri_median_wet']).toFloat()

    priImgDry = img.expression(
                            "float((b('green_median') - b('blue_median')) / (b('green_median') + b('blue_median')))"
                        ).rename(['pri_median'])   
    spriImgDry =   priImgDry.expression(
                            "float((b('pri_median') + 1) / 2)").rename(['spri_median']).toFloat()

    return img.addBands(spriImgY).addBands(spriImgWet).addBands(spriImgDry)


def agregateBandsIndexCO2Flux(img):        
    ndviImg = img.expression(
                        "float(b('nir_median') - b('swir2_median')) / (b('nir_median') + b('swir2_median'))"
                    ).rename(['ndvi']).toFloat() 
    
    priImg = img.expression(
                        "float((b('green_median') - b('blue_median')) / (b('green_median') + b('blue_median')))"
                    ).rename(['pri_median']).toFloat()   
    spriImg =   priImg.expression(
                            "float((b('pri_median') + 1) / 2)").rename(['spri_median']).toFloat()

    co2FluxImg = ndviImg.multiply(spriImg).rename(['co2flux_median'])   
    
    return img.addBands(co2FluxImg)


def agregateBandsTexturasGLCM(img):        
    # img = img.toInt()                
    textura2 = img.select('nir_median').multiply(10000).toUint16().glcmTexture(3)  
    contrastnir = textura2.select('nir_median_contrast').divide(10000).toFloat()
    textura2Dry = img.select('nir_median_dry').multiply(10000).toUint16().glcmTexture(3)  
    contrastnirDry = textura2Dry.select('nir_median_dry_contrast').divide(10000).toFloat()
    #
    textura2R = img.select('red_median').multiply(10000).toUint16().glcmTexture(3)  
    contrastred = textura2R.select('red_median_contrast').divide(10000).toFloat()
    textura2RDry = img.select('red_median_dry').multiply(10000).toUint16().glcmTexture(3)  
    contrastredDry = textura2RDry.select('red_median_dry_contrast').divide(10000).toFloat()

    return  img.addBands(contrastnir).addBands(contrastred
                    ).addBands(contrastnirDry).addBands(contrastredDry)    

def agregateBands_SMA_NDFIa(img):
    pass


#endregion

lst_bandExt = [
        'blue_min','blue_stdDev','green_min','green_stdDev','green_median_texture', 
        'red_min', 'red_stdDev','nir_min','nir_stdDev', 'swir1_min', 'swir1_stdDev', 
        'swir2_min', 'swir2_stdDev'
    ]

# add bands with slope and hilshade informations 
def addSlopeAndHilshade(img):
    # A digital elevation model.
    # NASADEM: NASA NASADEM Digital Elevation 30m
    dem = ee.Image('NASA/NASADEM_HGT/001').select('elevation')

    # Calculate slope. Units are degrees, range is [0,90).
    slope = ee.Terrain.slope(dem).divide(500).toFloat()

    # Use the ee.Terrain.products function to calculate slope, aspect, and
    # hillshade simultaneously. The output bands are appended to the input image.
    # Hillshade is calculated based on illumination azimuth=270, elevation=45.
    terrain = ee.Terrain.products(dem)
    hillshade = terrain.select('hillshade').divide(500).toFloat()

    return img.addBands(slope.rename('slope')).addBands(hillshade.rename('hillshade'))



def process_re_escalar_img (imgA):
    imgNormal = imgA.select(['slope'], ['slopeA']).divide(1500).toFloat()
    bandMos = copy.deepcopy(arqParams.featureBands)
    bandMos.remove('slope')
    imgEscalada = imgA.select(bandMos).divide(10000);

    return imgA.select(['slope']).addBands(imgEscalada.toFloat()).addBands(imgNormal)
    #return imgEscalada.toFloat().addBands(imgNormal)

def CalculateIndice(imagem):

    band_feat = [
            "ratio","rvi","ndwi","awei","iia","evi",
            "gcvi","gemi","cvi","gli","shape","afvi",
            "avi","bsi","brba","dswi5","lswi","mbi","ui",
            "osavi","ri","brightness","wetness","gvmi",
            "nir_contrast","red_contrast", 'nddi',"ndvi"
        ]
    # lstSuf = [bndInd + mypreFixo for bndInd in band_feat]
    # imagem em Int16 com valores inteiros ate 10000        
    # imageF = self.agregateBandsgetFractions(imagem)        
    # print(imageF.bandNames().getInfo())
    # imageW = copy.deepcopy(imagem.select(lstBandRed,lstBandsL))
    
    imageW = agregateBandsIndexEVI(imagem)  # "evi",    
    imageW = agregateBandsIndexNDVI(imageW) # "ndvi"
    imageW = agregateBandsIndexRATIO(imageW)  # "ratio" 
    imageW = agregateBandsIndexRVI(imageW)    # "rvi"
    imageW = agregateBandsIndexNDWI(imageW)   # "ndwi"
    imageW = AutomatedWaterExtractionIndex(imageW)  # "awei"     
    imageW = IndiceIndicadorAgua(imageW)    #  "iia"   
    imageW = agregateBandsIndexGCVI(imageW)   #  "gcvi" 
    imageW = agregateBandsIndexGEMI(imageW)  # "gemi"
    imageW = agregateBandsIndexCVI(imageW)  # "cvi"
    imageW = agregateBandsIndexGLI(imageW)  # "gli"
    imageW = agregateBandsIndexShapeI(imageW)  # "shape"
    imageW = agregateBandsIndexAFVI(imageW)  # "afvi"
    imageW = agregateBandsIndexAVI(imageW)   # "avi"
    imageW = agregateBandsIndexBSI(imageW)  # "bsi"
    imageW = agregateBandsIndexBRBA(imageW)  # "brba"
    imageW = agregateBandsIndexDSWI5(imageW)  # "dswi5"
    imageW = agregateBandsIndexLSWI(imageW) # "lswi"
    imageW = agregateBandsIndexMBI(imageW)  # "mbi"
    imageW = agregateBandsIndexUI(imageW)  # "ui"
    imageW = agregateBandsIndexRI(imageW)  # "ri"
    imageW = agregateBandsIndexOSAVI(imageW)  #  "osavi"   
    imageW = agregateBandsIndexwetness(imageW)   #  "wetness" 
    imageW = agregateBandsIndexBrightness(imageW)  #  "brightness"     
    imageW = agregateBandsTexturasGLCM(imageW)     # "nir_contrast","red_contrast"
    imageW = agregateBandsIndexGVMI(imageW)  # "gvmi"
    imageW = agregateBandsIndexNDDI(imageW) # 'nddi'
    imageW = addSlopeAndHilshade(imageW)

    return imageW



def make_mosaicofromReducer(colMosaic):
    band_year = [nband + '_median' for nband in param['bnd_L']]
    band_drys = [bnd + '_dry' for bnd in band_year]    
    band_wets = [bnd + '_wet' for bnd in band_year]
    # self.bandMosaic = band_year + band_wets + band_drys
    # print("bandas principais \n ==> ", self.bandMosaic)
    # bandsDry =None
    percentilelowDry = 5
    percentileDry = 35
    percentileWet = 65

    # get dry season collection
    evilowDry = (
        colMosaic.select(['evi'])
                .reduce(ee.Reducer.percentile([percentilelowDry]))
    )
    eviDry = (
        colMosaic.select(['evi'])
                .reduce(ee.Reducer.percentile([percentileDry]))
    )
    collectionDry = (
        colMosaic.map(lambda img: img.mask(img.select(['evi']).gte(evilowDry))
                                    .mask(img.select(['evi']).lte(eviDry)))
    )

    # get wet season collection
    eviWet = (
        colMosaic.select(['evi'])        
                .reduce(ee.Reducer.percentile([percentileWet]))
    )
    collectionWet = (
        colMosaic.map(lambda img: img.mask(img.select(['evi']).gte(eviWet)))                                        
    )

    # Reduce collection to median mosaic
    mosaic = (
        colMosaic.select(param['bnd_L'])
            .reduce(ee.Reducer.median()).rename(band_year)
    )

    # get dry median mosaic
    mosaicDry = (
        collectionDry.select(param['bnd_L'])
            .reduce(ee.Reducer.median()).rename(band_drys)
    )

    # get wet median mosaic
    mosaicWet = (
        collectionWet.select(param['bnd_L'])
            .reduce(ee.Reducer.median()).rename(band_wets)
    )

    # get stdDev mosaic
    mosaicStdDev = (
        colMosaic.select(param['bnd_L'])
                    .reduce(ee.Reducer.stdDev())
    )

    mosaic = (mosaic.addBands(mosaicDry)
                    .addBands(mosaicWet)
                    .addBands(mosaicStdDev)
    )

    return mosaic



def make_mosaicofromIntervalo(colMosaic, year_courrent):
    band_year = [nband + '_median' for nband in param['bnd_L']]
    band_drys = [bnd + '_dry' for bnd in band_year]    
    band_wets = [bnd + '_wet' for bnd in band_year]

    dictPer = {
        'year': {
            'start': str(str(year_courrent)) + '-01-01',
            'end': str(year_courrent) + '-12-31',
            'surf': 'year',
            'bnds': band_year
        },
        'dry': {
            'start': str(year_courrent) + '-08-01',
            'end': str(year_courrent) + '-12-31',
            'surf': 'dry',
            'bnds': band_drys
        },
        'wet': {
            'start': str(year_courrent) + '-01-01',
            'end': str(year_courrent) + '-07-31',
            'surf': 'wet',
            'bnds': band_wets
        }
    }       
    mosaico = None
    lstPeriodo = ['year', 'dry', 'wet']
    for periodo in lstPeriodo:
        dateStart =  dictPer[periodo]['start']
        dateEnd = dictPer[periodo]['end']
        bands_period = dictPer[periodo]['bnds']
        # get dry median mosaic
        mosaictmp = (
            colMosaic.select(param['bnd_L'])
                .filter(ee.Filter.date(dateStart, dateEnd))
                .max()
                .rename(bands_period)
        )
        if periodo == 'year':
            mosaico = copy.deepcopy(mosaictmp)
        else:
            mosaico = mosaico.addBands(mosaictmp)

    return mosaico


def calculate_indices_x_blocos(imageCol):

    bnd_L = ['blue','green','red','nir','swir1','swir2']        
    # band_year = [bnd + '_median' for bnd in self.option['bnd_L']]
    band_year = [
            'blue_median','green_median','red_median',
            'nir_median','swir1_median','swir2_median'
        ]
    band_drys = [bnd + '_median_dry' for bnd in bnd_L]    
    band_wets = [bnd + '_median_wet' for bnd in bnd_L]
    band_std = [bnd + '_stdDev'for bnd in bnd_L]
    # band_features = [
    #             "ratio","rvi","ndwi","awei","iia",
    #             "gcvi","gemi","cvi","gli","shape","afvi",
    #             "avi","bsi","brba","dswi5","lswi","mbi","ui",
    #             "osavi","ri","brightness","wetness",
    #             "nir_contrast","red_contrast"
    # ] # , "ndfia"
    # band_features.extend(self.option['bnd_L'])        
    
    # image_year = imageCol.select(band_year)
    img_recMosaico = imageCol.map(lambda img: calculateBandsIndexEVI(img))
    mosaicoBuilded = make_mosaicofromReducer(img_recMosaico)
    # print("mosaicoBuilded   ", mosaicoBuilded.bandNames().getInfo())
    image_year = CalculateIndice(mosaicoBuilded)    
    # print("  imagem bandas index    ")    
    # print("  ", image_year.bandNames().getInfo())

    # sys.exit()

    return image_year

#endregion
#============================================================


mosaico = 'mosaico_mapbiomas'
param = {    
    'bioma': "CAATINGA", #nome do bioma setado nos metadados
    'biomas': ["CAATINGA","CERRADO", "MATAATLANTICA"],
    'asset_bacias': "projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga49div",
    'asset_bacias_buffer' : 'projects/ee-solkancengine17/assets/shape/bacias_buffer_caatinga_49_regions',
    # 'asset_bacias_buffer42' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',
    'asset_IBGE': 'users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas',
    'assetOutMB': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/Classify_fromMMBV2',
    'assetOut': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/ClassifyV2',
    # 'assetROIgrade': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_merged_Indall'},   
    # 'asset_joinsGrBa': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_cleaned_downsamplesv4C',
    'asset_joinsGrBa': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_cleaned_DS_v4CC',
    'asset_joinsGrBaMB': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_cleaned_MB_V4C',
    'outAssetROIs': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/roisJoinedBaGrNN', 
    'classMapB': [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45],
    'classNew': [3, 4, 3, 3,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33, 21,33,33,21,21,21,21,21,21,21],
    'asset_mosaic': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',
    'asset_collectionId': 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    'bnd_L': ['blue','green','red','nir','swir1','swir2'],
    'version': 4,
    'yearInicial': 1985,
    'yearFinal': 2024,
    'sufix': "_01",    
    'lsBandasMap': [],
    'numeroTask': 6,
    'numeroLimit': 50,
    'conta' : {
        '0': 'caatinga01',   # 
        '5': 'caatinga02',
        '10': 'caatinga03',
        '15': 'caatinga04',
        '20': 'caatinga05',        
        '25': 'solkan1201',    
        '30': 'solkanGeodatin',
        '35': 'diegoUEFS',
        '40': 'superconta'   
    },
    'pmtRF': {
        'numberOfTrees': 165, 
        'variablesPerSplit': 15,
        'minLeafPopulation': 40,
        'bagFraction': 0.8,
        'seed': 0
    },
    # https://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting
    'pmtGTB': {
        'numberOfTrees': 25, 
        'shrinkage': 0.1,         
        'samplingRate': 0.8, 
        'loss': "LeastSquares",#'Huber',#'LeastAbsoluteDeviation', 
        'seed': 0
    },
    'dict_classChangeBa': arqParams.dictClassRepre
}
# print(param.keys())
print("vai exportar em ", param['assetOut'])

#============================================================
#========================METODOS=============================
#============================================================

def gerenciador(cont):
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
    numberofChange = [kk for kk in param['conta'].keys()]    
    print(numberofChange)
    
    if str(cont) in numberofChange:
        print(f"inicialize in account #{cont} <> {param['conta'][str(cont)]}")
        switch_user(param['conta'][str(cont)])
        projAccount = get_project_from_account(param['conta'][str(cont)])
        try:
            ee.Initialize(project= projAccount) # project='ee-cartassol'
            print('The Earth Engine package initialized successfully!')
        except ee.EEException as e:
            print('The Earth Engine package failed to initialize!') 
        
        # relatorios.write("Conta de: " + param['conta'][str(cont)] + '\n')

        tarefas = tasks(
            n= param['numeroTask'],
            return_list= True)
        
        for lin in tarefas:   
            print(str(lin))         
            # relatorios.write(str(lin) + '\n')
    
    elif cont > param['numeroLimit']:
        return 0
    cont += 1    
    return cont

#exporta a FeatCollection Samples classificada para o asset
# salva ftcol para um assetindexIni
def save_ROIs_toAsset(collection, name):

    optExp = {
        'collection': collection,
        'description': name,
        'assetId': param['outAssetROIs'] + "/" + name
    }

    task = ee.batch.Export.table.toAsset(**optExp)
    task.start()
    print("exportando ROIs da bacia $s ...!", name)

    
#exporta a imagem classificada para o asset
def processoExportar(mapaRF, regionB, nameB, proc_mosaicEE):
    nomeDesc = 'BACIA_'+ str(nameB)
    idasset =  os.path.join(param['assetOut'] , nomeDesc)
    if not proc_mosaicEE:
        idasset = param['assetOutMB']
    optExp = {
        'image': mapaRF, 
        'description': nomeDesc, 
        'assetId':idasset, 
        'region':regionB.getInfo(), #['coordinates']
        'scale': 30, 
        'maxPixels': 1e13,
        "pyramidingPolicy":{".default": "mode"},
        # 'priority': 1000
    }
    task = ee.batch.Export.image.toAsset(**optExp)
    task.start() 
    print("salvando ... " + nomeDesc + "..!")
    # print(task.status())
    for keys, vals in dict(task.status()).items():
        print ( "  {} : {}".format(keys, vals))



def check_dir(file_name):
    if not os.path.exists(file_name):
        arq = open(file_name, 'w+')
        arq.close()

def getPathCSV (nfolder):
    # get dir path of script 
    mpath = os.getcwd()
    # get dir folder before to path scripts 
    pathparent = str(Path(mpath).parents[0])
    # folder of CSVs ROIs
    roisPath = '/dados/' + nfolder
    mpath = pathparent + roisPath
    print("path of CSVs Rois is \n ==>",  mpath)
    return mpath


tesauroBasin = arqParams.tesauroBasin
lstSat = ["l5","l7","l8"]
pathJson = getPathCSV("regJSON/")

def get_bands_mosaicos ():
    band_year = [nband + '_median' for nband in param['bnd_L']]
    band_drys = [bnd + '_dry' for bnd in band_year]    
    band_wets = [bnd + '_wet' for bnd in band_year]
    # retornando as 3 listas em 1 só
    return band_year + band_wets + band_drys

print("==================================================")
# process_normalized_img
# imagens_mosaic = imagens_mosaico.map(lambda img: process_re_escalar_img(img))          
# ftcol_baciasbuffer = ee.FeatureCollection(param['asset_bacias_buffer'])
# print(imagens_mosaic.first().bandNames().getInfo())
#nome das bacias que fazem parte do bioma7619
# nameBacias = arqParams.listaNameBacias
# print("carregando {} bacias hidrograficas ".format(len(nameBacias)))
# sys.exit()
#lista de anos
listYears = [k for k in range(param['yearInicial'], param['yearFinal'] + 1)]
print(f'lista de bandas anos entre {param['yearInicial']} e {param['yearFinal']}')
param['lsBandasMap'] = ['classification_' + str(kk) for kk in listYears]
print(param['lsBandasMap'])

# @mosaicos: ImageCollection com os mosaicos de Mapbiomas 
bandNames = ['awei_median_dry', 'blue_stdDev', 'brightness_median', 'cvi_median_dry',]
# a_file = open(pathJson + "filt_lst_features_selected_spIndC9.json", "r")
# dictFeatureImp = json.load(a_file)
# print("dict Features ",dictFeatureImp.keys())
pathHiperpmtros = os.path.join(pathparent, 'dados', 'dictBetterModelpmtCol10v1.json')
b_file = open(pathHiperpmtros, 'r')
dictHiperPmtTuning = json.load(b_file)
pathFSJson = getPathCSV("FS_col10_json/")
print("==== path of CSVs of Features Selections ==== \n >>> ", pathFSJson)
lstBandMB = get_bands_mosaicos()
print("bandas mapbiomas ", lstBandMB)


# sys.exit()
def iterandoXBacias( _nbacia, myModel, makeProb, process_mosaic_EE):
    exportatROIS = False
    fazerSimples = True
    # selectBacia = ftcol_bacias.filter(ee.Filter.eq('nunivotto3', _nbacia)).first()
    # https://code.earthengine.google.com/2f8ea5070d3f081a52afbcfb7a7f9d25 

    baciabuffer = ee.FeatureCollection(param['asset_bacias_buffer']).filter(
                        ee.Filter.eq('nunivotto4', _nbacia))
    print(f"know about the geometry 'nunivotto4' >>  {_nbacia
                    } loaded < {baciabuffer.size().getInfo()} > geometry" )  
    bacia_raster =  baciabuffer.reduceToImage(['id_codigo'], ee.Reducer.first()).gt(0)  
    baciabuffer = baciabuffer.geometry()

    # https://code.earthengine.google.com/48effe10e1fffbedf2076a53b472be0e?asset=projects%2Fgeo-data-s%2Fassets%2Ffotovoltaica%2Fversion_4%2Freg_00000000000000000017_2015_10_pred_g2c
    imagens_mosaicoEE = (
        ee.ImageCollection(param['asset_collectionId'])
                .filterBounds(baciabuffer)
                .select(param['bnd_L'])
    )
    imagens_mosaico = (ee.ImageCollection(param['asset_mosaic'])
                            .filter(ee.Filter.inList('biome', param['biomas']))
                            .filter(ee.Filter.inList('satellite', lstSat))
                            .filterBounds(baciabuffer)
                            .select(lstBandMB)
                )

    # lsNamesBaciasViz = arqParams.basinVizinhasNew[_nbacia]
    # print("lista de Bacias vizinhas", lsNamesBaciasViz)
    # lsNamesBaciasVizConv = [tesauroBasin[kk] for kk in lsNamesBaciasViz]
    # lstSoViz = [kk for kk in lsNamesBaciasViz if kk != _nbacia]
    # print("lista de bacias ", lstSoViz)
    # lstSoVizConv = [tesauroBasin[kk] for kk in lstSoViz]
    # print("Lista de bacias convertidas ", lstSoVizConv) 
    # lstSoVizConv = reduce_duplicidade(lstSoVizConv)

    # lista de classe por bacia 
    lstClassesUn = param['dict_classChangeBa'][tesauroBasin[_nbacia]]
    print(f" ==== lista de classes ness bacia na bacia < {_nbacia} >  ====")
    print(f" ==== {lstClassesUn} ======" )
    print("---------------------------------------------------------------")
    # sys.exit()
    imglsClasxanos = ee.Image().byte()

    mydict = None
    pmtroClass = copy.deepcopy(param['pmtGTB'])
    # print("area ", baciabuffer.area(0.1).getInfo())

    path_ptrosFS = os.path.join(pathFSJson, f"feat_sel_{_nbacia}.json")
    print("load features json ", path_ptrosFS)
    # Open the JSON file for reading
    with open(path_ptrosFS, 'r') as file:
        # Load the JSON data
        bandas_fromFS = json.load(file)

    print(f"lista de Bacias Anos no dict de FS  {len(bandas_fromFS.keys())} years  " )
    print(' as primeiras 3 \n ==> ', list(bandas_fromFS.keys())[:3])
    # bandas_fromFS = bandas_fromFS[:45]
    # bandas_imports = []
    # sys.exit()
    for cc, nyear in enumerate(listYears[:]):        
        #se o nyear for 2018 utilizamos os dados de 2017 para fazer a classificacao
        bandActiva = 'classification_' + str(nyear)        
        print( "banda activa: " + bandActiva) 

        # nameFeatROIs = 'rois_grade_' + _nbacia
        nameFeatROIs =  f"{_nbacia}_{nyear}_cd"  
        print("loading Rois JOINS = ", nameFeatROIs)
        asset_rois = param['asset_joinsGrBa']
        if not process_mosaic_EE:
            asset_rois = param['asset_joinsGrBaMB']

        
        # bandas_ROIs = [kk for kk in ROIs_toTrain.first().propertyNames().getInfo()]  
        # print("distribuição de pontos ", ROIs_toTrain.aggregate_histogram('class').getInfo())        
        

        # cria o mosaico a partir do mosaico total, cortando pelo poligono da bacia 
        date_inic = ee.Date.fromYMD(int(nyear),1,1)      
        date_end = ee.Date.fromYMD(int(nyear),12,31)   
        if process_mosaic_EE:
            # de mosaico EE y para mosaico Mapbiomas (X)
            lstCoef = [0.8425, 0.8957, 0.9097, 0.3188, 0.969, 0.9578]
            bandsCoef = ee.Image.constant(lstCoef + lstCoef + lstCoef)
            lstIntercept = [106.7546, 115.1553, 239.0688, 1496.4408, 392.3453, 366.57]
            bandsIntercept = ee.Image.constant(lstIntercept + lstIntercept + lstIntercept)

            colmosaicMapbiomas = imagens_mosaico.filter(ee.Filter.eq('year', nyear)).median()
            imagens_mosaicoEEv = colmosaicMapbiomas.multiply(bandsCoef).add(bandsIntercept) 
            imagens_mosaicEEv = imagens_mosaicoEEv.divide(10000)#.rename(param.bnd_L)
            # print(f" we have {imagens_mosaicoEEv.bandNames().getInfo()} images ")
        
            #cria o mosaico a partir do mosaico total, cortando pelo poligono da bacia    
            mosaicColGoogle = imagens_mosaicoEE.filter(ee.Filter.date(date_inic, date_end))        
            mosaicoBuilded = make_mosaicofromIntervalo(mosaicColGoogle, nyear) 
            # print(f" we have {mosaicoBuilded.bandNames().getInfo()} images ")
            maskGaps = mosaicoBuilded.unmask(-1000).eq(-1000)
            ## preenchendo o gap do mosaico do EE pelo mosaico dao mapbiomas
            mosaicoBuilded = mosaicoBuilded.unmask(0).where(maskGaps, imagens_mosaicEEv)
            # print(f" we have {mosaicoBuilded.bandNames().getInfo()} images ")
        else:

            # de mosaico Mapbiomas para mosaico EE (X)
            lstCoef = [6499.0873, 8320.9741, 7243.8252, 5944.0973, 7494.4502, 7075.1618]
            bandsCoef = ee.Image.constant(lstCoef + lstCoef + lstCoef)
            lstIntercept = [64.0821, 55.127, 36.7782, 1417.7931, 325.8045, 141.9352]
            bandsIntercept = ee.Image.constant(lstIntercept + lstIntercept + lstIntercept)             

            #cria o mosaico a partir do mosaico total, cortando pelo poligono da bacia    
            mosaicColGoogle = imagens_mosaicoEE.filter(ee.Filter.date(date_inic, date_end))        
            mosaicoGoogle = make_mosaicofromIntervalo(mosaicColGoogle, nyear) 
            imagens_mosaicoEEv = mosaicoGoogle.multiply(bandsCoef).add(bandsIntercept)
            
            colmosaicMapbiomas = imagens_mosaico.filter(ee.Filter.eq('year', nyear)).median()
            maskGaps = colmosaicMapbiomas.unmask(-1000).eq(-1000)
            ## preenchendo o gap do mosaico do EE pelo mosaico dao mapbiomas
            ## preenchendo o gap do mosaico do EE pelo mosaico dao mapbiomas
            mosaicoBuilded = colmosaicMapbiomas.unmask(0).where(maskGaps, imagens_mosaicoEEv)
            # print(f" we have {mosaicoBuilded.bandNames().getInfo()} images ")

        # lstBandasBuildMoisac = mosaicProcess.bandNames().getInfo()
        # print(f" we have {len(lstBandasBuildMoisac)} bands builded in the mosaic ")

        #cria o classificador com as especificacoes definidas acima 
        limitlsb = 15
        # print( bandas_fromFS[f"{_nbacia}_{nyear}"])
        
        lstbandas_import = bandas_fromFS[f"{_nbacia}_{nyear}"]['features']
        bandas_imports = [bnd for bnd in lstbandas_import if 'stdDev' not in bnd]
        if 'solpe' in bandas_imports:
            bandas_imports.remove('solpe')
        bandas_imports = bandas_imports[:limitlsb]
        if 'slope' not in bandas_imports:
            bandas_imports += ['slope']
        if 'hillshade' not in bandas_imports:
            bandas_imports += ['hillshade']
        print(f" numero de bandas selecionadas {len(bandas_imports)} ")  


        print("----- calculado todos os 102 indices ---------------------")
        mosaicProcess = CalculateIndice(mosaicoBuilded.updateMask(bacia_raster))
        mosaicProcess = mosaicProcess.select(bandas_imports)
        print(f" we have {mosaicProcess.bandNames().getInfo()} images ")


        ROIs_toTrain = (
            ee.FeatureCollection( os.path.join(asset_rois, nameFeatROIs)) 
                        # .filter(ee.Filter.eq("year", nyear))  
                        .filter(ee.Filter.inList('class', lstClassesUn))  
                        .select(bandas_imports + ['class'])
        )       
        # excluindo a classe 12
        if '745' == tesauroBasin[_nbacia]:
            ROIs_toTrain = ROIs_toTrain.filter(ee.Filter.neq('class', 12))           
        # sys.exit()

        ### --------------------------------------------------------###
        ### ---- limpando a lista de bandas importantes  -----------###
        # lstSearch = []
        # for nbandsM in bandas_imports:
        #     if nbandsM not in lstBandasBuildROIs:
        #         lstSearch.append(nbandsM)
        #         bandas_imports.remove(nbandsM)
        # print("bandas em importancias que não estão nos ROIs \n ", lstSearch)

        # lstSearch = []
        # for nbandsM in bandas_imports:
        #     if nbandsM not in lstBandasBuildMoisac:
        #         lstSearch.append(nbandsM)
        #         bandas_imports.remove(nbandsM)
        # print("bandas em importancias que não estão no mosaico \n ", lstSearch)        
        # sys.exit()

        print("parameter loading ", dictHiperPmtTuning[_nbacia])
        # gradeExpMemo = ['763','7438','7443','7721','7613','7616','7615','771','7625']
        gradeExpMemo = [
            '7625', '7616', '7613', '7618', '7617', '761112', '7741', 
            '7615', '7721', '7619', '7443', '763', '746'
        ]
        if _nbacia in gradeExpMemo:
            pmtroClass['numberOfTrees'] = 18
            pmtroClass['shrinkage'] = 0.1    # 
        else:            
            pmtroClass['shrinkage'] = dictHiperPmtTuning[_nbacia]['learning_rate']
            lstBacias_prob = [ '7541', '7544', '7584', '7592', '7612', '7615',  '7712', '7721', '7741', '7746']
            if _nbacia in lstBacias_prob:
                numberTrees = 5
                if dictHiperPmtTuning[_nbacia]["n_estimators"] < numberTrees:
                    pmtroClass['numberOfTrees'] = dictHiperPmtTuning[_nbacia]["n_estimators"] - 3
                else:
                    pmtroClass['numberOfTrees'] = numberTrees       

        print("pmtros Classifier ==> ", pmtroClass)

        # ee.Classifier.smileGradientTreeBoost(numberOfTrees, shrinkage, samplingRate, maxNodes, loss, seed)
        classifierGTB = ee.Classifier.smileGradientTreeBoost(**pmtroClass).train(
                                            ROIs_toTrain, 'class', bandas_imports)              
        classifiedGTB = mosaicProcess.classify(classifierGTB, bandActiva)        
        # print("classificando!!!! ")

        #se for o primeiro ano cria o dicionario e seta a variavel como
        #o resultado da primeira imagem classificada
        print("addicionando classification bands = " , bandActiva)            
        if param['yearInicial'] == nyear:
            print ('entrou em 1985, no modelo ', myModel)            
            print("===> ", myModel)    
            imglsClasxanos = copy.deepcopy(classifiedGTB)                                        
            nomec = _nbacia + '_' + 'GTB_col10-v' + str(param['version'])            
            mydict = {
                'id_bacia': _nbacia,
                'version': param['version'],
                'biome': param['bioma'],
                'classifier': myModel,
                'collection': '10.0',
                'sensor': 'Landsat',
                'source': 'geodatin',                
            }
            imglsClasxanos = imglsClasxanos.set(mydict)
        #se nao, adiciona a imagem como uma banda a imagem que ja existia
        else:
            # print("Adicionando o mapa do ano  ", nyear)
            # print(" ", classifiedGTB.bandNames().getInfo())     
            imglsClasxanos = imglsClasxanos.addBands(classifiedGTB)  
                                    
        
  
    imglsClasxanos = imglsClasxanos.select(param['lsBandasMap'])    
    imglsClasxanos = imglsClasxanos.set("system:footprint", baciabuffer.coordinates())
    # exporta bacia
    processoExportar(imglsClasxanos, baciabuffer.coordinates(), nomec, process_mosaic_EE)         
         
        
    # sys.exit()


## Revisando todos as Bacias que foram feitas 
registros_proc = "registros/lsBaciasClassifyfeitasv_1.txt"
pathFolder = os.getcwd()
path_MGRS = os.path.join(pathFolder, registros_proc)
baciasFeitas = []
check_dir(path_MGRS)

arqFeitos = open(path_MGRS, 'r')
for ii in arqFeitos.readlines():    
    ii = ii[:-1]
    # print(" => " + str(ii))
    baciasFeitas.append(ii)

arqFeitos.close()
arqFeitos = open(path_MGRS, 'a+')

# mpath_bndImp = pathFolder + '/dados/regJSON/'
# filesJSON = glob.glob(pathJson + '*.json')
# print("  files json ", filesJSON)param
# nameDictGradeBacia = ''
# sys.exit()

# 100 arvores
# nameBacias = ['7619']
# lista de 49 bacias 
nameBacias = [
    '7754', '7691', '7581', '7625', '7584', '751', '7614', 
    '752', '7616', '745', '7424', '773', '7612', '7613', 
    '7618', '7561', '755', '7617', '7564', '761111','761112', 
    '7741', '7422', '76116', '7761', '7671', '7615', '7411', 
    '7764', '757', '771', '7712', '766', '7746', '753', '764', 
    '7541', '7721', '772', '7619', '7443', '765', '7544', '7438', 
    '763', '7591', '7592', '7622', '746'
]
print(f"we have {len(nameBacias)} bacias")
# "761112",procMosaicEE
modelo = "GTB"
knowMapSaved = False
procMosaicEE = True
listBacFalta = [
    '7584', '7616', '7612', '7618', '7561', '755', '7617', '7564', '7741', '76116', '7615', '757', '7712', '7746', '7541', '7619', '7544', '763', '7592'
]
# listBacFalta = []
lst_bacias_proc = [item for item in nameBacias if item in listBacFalta]
# bacias_prioritarias = [
#     '7411',  '746', '7541', '7544', '7591', '7592', '761111', '761112', '7612', '7613', '7614', 
#     '7615', '771', '7712', '772', '7721', '773', '7741', '7746', '7754', '7761', '7764'
# ]

bacias_prioritarias = [
    '7541', '7544', '7592', '7612', '7615',  '7712', '7721', '7741', '7746'
]
print(lst_bacias_proc)
cont = 15
cont = gerenciador(cont)
# sys.exit(0)
for _nbacia in bacias_prioritarias[1:]:
    if knowMapSaved:
        try:
            nameMap = 'BACIA_' + _nbacia + '_' + 'GTB_col10-v' + str(param['version'])
            imgtmp = ee.Image(os.path.join(param['assetOut'], nameMap))
            print(" 🚨 loading ", nameMap, " ", len(imgtmp.bandNames().getInfo()), " bandas 🚨")
        except:
            listBacFalta.append(_nbacia)
    else:        
        print("-------------------.kmkl---------------------------------------------")
        print(f"--------    classificando bacia nova {_nbacia} and seus properties da antinga {tesauroBasin[_nbacia]}-----------------")   
        print("---------------------------------------------------------------------") 
        iterandoXBacias(_nbacia, modelo, False, procMosaicEE) 
        arqFeitos.write(_nbacia + '\n')
        # cont = gerenciador(cont) 

    # sys.exit()
arqFeitos.close()


if knowMapSaved:
    print("lista de bacias que faltam \n ",listBacFalta)
    print("total ", len(listBacFalta))