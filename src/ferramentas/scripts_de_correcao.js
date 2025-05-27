
var palettes = require('users/mapbiomas/modules:Palettes.js');
// --- Visualização ---
var vis = {
  min: 0,
  max: 69,
  palette: palettes.get('classification9')
};

var param = {
    'asset_input':'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/transitionTest',
    'asset_polygon': 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/poligons_corretores',
    'asset_painel_sol': 'projects/mapbiomas-arida/energias/solar-panel-br-30m',
    'asset_restinga': 'projects/mapbiomas-arida/restinga_ibge_2014'
}

var raster_map = ee.ImageCollection(param.asset_input).max().select('classification_2024');
var raster_FV = ee.Image(param.asset_painel_sol).select("Panel_2024")
                      .selfMask().multiply(22);
print("show metadata FV ", raster_FV);
raster_map = raster_map.blend(raster_FV);

var feat_pol = ee.FeatureCollection(param.asset_polygon);
var lstLabel = feat_pol.reduceColumns(ee.Reducer.toList(), ['label']).get('list');
lstLabel = ee.List(lstLabel).distinct();

print("know about the metadata ", feat_pol);
print("list of labels ", lstLabel);
lstLabel = lstLabel.getInfo();

var shp_restinga = ee.FeatureCollection(param.asset_restinga)
                        .map(function(feat){return feat.set('id_codigo', 1)});
print("show metadata restinga ", shp_restinga);

Map.addLayer(raster_map, vis, 'classification');
Map.addLayer(shp_restinga, {color: 'red'}, 'restinga');

lstLabel.forEach(function(label){
    var tmpSHP = feat_pol.filter(ee.Filter.eq('label', label));
    print("show ", tmpSHP);
    var maskPolyCC = tmpSHP.reduceToImage(['class'], ee.Reducer.first());
    var maskPolyTo = tmpSHP.reduceToImage(['para'], ee.Reducer.first());
    print("know raster build maskPolyCC", maskPolyCC);
    print("know raster build maskPolyTo", maskPolyTo);
    Map.addLayer(tmpSHP, {}, 'shp ' + label, false);
    
    if (label === 'x21vira29'){
        print('processing ' + label);
        var mask21v29 = raster_map.eq(21).multiply(maskPolyCC.eq(21)).multiply(maskPolyTo);
        Map.addLayer(mask21v29.selfMask(), vis, 'to ' + label, false);
    }
    if (label === 'x22vira29'){
        var mask22v29 = raster_map.eq(22).multiply(maskPolyCC.eq(22)).multiply(maskPolyTo);
        Map.addLayer(mask22v29.selfMask(), vis, 'to ' + label, false);
    }
    if (label === 'x22vira21'){
        var mask22v21 = raster_map.eq(22).multiply(maskPolyCC.eq(22)).multiply(maskPolyTo);
        Map.addLayer(mask22v21.selfMask(), vis, 'to ' + label, false);
    }
    if (label === 'x29vira22'){
        var mask29v22 = raster_map.eq(29).multiply(maskPolyCC.eq(29)).multiply(maskPolyTo);
        Map.addLayer(mask29v22.selfMask(), vis, 'to ' + label, false);
    }
    if (label === 'x33vira29'){
        var mask33v29 = raster_map.eq(33).multiply(maskPolyCC.eq(33)).multiply(maskPolyTo);
        Map.addLayer(mask33v29.selfMask(), vis, 'to ' + label, false);
    }
    if (label === 'x33vira3'){
        var mask33v3 = raster_map.eq(33).multiply(maskPolyCC.eq(33)).multiply(maskPolyTo);
        Map.addLayer(mask33v3.selfMask(), vis, 'to ' + label, false);
    }
    if (label === 'x33vira21'){
        var mask33v21 = raster_map.eq(33).multiply(maskPolyCC.eq(33)).multiply(maskPolyTo);
        Map.addLayer(mask33v21.selfMask(), vis, 'to ' + label, false);
    }
    
})