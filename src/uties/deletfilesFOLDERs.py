import ee
import os
import sys
import collections
collections.Callable = collections.abc.Callable

from pathlib import Path
pathparent = str(Path(os.getcwd()).parents[0])
sys.path.append(pathparent)
from configure_account_projects_ee import get_current_account, get_project_from_account
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

def GetPolygonsfromFolder(assetFolder, sufixo, play_eliminar):
  
    getlistPtos = ee.data.getList(assetFolder)
    lstBacias = []
    sizeFiles = len(getlistPtos)
    for cc, idAsset in enumerate(getlistPtos): 
        path_ = idAsset.get('id') 
        lsFile =  path_.split("/")
        name = lsFile[-1]
        idBacia = name.split('_')[0]
        if idBacia not in lstBacias:
            lstBacias.append(idBacia)
        # print(name)
        # if str(name).startswith(sufixo): AMOSTRAS/col7/CAATINGA/classificationV
        if sufixo in str(name): 
            print("eliminando {}/{}:  {}".format(cc, sizeFiles,name))
            print(path_)
            if play_eliminar:
                ee.data.deleteAsset(path_) 
    
    print(lstBacias)

# asset = {'id': 'projects/nexgenmap/SAMPLES/Caatinga/ROIs'}
# asset = {'id': 'projects/nexgenmap/SAMPLES/caatinga/ROIs/col6'}
# asset = {'id': 'projects/nexgenmap/SAMPLES/caatinga/ROIs/col6_norm'}
# asset = {'id': 'projects/nexgenmap/SAMPLES/caatinga/ROIs/col6_norm_outlier'}
# asset = {'id': 'projects/nexgenmap/SAMPLES/caatinga/ROIs/col6_outlier'}
# asset ={'id' :'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/S2/ROIs/coleta2'}
# asset ={'id' : 'projects/nexgenmap/SAMPLES/Caatinga'}
# asset = {'id' : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/cROIsN245_allBND'}
# asset = {'id' : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/cROIsGradeallBNDNormal'}
# asset = {'id' : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/coletaROIsv1N245'}
# asset = {'id' : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/ROIsnotWithLabel'}
# asset = {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/S2/ROIs/coleta2red'}
# asset = {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/coletaROIsNormN2cluster'}
# asset = {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/coletaROIsNormN2manual'}
# asset = {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/ROIs/coletaROIsv6N2cluster'}
# asset = {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/ROIs/coletaROIsv7N2manual'}
# asset = {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_byGrades_info'}
# asset = {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_merged_IndAll'}
# asset = {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_byGradesAgrWat'}
# asset = {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_byGradesIndV2'}  # 
# asset = {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_byGradesIndExt'}
# asset = {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_Merges_info'}
# asset = {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_merged_Ind'}
asset = {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_merged_IndAll'}
# asset = {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_byGradesIndV3'}
eliminar_files = True
GetPolygonsfromFolder(asset, '', eliminar_files)  # 

