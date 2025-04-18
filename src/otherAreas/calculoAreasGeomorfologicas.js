/**
 * @description
 *    calculate area
 * 
 * @author
 *    João Siqueira
 * 
 */


var vis = {
    vis_aspect: {
        "opacity":1,
        "bands":["constant"],
        "min":0,"max":9,
        "palette":[
            "ffffff","9b9a6c","ff0202","ff3918","f3f70b",
            "9df315","08ffff","1dad6b","384895","9a3fff"
        ]
    },
    visHipso: {
        palette: ['fffdb1','00ffff','ffff00','ff0000','ffffff']
    },
    slope : {
        palette: [
            'white', 'fffdb1','ffc339','ff3918',
            'ac0000','5e0a02'
        ]
    },
    biomas_raster: {
        "opacity": 1,
        "bands":["first"],
        "min":1, "max": 6, 
        "gamma":1
    },
    morfologia: {
        min: 1, max: 9,
        palette: [
            '#449C1D', '#D4B983', '#C6A23E', '#A7770F', '#EDEC83', 
            '#A4120F', '#82AF4F', '#a83800', '#ff73df'
        ]
    }
}

/**
 * 
 */
// Territory image
// Scripts de Marcos 
// https://code.earthengine.google.com/f7288936e9b3630ad9069fdb8da2f126


var param = {
    asset_semiarido_old: 'projects/mapbiomas-workspace/AUXILIAR/semiarido',
    asset_semiarido: 'projects/mapbiomas-workspace/AUXILIAR/SemiArido_2024',
    asset_geomorf: 'projects/mapbiomas-workspace/AUXILIAR/ANALISES/cat33_geomorf_IBGE_3_WGS84_com_IDclass',
    "BR_ESTADOS_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_ESTADOS_2022",
    driverFolder: 'AREA-EXP-SEMIARIDO',
    scale: 30
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
    '17': 'TOCANTINS',
    '52': 'GOIÁS'
}

// Image area in km2
var pixelArea = ee.Image.pixelArea().divide(10000);

// Geometry to export
// var geometry = mapbiomas.geometry();

/**
 * Convert a complex ob to feature collection
 * @param obj 
 */

// ##############################################
// ###     Helper function
// ###    @param item 
// ##############################################
function convert2featCollection (item){
    var item = ee.Dictionary(item)
    var feature = ee.Feature(ee.Geometry.Point([0, 0])).set(
        'classe', item.get('classe'),"area", item.get('sum'))
        
    return feature;
}
/**
 * Calculate area crossing a cover map (deforestation, mapbiomas)
 * and a region map (states, biomes, municipalites)
 * @param image 
 * @param pixelArea 
 * @param geometry
 */
var calculateArea = function (image, pixelArea, geometry) {

    pixelArea = pixelArea.addBands(image.rename('classe')).clip(geometry);
    var reducer = ee.Reducer.sum().group(1, 'classe');
    var optRed = {
        'reducer': reducer,
        'geometry': geometry,
        'scale': param['scale'],
        'bestEffort': true, 
        'maxPixels': 1e13
    }    
    var areas = pixelArea.reduceRegion(optRed)

    areas = ee.List(areas.get('groups')).map(convert2featCollection)
    areas = ee.FeatureCollection(areas)    
    return areas
};


var shpSemiarido_old = ee.FeatureCollection(param.asset_semiarido_old);
var shpSemiarido = ee.FeatureCollection(param.asset_semiarido).geometry()
var masc_recorte = (ee.FeatureCollection([ee.Feature(shpSemiarido, {'valor': 1})])
                        .reduceToImage(['valor'], ee.Reducer.first()))

// var geomorfologia = ee.Image(param.asset_geomorf).updateMask(biomasCaat);
var feat_geom = ee.FeatureCollection(param.asset_geomorf)//.updateMask(biomasCaat);
print("show geomorfologia ", feat_geom.limit(4));
var geomorfologia = feat_geom.reduceToImage(['cd_comp_id'], ee.Reducer.first());
geomorfologia = geomorfologia.updateMask(masc_recorte)
var shpEstados = ee.FeatureCollection(param.BR_ESTADOS_2022);

var limite = ee.Image().byte().paint({
    featureCollection: shpSemiarido,
    color: 1,
    width: 2.5
});
var limiteOld = ee.Image().byte().paint({
    featureCollection: shpSemiarido_old,
    color: 1,
    width: 1.5
});

Map.addLayer(ee.Image.constant(1), {min:0, max: 1}, 'base');
Map.addLayer(geomorfologia, vis.morfologia, 'geomorfologia para col.9', true);
Map.addLayer(limite, {palette: '#484030'}, 'semiarido');
Map.addLayer(limiteOld, {palette: '#003434'}, 'semiarido_old');

var areaGeral = ee.FeatureCollection([]) ;
var lstEstCruz = ['17','21','22','23','24','25','26','27','28','29','31','32','52'];

lstEstCruz.forEach(function(estadoCod){
    print( "processing Estado" +  dictEst[estadoCod] + " with code " + estadoCod)
    var shpEstado = shpEstados.filter(ee.Filter.eq('CD_UF', estadoCod))
    var ppixelArea = ee.Image.pixelArea().divide(10000).updateMask(masc_recorte)
    var areaXestado = calculateArea(geomorfologia, ppixelArea, shpEstado.geometry())
    areaXestado = areaXestado.map(function(feat){
        return  feat.set(
                    'region', 'Semiarido', 
                    'estado_name', dictEst[estadoCod], 
                    'estado_codigo', estadoCod)
    })
    print("adding area ")
    areaGeral = areaGeral.merge(areaXestado)
})

// areaGeral = ee.FeatureCollection(areaGeral).flatten();

Export.table.toDrive({
    collection: areaGeral,
    description: 'area_geomorfologicas_Semiarido_state',
    folder: param.driverFolder,
    fileNamePrefix: 'area_geomorfologicas_Semiarido_state',
    fileFormat: 'CSV'
});
