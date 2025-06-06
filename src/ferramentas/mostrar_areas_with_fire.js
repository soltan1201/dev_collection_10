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
    biomas: ["CAATINGA","CERRADO", "MATAATLANTICA"],
    assetMapC80: 'projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_integration_v1',
    assetMapC90: 'projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1',
    asset_fire_annual: 'projects/mapbiomas-workspace/FOGO_COL4/1_Subprodutos/mapbiomas-fire-collection4-annual-burned-v1',
    asset_MapCX : 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Merger',
    asset_Map_inicial : 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Gap-fill',
    asset_MapCXBef : 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/transitionTest',
    assetrecorteCaatCerrMA : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/recorteCaatCeMA',
    asset_bacias_raster: 'projects/ee-solkancengine17/assets/bacias_raster_Caatinga_49_regions',

    asset_gapfil: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Gap-fill',
    asset_spatial: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Spatial',
    asset_spatials: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Spatials',
    asset_spatialall: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Spatials_all',
    asset_spatialint: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Spatial_int',
    asset_temporal: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Temporal',
    asset_temporalA: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/TemporalA',
    asset_temporalCC: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/TemporalCC',
    asset_frequency: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Frequency',
    asset_merger: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Merger',
    asset_mergerV5: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/MergerV5',
    asset_mergerV6: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/MergerV6',
    asset_transition: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/transition',
    asset_transitionT: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/transitionTest',

    asset_estradas: 'projects/mapbiomas-arida/estradas_dnit_caat',
    asset_mosaic: 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',  
    asset_collectionId: 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    asset_caat_buffer: 'users/CartasSol/shapes/caatinga_buffer5km',
    assetBacia: 'projects/ee-solkancengine17/assets/shape/bacias_buffer_caatinga_49_regions',    
    nyears: [
        '1985','1986','1987','1988','1989','1990','1991','1992','1993','1994',
        '1995','1996','1997','1998','1999','2000','2001','2002','2003','2004',
        '2005','2006','2007','2008','2009','2010','2011','2012','2013','2014',
        '2015','2016','2017','2018','2019','2020','2021','2022','2023','2024'
    ],
    bandas: ['red_median', 'green_median', 'blue_median'],
}

var lstSat = ["l5","l7","l8"]

var lstnameBaciasG = ["7754","773","761112","7591","7613","7746","7741","7581","757"];
var lstnameBaciasV9 = ["7754","773","761112"];

var bioma_caatinga = ee.FeatureCollection(param.asset_caat_buffer);
var FeatColbacia = ee.FeatureCollection(param.assetBacia)
                        // .filter(ee.Filter.eq('nunivotto4', selBacia));
print("bacia selecionada ", FeatColbacia);
Map.addLayer(FeatColbacia, {color: 'green'}, 'bacias', false);
var baciaRaster = FeatColbacia.reduceToImage(['id_codigo'], ee.Reducer.first()).gt(0);
var geom_marco = FeatColbacia.filter(ee.Filter.inList('nunivotto4', lstnameBaciasG));
///// -------------------------------------------///
var mapsCol10Bef = ee.ImageCollection(param.asset_MapCXBef)
                            .filter(ee.Filter.eq('version', 8));
                            
print(" mapsCol10Bef ", mapsCol10Bef);
var mapFiltered = ee.ImageCollection(param.asset_MapCX)                       
                        .filter(ee.Filter.eq('version', 10));
print(  "show metadado da versão 10 ", mapFiltered);

print('mapbiomas Coleção 10 Mapa Mix', mapFiltered);
print('mapbiomas Coleção 10 asset before ', mapsCol10Bef);

mapFiltered = mapFiltered.max();//.select('classification')
mapsCol10Bef = mapsCol10Bef.max();

var raster_fires = ee.Image(param.asset_fire_annual).updateMask(baciaRaster);
print("sheo metadados fire Raster Anual ", raster_fires);

var mapsCol10gapfill5 = ee.ImageCollection(param.asset_Map_inicial)
                              .filter(ee.Filter.eq('version', 5))
                              .filter(ee.Filter.inList('id_bacias', lstnameBaciasG).not());
var mapsCol10gapfill10 = ee.ImageCollection(param.asset_Map_inicial)
                              .filter(ee.Filter.eq('version', 10));
var mapsCol10gapfill9 = ee.ImageCollection(param.asset_Map_inicial)
                              .filter(ee.Filter.eq('version', 9)) 
                              .filter(ee.Filter.inList('id_bacias', lstnameBaciasV9));
print(mapsCol10gapfill9)
var mapsCol10gapfill = mapsCol10gapfill10.merge(mapsCol10gapfill5).merge(mapsCol10gapfill9)
print(  "show metadado da versão 10 do mapa Gap-fill ", mapsCol10gapfill);

mapsCol10gapfill = mapsCol10gapfill.max();
print(" visualizar ações de mapa mix", mapFiltered);
var collectionGEE = ee.ImageCollection(param.asset_collectionId)
                        .filter(ee.Filter.bounds(FeatColbacia.geometry()))
                        .select(spectralBands);  
var mosaicMapB = ee.ImageCollection(param.asset_mosaic)
                            .filter(ee.Filter.inList('biome', param.biomas))
                            .filter(ee.Filter.inList('satellite', lstSat))
                            .filterBounds(FeatColbacia.geometry())
var shp_estradas = ee.FeatureCollection(param.asset_estradas);                            

param.nyears.slice(0, 5).forEach(function(yyear){
    var banda_activa = 'classification_' + yyear;
    var tmp_img = mapFiltered.select(banda_activa);
    var tmp_bef = mapsCol10Bef.select(banda_activa);
    var raster_fires_year = raster_fires.select('burned_area_' + yyear);
    var mapsCol10gapfill_year = mapsCol10gapfill.select(banda_activa);
    var dateStart = ee.Date.fromYMD(parseInt(yyear), 1, 1);
    var dateEnd = ee.Date.fromYMD(parseInt(yyear), 12, 31);
    print(yyear, dateStart);
    
    var mosGEEyy = collectionGEE.filter(ee.Filter.date(dateStart, dateEnd)).median();
    var mosMByy =  mosaicMapB.filter(ee.Filter.eq('year', parseInt(yyear))).mosaic();
    
    Map.addLayer(mosMByy, visualizar.visMosaic, 'mosMP_' + yyear, false);
    Map.addLayer(mosGEEyy, visualizar.vismosaicoGEE, 'mosEE_' + yyear, false);
    Map.addLayer(tmp_img, visualizar.visclassCC, 'cc_' + yyear, false);
    Map.addLayer(tmp_bef, visualizar.visclassCC, 'cc_bef_' + yyear, false);
    Map.addLayer(mapsCol10gapfill_year, visualizar.visclassCC, 'cc_Gap-fill_' + yyear, false);
    Map.addLayer(raster_fires_year.selfMask(), {max: 1, palette: 'FF0000'}, "map_Fire " + yyear, false);
})





Map.addLayer(shp_estradas, {'color': '000000'}, estradas)
Map.addLayer(geom_marco, {}, 'bacia rev', false);
Map.addLayer(bioma_caatinga, {}, 'bioma Caatinga', false);