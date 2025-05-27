///++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++////
/// ++ https://code.earthengine.google.com/32cf43c0bc9a1c7670f7316afe190596  ++////
///++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++////

var palettes = require('users/mapbiomas/modules:Palettes.js');
var text = require('users/gena/packages:text');
var visualizar = {
    visclassCC: {
            "min": 0, 
            "max": 69,
            "palette":  palettes.get('classification9'),
            "format": "png"
    },
    visMosaic: {
        min: 10,
        max: 2000,
        bands: ['red_median', 'green_median', 'blue_median']
    },
    vismosaicoGEE: {
        'min': 0.001, 'max': 0.15,
        bands: ['red', 'green', 'blue']
    },
    props: {  
        textColor: 'ff0000', 
        outlineColor: 'ffffff', 
        outlineWidth: 1.5, 
        outlineOpacity: 0.2
    }
} 
var spectralBands = ['blue', 'red', 'green', 'nir', 'swir1', 'swir2'];
var param = { 
    biomas: ["CAATINGA","CERRADO", "MATAATLANTICA"],
    assetMapC80: 'projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_integration_v1',
    assetMapC90: 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1',
    // asset_MapCX : 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Temporal',
    asset_MapCX : 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/MergerV6',
    asset_MapCXBef : 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/transitionTest',
    // asset_MapCXBef : 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/ClassifyVA',
    assetrecorteCaatCerrMA : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/recorteCaatCeMA',
    asset_bacias_raster: 'projects/ee-solkancengine17/assets/bacias_raster_Caatinga_49_regions',
    asset_mosaic: 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',  
    asset_collectionId: 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    assetBacia: 'projects/ee-solkancengine17/assets/shape/bacias_buffer_caatinga_49_regions',    
    nyears: ['1985','1986','1987','1988','1989','1990','1991','1992','1993','1994',
           '1995','1996','1997','1998','1999','2000','2001','2002','2003','2004',
           '2005','2006','2007','2008','2009','2010','2011','2012','2013','2014',
           '2015','2016','2017','2018','2019','2020','2021','2022','2023','2024'],
    bandas: ['red_median', 'green_median', 'blue_median'],
    listaNameBacias: [

    ],
}
var lstSat = ["l5","l7","l8"]
// var asset = 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/ClassifyV2/BACIA_7625_GTB_col10-v3';
// var img = ee.Image(asset);
// print(img);
var selBacia = '7625';  //7613, 761112
var janela = 1
var FeatColbacia = ee.FeatureCollection(param.assetBacia)
                        // .filter(ee.Filter.eq('nunivotto4', selBacia));
print("bacia selecionada ", FeatColbacia);
Map.addLayer(FeatColbacia, {color: 'green'}, 'bacias', false);
var baciaRaster = FeatColbacia.reduceToImage(['id_codigo'], ee.Reducer.first()).gt(0);

///// -------------------------------------------///
var mapsCol10Bef = ee.ImageCollection(param.asset_MapCXBef);
var mapCol10 = ee.ImageCollection(param.asset_MapCX); //Gap Fil
print('mapbiomas Coleção 10 Gap- Fill', mapCol10);
print('mapbiomas Coleção 10 asset before ', mapsCol10Bef);

var mapFiltered = mapCol10;
if (janela > 2){
    mapFiltered = mapFiltered.filter(ee.Filter.eq('janela', janela));
}
mapFiltered = mapFiltered.max();//.select('classification')
var mapsBef = mapsCol10Bef.max();

var collectionGEE = ee.ImageCollection(param.asset_collectionId)
                        .filter(ee.Filter.bounds(FeatColbacia.geometry()))
                        .select(spectralBands);  
var mosaicMapB = ee.ImageCollection(param.asset_mosaic)
                            .filter(ee.Filter.inList('biome', param.biomas))
                            .filter(ee.Filter.inList('satellite', lstSat))
                            .filterBounds(FeatColbacia.geometry())
                            

param.nyears.slice(30, 40).forEach(function(yyear){
    var tmp_img = mapFiltered.select('classification_' + yyear);
    var tmp_bef = mapsBef.select('classification_' + yyear);
    
    var dateStart = ee.Date.fromYMD(parseInt(yyear), 1, 1);
    var dateEnd = ee.Date.fromYMD(parseInt(yyear), 12, 31);
    print(yyear, dateStart);
    
    var mosGEEyy = collectionGEE.filter(ee.Filter.date(dateStart, dateEnd)).median();
    var mosMByy =  mosaicMapB.filter(ee.Filter.eq('year', parseInt(yyear))).mosaic();
    
    Map.addLayer(mosMByy, visualizar.visMosaic, 'mosMP_' + yyear, false);
    Map.addLayer(mosGEEyy, visualizar.vismosaicoGEE, 'mosEE_' + yyear, false);
    Map.addLayer(tmp_img, visualizar.visclassCC, 'cc_' + yyear, false);
    Map.addLayer(tmp_bef, visualizar.visclassCC, 'cc_bef_' + yyear, false);
})