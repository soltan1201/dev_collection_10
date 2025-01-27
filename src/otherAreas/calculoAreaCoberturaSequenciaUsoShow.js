
var vis = {
    dinamica: {
        min: 1, max: 25,
        palette: [
            '#38a800', '#ff8150 ', '#d7c29e', '#d7c29e', '#cdaa66', '#cdaa66', '#a87000', '#ffff00', '#6e57d2 ', 
            '#6e57d2 ', '#6e57d2 ', '#6e57d2 ', '#a80000', '#a80000', '#abcd66', '#abcd66', '#abcd66', '#abcd66', 
            '#abcd66', '#160042', '#107c10', '#107c10', '#107c10', '#800000', '#393c3e'
        ]
    }
}

// ##############################################
// ###     Helper function
// ###    @param item 
// ##############################################
function convert2featCollection (item){
    item = ee.Dictionary(item);
    var feature = ee.Feature(ee.Geometry.Point([0, 0])).set(
        'classe', item.get('classe'),"area", item.get('sum'));
        
    return feature;
}
// #########################################################################
// ####     Calculate area crossing a cover map (deforestation, mapbiomas)
// ####     and a region map (states, biomes, municipalites)
// ####      @param image 
// ####      @param geometry
// #########################################################################
// # https://code.earthengine.google.com/5a7c4eaa2e44f77e79f286e030e94695
// # https://code.earthengine.google.com/?accept_repo=users%2Fmapbiomas%2Fuser-toolkit&scriptPath=users%2Fmapbiomas%2Fuser-toolkit%3Amapbiomas-user-toolkit-calculate-area.js
function calculateArea (image, pixelArea, geometry){
    pixelArea = pixelArea.addBands(image.rename('classe')).clip(geometry);
    var reducer = ee.Reducer.sum().group(1, 'classe');
    var optRed = {
        'reducer': reducer,
        'geometry': geometry,
        'scale': param['scale'],
        'bestEffort': true, 
        'maxPixels': 1e13
    };   
    var areas = pixelArea.reduceRegion(optRed);

    areas = ee.List(areas.get('groups')).map(convert2featCollection);
    areas = ee.FeatureCollection(areas) ;  
    return areas;
}
var param = {
    'asset_cobertura_col90': "projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1",
    'asset_matopiba': 'projects/mapbiomas-fogo/assets/territories/matopiba',
    "BR_ESTADOS_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_ESTADOS_2022",
    "br_estados_raster": 'projects/mapbiomas-workspace/AUXILIAR/estados-2016-raster',
    "BR_Municipios_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_Municipios_2022",
    "BR_Pais_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_Pais_2022",
    "Im_bioma_250" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/Im_bioma_250",
    'vetor_biomas_250': 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
    'biomas_250_rasters': 'projects/mapbiomas-workspace/AUXILIAR/RASTER/Bioma250mil',
    'classMapB': [3, 4, 5, 9, 12, 13, 15, 18, 18, 20, 21, 22, 23, 24, 25, 26, 29, 30, 31, 32, 33,
                      36, 39, 40, 41, 46, 47, 48, 49, 50, 62],
    'classNew':  [4, 4, 4, 4,  4,  4, 15, 18, 18, 18, 15, 22, 22, 22, 22, 33,  4, 22, 33, 4, 33,
                      18, 18, 18, 18, 18, 18, 18,  4,  12, 18],
    'lstYears': [
      1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998,
      1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 
      2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023
    ],
    'driverFolder': 'AREA-EXP-fireMATOPIBA',
    'scale': 30
}
var dictEst = {
    '21': 'MARANHÃO',
    '22': 'PIAUÍ',
    '23': 'CEARÁ',
    '24': 'RIO GRANDE DO NORTE',
    '25': 'PARAÍBA',
    '26': 'PERNAMBUCO',
    '27': 'ALAGOAS',
    '28': 'SERGIPE',
    '29': 'BAHIA',
    '31': 'MINAS GERAIS',
    '32': 'ESPÍRITO SANTO',
    '17': 'Tocantins',
}
Map.addLayer(ee.Image.constant(1), {min: 0, max: 1}, 'base')

function iterandoXanoImCruda (limiteEst, estadoCod){
    var est_raster = ee.Image(param.br_estados_raster).eq(parseInt(estadoCod));
    var biomas_raster = ee.Image(param.biomas_250_rasters).eq(2);
    var maskunico = est_raster.updateMask(biomas_raster);
    var pixelArea = ee.Image.pixelArea().updateMask(maskunico).divide(10000);
    
    var shpBioma = (
        ee.FeatureCollection(param.vetor_biomas_250)
                .filter(ee.Filter.eq('CD_Bioma', 2))
    );

    var recorteGeo = shpBioma.geometry().intersection(limiteEst.geometry());
    var areaEstado = ee.FeatureCollection([]);
    var imgDynamica = ee.Image.constant(0);

    param.lstYears.forEach(function (nyear){
        var nbandaCou = 'classification_' + String(nyear); 
        var nbandaBef = 'classification_' + String(nyear - 1);
        
        var imgCobCou = (
            ee.Image(param.asset_cobertura_col90)
                    .select(nbandaCou)
                    .remap(param.classMapB, param.classNew)
                    .updateMask(maskunico)
        ); 
        var imgCobBef = (
            ee.Image(param.asset_cobertura_col90)
                    .select(nbandaBef)
                    .remap(param.classMapB, param.classNew)
                    .updateMask(maskunico)
        );

        imgDynamica = (
            imgDynamica
                .where(imgCobBef.eq(4).and( imgCobCou.eq(15)), 1)    // Desmatamento to pasture
                .where(imgCobBef.eq(4).and( imgCobCou.eq(18)), 2)    // Desmatamento to agriculture
                .where(imgCobBef.eq(4).and( imgCobCou.eq(21)), 3)    // Desmatamento to Mosaic of uses
                .where(imgCobBef.eq(18).and(imgCobCou.eq(15)), 4)    // agriculture to pasture
                .where(imgCobBef.eq(18).and(imgCobCou.eq(21)), 5)    // agriculture to Mosaic of uses
                .where(imgCobBef.eq(18).and(imgCobCou.eq(4) ), 6)      // agriculture to Regeneration
                .where(imgCobBef.eq(15).and(imgCobCou.eq(18)), 7)      // Pasture to agriculture
                .where(imgCobBef.eq(15).and(imgCobCou.eq(21)), 8)      // Pasture to Mosaic of uses
                .where(imgCobBef.eq(15).and(imgCobCou.eq(4) ), 9)      // Pasture to Regeneration
                .where(imgCobBef.eq(21).and(imgCobCou.eq(15)), 10)     // Mosaic of uses to pasture
                .where(imgCobBef.eq(21).and(imgCobCou.eq(18)), 11)     // Mosaic of uses to agriculture
                .where(imgCobBef.eq(21).and(imgCobCou.eq(4) ), 12)     // Mosaic of uses to Regeneration
                .where(imgDynamica.eq(2).and(imgCobCou.eq(15)), 13)    // Desmatamento to agriculture to pasture
                .where(imgDynamica.eq(2).and(imgCobCou.eq(21)), 14)    // Desmatamento to agriculture to Mosaic of uses
                .where(imgDynamica.eq(2).and(imgCobCou.eq(4) ), 15)    // Desmatamento to agriculture to Regeneration
                .where(imgDynamica.eq(3).and(imgCobCou.eq(18)), 16)    // Desmatamento to Mosaic of uses to agriculture 
                .where(imgDynamica.eq(3).and(imgCobCou.eq(15)), 17)    // Desmatamento to Mosaic of uses to pasture 
                .where(imgDynamica.eq(3).and(imgCobCou.eq(4) ), 18)    // Desmatamento to Mosaic of uses to Regeneration 
                .where(imgDynamica.eq(1).and(imgCobCou.eq(21)), 19)    // Desmatamento to pasture to Mosaic of uses
                .where(imgDynamica.eq(1).and(imgCobCou.eq(18)), 20)    // Desmatamento to pasture to agriculture 
                .where(imgDynamica.eq(1).and(imgCobCou.eq(4) ), 21)    // Desmatamento to pasture to Regeneration                 
                .where(imgDynamica.eq(11).and(imgCobCou.eq(15)), 22)   // Mosaic of uses to agriculture to pasture
                .where(imgDynamica.eq(10).and(imgCobCou.eq(18)), 23)   // Mosaic of uses to pasture to agriculture 
                .where(imgDynamica.eq(7).and(imgCobCou.eq(15) ), 24)   // pasture to agriculture to pasture              
                .where(imgDynamica.eq(4).and(imgCobCou.eq(18) ), 25)   // agriculture to pasture to agriculture                 
                
            );
        });
    imgDynamica = imgDynamica.rename('classe').updateMask(maskunico);

    var areaTemp = calculateArea (imgDynamica.selfMask(), pixelArea, recorteGeo);        
    areaTemp = areaTemp.map( 
                    function (feat){ 
                        return feat.set(
                            'region', 'Caatinga', 
                            'estado_name', dictEst[String(estadoCod)], //# colocar o nome do estado
                            'estado_codigo', estadoCod
                        )
                    }
                );
    areaEstado = areaEstado.merge(areaTemp); 
    Map.addLayer(imgDynamica.selfMask(), vis.dinamica, 'imgDynamica');
    var lineCaat = ee.Image().byte().paint({
        featureCollection: shpBioma,
        color: 1,
        width: 1.5
    });
    Map.addLayer(lineCaat, {palette: '000000'}, 'shp Caat');
    
    return areaEstado;
}
// #exporta a imagem classificada para o asset
function processoExportar(areaFeat, nameT){      
    var optExp = {
          'collection': areaFeat, 
          'description': nameT, 
          'folder': param.driverFolder        
        };    
    Export.table.toDrive(optExp);
    print("salvando ... " + nameT + "..!");   
}
// # bioma = 'Caatinga'
// # rasterLimit = ee.Image(param['biomas_250_rasters']).eq(2)

var shpEstados = ee.FeatureCollection(param['BR_ESTADOS_2022'])
var lstEstCruz = ['22','23','24','25','26','27','28','29','31','32']

var areaGeral = ee.FeatureCollection([]) 

lstEstCruz.forEach( function(estadoCod){    
    print("processing Estado " + dictEst[String(estadoCod)] + " with code " + String(estadoCod))
    var shpEstado = shpEstados.filter(ee.Filter.eq('CD_UF', estadoCod))
    var areaXestado = iterandoXanoImCruda(shpEstado, estadoCod)
    print("adding area ")
    // # areaGeral = areaGeral.merge(areaXestado)

    print("exportando a área geral ")
    processoExportar(areaXestado, 'area_cobertura_col90_state_caatinga_' + String(estadoCod))

})