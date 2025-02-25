#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Produzido por Geodatin - Dados e Geoinformacao
DISTRIBUIDO COM GPLv2
@author: geodatin
"""
import ee
import sys
import eemont
import pandas as pd
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

def print_expression(sp_index):
    mIndex = eemont.listIndices()
    print(" ", mIndex[sp_index])

lstSpect_Index = [kk for kk in eemont.listIndices()]

# indices.BAIS2.formula
#indices.BAIS2.reference
mIndex = eemont.indices()
for cc, indice in enumerate(lstSpect_Index):
    # print(indice)
    print("# ", cc, "  formula = ", mIndex[indice].formula)
    #indices.BAIS2.reference
# print(mIndex.AFRI1600.formula)