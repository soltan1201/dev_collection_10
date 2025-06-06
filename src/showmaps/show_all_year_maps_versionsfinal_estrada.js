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
    asset_MapMerger : 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/MergerV6',
    asset_MapGapFill : 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Gap-fill',
    asset_estrada_buffer: 'projects/mapbiomas-arida/shp_estradas_dnit_caat_buffer',
    assetrecorteCaatCerrMA : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/recorteCaatCeMA',
    asset_bacias_raster: 'projects/ee-solkancengine17/assets/bacias_raster_Caatinga_49_regions',
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
    listaNameBacias: [

    ],
}

var lstSat = ["l5","l7","l8"];
var lstnameBaciasV9 = ["7754","773","761112"];
var lstnameBaciasG = ["7754","773","761112","7591","7613","7746","7741","7581","757"];
var bioma_caatinga = ee.FeatureCollection(param.asset_caat_buffer);
var FeatColbacia = ee.FeatureCollection(param.assetBacia)
                        // .filter(ee.Filter.eq('nunivotto4', selBacia));
print("bacia selecionada ", FeatColbacia);
Map.addLayer(FeatColbacia, {color: 'green'}, 'bacias', false);
var baciaRaster = FeatColbacia.reduceToImage(['id_codigo'], ee.Reducer.first()).gt(0);
var geom_marco = FeatColbacia.filter(ee.Filter.inList('nunivotto4', lstnameBaciasG));
///// -------------------------------------------///
var mapsCol10Gapfill9 = ee.ImageCollection(param.asset_MapGapFill)
                        .filter(ee.Filter.inList('id_bacias', lstnameBaciasV9))
                        .filter(ee.Filter.eq('version', 9));

var mapsCol10Gapfill1 = ee.ImageCollection(param.asset_MapGapFill)
                            .filter(ee.Filter.eq('version', 10));
var mapsCol10Gapfill7 = ee.ImageCollection(param.asset_MapGapFill)
                        .filter(ee.Filter.inList('id_bacias', lstnameBaciasG).not())
                        .filter(ee.Filter.eq('version', 7));
var mapFiltGapFill = mapsCol10Gapfill7.merge(mapsCol10Gapfill9).merge(mapsCol10Gapfill1);

print(" mapFiltGapFill ", mapFiltGapFill.aggregate_histogram('version'));

var mapCol10Merger = ee.ImageCollection(param.asset_MapMerger)                        
                        .filter(ee.Filter.eq('version', 12));
print(  "show metadado da versão 12 merger ", mapCol10Merger);

mapFiltGapFill = mapFiltGapFill.max();//.select('classification')
mapCol10Merger = mapCol10Merger.max();

print(" visualizar as informações de mapa mix", mapFiltGapFill);
var collectionGEE = ee.ImageCollection(param.asset_collectionId)
                        .filter(ee.Filter.bounds(FeatColbacia.geometry()))
                        .select(spectralBands);  
var mosaicMapB = ee.ImageCollection(param.asset_mosaic)
                            .filter(ee.Filter.inList('biome', param.biomas))
                            .filter(ee.Filter.inList('satellite', lstSat))
                            .filterBounds(FeatColbacia.geometry())
var shp_estrada = ee.FeatureCollection(param.asset_estrada_buffer);

param.nyears.slice(0, 5).forEach(function(yyear){
    var banda_activa = 'classification_' + yyear;
    var tmp_img = mapCol10Merger.select(banda_activa);
    var tmp_bef = mapFiltGapFill.select(banda_activa);

    var dateStart = ee.Date.fromYMD(parseInt(yyear), 1, 1);
    var dateEnd = ee.Date.fromYMD(parseInt(yyear), 12, 31);
    print(yyear, dateStart);
    
    var mosGEEyy = collectionGEE.filter(ee.Filter.date(dateStart, dateEnd)).median();
    var mosMByy =  mosaicMapB.filter(ee.Filter.eq('year', parseInt(yyear))).mosaic();
    
    Map.addLayer(mosMByy, visualizar.visMosaic, 'mosMP_' + yyear, false);
    Map.addLayer(mosGEEyy, visualizar.vismosaicoGEE, 'mosEE_' + yyear, false);
    Map.addLayer(tmp_img, visualizar.visclassCC, 'merger_' + yyear, false);
    Map.addLayer(tmp_bef, visualizar.visclassCC, 'gapfil_' + yyear, false);
})

Map.addLayer(geom_marco, {}, 'bacia rev');
Map.addLayer(bioma_caatinga, {}, 'bioma Caatinga');
Map.addLayer(shp_estrada, {color: '#191A1BFF'}, 'estrada');