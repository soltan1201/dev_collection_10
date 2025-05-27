
var palettes = require('users/mapbiomas/modules:Palettes.js');
var text = require('users/gena/packages:text')

var visualizar = {
    visclassCC: {
            "min": 0, 
            "max": 69,
            "palette":  palettes.get('classification9'),
            "format": "png"
    },
    vismosaicoGEE: {
        'min': 0.001, 'max': 0.15,
        bands: ['red', 'green', 'blue']
    },
    presencia : {
        max: 2,
        min: -1,
        palette: ['#D23519','#FFFFFF','#7D7C7CFF','#32D22DFF']
    },
    afloramento: {
        min:0, max: 1,
        palette: ['#EF3207']
    }  

} 
var functionExports = function(cc_image, nameEXp, geomSHP, nassetId){
    var pmtExpo = {
        image: cc_image,
        description: nameEXp,
        scale: param.scale, // Escolha a escala de acordo com sua necessidade
        region: geomSHP,
        assetId: nassetId + nameEXp, // Substitua pelo nome da sua pasta no Google Drive
        maxPixels: 1e13 // Escolha o valor adequado para o número máximo de pixels permitidos
    };
    Export.image.toAsset(pmtExpo);
    print("maps salvo " + nameEXp + " ...");
};
var maxNumbPixels = 50;
function buildingLayerconnectado(imgClasse){    
    var manchas_conectados = imgClasse.connectedPixelCount({
                                            'maxSize': maxNumbPixels, 
                                            'eightConnected': true
                                        });
    return manchas_conectados;
}

var spectralBands = ['blue', 'red', 'green', 'nir', 'swir1', 'swir2'];
var param = {
    assetrois: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_cleaned_downsamplesv4C/',
    asset_maps_new: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Spatials_all',
    asset_maps_old: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Temporal',
    asset_bacias_buffer:  'projects/ee-solkancengine17/assets/shape/bacias_buffer_caatinga_49_regions',
    asset_afloramento: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/rockyoutcropcol10',
    asset_collectionId: 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    output_asset: 'projects/geo-data-s/assets/'
}
var featBacias = ee.FeatureCollection(param.asset_bacias_buffer);
// raster com o novo mapa 
var rastermapSpatial = ee.ImageCollection(param.asset_maps_new)
                        .filter(ee.Filter.eq('version', 8))
                        .max();
print("show metadatas from new maps ", rastermapSpatial);

// raster com os mapas mais antigos 
var rastermapTemporal = ee.ImageCollection(param.asset_maps_old)
                          .filter(ee.Filter.eq('version', 8))
                          .max();
print("show metadatas from old maps ", rastermapTemporal);
var mapSpatial90 = rastermapSpatial.select('classification_1990');
var listColor = ['#000000', '#330d0b', '#7a49a5','#bf2929','#601616']
var lstYears = ['1985','1986','1987','1988','1989'];
var maskGeral = ee.Image().byte();
var maxVal = 5;
var cc = 0;
lstYears.forEach(function(nyear){
    var visualizar_map = false;
    if(nyear === lstYears[-1]){
        visualizar_map = true;
    }
    print();
    var class_especf = 4;
    // var nyear = 2023;
    var dateStart = ee.Date.fromYMD(parseInt(nyear), 1, 1);
    var dateEnd = ee.Date.fromYMD(parseInt(nyear), 12, 31);
       
    
    var rasterSpatialYear = rastermapSpatial.select('classification_' + nyear);

    var mosGEEyy = ee.ImageCollection(param.asset_collectionId)
                            .filter(ee.Filter.date(dateStart, dateEnd))
                            .median()
                            .select(spectralBands);  
    print("mosaico mensal GEE no ano", mosGEEyy);
    maxVal -= cc
    print(" max Val " + maxVal);
    var map_temporalYear = rastermapTemporal.select('classification_' + nyear);
    var maskSavana = mapSpatial90.eq(4).subtract(map_temporalYear.eq(4)).multiply(maxVal);
    
    maskGeral = maskGeral.addBands(maskSavana.rename('classification_' + nyear));
    
    var maps_conectionTemp = buildingLayerconnectado(map_temporalYear);
    maps_conectionTemp = maps_conectionTemp.lt(maxNumbPixels).and(maps_conectionTemp.gt(16));
    var maps_conectionSpat = buildingLayerconnectado(rasterSpatialYear);
    maps_conectionSpat = maps_conectionSpat.lt(maxNumbPixels);
    
    Map.addLayer(mosGEEyy,   visualizar.vismosaicoGEE, 'mosEE_' + String(nyear), visualizar_map);

    Map.addLayer(map_temporalYear, visualizar.visclassCC, "map TemporalJ3 " + nyear, visualizar_map);
    Map.addLayer(maps_conectionTemp.selfMask(), {max: 1, palette: '000000'}, "map conection " + nyear, visualizar_map);
    Map.addLayer(rasterSpatialYear, visualizar.visclassCC, "map Spatial End " + nyear, visualizar_map);
    Map.addLayer(maps_conectionSpat.selfMask(), {max: 1, palette: listColor[cc]}, "map conection " + nyear, visualizar_map);
    cc += 1;
});


 
var name_exp = 'mascara_savana_ult_anos';
functionExports(maskGeral.updateMask(maskGeral.neq(0)), name_exp, featBacias.geometry(), param.output_asset);


