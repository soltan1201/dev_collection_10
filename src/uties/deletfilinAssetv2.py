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

def Get_Remove_Array_from_ImgCol(asset_imgcol, fVers= False, vers= 1, fJanela= False, janele= 3, fList= False, lsBacias= [], play_eliminar= False):

    
    imgCol = ee.ImageCollection(asset_imgcol)
    
    if fVers:
        imgCol = imgCol.filter(ee.Filter.eq('version', vers))
    if fJanela:
        imgCol = imgCol.filter(ee.Filter.eq('janela', 4))    
    if fList:
        imgCol = imgCol.filter(ee.Filter.inList('bacia', lsBacias))
    
    lst_id = imgCol.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()
    print(f'we will eliminate {len(lst_id)} file image from {asset_imgcol} ')
    
    for cc, idss in enumerate(lst_id):    
        path_ = str(asset_imgcol + '/' + idss)    
        print (f"... eliminando ❌ ... item 📍{cc}/{len(lst_id)} : {idss}  ▶️ ")    
        try:
            if play_eliminar:
                ee.data.deleteAsset(path_)
                print(" > " , path_)
        except:
            print(f" {path_} -- > NAO EXISTE!")


# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/maks_estaveis_v2'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/maks_coinciden'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/maks_fire_w5'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/mask_pixels_toSample'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/S2/Classifier/ClassVY'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/S2/POS-CLASS/toExport' #
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/S2/POS-CLASS/ilumination'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/S2/POS-CLASS/grass_aflor'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/S2/POS-CLASS/Temporal'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/S2/POS-CLASS/Gap-fill'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/S2/POS-CLASS/clean_water'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Validation/aggrements'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassV1'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVP'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mosaics-CAATINGA-4'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/classAfloramento'
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/aggrements'
asset = 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/estabilidade_colecoes'
lsBacias = [
    '7754', '7691', '7581', '7625', '7584', '751', '7614', 
    '752', '7616', '745', '7424', '773', '7612', '7613', 
    '7618', '7561', '755', '7617', '7564', '761111','761112', 
    '7741', '7422', '76116', '7761', '7671', '7615', '7411', 
    '7764', '757', '771', '7712', '766', '7746', '753', '764', 
    '7541', '7721', '772', '7619', '7443', '765', '7544', '7438', 
    '763', '7591', '7592', '7622', '746'
]

eliminar_files = True
Get_Remove_Array_from_ImgCol(asset,  play_eliminar= eliminar_files)  