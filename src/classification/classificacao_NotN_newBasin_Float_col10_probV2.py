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
        
    eviImgY = img.expression(
        "float(2.4 * (b('nir_median') - b('red_median')) / (1 + b('nir_median') + b('red_median')))")\
            .rename(['evi_median']).toFloat() 

    eviImgWet = img.expression(
        "float(2.4 * (b('nir_median_wet') - b('red_median_wet')) / (1 + b('nir_median_wet') + b('red_median_wet')))")\
            .rename(['evi_median_wet']).toFloat()   

    eviImgDry = img.expression(
        "float(2.4 * (b('nir_median_dry') - b('red_median_dry')) / (1 + b('nir_median_dry') + b('red_median_dry')))")\
            .rename(['evi_median_dry']).toFloat()   
    
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



param = {    
    'bioma': "CAATINGA", #nome do bioma setado nos metadados
    'biomas': ["CAATINGA","CERRADO", "MATAATLANTICA"],
    'asset_bacias': "projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga49div",
    'asset_bacias_buffer' : 'projects/ee-solkancengine17/assets/shape/bacias_buffer_caatinga_49_regions',
    # 'asset_bacias_buffer42' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',
    'asset_IBGE': 'users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas',
    # 'assetOut': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVY/',
    'assetOut': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/ClassifyVA',
    'assetROIgrade': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_merged_Indall'},   
    'asset_joinsGrBa': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_merged_Indall',
    'outAssetROIs': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/roisJoinedBaGrNN', 
    'classMapB': [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45],
    'classNew': [3, 4, 3, 3,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33, 21,33,33,21,21,21,21,21,21,21],
    'asset_mosaic': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',
    'asset_collectionId': 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    'bnd_L': ['blue','green','red','nir','swir1','swir2'],
    'version': 3,
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
    'pmtSVM' : {
        'decisionProcedure' : 'Margin', 
        'kernelType' : 'RBF', 
        'shrinking' : True, 
        'gamma' : 0.001
    },
    'dict_classChangeBa': arqParams.dictClassRepre

}
# print(param.keys())
print("vai exportar em ", param['assetOut'])
# print(param['conta'].keys())
bandNames = [
    "swir1_stdDev_1","nir_stdDev_1","green_stdDev_1","ratio_median_dry","gli_median_wet","dswi5_median_dry",
    "ri_median","osavi_median","swir2_min","shape_median","mbi_median_dry","wetness_median_dry","green_median_texture_1",
    "iia_median_wet","slopeA_1","brba_median_dry","nir_median","lswi_median_wet","red_min","rvi_median","green_min",
    "gcvi_median_dry","shape_median_dry","cvi_median_dry","blue_median_dry","mbi_median","nir_median_dry_contrast",
    "swir2_median_wet","ui_median_wet","red_median_wet","avi_median","nir_stdDev","swir1_stdDev","red_median_dry",
    "gemi_median","osavi_median_dry","blue_median_dry_1","swir2_median_dry_1","brba_median","ratio_median",
    "gli_median_dry","blue_min_1","wetness_median","green_median_wet","blue_median_wet_1","brightness_median_wet",
    "blue_min","blue_median","red_median_contrast","swir1_min_1","evi_median","blue_stdDev_1","lswi_median_dry",
    "blue_median_wet","cvi_median","red_stdDev_1","shape_median_wet","red_median_dry_1","swir2_median_wet_1",
    "dswi5_median_wet","red_median_wet_1","afvi_median","ndwi_median","avi_median_wet","gli_median","evi_median_wet",
    "nir_median_dry","gvmi_median","cvi_median_wet","swir2_min_1","iia_median","ndwi_median_dry","green_min_1",
    "ri_median_dry","osavi_median_wet","green_median_dry","ui_median_dry","red_stdDev","nir_median_wet_1",
    "swir1_median_dry_1","red_median_1","nir_median_dry_1","swir1_median_wet","blue_stdDev","bsi_median",
    "swir1_median","swir2_median","gvmi_median_dry","red_median","gemi_median_wet","lswi_median",
    "brightness_median_dry","awei_median_wet","nir_min","afvi_median_wet","nir_median_wet","evi_median_dry",
    "swir2_median_1","ndwi_median_wet","ratio_median_wet","swir2_stdDev","gcvi_median","ui_median","rvi_median_wet",
    "green_median_wet_1","ri_median_wet","nir_min_1","rvi_median_1","swir1_median_dry","blue_median_1","green_median_1",
    "avi_median_dry","gvmi_median_wet","wetness_median_wet","swir1_median_1","dswi5_median","swir2_stdDev_1",
    "awei_median","red_min_1","mbi_median_wet","brba_median_wet","green_stdDev","green_median_texture","swir1_min",
    "awei_median_dry","swir1_median_wet_1","gemi_median_dry","nir_median_1","red_median_dry_contrast","bsi_median_1",
    "bsi_median_2","nir_median_contrast","green_median_dry_1","afvi_median_dry","gcvi_median_wet","iia_median_dry",
    "brightness_median","green_median","swir2_median_dry"
]

bandasComuns = [
    'slope', 'blue_median', 'blue_median_wet', 'blue_median_dry', 'blue_min', 'blue_stdDev', 'green_median', 
    'green_median_wet', 'green_median_dry', 'green_min', 'green_stdDev', 'green_median_texture', 'red_median', 
    'red_median_wet', 'red_median_dry', 'red_min', 'red_stdDev', 'nir_median', 'nir_median_wet', 'nir_median_dry', 
    'nir_min', 'nir_stdDev', 'swir1_median', 'swir1_median_wet', 'swir1_median_dry', 'swir1_min', 'swir1_stdDev', 
    'swir2_median', 'swir2_median_wet', 'swir2_median_dry', 'swir2_min', 'swir2_stdDev', 'slopeA', 'ratio_median', 
    'rvi_median', 'ndwi_median', 'awei_median', 'iia_median', 'gcvi_median', 'gemi_median', 'cvi_median', 'gli_median', 
    'shape_median', 'afvi_median', 'avi_median', 'bsi_median', 'brba_median', 'dswi5_median', 'lswi_median', 'mbi_median', 
    'ui_median', 'osavi_median', 'ri_median', 'brightness_median', 'wetness_median', 'nir_contrast_median', 
    'red_contrast_median', 'ratio_median_dry', 'rvi_median_dry', 'ndwi_median_dry', 'awei_median_dry', 'iia_median_dry', 
    'gcvi_median_dry', 'gemi_median_dry', 'cvi_median_dry', 'gli_median_dry', 'shape_median_dry', 'afvi_median_dry', 
    'avi_median_dry', 'bsi_median_dry', 'brba_median_dry', 'dswi5_median_dry', 'lswi_median_dry', 'mbi_median_dry', 
    'ui_median_dry', 'osavi_median_dry', 'ri_median_dry', 'brightness_median_dry', 'wetness_median_dry', 
    'nir_contrast_median_dry', 'red_contrast_median_dry', 'ratio_median_wet', 'rvi_median_wet', 
    'ndwi_median_wet', 'awei_median_wet', 'iia_median_wet', 'gcvi_median_wet', 'gemi_median_wet', 
    'cvi_median_wet', 'gli_median_wet', 'shape_median_wet', 'afvi_median_wet', 'avi_median_wet', 
    'bsi_median_wet', 'brba_median_wet', 'dswi5_median_wet', 'lswi_median_wet', 'mbi_median_wet', 
    'ui_median_wet', 'osavi_median_wet', 'ri_median_wet', 'brightness_median_wet', 'wetness_median_wet', 
    'nir_contrast_median_wet', 'red_contrast_median_wet'
]
bandasComunsCorr = [
    'slope', 'blue_median_1', 'blue_median_wet_1', 'blue_median_dry_1', 'blue_min_1', 'blue_stdDev_1', 'green_median_1', 
    'green_median_wet_1', 'green_median_dry_1', 'green_min_1', 'green_stdDev_1', 'green_median_texture_1', 'red_median_1', 
    'red_median_wet_1', 'red_median_dry_1', 'red_min_1', 'red_stdDev_1', 'nir_median_1', 'nir_median_wet_1', 'nir_median_dry_1', 
    'nir_min_1', 'nir_stdDev_1', 'swir1_median_1', 'swir1_median_wet_1', 'swir1_median_dry_1', 'swir1_min_1', 'swir1_stdDev_1', 
    'swir2_median_1', 'swir2_median_wet_1', 'swir2_median_dry_1', 'swir2_min_1', 'swir2_stdDev_1', 'slopeA_1', 'ratio_median', 
    'rvi_median', 'ndwi_median', 'awei_median', 'iia_median', 'gcvi_median', 'gemi_median', 'cvi_median', 'gli_median', 
    'shape_median', 'afvi_median', 'avi_median', 'bsi_median', 'brba_median', 'dswi5_median', 'lswi_median', 'mbi_median', 
    'ui_median', 'osavi_median', 'ri_median', 'brightness_median', 'wetness_median', 'nir_contrast_median', 
    'red_contrast_median', 'ratio_median_dry', 'rvi_median_dry', 'ndwi_median_dry', 'awei_median_dry', 'iia_median_dry', 
    'gcvi_median_dry', 'gemi_median_dry', 'cvi_median_dry', 'gli_median_dry', 'shape_median_dry', 'afvi_median_dry', 
    'avi_median_dry', 'bsi_median_dry', 'brba_median_dry', 'dswi5_median_dry', 'lswi_median_dry', 'mbi_median_dry', 
    'ui_median_dry', 'osavi_median_dry', 'ri_median_dry', 'brightness_median_dry', 'wetness_median_dry', 
    'nir_contrast_median_dry', 'red_contrast_median_dry', 'ratio_median_wet', 'rvi_median_wet', 
    'ndwi_median_wet', 'awei_median_wet', 'iia_median_wet', 'gcvi_median_wet', 'gemi_median_wet', 
    'cvi_median_wet', 'gli_median_wet', 'shape_median_wet', 'afvi_median_wet', 'avi_median_wet', 
    'bsi_median_wet', 'brba_median_wet', 'dswi5_median_wet', 'lswi_median_wet', 'mbi_median_wet', 
    'ui_median_wet', 'osavi_median_wet', 'ri_median_wet', 'brightness_median_wet', 'wetness_median_wet', 
    'nir_contrast_median_wet', 'red_contrast_median_wet'
]
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
def processoExportar(mapaRF, regionB, nameB):
    nomeDesc = 'BACIA_'+ str(nameB)
    idasset =  param['assetOut'] + "/" + nomeDesc
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

def process_reduce_ROIsXclass(featColROIs, featColROIsbase ,lstclassVal, dfProp, mbacia):
    # 12': 1304, '15': 1247, '18': 1280, '22': 1635, '3': 1928, '33': 1361, '4': 1378
    dictQtLimit = {
        3: 600,
        4: 2500,
        12: 600,
        15: 1200,
        18: 900,
        21: 1200,
        22: 1000,
        33: 400
    }
    nFeatColROIs = ee.FeatureCollection([])
    lstBac21 = ["76111","76116","7742","757","758","759","771","772","773","775","776","777"]
    # lstBac3 = ['766', '776', '764', '765', '7621', '744']
    listLitoral = ["7584","7612","7561","755","7564","7541","7544"]
    lstLitoral = ['758','761','756','755','754']
    for ccclass in lstclassVal:
        # print("classse ", ccclass)
        if ccclass in [15, 18]:
            myClass = 21
        else:
            myClass = int(ccclass)
        try:
            valpropCC = dfProp[dfProp['classe'] == myClass]['area_prob'].values[0]
            if ccclass == 21 and str(mbacia) not in ['771', '7613', '7617', '7615']:
                valpropCC += 0.1
            if str(mbacia) in ['771', '7613', '7617', '7615'] and ccclass == 4:
                valpropCC += 0.15

            if str(mbacia) in ['776', '757', '758'] and ccclass == 3:   # 7622
                valpropCC += 0.1

            if ccclass == 3:
                if valpropCC < 0.05:
                    valpropCC = 0.15
            if str(mbacia) in lstBac21:
                if ccclass == 21:
                    valpropCC += 0.25
            
        except:
            valpropCC = 0.01

        if str(mbacia) in lstLitoral and ccclass == 4:
            valpropCC = 0.05
            dictQtLimit[ccclass] = 400

        if str(mbacia) in ['754','756', '7614','7421'] and ccclass == 4:
            valpropCC = 0.2
            dictQtLimit[ccclass] = 1300
        if str(mbacia) in ['753', '752'] and ccclass == 4:
            valpropCC = 0.2
            dictQtLimit[ccclass] = 800
        # print(" valpropCC ", valpropCC)
        tmpROIs = featColROIs.filter(ee.Filter.eq('class', int(ccclass))).randomColumn('random')
        threhold = ee.Number(dictQtLimit[ccclass]).multiply(valpropCC).divide(tmpROIs.size())
        tmpROIs = tmpROIs.filter(ee.Filter.lte('random', threhold))
        
        tmpROIff = featColROIsbase.filter(ee.Filter.eq('class', int(ccclass))).randomColumn('random')
        threhold2 = ee.Number(dictQtLimit[ccclass]).divide(tmpROIff.size())
        tmpROIff = tmpROIff.filter(ee.Filter.lte('random', threhold2))
        # if ccclass  == 4:
        #     print("size class 4 ", tmpROIs.size().getInfo())
        #     print("size class 4 ", tmpROIff.size().getInfo(), "  ", valpropCC)

        if str(mbacia) in ['771', '7613', '7617', '7615'] and ccclass == 12:
            tmpROIs = tmpROIs.limit(200)
            tmpROIff = tmpROIff.limit(200)
        if str(mbacia) in ['757', '758'] and ccclass == 12:
            tmpROIs = tmpROIs.limit(350)
            tmpROIff = tmpROIff.limit(350)
        if ccclass == 22:
            tmpROIs = tmpROIs.limit(100)
            tmpROIff = tmpROIff.limit(100)
        if ccclass == 4 and str(mbacia) in lstBac21:
            tmpROIs = tmpROIs.limit(1000)
            tmpROIff = tmpROIff.limit(1000)

        nFeatColROIs = nFeatColROIs.merge(tmpROIs).merge(tmpROIff)
    
    return nFeatColROIs

def reduce_duplicidade(mList):
    tmplist = []
    for kk in mList:
        if kk not in tmplist:
            tmplist.append(kk)
    return tmplist

def GetPolygonsfromFolder(nBacias, lstClasesBacias, yyear):    
    # print("lista de classe ", lstClasesBacias)
    getlistPtos = ee.data.getList(param['assetROIgrade'])
    ColectionPtos = ee.FeatureCollection([])
    dictQtLimit = {
        3: 800,
        4: 5500,
        12: 1600,
        15: 1200,
        18: 800,
        21: 1500,
        22: 1200,
        33: 400
    }
    for idAsset in getlistPtos:         
        path_ = idAsset.get('id')
        lsFile =  path_.split("/")
        name = lsFile[-1]
        newName = name.split('_')[-1]
        # print("cole", str(newName))
        if str(newName) in str(nBacias) :  #and str(newName[1]) == str(yyear)
            # print(f"reading year {yyear} from basin {name}")
            FeatTemp = ee.FeatureCollection(path_)
             # print(FeatTemp.size().getInfo())
            ColectionPtos = ColectionPtos.merge(FeatTemp) # .select(bandasComunsCorr)
    nFeatColROIs = ee.FeatureCollection([])
    for ccclass in lstClasesBacias:
        tmpROIs = ColectionPtos.filter(ee.Filter.eq('class', int(ccclass))).randomColumn('random')
        threhold = ee.Number(dictQtLimit[ccclass]).divide(tmpROIs.size())
        tmpROIs = tmpROIs.filter(ee.Filter.lte('random', threhold))
        nFeatColROIs = nFeatColROIs.merge(tmpROIs)

    return  ee.FeatureCollection(nFeatColROIs)


def FiltrandoROIsXimportancia(nROIs, baciasAll, nbacia):
    limitCaat = ee.FeatureCollection('users/CartasSol/shapes/nCaatingaBff3000')
    # selecionando todas as bacias vizinhas 
    baciasB = baciasAll.filter(ee.Filter.eq('nunivotto3', nbacia))
    # limitando pelo bioma novo com buffer
    baciasB = baciasB.geometry().buffer(2000).intersection(limitCaat.geometry())
    # filtrando todo o Rois pela área construida 
    redROIs = nROIs.filterBounds(baciasB)
    mhistogram = redROIs.aggregate_histogram('class').getInfo()
    ROIsEnd = ee.FeatureCollection([])
    
    roisT = ee.FeatureCollection([])
    for kk, vv in mhistogram.items():
        print("class {}: == {}".format(kk, vv))
        
        roisT = redROIs.filter(ee.Filter.eq('class', int(kk)))
        roisT =roisT.randomColumn()
        
        if int(kk) == 4:
            roisT = roisT.filter(ee.Filter.gte('random',0.5))
            # print(roisT.size().getInfo())

        elif int(kk) != 21:
            roisT = roisT.filter(ee.Filter.lte('random',0.9))
            # print(roisT.size().getInfo())

        ROIsEnd = ROIsEnd.merge(roisT)
        # roisT = None
    
    return ROIsEnd

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

def clean_lstBandas(tmplstBNDs):
    lstFails = ['green_median_texture']
    lstbndsRed = []
    for bnd in tmplstBNDs:
        bnd = bnd.replace('_1','')
        bnd = bnd.replace('_2','')
        bnd = bnd.replace('_3','')
        if bnd not in lstbndsRed and 'min' not in bnd and bnd not in lstFails and 'stdDev' not in bnd:
            lstbndsRed.append(bnd)
    return lstbndsRed

dictPmtroArv = {
    '35': [
            '741', '746', '753', '766', '7741', '778', 
            '7616', '7617', '7618', '7619'
    ],
    '50': [
            '7422', '745', '752', '758', '7621', 
            '776', '777',  '7612', '7615'# 
    ],
    '65':  [
            '7421','744','7492','751',
            '754','755','756','757','759','7622','763','764',
            '765','767','771','772','773', '7742','775',
            '76111','76116','7614','7613'
    ]
}

tesauroBasin = arqParams.tesauroBasin
lstSat = ["l5","l7","l8"];
pathJson = getPathCSV("regJSON/")

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
a_file = open(pathJson + "filt_lst_features_selected_spIndC9.json", "r")
dictFeatureImp = json.load(a_file)
# print("dict Features ",dictFeatureImp.keys())
b_file = open(pathJson +  "regBacia_Year_hiperPmtrosTuningfromROIs2Y.json", 'r')
dictHiperPmtTuning = json.load(b_file)

def iterandoXBacias( _nbacia, myModel, makeProb):
    exportatROIS = False
    classifiedRF = None;
    # selectBacia = ftcol_bacias.filter(ee.Filter.eq('nunivotto3', _nbacia)).first()
    # https://code.earthengine.google.com/2f8ea5070d3f081a52afbcfb7a7f9d25 

    dfareasCC = pd.read_csv('areaXclasse_CAATINGA_Col71_red.csv')
    print("df areas CC ", dfareasCC.columns)
    dfareasCC = dfareasCC[dfareasCC['Bacia'] == tesauroBasin[_nbacia]]
    print(" dfareasCC shape table ", dfareasCC.shape)
    # if _nbacia in ['761111', '761112']:        
    #     # asset_bacias_buffer42
    #     baciabuffer = ee.FeatureCollection(param['asset_bacias_buffer42']).filter(
    #                         ee.Filter.eq('nunivotto4', tesauroBasin[_nbacia]))
    # else:
    baciabuffer = ee.FeatureCollection(param['asset_bacias_buffer']).filter(
                        ee.Filter.eq('nunivotto4', _nbacia))
    print(f"know about the geometry 'nunivotto4' >>  {_nbacia
                    } loaded < {baciabuffer.size().getInfo()} > geometry" )    
    baciabuffer = baciabuffer.geometry()
    imagens_mosaico = (
        ee.ImageCollection(param['asset_collectionId'])
                .filterBounds(baciabuffer)
                .select(param['bnd_L'])
    )
    # print("  ", imagens_mosaico.size().getInfo())
    # print("see band Names the first ", imagens_mosaico.first().bandNames().getInfo())
    # sys.exit()

    lsNamesBaciasViz = arqParams.basinVizinhasNew[_nbacia]
    print("lista de Bacias vizinhas", lsNamesBaciasViz)
    lsNamesBaciasVizConv = [tesauroBasin[kk] for kk in lsNamesBaciasViz]
    lstSoViz = [kk for kk in lsNamesBaciasViz if kk != _nbacia]
    print("lista de bacias ", lstSoViz)
    lstSoVizConv = [tesauroBasin[kk] for kk in lstSoViz]
    print("Lista de bacias convertidas ", lstSoVizConv) 
    lstSoVizConv = reduce_duplicidade(lstSoVizConv)

    # lista de classe por bacia 
    lstClassesUn = param['dict_classChangeBa'][tesauroBasin[_nbacia]]
    print(f" ==== lista de classes ness bacia na bacia < {_nbacia} >  ====")
    print(f" ==== {lstClassesUn} ======" )
    print("---------------------------------------------------------------")
    # sys.exit()
    imglsClasxanos = ee.Image().byte()
    imglsClasxanos_prob = ee.Image().byte()
    mydict = None
    pmtroClass = copy.deepcopy(param['pmtGTB'])
    # print("area ", baciabuffer.area(0.1).getInfo())
    bandas_imports = []
    for cc, nyear in enumerate(listYears[:]):        
        #se o nyear for 2018 utilizamos os dados de 2017 para fazer a classificacao
        bandActiva = 'classification_' + str(nyear)        
        print( "banda activa: " + bandActiva) 

        if nyear < 2022:
            dfareasccYY = dfareasCC[dfareasCC['year'] == nyear][['area', 'classe']]
            total = dfareasccYY['area'].sum()
            dfareasccYY['area_prob'] = dfareasccYY['area'] / total
            # print(" ", dfareasccYY.head(9))

        if nyear < 2023:
            keyDictFeat = tesauroBasin[_nbacia] + "_" + str(nyear) 
            print("o que keyDictFeat >> ", keyDictFeat)
            bandas_lst = clean_lstBandas(dictFeatureImp[keyDictFeat][:])
            print(f"lista de bandas ótimas com {len(bandas_lst)} bandas " )
            print(' as primeiras 3 \n ==> ', bandas_lst[:3])
            bandas_lst = bandas_lst[:45]

        nameFeatROIs = 'rois_grade_' + _nbacia
        print("loading Rois JOINS = ", nameFeatROIs)
        ROIs_toTrain = (
            ee.FeatureCollection(param['asset_joinsGrBa'] + '/' + nameFeatROIs) 
                        .filter(ee.Filter.eq("year", nyear))  
                        .filter(ee.Filter.inList('class', lstClassesUn))  
        )                  
        ROIs_toTrainViz = GetPolygonsfromFolder(lstSoVizConv, lstClassesUn, nyear)
        ROIs_toTrain = process_reduce_ROIsXclass(ROIs_toTrain, ROIs_toTrainViz, lstClassesUn, dfareasccYY, _nbacia)
        #     ROIs_toTrain = ROIs_toTrain.map(lambda feat: feat.set('class', ee.Number(feat.get('class')).toInt8()))
        # ROIs_toTrain = ROIs_toTrain.filter(ee.Filter.notNull(bandas_imports))
        # print(f"===  {ROIs_toTrain.aggregate_histogram('class').getInfo()}  ===") 
        # print(f"=== vizinhas {ROIs_toTrainViz.aggregate_histogram('class').getInfo()}  ===") 
        # sys.exit()
        # excluindo a classe 12
        if '745' == tesauroBasin[_nbacia]:
            ROIs_toTrain = ROIs_toTrain.filter(ee.Filter.neq('class', 12))
        # bandas_ROIs = [kk for kk in ROIs_toTrain.first().propertyNames().getInfo()]  
        # print()    
        # ROIs_toTrain  = ROIs_toTrain.filter(ee.Filter.notNull(bandasComuns))
        if exportatROIS:
            save_ROIs_toAsset(ROIs_toTrain, nameFeatROIs + "_red")

            
        # if param['yearInicial'] == nyear : #or nyear == 2021      
        #     # print("lista de bandas loaded \n ", bandas_lst)      
        #     # pega os dados de treinamento utilizando a geometria da bacia com buffer           
        #     print(f" Distribuição dos pontos na bacia << {_nbacia} >> year << {nyear} >>")
        #     print("===  {}  ===".format(ROIs_toTrain.aggregate_histogram('class').getInfo()))            
        #     # ===  {'12': 1304, '15': 1247, '18': 1280, '22': 1635, '3': 1928, '33': 1361, '4': 1378}  ===
        # pass
        date_inic =  str(nyear) + '-01-01'      
        date_end = str(nyear) + '-12-31'
        #cria o mosaico a partir do mosaico total, cortando pelo poligono da bacia    
        mosaicColGoogle = imagens_mosaico.filter(ee.Filter.date(date_inic, date_end))
        mosaicoBuilded = make_mosaicofromIntervalo(mosaicColGoogle, nyear) 
        # print(f" we have {mosaicoBuilded.bandNames().getInfo()} images ")
        print("----- calculado todos os 102 indices ---------------------")
        mosaicProcess = CalculateIndice(mosaicoBuilded)
        # mosaicProcess = colmosaicMapbiomas.addBands(mosaicProcess)
        # mosaicMapbiomas = mosaicMapbiomas.select(bandasComuns, bandasComunsCorr)
        # print(mosaicProcess.size().getInfo())
        ################################################################
        # listBandsMosaic = mosaicProcess.bandNames().getInfo()
        # print("bandas do mosaico ", listBandsMosaic)
        # print(ROIs_toTrain.first().propertyNames().getInfo())
        # sys.exit()
        # print('NUMERO DE BANDAS MOSAICO ',len(listBandsMosaic) )
        # # if param['yearInicial'] == nyear:
        # #     print("bandas ativas ", listBandsMosaic)
        # # for bband in lsAllprop:
        # #     if bband not in listBandsMosaic:
        # #         print("Alerta com essa banda = ", bband)
        # print('bandas importantes ', len(bandas_lst))
        #bandas_filtered = [kk for kk in bandas_lst if kk in listBandsMosaic]  # 
        #bandas_imports = [kk for kk in bandas_filtered if kk in bandas_ROIs]  # 
        # bandas_imports = []
        # for bandInt in bandas_lst:
        #     for bndCom in bandasComuns:
        #         if bandInt == bndCom:
        #             # if param['yearInicial'] == nyear :
        #                 # print("band " + bandInt)
        #             bandas_imports.append(bandInt)

        # # bandas_imports.remove('class')
        # # print("bandas cruzadas <<  ",len(bandas_imports) , " >> ")
        # if param['yearInicial'] == nyear:
        #     print("bandas ativas ", bandas_imports)
        # sys.exit()
        # print("        ", ROIs_toTrain.first().propertyNames().getInfo())


        ###############################################################
        # print(ROIs_toTrain.size().getInfo())
        # ROIs_toTrain_filted = ROIs_toTrain.filter(ee.Filter.notNull(bandas_imports))
        # print(ROIs_toTrain_filted.size().getInfo())
        # lsAllprop = ROIs_toTrain_filted.first().propertyNames().getInfo()
        # print('PROPERTIES FEAT = ', lsAllprop)
        #cria o classificador com as especificacoes definidas acima 
        bandas_imports = bandas_lst + ['slope', 'hillshade'] 

        print(f" numero de bandas selecionadas {len(bandas_imports)} ")  

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
            if nyear <= 2016:
                pmtroClass['shrinkage'] = dictHiperPmtTuning[_nbacia]['2016'][0]
                pmtroClass['numberOfTrees'] = dictHiperPmtTuning[_nbacia]['2016'][1]
            else:
                pmtroClass['shrinkage'] = dictHiperPmtTuning[_nbacia]['2021'][0]
                pmtroClass['numberOfTrees'] = dictHiperPmtTuning[_nbacia]['2021'][1]
        
        print("pmtros Classifier ==> ", pmtroClass)
        # # reajusta os parametros 
        # if pmtroClass['numberOfTrees'] > 35 and _nbacia in dictPmtroArv['35']:
        #     pmtroClass['numberOfTrees'] = 35
        # elif pmtroClass['numberOfTrees'] > 50 and _nbacia in dictPmtroArv['50']:
        #     pmtroClass['numberOfTrees'] = 50
        # sys.exit()
        # print("===="*10)
        # print("pmtros Classifier Ajustado ==> ", pmtroClass)

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
                        
              
        
    # i+=1
    # print(param['lsBandasMap'])   
    if not exportatROIS: 
        # seta as propriedades na imagem classificada    
        # print("show names bands of imglsClasxanos ", imglsClasxanos.bandNames().getInfo() )        
        imglsClasxanos = imglsClasxanos.select(param['lsBandasMap'])    
        imglsClasxanos = imglsClasxanos.clip(baciabuffer).set("system:footprint", baciabuffer.coordinates())
        # exporta bacia
        processoExportar(imglsClasxanos, baciabuffer.coordinates(), nomec)         

                
        
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
# print("  files json ", filesJSON)
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
# "761112",
modelo = "GTB"
knowMapSaved = False
listBacFalta = []
cont = 0
# cont = gerenciador(cont)
# sys.exit(0)
for _nbacia in nameBacias[:]:
    if knowMapSaved:
        try:
            nameMap = 'BACIA_' + _nbacia + '_' + 'GTB_col9-v' + str(param['version'])
            imgtmp = ee.Image(param['assetOut'] + nameMap)
            print(" 🚨 loading ", nameMap, " ", len(imgtmp.bandNames().getInfo()), " bandas 🚨")
        except:
            listBacFalta.append(_nbacia)
    else:        
        print("-------------------.kmkl---------------------------------------------")
        print(f"--------    classificando bacia nova {_nbacia} and seus properties da antinga {tesauroBasin[_nbacia]}-----------------")   
        print("---------------------------------------------------------------------") 
        iterandoXBacias(_nbacia, modelo, False) 
        arqFeitos.write(_nbacia + '\n')
        cont = gerenciador(cont) 
arqFeitos.close()


if knowMapSaved:
    print("lista de bacias que faltam \n ",listBacFalta)
    print("total ", len(listBacFalta))