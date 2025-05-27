
var palettes = require('users/mapbiomas/modules:Palettes.js');
var text = require('users/gena/packages:text')

var visualizar = {
    visclassCC: {
            "min": 0, 
            "max": 69,
            "palette":  palettes.get('classification9'),
            "format": "png"
    },
    vismosaicoGEE: {
        'min': 0.001, 'max': 0.15,
        bands: ['red', 'green', 'blue']
    },
    diferentes: {
        min: -5, 
        max: 5,
        palette: ['#697c37', '#8ba34e', '#ccda46', '#d4e391', '#f3e69a', 
                  '#d8b269', '#fe9801', '#8d4a87', '#b03c77', '#bf1540']
    } 

} 
var functionExports = function(cc_image, nameEXp, geomSHP, nassetId){
    var pmtExpo = {
        image: cc_image,
        description: nameEXp,
        scale: param.scale, // Escolha a escala de acordo com sua necessidade
        region: geomSHP,
        assetId: nassetId + nameEXp, // Substitua pelo nome da sua pasta no Google Drive
        maxPixels: 1e13 // Escolha o valor adequado para o número máximo de pixels permitidos
    };
    Export.image.toAsset(pmtExpo);
    print("maps salvo " + nameEXp + " ...");
};
var maxNumbPixels = 60;
function buildingLayerconnectado(imgClasse){    
    var manchas_conectados = imgClasse.connectedPixelCount({
                                            'maxSize': maxNumbPixels, 
                                            'eightConnected': true
                                        });
    return manchas_conectados;
}
Map.addLayer(ee.Image.constant(1), {min: 0, max: 1}, 'base');
var spectralBands = ['blue', 'red', 'green', 'nir', 'swir1', 'swir2'];
var param = {
    assetrois: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_cleaned_downsamplesv4C/',
    asset_maps_new: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Spatials_all',
    asset_maps_old: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/Temporal',
    asset_bacias_buffer:  'projects/ee-solkancengine17/assets/shape/bacias_buffer_caatinga_49_regions',
    asset_difMasps : 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/POS-CLASS/extras_yy',
    asset_afloramento: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/rockyoutcropcol10',
    asset_collectionId: 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
    output_asset: 'projects/geo-data-s/assets/'
}
var listCC = ['-5', '-4', '-3', '-2', '-1', '1', '2', '3', '4', '5'];
var maps_diferent = ee.ImageCollection(param.asset_difMasps).max();
var rastermapSpatial = ee.ImageCollection(param.asset_maps_new)
                        .filter(ee.Filter.eq('version', 8))
                        .max();
print("show metadatas from new maps ", rastermapSpatial);
var lstYears = ['1985','1986','1987','1988','1989'];
var dict_int = {
    '1985': {
        'gt': 0,
        'lt': 0
    },
    '1986': {
        'gt': 10,
        'lt': 20
    },
    '1987':{
        'gt': 20,
        'lt': 35
    },
    '1988':{
        'gt': 0,
        'lt': 0
    },
    '1989': {
        'gt': 15,
        'lt': 25
    }
}
var maskGeral = ee.Image().byte();
var maxVal = 5;
var cc = 0;
lstYears.forEach(function(nyear){
    var visualizar_map = false;
    if(nyear === lstYears[-1]){
        visualizar_map = true;
    }
    print();
    var mapSpatialYY =    rastermapSpatial.select('classification_' + nyear);
    var maps_diferentYY = maps_diferent.select('classification_' + nyear);
    var connect_pixel = buildingLayerconnectado(maps_diferentYY);
    var limiar_menor = dict_int[nyear]['gt']
    var limiar_maior = dict_int[nyear]['lt']
    connect_pixel = connect_pixel.gt(limiar_menor).and(connect_pixel.lte(limiar_maior))


    Map.addLayer(mapSpatialYY, visualizar.visclassCC, "map Spatial_" + nyear, visualizar_map);
    Map.addLayer(maps_diferentYY, visualizar.diferentes, 'mapsDiferent ' + nyear, visualizar_map );
    Map.addLayer(connect_pixel, {}, 'conect ' + nyear, visualizar_map );


})




var styles = {
    style_painel: {
        width: "150px",
        height: "350px",
        margin: '2px"',
        padding: '10px',
        position: 'bottom-left',
    },
    style_title: {
        fontWeight: 'bold', 
        fontSize: '10px', 
        margin: '0 0 0 0px', 
        padding: '0'
    },
    sytle_legend: {
        fontWeight: 'bold', 
        fontSize: '12px', 
        margin: '0 0 0 0', 
        padding: '0'
    },
}

var toolPanel = ui.Panel({
    widgets: [ui.Label('Cores em transcição -5 a 5')],
    layout: ui.Panel.Layout.flow("vertical"),
    style: styles.style_painel
});

var legendPanel = ui.Panel({
    style: styles.style_title
});
toolPanel.add(legendPanel);

var legendTitle = ui.Label( 'Legenda', styles.sytle_legend );
legendPanel.add(legendTitle);

var makeRow = function(color, name) {
    // Create the label that is actually the colored box.
    var colorBox = ui.Label({ style:  {
        backgroundColor: color,
        // Use padding to give the box height and width.
        padding: '8px',
        margin: '0 0 4px 0'
    } });

    // Create the label filled with the description text.
    var description = ui.Label({
        value: name,
        style: {margin: '0 0 8px 6px',fontSize: '12px'}
    });

    return ui.Panel({
        widgets: [colorBox, description],
        layout: ui.Panel.Layout.Flow('horizontal')
    });
};
var cc = 0;
listCC.forEach(function(valCC){
  print(valCC)
    toolPanel.add(makeRow(String(visualizar.diferentes.palette[cc]), '>> valor ' + valCC));
    cc += 1
})


Map.add(toolPanel)