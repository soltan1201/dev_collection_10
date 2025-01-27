//https://code.earthengine.google.com/a439f870a02b371daf094c5b6cf6de34
//https://code.earthengine.google.com/c6be8cee51ed15cb9cd80c031f8f2729
var palettes = require('users/mapbiomas/modules:Palettes.js');
var text = require('users/gena/packages:text')

var visualizar = {
    visclassCC: {
            "min": 0, 
            "max": 62,
            "palette":  palettes.get('classification8'),
            "format": "png"
    },
    visMosaic: {
        min: 0,
        max: 2000,
        bands: ['red_median', 'green_median', 'blue_median']
    },
    visIncident : {
        max: 5,
        min: 1,
        palette: ['#faf3dd','#c8d5b9','#f19c79','#fec601','#013a63']
    },
    props: {  
        textColor: 'ff0000', 
        outlineColor: 'ffffff', 
        outlineWidth: 1.5, 
        outlineOpacity: 0.2
    }
} 

var param = { 
    assetMapC7: 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
    assetMapC8: 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    assset_Frequency: 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/FrequencyV3',
    asset_Temporal : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/TemporalV3',
    asset_mata_atlantica: 'projects/mapbiomas-workspace/COLECAO9/pos_classificacao-ma/MA_col9_p10e_v135',
    asset_baciasN1raster: 'projects/mapbiomas-workspace/AUXILIAR/bacias-nivel-1-raster',
    asset_points_campo: 'users/nerivaldogeo/pontos_campo_caatinga',
    asset_gedi: 'users/potapovpeter/GEDI_V27',
    asset_bioma_raster : 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41',
    assetIm: 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',    
    assetBacia: "projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga", 
    asset_caat_buffer: 'users/CartasSol/shapes/caatinga_buffer5km',   
    anos: ['1985','1986','1987','1988','1989','1990','1991','1992','1993','1994',
           '1995','1996','1997','1998','1999','2000','2001','2002','2003','2004',
           '2005','2006','2007','2008','2009','2010','2011','2012','2013','2014',
           '2015','2016','2017','2018','2019','2020','2021','2022'],
    bandas: ['red_median', 'green_median', 'blue_median'],
    
    listaNameBacias: [
        '741','7421','7422','744','745','746','7492','751','752',
        '753', '754','755','756','757','758','759','7621','7622','763',
        '764','765','766','767','771','772','773', '7741','7742','775',
        '776','777','778','76111','76116','7612','7613','7614','7615',
        '7616','7617','7618','7619'
    ],
    classMapB: [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,39,40,41,46,47,48,49,50,62],
    classNew:  [3, 4, 3, 3,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33,21,21,21,21,21,21,21, 3,12,21],
    classesMapAmp:  [3, 4, 3, 3,12,12,15,18,18,18,21,22,22,22,22,33,29,22,33,12,33,18,18,18,18,18,18,18, 3,12,18],
}
var savanaYY, usoYY, diferenceYY,banda_before, diference;
var lstYears = [2023, 2022, 2021,2020,2019,2018];
var banda_activa = 'classification_2023';
var version = 18;
var teste = true;
var imgMapCol9Tp = ee.ImageCollection(param.asset_Temporal)
                        .filter(ee.Filter.eq('version', version))
                        .filter(ee.Filter.eq('janela', 3))
var imgMapCol9FQ = ee.ImageCollection(param.assset_Frequency)
                        .filter(ee.Filter.eq('version', version))
                        // .filter(ee.Filter.eq('type_filter', 'frequence'))
                        // .select(bandas_activas);
var asset_change = "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV3"; // /filterSPU_BACIA_7616_GTB_V18_step1";
var mapsUseChange = ee.ImageCollection(asset_change).filter(ee.Filter.eq('filter', 'spatial_use'));
if (teste){

    var savanaTemp = imgMapCol9Tp.select(banda_activa).min()
    var savana2022 = imgMapCol9FQ.select(banda_activa).min().eq(4)
                        .subtract(imgMapCol9FQ.select('classification_2022').min().eq(4)) ;
    var uso2022 = imgMapCol9FQ.select('classification_2022').min().eq(21)
                            .subtract(imgMapCol9FQ.select(banda_activa).min().eq(21));
    var diference = savana2022.eq(1).subtract(uso2022.eq(1));

    // var change_uso_YYConnected = uso2022.connectedPixelCount(10, true)           
    // var mask_Uso_kernel = uso2022.updateMask(change_uso_YYConnected.lte(min_connect_pixel))
    // var alertas21 = uso2022.updateMask(mask_Uso_kernel)
    var newMask = uso2022.focalMin(2).focalMax(4);
    var maskPixelsRem = uso2022.updateMask(newMask.eq(0));
    var newCollection = imgMapCol9FQ.select(banda_activa).min().where(maskPixelsRem, 21);
    
    Map.addLayer(imgMapCol9FQ.select('classification_2022').min(), visualizar.visclassCC, 'class 2022');
    Map.addLayer(imgMapCol9FQ.select(banda_activa).min(), visualizar.visclassCC, 'class 2023');
    Map.addLayer(newCollection, visualizar.visclassCC, 'class mod 2023');    
    Map.addLayer(mapsUseChange.select(banda_activa).min(), visualizar.visclassCC, 'class mod sav 2023');
    Map.addLayer(savanaTemp.updateMask(uso2022), visualizar.visclassCC, 'Pixels temp', false);
    Map.addLayer(uso2022.selfMask(), {palette: ['black'], min:-1, max:1}, 'Uso -');
    Map.addLayer(maskPixelsRem.selfMask(), {palette: ['red'], min:-1, max:1}, 'Alertas21 -');
    Map.addLayer(savana2022.selfMask(), {palette: ['2E3D0E'], min:-1, max:1}, 'Savana +', false);
   
    
    
    
    

}else{

    var deltaSavMap = ee.Image.constant(0);
    var deltaUso = ee.Image.constant(0);
    lstYears.slice(0, 5).forEach(
        function(yyear){
            banda_activa = 'classification_' + String(yyear);
            banda_before = 'classification_' + String(yyear - 1);
            savanaYY = imgMapCol9FQ.select(banda_activa).min().eq(4);    // savana no ano T
            usoYY = imgMapCol9FQ.select(banda_before).min().eq(21);      // Uso no ano T -1
            diference = savanaYY.subtract(usoYY);    // captura toda a savana que aumento nesse ano 
            deltaSavMap = deltaSavMap.add(diference.eq(1));
            deltaUso = deltaUso.add(diference.eq(-1));
    })
    var year19Maps = imgMapCol9FQ.select('classification_2019').min();
    var year23Maps = imgMapCol9FQ.select('classification_2023').min()
    Map.addLayer(year19Maps, visualizar.visclassCC, 'class 2019')
    Map.addLayer(year23Maps, visualizar.visclassCC, 'class 2023')
    Map.addLayer(deltaSavMap.selfMask(), visualizar.visIncident, 'dife Savana')
    Map.addLayer(deltaUso.selfMask(), visualizar.visIncident, 'dife Uso')
}