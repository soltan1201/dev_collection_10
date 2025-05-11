//var ano = 2021

// AZUL somente na col 9
// VERMELHO somente col 8
// CINZA mapeado nos 2 

var Palettes = require('users/mapbiomas/modules:Palettes.js');
var palette = Palettes.get('classification9');
var vis ={ 
        classMapa: {
            'min': 0,
            'max': 69,
            'palette': palette,
            'format': 'png'      
        },
        concordancia: {
            min:1, max:3,
            palette: ['gray', 'blue', 'red'] 
        },
        visPar: {'palette':'000000','opacity': 0.6}  
    };

print(vis)

var param = {
    asset_biomasRaster : 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019-raster',
    asset_col8: 'projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_integration_v1',
    asset_col9 : "projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1",
    asset_biomasVector: 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
    asset_integration: 'projects/mapbiomas-workspace/COLECAO9/integracao'
}
// listar classes para performar a análise 
var classes = [3,4,5,6,49,11,12,13,32,29,50,15,18,9,21,23,24,30,25,33,31];
// listar anos para poerformar a análise
var years = [2022];
var rasterCaat = ee.Image(param.asset_biomasRaster).eq(5); 
// Join with Mata Atlantica 
// rasterCaat = rasterCaat.add(ee.Image(param.asset_biomasRaster).eq(2));
// // Join with Cerrado 
// rasterCaat = rasterCaat.add(ee.Image(param.asset_biomasRaster).eq(4));
rasterCaat = rasterCaat.selfMask();


var bioma250mil = ee.FeatureCollection(param.asset_biomasVector);
var biomaCaat = bioma250mil.filter(ee.Filter.eq('CD_Bioma', 2));
var class_col80 = ee.Image(param.asset_col8).updateMask(rasterCaat);
var class_col90 = ee.Image(param.asset_col9).updateMask(rasterCaat);
print('show metadata from class_col90 ', class_col90);

Map.addLayer(ee.Image.constant(1), {min: 0, max: 1}, 'base', false);
Map.addLayer(rasterCaat, {min:1, max: 6}, "biomas", false);

years.forEach(function(year_j) {
    // para cada classe 
    // para cada ano
    var col8_j = class_col80.select('classification_' + year_j);
    var col9_j = class_col90.select('classification_' + year_j);
    classes.forEach(function(class_i) {
        var images = ee.Image([]);
        // selecionar a classificação do ano j    
        // calcular concordância
        var conc = ee.Image(0).where(col8_j.eq(class_i).and(col9_j.eq(class_i)), 1) // [1]: Concordância entre col8 e 9
                            .where(col9_j.neq(class_i).and(col8_j.eq(class_i)), 2)  // [2]: presente na 8 e não está na 9
                            .where(col9_j.eq(class_i).and(col8_j.neq(class_i)), 3)  // [3]: presente na 9 e não está na 8
                             //.updateMask(biomes.eq(4));
            conc = conc.updateMask(conc.neq(0)).rename('territory_' + year_j);
        
        // build sinthetic image to compute areas
        var synt = ee.Image(0).where(conc.eq(1), col9_j)
                            .where(conc.eq(2), col8_j)
                            .where(conc.eq(3), col9_j)
                            .updateMask(conc)
                            .rename(['classification_' + year_j]);
        // build database
        images = images.addBands(conc).addBands(synt);        
        Map.addLayer(images.select(['territory_' + year_j]), vis.concordancia, year_j + ' Agreement - Class ' + class_i, false);

    });
    Map.addLayer(col8_j, vis.classMapa, 'Col 8 ' + year_j, false)
    Map.addLayer(col9_j, vis.classMapa, 'Col9 ' + year_j, false)

});


var outline = ee.Image(0).mask(0).paint(biomaCaat, 'AA0000', 2); 
Map.addLayer(outline, vis.visPar, 'Caatinga 250mil');
