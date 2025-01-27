

var palettes = require('users/mapbiomas/modules:Palettes.js');
var vis = {
    visMosaic: {
        min: 0,
        max: 2500,
        bands: ['red_median', 'green_median', 'blue_median']
    },
    props: {  
        textColor: 'ff0000', 
        outlineColor: 'ffffff', 
        outlineWidth: 1.5, 
        outlineOpacity: 0.2
    },
    visclassCC: {
        "min": 0, 
        "max": 62,
        "palette":  palettes.get('classification9'),
        "format": "png"
    },
};

var recortarFeatCol = function(geoLimit, featColreg){
    var newFeatCol = featColreg.map(
        function(feat){
            return feat.intersection(geoLimit);
    });
    return newFeatCol;
};
var lstEstCruz = ['22','23','24','25','26','27','28','29','31','32'];  
var param = {
    'classMapB': [3, 4, 5, 9, 12, 13, 15, 18, 18, 20, 21, 22, 23, 24, 25, 26, 29, 30, 31, 32, 33,
                      36, 39, 40, 41, 46, 47, 48, 49, 50, 62],
    'classNew':  [0, 0, 0, 0,  0,  0,  1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  0,  1,  2,  0,  2,
                       1,  1,  1,  1,  1,  1,  1,  0,  0,  1],
    'assetMosaic': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',
    'asset_bacias' : "projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga",
    'asset_cobertura_col90': "projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1",
    'vetor_biomas_250': 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
    "BR_ESTADOS_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_ESTADOS_2022",
} 
var biomas_raster = ee.Image(param.biomas_250_rasters).eq(2);
var imgColMosaic = ee.ImageCollection(param.assetMosaic)
                            .filter(ee.Filter.eq('biome', 'CAATINGA'))
                            .filter(ee.Filter.eq('year', 2023))
                            .mosaic().updateMask(biomas_raster);
print("Mosaico filtrado ", imgColMosaic);

var mapsBioma = ee.Image(param.asset_cobertura_col90)
                    .select('classification_2023').updateMask(biomas_raster)
                    .remap(param.classMapB, param.classNew);                    

var shpBioma = ee.FeatureCollection(param.vetor_biomas_250)
                    .filter(ee.Filter.eq('CD_Bioma', 2));

var shpEstados = ee.FeatureCollection(param.BR_ESTADOS_2022)
                    .filter(ee.Filter.inList('CD_UF', lstEstCruz))

var  shpBiomaUp = recortarFeatCol(shpBioma.geometry(), shpEstados)


Map.addLayer(ee.Image.constant(1), {min:0, max: 1}, 'layer base');
Map.addLayer(imgColMosaic, vis.visMosaic, "mosaic 2023");
Map.addLayer(mapsBioma, vis.visclassCC, "MapBiomas 2023");
var lineEst = ee.Image().byte().paint({
    featureCollection: shpBiomaUp,
    color: 1,
    width: 1.5
});

var lineCaat = ee.Image().byte().paint({
    featureCollection: shpBioma,
    color: 1,
    width: 1.5
});
Map.addLayer(lineEst, {palette: 'FF0000'}, 'estados Caat');
Map.addLayer(lineCaat, {palette: '000000'}, 'shp Caat');