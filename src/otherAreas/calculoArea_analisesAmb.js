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
            '#a8a800', '#a8a800', '#e2b9f8', '#e2b9f8', '#fa9d66', '#fa9d66',
            '#ffd37f', '#bee8ff', '#a83800', '#ff73df'
        ]
    }
}

// Change the scale if you need.
var scale = 30;

// Define a list of years to export
var years = [
    '1985', '1986', '1987', '1988', '1989', '1990', '1991', '1992',
    '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000',
    '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008',
    '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016',
    '2017', '2018', '2019', '2020', '2021', '2022', '2023'
];

// Define a Google Drive output folder 
var driverFolder = 'AREA-EXPORT_col9';

/**
 * 
 */
// Territory image
var territory = bioma_terreno;

// LULC mapbiomas image
var mapbiomas_orig = class_col90;
var class_now = [3,4,5,6,49,11,12,32,29,50,13,15,19,39,20,40,62,41,46,47,35,48,9,21,23,24,30,25,33,31];
var new_class = [3,4,5,6,49,11,12,32,29,50,13,15,18,18,18,18,18,18,18,18,18,18,9,21,23,24,30,25,33,31];
var param = {
    asset_hipso : 'projects/mapbiomas-workspace/AUXILIAR/RASTER/hipso_class_temp',
    asset_slope: 'projects/mapbiomas-workspace/AUXILIAR/RASTER/slope_class_temp_v2',
    asset_aspect : 'projects/mapbiomas-workspace/AUXILIAR/RASTER/aspect_class_temp_v2',
    asset_biomas_raster: 'projects/mapbiomas-workspace/AUXILIAR/RASTER/Bioma250mil',
    asset_biomas_shp: 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
    "BR_ESTADOS_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_ESTADOS_2022",
    'asset_cobertura_col90': "projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1",
    'asset_geomorf': 'projects/mapbiomas-workspace/AUXILIAR/ANALISES/cat33_geomorf_IBGE_3_WGS84_com_IDclass',
}
// remap_level2
var anos = [
    1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,
    1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,
    2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023
];
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
var region = 'caatinga';
var rasterGeo = null;
var shpGeo = null;

if (region == 'caatinga'){
    // select caatinga biomas = 2
    shpGeo = ee.FeatureCollection(param.asset_biomas_shp).filter(ee.Filter.eq('CD_Bioma', 2)).geometry();
    rasterGeo = ee.Image(param.asset_biomas_raster).eq(2);

}else{
    shpGeo = ee.FeatureCollection(param['asset_semiarido']).geometry()
    rasterGeo = (ee.FeatureCollection([ee.Feature(shpSemiarido, {'valor': 1})])
                        .reduceToImage(['valor'], ee.Reducer.first()))
}


var feat_geom = ee.FeatureCollection(param.asset_geomorf)
// # print("show geomorfologia ", feat_geom.size().getInfo());
var geomorfologia = feat_geom.reduceToImage(['cd_comp_id'], ee.Reducer.first())
geomorfologia = geomorfologia.rename('class_morfo').updateMask(rasterGeo)
var hipso_class = ee.Image(param.asset_hipso).updateMask(rasterGeo);
var slope_class = ee.Image(param.asset_slope).updateMask(rasterGeo);
var aspect_class = ee.Image(param.asset_aspect).updateMask(rasterGeo);
var bioma_terreno = rasterGeo.add(slope_class).updateMask(rasterGeo);

Map.addLayer(ee.Image.constant(1), {min:0, max: 1}, 'base');
// Map.addLayer(hipso_class, vis.visHipso, 'Classes Hipsométricas para col. 9', true);
// Map.addLayer(slope_class, vis.slope, 'Classes de Declividade para col. 9', true);
// Map.addLayer(aspect_class, vis.vis_aspect, 'Orientação de Vertentes para col. 9', true);
Map.addLayer(shpGeo, {color: 'black'}, 'biomas',false);
Map.addLayer(geomorfologia, vis.morfologia, 'geomorfologia para col.9', true);
// Map.addLayer(rasterGeo.selfMask(), vis.biomas_raster, 'raster_biomas');
// Map.addLayer(bioma_terreno);


var class_col90 = ee.Image(param.asset_cobertura_col90)
                           .updateMask(rasterGeo);
var mapbiomas = null;            
years.forEach(function(nyear){
    // print(ano)
    var mapbiomas_ano = class_col90.select('classification_'+ nyear)
                              .remap(class_now, new_class)
                              .rename('classification_' + nyear)
    if (nyear == '1985'){ 
        mapbiomas = mapbiomas_ano; 
    }  
    else {
        mapbiomas = mapbiomas.addBands(mapbiomas_ano); 
    }
});
print('show new map raster mapbiomas', mapbiomas);


// Image area in km2
var pixelArea = ee.Image.pixelArea().divide(10000);

// Geometry to export
// var geometry = mapbiomas.geometry();

/**
 * Convert a complex ob to feature collection
 * @param obj 
 */
var convert2table = function (obj) {

    obj = ee.Dictionary(obj);

    var territory = obj.get('territory');

    var classesAndAreas = ee.List(obj.get('groups'));

    var tableRows = classesAndAreas.map(
        function (classAndArea) {
            classAndArea = ee.Dictionary(classAndArea);

            var classId = classAndArea.get('class');
            var area = classAndArea.get('sum');

            var tableColumns = ee.Feature(null)
                .set('territory', territory)
                .set('class', classId)
                .set('area', area);

            return tableColumns;
        }
    );

    return ee.FeatureCollection(ee.List(tableRows));
};

/**
 * Calculate area crossing a cover map (deforestation, mapbiomas)
 * and a region map (states, biomes, municipalites)
 * @param image 
 * @param territory 
 * @param geometry
 */
var calculateArea = function (image, territory, geometry, shpState) {
    
    var recorteGeo = geometry.intersection(shpState.geometry())
    var masc_recorte = (ee.FeatureCollection([ee.Feature(recorteGeo, {'valor': 1})])
                        .reduceToImage(['valor'], ee.Reducer.first()))
    var reducer = ee.Reducer.sum().group(1, 'class').group(1, 'territory');

    var territotiesData = pixelArea.addBands(territory).addBands(image)
        .updateMask(masc_recorte)
        .reduceRegion({
            reducer: reducer,
            geometry: recorteGeo,
            scale: scale,
            maxPixels: 1e12
        });

    territotiesData = ee.List(territotiesData.get('groups'));

    var areas = territotiesData.map(convert2table);

    areas = ee.FeatureCollection(areas).flatten();

    return areas;
};

var shpEstados = ee.FeatureCollection(param.BR_ESTADOS_2022)
// lstEstCruz = [21,22,23,24,25,26,27,28,29,31,32]
var lstEstCruz = ['17','21','22','23','24','25','26','27','28','29','31','32','52']
var areaGeral = ee.FeatureCollection([])
lstEstCruz.forEach(function(estadoCod){
    print("processing Estado " + dictEst[estadoCod] + "  with code " + estadoCod)
    var shpEstado = shpEstados.filter(ee.Filter.eq('CD_UF', estadoCod))
    var areas = years.map(
        function (year) {
            var image = mapbiomas.select('classification_' + year);
            var areas = calculateArea(image, geomorfologia.rename('morfo'), shpGeo, shpEstado);
            // set additional properties
            areas = areas.map(
                function (feature) {
                    return feature.set(
                                    'year', year,
                                    'region', 'Semiarido', 
                                    'estado_name', dictEst[estadoCod], 
                                    'estado_codigo', estadoCod
                                    );
                }
            );

            return areas;
        }
    );
    areas = ee.FeatureCollection(areas).flatten();
    areaGeral = areaGeral.merge(areas)
})


Export.table.toDrive({
    collection: areaGeral,
    description: 'area_col9_Semiarido_geomorfologia',
    folder: driverFolder,
    fileNamePrefix: 'area_col9_Semiarido_geomorfologia',
    fileFormat: 'CSV'
});


