var vis = {
    visMosaic: {
        min: 0,
        max: 2500,
        bands: ['red_median', 'green_median', 'blue_median']
    },

    visclassCC: {
        "min": 1, 
        "max": 12,
        "palette": ['#006400', '#6b9932', '#687537', '#B8AF4F', '#fc8114', '#66ffcc',
                    '#E974ED', '#FFEFC3', '#EA9999', '#DD7E6B', '#af2a2a', '#0000FF'],
        "format": "png"
    },
};

/// ===== FUNÇÕES =====
var ExportarImgMapstoDriver = function(image_map, name_img, regiao){
   
    var paramExpD = {
        image: image_map, 
        description: name_img + "_img", 
        folder: 'tif_mapbiomas_costa', 
        scale: 30, 
        maxPixels: 1e13, 
        fileFormat:  'GeoTIFF',
        region: regiao
    };
    Export.image.toDrive(paramExpD);     
    print("Export all Image to Driver" + name_img + " ....");

};

var param = {
    'classMapB': [ 0, 3, 4, 5, 6, 9,11,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,39,40,41,42,43,44,45,46,47,48,49,50,62],
    'classNew':  [ 0, 1, 1, 3, 1, 7, 4, 4,12, 7, 7, 7, 7, 8, 9,10,11, 9,12, 4, 9,12, 5,12, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 6, 7],
    'assetMosaic': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',
    'asset_costa' : "users/CartasSol/shapes/costa",
    'asset_cobertura_col90': "projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1",
    anos: [
        '1985','1986','1987','1988','1989','1990','1991','1992','1993','1994',
        '1995','1996','1997','1998','1999','2000','2001','2002','2003','2004',
        '2005','2006','2007','2008','2009','2010','2011','2012','2013','2014',
        '2015','2016','2017','2018','2019','2020','2021','2022','2023'],
} 

var mapsBioma = ee.Image(param.asset_cobertura_col90);
                    
var shpCosta = ee.FeatureCollection(param.asset_costa);
var rasterCosta = shpCosta.map(function(feat){return feat.set('class', 1)});
rasterCosta = rasterCosta.reduceToImage(['class'], ee.Reducer.first());
mapsBioma = mapsBioma.updateMask(rasterCosta);
Map.addLayer(ee.Image.constant(1), {min:0, max: 1}, 'layer base', false);
param.anos.forEach(function(nyear){
    var mapbiomas_tmp = mapsBioma.select('classification_' + nyear).remap(param.classMapB, param.classNew);
    // Map.addLayer(imgColMosaic, vis.visMosaic, "mosaic 2023");
    Map.addLayer(mapbiomas_tmp, vis.visclassCC, "MapBiomas " + nyear, false);
    ExportarImgMapstoDriver(mapbiomas_tmp, "recorte_costa_baixo_sul_BA_" + nyear, shpCosta.geometry());
})

var lineEst = ee.Image().byte().paint({
    featureCollection: shpCosta,
    color: 1,
    width: 1.5
});

Map.addLayer(lineEst, {palette: 'FF0000'}, 'linha de costa ');
