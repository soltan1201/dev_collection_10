var palettes = require('users/mapbiomas/modules:Palettes.js');
var vis = {
    'alerta': {
        min: 0, max: 1,
        palette: '000000,a52a2a'
    }, 
    'fire' :{
        min: 0, max: 1,
        palette: '#c71585'
    },
    estavel: {
        min: 0, max: 1,
        palette: '#eee8aa'
    },
    coincidentes: {
        min: 0, max: 1,
        palette: '#4169e1'
    },
    areaColeta: {
        min: 0, max: 1,
        palette: '#648c11'
    },
    visclassCC: {
        "min": 0, 
        "max": 62,
        "palette":  palettes.get('classification8'),
        "format": "png"
},
}

var parameters = {
    "asset_alerta": 'users/data_sets_solkan/Alertas/dashboard_alerts-shapefile_2024_02',
    "asset_fogo": 'projects/ee-geomapeamentoipam/assets/MAPBIOMAS_FOGO/COLECAO_2/Colecao2_fogo_mask_v1',
    'limit_caat': 'users/CartasSol/shapes/nCaatingaBff3000',
    'asset_img_alerts': 'users/data_sets_solkan/Alertas/layersImgClassTP_2024_02',
    'asset_alerts_col': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_deforestation_secondary_vegetation_v2',
    'asset_Coincidencia': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/maks_coinciden/',
    'asset_estaveis': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/maks_estaveis/',
    'asset_fire_mask': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/maks_fire_w5/',
    'assetMapC7': 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
    'assetMapC8': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    'asset_MapC9': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVX',
    'classMapB': [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45],
    'classNew': [3, 4, 3, 3,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33, 21,33,33,21,21,21,21,21,21,21]

};
var version = 5;
var year_select = 1996;
var banda_activa = 'classification_' + year_select.toString();
var shp_limit = ee.FeatureCollection(parameters.limit_caat);
var imgMapCol71= ee.Image(parameters.assetMapC7).clip(shp_limit.geometry());
var imgMapCol8= ee.Image(parameters.assetMapC8).clip(shp_limit.geometry());
var imgMapCol9RF =  ee.ImageCollection(parameters.asset_MapC9)
                            .filter(ee.Filter.eq('version', version))
                            .filter(ee.Filter.eq("classifier", "RF"))
                            .max().clip(shp_limit.geometry());

var imgMapCol9GTB =  ee.ImageCollection(parameters.asset_MapC9)
                            .filter(ee.Filter.eq('version', version))
                            .filter(ee.Filter.eq("classifier", "GTB"))
                            .max().clip(shp_limit.geometry());

print("imagem no Asset Geral Mapbiomas Col 7.1", imgMapCol71);
print("imagem no Asset Geral Mapbiomas Col 8.0", imgMapCol8);
print("imagem no Asset Geral X Bacias col 9 RF", imgMapCol9RF);
print("imagem no Asset Geral X Bacias col 9 GTB", imgMapCol9GTB);

imgMapCol71 = imgMapCol71.select(banda_activa)
imgMapCol8 = imgMapCol8.select(banda_activa)
imgMapCol9RF = imgMapCol9RF.select(banda_activa)
imgMapCol9GTB = imgMapCol9GTB.select(banda_activa)
//projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/maks_fire_w5/
// 
var nameFireMask = 'masks_fire_wind5_' + year_select.toString();
var imgFire = ee.Image(parameters.asset_fire_mask + nameFireMask);
print("show data img fire ", imgFire);

var imgALerts = ee.Image(parameters.asset_alerts_col)
                          .divide(100).int().eq(4)
                          .select('classification_' + year_select.toString());
print("show layer alertas mapbiomas col 8 ", imgALerts);

if (year_select >= 2020){
    imgALerts = ee.Image(parameters.asset_img_alerts).unmask(0);
};
print("show data img Alertas ", imgALerts);
// 1 Concordante, 2 concordante recente, 3 discordante recente,
// 4 discordante, 5 muito discordante
var nameCoinc = 'masks_pixels_incidentes_' + year_select.toString();
var imgCoincd = ee.Image(parameters.asset_Coincidencia + nameCoinc).lt(3).rename('coincident');
print("show data img maps de coincidencias ", imgCoincd);

var nameEst = 'masks_estatic_pixels_' + year_select.toString();
var imgEstavel = ee.Image(parameters.asset_estaveis + nameEst);
print("show data img maps de Estaveis ", imgEstavel);

var areaColeta = imgCoincd.multiply(imgEstavel).multiply(imgALerts.eq(0))
                                    .multiply(imgFire.eq(0));


Map.addLayer(imgMapCol71, vis.visclassCC,'Col71_' + String(year_select), false);
Map.addLayer(imgMapCol8,  vis.visclassCC, 'Col8_'+ String(year_select))
Map.addLayer(imgMapCol9RF,  vis.visclassCC, 'Col9_ClassV1', false);
Map.addLayer(imgMapCol9GTB,  vis.visclassCC, 'Col9_ClassV1', false);
Map.addLayer(imgEstavel.selfMask(), vis.estavel, "Áreas estaveis", false);
Map.addLayer(imgCoincd.selfMask(), vis.coincidentes, "Áreas Coincidentes", false);
Map.addLayer(imgFire.gt(0).selfMask(), vis.fire, "fire year " + year_select.toString(), false) ;
Map.addLayer(imgALerts.selfMask(), vis.alerta, "Alertas ", false);
Map.addLayer(areaColeta.selfMask(), vis.areaColeta, "Área de coleta " + year_select.toString());













