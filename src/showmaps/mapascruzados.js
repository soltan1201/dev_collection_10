


//var imageVisParam = {"opacity":1,"bands":["classes"],"min":1,"palette":["cecece","dae792","ff9a7c","ef00ff","ff3131"]};
var imageVisParam = {"opacity":1,"bands":["classes"],"min":1,"palette":["a6a6a6","d9d9d9","dbed55","ff5050","990033"]};

//var biomes = ee.Image('projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41')
//var pampa = biomes.mask(biomes.eq(6))

var dirCol5 = 'projects/mapbiomas-workspace/public/collection5/mapbiomas_collection50_integration_v1';
var dirCol6 = 'projects/mapbiomas-workspace/public/collection6/mapbiomas_collection60_integration_v1';
var dirCol7 = 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1'
//var dirCol7 = 'projects/mapbiomas-workspace/COLECAO7/integracao';
//var inputVersion = '0-29';


var col5 = ee.Image(dirCol5)
print(col5)
var col6 = ee.Image(dirCol6)
print(col6)
var col7 = ee.Image(dirCol7)//.filterMetadata('version','equals','0-29').mosaic()
//Map.addLayer(col7,{},'col7')
print(col7)

var palettes = require('users/mapbiomas/modules:Palettes.js');
//vis coll 05
var vis = { 'min': 0, 'max': 45,  'palette': palettes.get('classification5')};

var anos = [
    1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,
    1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,
    2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,
    2015,2016,2017,2018,2019
  ];
    
  anos = [2019]

for (var i_ano=0;i_ano<anos.length; i_ano++){
  var ano = anos[i_ano];
  
  var img5 = col5.select('classification_' + ano ).remap(							
      [3, 4, 5, 49 ,9, 11, 12, 13, 29, 50, 15, 21, 23, 24, 25, 30, 31, 33, 39, 20, 40, 62, 41, 36, 46, 47, 48],							
      [3, 4, 3,  3 ,9, 12, 12, 12, 12, 12, 21, 21, 22, 22, 22, 30, 33, 33, 21, 21, 21, 21, 21, 21, 21, 21, 21]).rename('c5_class_' + ano)
  
  var img6 = col6.select('classification_' + ano ).remap(							
      [3, 4, 5, 49 ,9, 11, 12, 13, 29, 50, 15, 21, 23, 24, 25, 30, 31, 33, 39, 20, 40, 62, 41, 36, 46, 47, 48],							
      [3, 4, 3,  3 ,9, 12, 12, 12, 12, 12, 21, 21, 22, 22, 22, 30, 33, 33, 21, 21, 21, 21, 21, 21, 21, 21, 21]).rename('c6_class_' + ano)
  
  var img7 = col7.select('classification_' + ano ).remap(							
      [3, 4, 5, 49 ,9, 11, 12, 13, 29, 50, 15, 21, 23, 24, 25, 30, 31, 33, 39, 20, 40, 62, 41, 36, 46, 47, 48],							
      [3, 4, 3,  3 ,9, 12, 12, 12, 12, 12, 21, 21, 22, 22, 22, 30, 33, 33, 21, 21, 21, 21, 21, 21, 21, 21, 21]).rename('c7_class_' + ano)

  var img = img5.addBands(img6).addBands(img7)
  var incidentes = img.reduce(ee.Reducer.countRuns()).subtract(1).rename('incidentes');
  var states = img.reduce(ee.Reducer.countDistinctNonNull()).rename('states');
  print(img)
  var moda = img.reduce(ee.Reducer.mode())
  
  ///logica de definição de classes está embasada no fato de termos 3 coleções de entrada
  //para analisar mais coleções a logica precisa ser reestruturada
  var clas1 = incidentes.eq(0).selfMask()
  var clas2 = incidentes.eq(1).and(img.select(2).subtract(moda).eq(0)).selfMask()
  var clas3 = incidentes.eq(1).and(img.select(0).subtract(moda).eq(0)).selfMask()
  var clas4 = incidentes.eq(2).and(states.eq(2)).selfMask()
  var clas5 = incidentes.eq(2).and(states.eq(3)).selfMask()
  
  var out = clas1.blend(clas2.multiply(2))
                 .blend(clas3.multiply(3))
                 .blend(clas4.multiply(4))
                 .blend(clas5.multiply(5))
                 .rename('classes')
                 
  
  Map.addLayer(incidentes, visIncidentes, 'incidentes');
  Map.addLayer(states, visStates, 'states');
  Map.addLayer(img.select(0),vis,'col 05')
  Map.addLayer(img.select(1),vis,'col 06')
  Map.addLayer(img.select(2),vis,'col 07')
  Map.addLayer(moda,vis,'moda')
  Map.addLayer(out,imageVisParam,'saída')
  print(moda)
  
  
  out = out.addBands(incidentes)
           .addBands(states)
           .addBands(moda)
           .addBands(img)
           .toByte()

print('out',out)

Export.image.toAsset({
  'image': out,
  'description': 'pampa_colecoes_' + ano,
  'assetId': 'projects/mapbiomas-workspace/AMOSTRAS/col8/PAMPA/estabilidade_colecoes/pampa_colecoes_' + ano,
  'scale': 30,
  'pyramidingPolicy': {
      '.default': 'mode'
  },
  'maxPixels': 1e13,
  'region': geometry
});    



  
  
  

}