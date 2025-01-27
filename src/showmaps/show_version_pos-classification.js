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
function set_class_level1(feat){
    var dict_points = ee.Dictionary({
            'afloramentos': 29,
            'agricultura': 21,
            'agua': 33,
            'aquicultura': 33,
            'campo': 12,
            'carnaúbas': 21,
            'desmatamento': 22 ,
            'exotica': 21,
            'floresta': 3,
            'mineração': 22,
            'mosaico de uso': 21,
            'pastagem': 21,
            'regeneração savana': 4,
            'savana': 4,
            'solo exposto': 22,
            'urbano': 22,
            'áreas não vegetadas': 22
    })
    return feat.set('level_1', dict_points.get(feat.get('classe')))
}
var param = { 
    assetMapC7: 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
    assetMapC8: 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    asset_MapC9X : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVX',
    asset_MapC9P : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVP',
    asset_MapC9Y : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVY',
    asset_ptosDifLapigvsCol7: 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/occTab_acc_Dif_Caat_mapbiomas_71_integration_v1',
    asset_ptosDifLapigvsCol8: 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/occTab_acc_Dif_Caat_mapbiomas_80_integration_v1',
    asset_Gapfill : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fill',   
    asset_Spatial : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Spatial', 
    asset_Temporal : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Temporal', 
    asset_Frequence: 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Frequency',
    assset_Frequency: 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/FrequencyV2',
    asset_mixed: 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExport',
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

function makeDiferencebettwenPoints(feat){ 
  
    var classRef = ee.Number(feat.get('CLASS_' + String(yearcourrent)));
    var classCf = ee.Number(feat.get('classification'))
    return feat.set('diferente', classRef.neq(classCf));
}


function get_layerIncidentes (mapYY71, mapYY80, mapYY90){
    mapYY71 = mapYY71.remap(param.classMapB, param.classNew);
    mapYY80 = mapYY80.remap(param.classMapB, param.classNew);
    var mapAdding = mapYY71.addBands(mapYY80).addBands(mapYY90);
    var incidentesMaps = mapAdding.reduce(ee.Reducer.countRuns())
                                    .subtract(1).rename('incidentes');
    var statesMaps = mapAdding.reduce(ee.Reducer.countDistinctNonNull()).rename('states');
    var modaMaps = mapAdding.reduce(ee.Reducer.mode());
    ///logica de definição de classes está embasada no fato de termos 3 coleções de entrada
    //para analisar mais coleções a logica precisa ser reestruturada
    var clas1_add = incidentesMaps.eq(0).selfMask();
    var clas2_add = incidentesMaps.eq(1).and(mapAdding.select(2).subtract(modaMaps).eq(0)).selfMask();
    var clas3_add = incidentesMaps.eq(1).and(mapAdding.select(0).subtract(modaMaps).eq(0)).selfMask();
    var clas4_add = incidentesMaps.eq(2).and(statesMaps.eq(2)).selfMask();
    var clas5_add = incidentesMaps.eq(2).and(statesMaps.eq(3)).selfMask();

    var outMaps = clas1_add.blend(clas2_add.multiply(2))
                    .blend(clas3_add.multiply(3))
                    .blend(clas4_add.multiply(4))
                    .blend(clas5_add.multiply(5))
                    .rename('classes');
    
    return outMaps
}

var selBacia = 'all';
var baciaProcura = '757';
var yearcourrent = 2020;
var version = 10;
var versnew = 13;
var assetCol9 = param.asset_MapC9X;
if (version > 5){
    assetCol9 = param.asset_MapC9P;
}
var biomaRaster = ee.Image(param.asset_bioma_raster).eq(5);
var banda_activa = 'classification_' + String(yearcourrent)
var FeatColbacia = ee.FeatureCollection(param.assetBacia);
var caatBuffer = ee.FeatureCollection(param.asset_caat_buffer).geometry();

var baciaRaster = ee.Image(param.asset_baciasN1raster);
var maskBacia = baciaRaster.eq(104).add(baciaRaster.eq(103))
                          .add(baciaRaster.eq(106)).add(baciaRaster.eq(107));
var imgGEDI = ee.ImageCollection(param.asset_gedi).mosaic().updateMask(biomaRaster);
var maskGEDI = imgGEDI.neq(0);
var pointsCampo = ee.FeatureCollection(param.asset_points_campo)
                    .filter(ee.Filter.neq('classe', null));
// pointsCampo = pointsCampo.map(set_class_level1);
print("show points collected in campo ", pointsCampo);
print("dictionary of property classe ", pointsCampo.aggregate_histogram('classe'));
// print("dictionary of property level 1 ", pointsCampo.aggregate_histogram('level_1'));
var featSearch = FeatColbacia.filter(ee.Filter.eq('nunivotto3', baciaProcura));

var imgMapCol71= ee.Image(param.assetMapC7).updateMask(maskBacia.gt(0))
                        .select(banda_activa);
var imgMapCol8= ee.Image(param.assetMapC8).updateMask(maskBacia.gt(0))
                        .select(banda_activa);
var imgMapCol9Yv15 = ee.ImageCollection(param.asset_MapC9Y)
                            .filter(ee.Filter.eq('version', 15))
                            .select(banda_activa).min();
var imgMapCol9GTB =  ee.ImageCollection(assetCol9)
                            .filter(ee.Filter.eq('version', version))
                            .filter(ee.Filter.eq("classifier", "GTB"))
                            .select(banda_activa);
var imgMapCol9GTBNew =  ee.ImageCollection(assetCol9)
                            .filter(ee.Filter.eq('version', versnew))
                            .filter(ee.Filter.eq("classifier", "GTB"))
                            .select(banda_activa);
var imgMapCol9RFNew =  ee.ImageCollection(assetCol9)
                            .filter(ee.Filter.eq('version', versnew))
                            .filter(ee.Filter.eq("classifier", "RF"))
                            .select(banda_activa);

print("  imgMapCol9GTB", imgMapCol9GTB);
var imgMapCol9GF = ee.ImageCollection(param.asset_Gapfill)
                        .filter(ee.Filter.eq('version', versnew))
                        .select(banda_activa);
var imgMapCol9SP = ee.ImageCollection(param.asset_Spatial)
                        .filter(ee.Filter.eq('version', versnew))
                        .select(banda_activa);
var imgMapCol9TP = ee.ImageCollection(param.asset_Temporal)
                        .filter(ee.Filter.eq('version', versnew))
                        .filter(ee.Filter.neq('janela', 4))
                        .select(banda_activa);
var imgMapCol9TPJ4 = ee.ImageCollection(param.asset_Temporal)
                        .filter(ee.Filter.eq('version', versnew))
                        .filter(ee.Filter.eq('janela', 4))
                        .select(banda_activa);
var imgMapCol9FQ = ee.ImageCollection(param.asset_Frequence)
                        .filter(ee.Filter.eq('version', versnew))
                        .select(banda_activa);
var imgMapmixed = ee.ImageCollection(param.asset_mixed)
                        .filter(ee.Filter.eq('version', version))
                        .map(function(img){
                            return ee.Image.cat(img).toByte();
                        })
                        .select(banda_activa);                        

var Mosaicos = ee.ImageCollection(param.assetIm).filter(
                        ee.Filter.eq('biome', 'CAATINGA')).select(param.bandas);
var poitsRefCol71compY = null;
var pointRefCol80compY = null;
var propYYPoints = ['CLASS_' + String(yearcourrent), 'classification_' +  String(yearcourrent)] ;
var poitsRefCol71comp = ee.FeatureCollection(param.asset_ptosDifLapigvsCol7).select(propYYPoints);
var pointRefCol80comp = ee.FeatureCollection(param.asset_ptosDifLapigvsCol8)
                            .select(propYYPoints).filterBounds(featSearch);
pointRefCol80comp = pointRefCol80comp.filter(ee.Filter.neq('CLASS_' + String(yearcourrent), 27));
print("pontos lapig ", pointRefCol80comp.limit(4));

var listAllClass =    [3,4,10,15,18,22,27,33];
var listAllClassrem = [3,4,12,21,21,22,27,33];
pointRefCol80comp = pointRefCol80comp.remap(listAllClass, listAllClassrem, 'CLASS_' + String(yearcourrent));

if(yearcourrent < 2022){
    poitsRefCol71compY = poitsRefCol71comp.filter(ee.Filter.eq('diference' + String(yearcourrent), true));
    pointRefCol80compY = pointRefCol80comp.filter(ee.Filter.eq('diference' + String(yearcourrent), true));
    // print(" size points filtered Col7.1", poitsRefCol71compY.size());
}else{
    print("We don´t have points of references in this year, sorry !");
}
// ========================================================================= //
// set as 'all' to show all map or set the basin from pamareter dictionary
// ========================================================================= //
var imgMapCol9GTBjoin = null;
var imgMapCol9FQjoin = null;
var imgMapCol9SPjoin = null;
var imgMapCol9TPjoin = null;
var imgMapCol9TPJ4join = null;
var imgMapCol9GFjoin = null;
var imgMapmixedJoin = null;
var ptosfromBacia = null;
var imgMapCol9GTBNjoin = null;
var imgMapCol9RFNjoin = null;


if (selBacia === 'all'){
    imgMapCol9GTBjoin = imgMapCol9GTB.min().updateMask(biomaRaster)
                                .remap(param.classMapB, param.classNew);
    imgMapCol9SPjoin = imgMapCol9SP.min().updateMask(biomaRaster);
    imgMapCol9GFjoin = imgMapCol9GF.max().updateMask(biomaRaster);
    imgMapCol9TPjoin = imgMapCol9TP.min().updateMask(biomaRaster);
    imgMapCol9TPJ4join = imgMapCol9TPJ4.min().updateMask(biomaRaster);
    imgMapCol9FQjoin = imgMapCol9FQ.min().updateMask(biomaRaster);
    imgMapmixedJoin = imgMapmixed.min().updateMask(biomaRaster);
    imgMapCol9GTBNjoin = imgMapCol9GTBNew.min().updateMask(biomaRaster)
                                .remap(param.classMapB, param.classNew);
    imgMapCol9RFNjoin = imgMapCol9RFNew.min().updateMask(biomaRaster)
                                .remap(param.classMapB, param.classNew);
    ptosfromBacia = poitsRefCol71comp;
}else{
    FeatColbacia = FeatColbacia.filter(ee.Filter.eq('nunivotto3', selBacia));   
    imgMapCol9GTBjoin = imgMapCol9GTB.filter(ee.Filter.eq("id_bacia", selBacia))
                                .remap(param.classMapB, param.classNew); 
    imgMapCol9SPjoin = imgMapCol9SP.filter(ee.Filter.eq("id_bacia", selBacia)); 
    imgMapCol9GFjoin = imgMapCol9GF.filter(ee.Filter.eq("id_bacia", selBacia)); 
    imgMapCol9FQjoin = imgMapCol9FQ.filter(ee.Filter.eq("id_bacia", selBacia)); 
    imgMapCol9TPjoin = imgMapCol9TP.filter(ee.Filter.eq("id_bacia", selBacia)); 
    imgMapCol9TPJ4join = imgMapCol9TPJ4.filter(ee.Filter.eq("id_bacia", selBacia))
                                  .updateMask(biomaRaster);
    imgMapmixedJoin = imgMapmixed.filter(ee.Filter.eq("id_bacia", selBacia));
    imgMapCol9GTBNjoin = imgMapCol9GTBNew.filter(ee.Filter.eq("id_bacia", selBacia))
                                .remap(param.classMapB, param.classNew);
    imgMapCol9RFNjoin = imgMapCol9RFNew.filter(ee.Filter.eq("id_bacia", selBacia))
                                .remap(param.classMapB, param.classNew);
    Mosaicos = Mosaicos.filterBounds(FeatColbacia);
    poitsRefCol71compY = poitsRefCol71compY.filterBounds(FeatColbacia);
    pointRefCol80compY = pointRefCol80compY.filterBounds(FeatColbacia);
    ptosfromBacia = poitsRefCol71comp.filterBounds(FeatColbacia);
}

var incidencias = get_layerIncidentes(imgMapCol71, imgMapCol8, imgMapmixedJoin);


var pointsLapigC = imgMapCol9RFNjoin.rename('classification').sampleRegions({
                                            collection: pointRefCol80comp,
                                            properties: propYYPoints, 
                                            scale: 30, 
                                            geometries: true
                                        })

pointsLapigC =  pointsLapigC.map(makeDiferencebettwenPoints);
pointsLapigC = pointsLapigC.filter(ee.Filter.eq('diferente', 1));
print("pontos revisados ", pointsLapigC.limit(10));


print(" 📍 imagem no Asset Geral Mapbiomas Col 7.1  ‼️", imgMapCol71);
print(" 📍 imagem no Asset Geral Mapbiomas Col 8.0  ‼️", imgMapCol8);
print(" 📍 imagem no Asset Geral X Bacias col 9 GTB", imgMapCol9GTB);
print(" 📍 imagem no Asset Geral X Bacias pos-Class col 9 Gap Fill", imgMapCol9GFjoin);
print(" 📍 imagem no Asset Geral X Bacias pos-Class col 9 Spatial", imgMapCol9SPjoin);
print(" 📍 imagem no Asset Geral X Bacias pos-Class col 9 Mixed", imgMapmixedJoin);
print(" 📍 shp no Asset ptos Lapig X Bacias", ptosfromBacia.size());

var mosaic_year = Mosaicos.filter(ee.Filter.eq('year', yearcourrent)).median();                     
Map.addLayer(FeatColbacia, {color: 'green'}, 'bacia', false);
Map.addLayer(mosaic_year, visualizar.visMosaic,'Mosaic Col8', false);

var baciaBuf = ee.Image().byte().paint({
                    featureCollection: FeatColbacia,
                    color: 1,
                    width: 3
                    });


// var imgMapCol71temp = imgMapCol71.select(banda_activa).remap(param.classMapB, param.classNew);
// var imgMapCol8temp = imgMapCol8.select(banda_activa).remap(param.classMapB, param.classNew);

Map.addLayer(imgMapCol9FQjoin,  visualizar.visclassCC, 'Class Frequency ' + String(versnew));
Map.addLayer(imgMapCol9TPjoin,  visualizar.visclassCC, 'Class Temporal J3' + String(versnew), false);
Map.addLayer(imgMapCol9TPJ4join,  visualizar.visclassCC, 'Class Temporal J4' + String(versnew), false);
// Map.addLayer(imgMapCol9SPjoin,  visualizar.visclassCC, 'Class Spatial ' + String(versnew), false);
// Map.addLayer(imgMapCol9GFjoin,  visualizar.visclassCC, 'Class Gap-fill ' + String(versnew), false);
Map.addLayer(imgMapCol9GTBjoin,  visualizar.visclassCC, 'Class GTB ' + String(version), false);
Map.addLayer(imgMapCol9GTBNjoin,  visualizar.visclassCC, 'Class GTB ' + String(versnew), false);
Map.addLayer(imgMapCol9Yv15,  visualizar.visclassCC, 'Class GTB 15', false);

// Map.addLayer(imgMapCol9RFNjoin,  visualizar.visclassCC, 'Class RF ' + String(versnew), false);
// Map.addLayer(imgMapmixedJoin,  visualizar.visclassCC, 'Class Mixed', false);
Map.addLayer(imgMapCol71, visualizar.visclassCC,'Col71_' + String(yearcourrent), false);
Map.addLayer(imgMapCol8,  visualizar.visclassCC, 'Col8_'+ String(yearcourrent), false);
Map.addLayer(incidencias,  visualizar.visIncident, 'Inc_'+ String(yearcourrent), false);
Map.addLayer(maskGEDI.selfMask(), {min:0, max: 1, palette: '00A36C'}, 'mask GEDI', false)
Map.addLayer(ptosfromBacia, {color: 'red'}, 'ptos do Lapig', false);
Map.addLayer(pointRefCol80compY, {}, 'Point Ref col8.0 ', false);
// Map.addLayer(poitsRefCol71compY, {}, 'Point Ref col7.1', false);
// Map.addLayer(featSearch, {}, 'bacia Analises');
Map.addLayer(baciaBuf, {palette: 'FF0000'}, 'caatinga buffer');
Map.centerObject(featSearch)
var lstPoint = pointRefCol80comp.reduceColumns(ee.Reducer.toList(), ['CLASS_' + String(yearcourrent)]).get('list');
lstPoint = ee.List(lstPoint).distinct().getInfo();
print("lista de pontos ", lstPoint);
var listaPontos = [3,4,12,21,22,33];

listaPontos.forEach(function(nClasse){
    var temFeatPoint =  pointsLapigC.filter(ee.Filter.eq('CLASS_' + String(yearcourrent), nClasse));
    print(nClasse, temFeatPoint);
    Map.addLayer(temFeatPoint , {color: 'red'}, 'ptos classe ' + String(nClasse));
})



// Paint all the polygon edges with the same number and width, display.
// var CaatingaBuffer = ee.Image().byte().paint({
//                     featureCollection: caatBuffer,
//                     color: 1,
//                     width: 3
//                     });
// Map.addLayer(CaatingaBuffer, {palette: 'FF0000'}, 'caatinga buffer');


var legend = ui.Panel({style: {position: 'bottom-left', padding: '8px 15px'}});
var makeRow = function(color, name) {
    var colorBox = ui.Label({
      style: {color: '#ffffff',
        backgroundColor: color,
        padding: '10px',
        margin: '0 0 4px 0',
      }
    });
    var description = ui.Label({
      value: name,
      style: {
        margin: '0px 0 4px 6px',
      }
    }); 
    return ui.Panel({
      widgets: [colorBox, description],
      layout: ui.Panel.Layout.Flow('horizontal')}
  )};
  
  var title = ui.Label({
    value: 'Coincidencias das classes',
    style: {
          fontWeight: 'bold',
          fontSize: '16px',
          margin: '0px 0 4px 0px'
      }
  });
  
  legend.add(title);
  legend.add(makeRow('#faf3dd','Concordante'));
  legend.add(makeRow('#c8d5b9','Concordante Recente'));
  legend.add(makeRow('#f19c79','Discordante Recente'));
  legend.add(makeRow('#fec601','Discordante'));
  legend.add(makeRow('#013a63','Muito discordante'));
  Map.add(legend);



