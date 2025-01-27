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
    visFreq : {
        max: 5,
        min: 0,
        palette: ['#000000','#faf3dd','#c8d5b9','#f19c79','#fec601','#013a63']
    },
    props: {  
        textColor: 'ff0000', 
        outlineColor: 'ffffff', 
        outlineWidth: 1.5, 
        outlineOpacity: 0.2
    }
} 

var legend = ui.Panel({
    style: {
        position: 'bottom-left',
        width: '500px',
        height: '750px',
        padding: '8px 15px'
    }
});
Map.add(legend);
function getCoordSerie(coords){
    // Add a red dot for the point clicked on.
    var point = ee.Geometry.Point(coords.lon, coords.lat);

    var graph = ui.Chart.image.regions(colNatForwardCor, point, ee.Reducer.mean(),30)
              //.setSeriesNames(['Co2Flux', 'Ajustes'])
              .setOptions({
                    trendlines: {
                        0: {color: 'CC0000'}
                    },
                    title: 'Variação classes mapeadas',
                    vAxis: {title: 'Nº da classe mapeada'},
                    hAxis: {title: 'Anos'},
                    lineWidth: 4,
                    pointSize: 10,
                    series: {
                        0: {color: 'FF0000'}, // urban
                        1: {color: '00FF00'}, // forest
                        2: {color: '0000FF'}  // desert
                    }
                });

    // print(graph)
    var graphuso = ui.Chart.image.regions(maskUSO, point, ee.Reducer.mean(),30)
              //.setSeriesNames(['Co2Flux', 'Ajustes'])
              .setOptions({
                    trendlines: {
                        0: {color: 'CC00CC' }
                    },
                    title: 'Variação classes mapeadas',
                    vAxis: {title: 'Nº da classe mapeada'},
                    hAxis: {title: 'Anos Uso'},
                    lineWidth: 4,
                    pointSize: 10,
                    series: {
                        0: {color: 'FF0000'}, // urban
                        1: {color: '00FF00'}, // forest
                        2: {color: '0000FF'}  // desert
                    }
                });
                
      var graphMod = ui.Chart.image.regions(mapFinal.eq(21), point, ee.Reducer.mean(),30)
              //.setSeriesNames(['Co2Flux', 'Ajustes'])
              .setOptions({
                    trendlines: {
                        0: {color: 'CC00CC' }
                    },
                    title: 'Variação classes mapeadas',
                    vAxis: {title: 'Nº da classe mapeada'},
                    hAxis: {title: 'Anos Uso'},
                    lineWidth: 4,
                    pointSize: 10,
                    series: {
                        0: {color: 'FF0000'}, // urban
                        1: {color: '00FF00'}, // forest
                        2: {color: '0000FF'}  // desert
                    }
                });

    // print(graphuso)

    var dot = ui.Map.Layer(point, {color: 'FF0000'});
    Map.layers().set(5, dot);

    legend.clear();
    legend.add(graph);
    legend.add(graphuso);
    legend.add(graphMod);
    
} 

function getwindows(lstyear, pos, janela){
    if (lstyear.length - pos < 5){
        return lstyear.slice(lstyear.length - janela, lstyear.length);
    }else{
        
        return lstyear.slice(pos, pos + janela);
    }
}

function getwindowsfeed(lstyear, pos, janela){
    if (lstyear.length - pos < 5){
        return lstyear.slice(lstyear.length - janela, lstyear.length);
    }else{
        if (pos < 2){
            return lstyear.slice(0, janela);
        }else{
            return lstyear.slice(pos - 2, pos + 3);
        }
    }
}
var cc = 0;
var janela = 5;
var lstWindowsforward, lstWindowsback,rasterWindwsNat;
var banda_activate;
var param = {       
    // input_asset: 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/FrequencyV2',
    input_asset: 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/TemporalV2',
    years: [
        '1985','1986','1987','1988','1989','1990','1991','1992','1993','1994',
        '1995','1996','1997','1998','1999','2000','2001','2002','2003','2004',
        '2005','2006','2007','2008','2009','2010','2011','2012','2013','2014',
        '2015','2016','2017','2018','2019','2020','2021','2022','2023'
    ],
}
var nbacia = '758'
var lstBands = [];
param.years.forEach(function(yyear){
    lstBands.push('classification_' + yyear);
})
var rasterImg = ee.ImageCollection(param.input_asset)
                    .filter(ee.Filter.eq('id_bacia', nbacia))
                    .filter(ee.Filter.eq('version', 15))
                    .filter(ee.Filter.eq('janela', 3))
                    .first();
rasterImg = rasterImg.select(lstBands);                    
                    
                    
print("know raster img ", rasterImg);
var maskNatural = rasterImg.eq(3).or(rasterImg.eq(4)).or(rasterImg.eq(12))
var maskUSO = rasterImg.eq(21)
print("mascara natural bandas ", maskNatural);

print(lstBands);
var colNatForward = ee.Image().byte();

lstBands.forEach(function(yyear){
    lstWindowsforward = getwindows(lstBands, cc, janela);
    // print(lstWindowsforward);
    rasterWindwsNat = maskNatural.select(lstWindowsforward).reduce(ee.Reducer.sum());
    // print(rasterWindwsNat.rename(yyear));
    colNatForward = colNatForward.addBands(rasterWindwsNat.rename(yyear));
    cc += 1;
});
colNatForward = colNatForward.select(lstBands);
print("know bands colNatForward ", colNatForward);

var colNatForwardCor = ee.Image().byte();
cc = 0;
lstBands.forEach(function(yyear){
        // print(yyear)
        
        lstWindowsforward = getwindowsfeed(lstBands, cc, janela);
        rasterWindwsNat = colNatForward.select(lstWindowsforward);
        // print(lstWindowsforward)
        if (cc > 2){
            var mmasQ1 = rasterWindwsNat.select([0]).eq(1).and(
                          rasterWindwsNat.select([1]).eq(2)).and(
                            rasterWindwsNat.select([2]).eq(3)).and(
                                rasterWindwsNat.select([3]).eq(4)).and(
                                    rasterWindwsNat.select([4]).eq(5));

            var mmasQ2 = rasterWindwsNat.select([0]).eq(2).and(
                            rasterWindwsNat.select([1]).eq(3)).and(
                                rasterWindwsNat.select([2]).eq(4)).and(
                                    rasterWindwsNat.select([3]).eq(5)).and(
                                        rasterWindwsNat.select([4]).eq(5))

            var mmasQ3 = rasterWindwsNat.select([0]).eq(2).and(
                            rasterWindwsNat.select([1]).eq(3)).and(
                                rasterWindwsNat.select([2]).eq(4)).and(
                                    rasterWindwsNat.select([3]).eq(5)).and(
                                        rasterWindwsNat.select([4]).eq(4))
                                        
            var mmasQ4 = rasterWindwsNat.select([0]).eq(5).and(
                            rasterWindwsNat.select([1]).eq(5)).and(
                                rasterWindwsNat.select([2]).eq(4)).and(
                                    rasterWindwsNat.select([3]).eq(3)).and(
                                        rasterWindwsNat.select([4]).eq(2))
                                        
            var mmasQ5 = rasterWindwsNat.select([0]).eq(5).and(
                            rasterWindwsNat.select([1]).eq(4)).and(
                                rasterWindwsNat.select([2]).eq(3)).and(
                                    rasterWindwsNat.select([3]).eq(2)).and(
                                        rasterWindwsNat.select([4]).eq(1))
                                        
            var mmasQ6 = rasterWindwsNat.select([0]).eq(4).and(
                            rasterWindwsNat.select([1]).eq(3)).and(
                                rasterWindwsNat.select([2]).eq(2)).and(
                                    rasterWindwsNat.select([3]).eq(1)).and(
                                        rasterWindwsNat.select([4]).eq(0))
                                            
            var colNatForwardGG = colNatForward.select(yyear).where(mmasQ1.eq(1), ee.Image.constant(0))
            colNatForwardGG = colNatForwardGG.where(mmasQ2.eq(1), ee.Image.constant(0))
            colNatForwardGG = colNatForwardGG.where(mmasQ3.eq(1), ee.Image.constant(0))
            colNatForwardGG = colNatForwardGG.where(mmasQ4.eq(1), ee.Image.constant(5))
            colNatForwardGG = colNatForwardGG.where(mmasQ5.eq(1), ee.Image.constant(5))
            colNatForwardGG = colNatForwardGG.where(mmasQ6.eq(1), ee.Image.constant(5))
            colNatForwardCor = colNatForwardCor.addBands(colNatForwardGG.rename(yyear))
            
        }else{
            colNatForwardCor = colNatForwardCor.addBands(colNatForward.select(yyear))
        }                   
        cc += 1;        
  
});

colNatForwardCor = colNatForwardCor.select(lstBands);
print("ver bandas ", colNatForwardCor);

Map.addLayer(colNatForward.select('classification_2020'), visualizar.visFreq, 'Mask 2020');
Map.addLayer(rasterImg.select('classification_2020'), visualizar.visclassCC, 'Maps 2020')

var mapFinal = ee.Image().byte();
// colNatForward
var areaAnalises = rasterImg.eq(4).or(rasterImg.eq(21));
print(areaAnalises)
param.years.forEach(function(yyear){
    banda_activate = 'classification_' + yyear;
    var imageYY = rasterImg.select(banda_activate)
    
    imageYY = imageYY.where(
                    areaAnalises.select(banda_activate).eq(1).and(colNatForwardCor.select(banda_activate).lte(2)), 21
                  ).where(
                    areaAnalises.select(banda_activate).eq(1).and(colNatForwardCor.select(banda_activate).gte(3)), 4
                  );                  
    mapFinal = mapFinal.addBands(imageYY.rename(banda_activate));
  
})

mapFinal = mapFinal.select(lstBands);
Map.addLayer(mapFinal.select('classification_2020'), visualizar.visclassCC, 'Maps mod 2020');
Map.addLayer(mapFinal.select('classification_2021'), visualizar.visclassCC, 'Maps mod 2021');
////////////////////////////////////////////////////////////
//               GUI   

Map.onClick(getCoordSerie);
Map.style().set('cursor', 'crosshair');

