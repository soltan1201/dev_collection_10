
var palettes = require('users/mapbiomas/modules:Palettes.js');
var text = require('users/gena/packages:text')

var visualizar = {
    visclassCC: {
            "min": 0, 
            "max": 62,
            "palette":  palettes.get('classification8'),
            "format": "png"
    },
    solo: {
        min: 0, max: 1,
        palette: '000000,ffaa5f'
    },
    'soilv4': {  
        'min': 0, 'max': 1,
        'palette': 'f55435'
    },
}

var param = { 
    assetMapC8: 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    assetlimitBacias: "projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatingaUnion",
    asset_soilGT: 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4',
    asset_soil_doct: 'projects/mapbiomas-arida/doctorate/soil_random_forest_caatinga',
    asset_baciasN1raster: 'projects/mapbiomas-workspace/AUXILIAR/bacias-nivel-1-raster',
    'classMapB' : [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
    'classNew'  : [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2],
}

var year_courrent = 2020;
var bandAct = 'classification_' + String(year_courrent);

var baciaRaster = ee.Image(param.asset_baciasN1raster);
var maskBacia = baciaRaster.eq(104).add(baciaRaster.eq(103))
                          .add(baciaRaster.eq(106)).add(baciaRaster.eq(107));
var limitBacias = ee.FeatureCollection(param.assetlimitBacias);
var imgColSolo = ee.ImageCollection(param.asset_soilGT)
                            .filterBounds(limitBacias.geometry());
var layerSoil = ee.ImageCollection(param.asset_soil_doct)
                                .filter(ee.Filter.eq('year', year_courrent))
                                .first();
var imgMapCol8= ee.Image(param.assetMapC8).updateMask(maskBacia.gt(0))
                        .select(bandAct);
                
print("know image collection soil GT ", imgColSolo);
print("Know year work ", imgColSolo.aggregate_histogram('year'));
print("know the biomes save", imgColSolo.aggregate_histogram('biome'));

var soloYY = imgColSolo.filter(ee.Filter.eq('year', 2020));
soloYY = soloYY.max().gt(0.9).selfMask();

var areasIntMapb = imgMapCol8.remap(param.classMapB, param.classNew);
var maskExcluir = areasIntMapb.eq(1);
var maskAgrop = areasIntMapb.eq(2);



Map.addLayer(imgMapCol8,  visualizar.visclassCC, 'Col8_'+ String(year_courrent), false);
Map.addLayer(layerSoil, visualizar.soilv4, 'soil layer');
Map.addLayer(soloYY, visualizar.solo, 'soil gt');
Map.addLayer(maskExcluir.selfMask(), {min:0, max: 1, palette: 'black,red'}, 'remover');
Map.addLayer(maskAgrop.selfMask(), {max: 1, palette: 'black,blue'}, 'agro');