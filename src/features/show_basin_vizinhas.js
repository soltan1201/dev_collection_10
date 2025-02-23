//https://code.earthengine.google.com/7652dcbdb32e06f2f1dc07685470196e
var getDictViz = false;

var asset_bacias = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/bacias_hidrografica_caatinga_49_regions'
var bacias = ee.FeatureCollection(asset_bacias)
var ls_name = bacias.reduceColumns(ee.Reducer.toList(), ['nunivotto4']).get('list').getInfo()
Map.addLayer(bacias, {}, 'bacias 49 Reg');
print(ls_name);

if (getDictViz === true) {
    ls_name.forEach(function (name) {
        print("bacias ", name);
        var bacia_a = bacias.filter(ee.Filter.eq('nunivotto4', name));
        var bacias_viz = bacias.filterBounds(bacia_a);
        var ls_name_t = bacias_viz.reduceColumns(ee.Reducer.toList(), ['nunivotto4']);
        print(ls_name_t);
        Map.addLayer(bacias_viz, {color: 'green'}, name + '_viz', false);
    })
} else {
    var lst10first = ['7544', '7615', '7584', '763', '7438', '7619', '761111', '771', '7712'];
    var basin10F = bacias.filter(ee.Filter.inList('nunivotto4', lst10first));
    Map.addLayer(basin10F, { color: "#FF0000" }, 'basin10F');

    var basinsinaliz = bacias.filterBounds(sinalizados);
    var lst_sinalizados = basinsinaliz.reduceColumns(ee.Reducer.toList(), ['nunivotto4']);
    print(lst_sinalizados);
}

// vizinhos sinalizados 
// "7438","752","7584","761111","7619","765","7712","773","7746", "7591", "7615"