
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
    presencia : {
        max: 2,
        min: -1,
        palette: ['#D23519','#FFFFFF','#7D7C7CFF','#32D22DFF']
    },
    afloramento: {
        min:0, max: 1,
        palette: ['#EF3207']
    }  

} 
var spectralBands = ['blue', 'red', 'green', 'nir', 'swir1', 'swir2'];
var param = {
    assetrois: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_cleaned_downsamplesv4C/',
    asset_maps_new: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/ClassifyV2YY',
    asset_maps_old: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/ClassifyV2Y',
    asset_bacias_buffer:  'projects/ee-solkancengine17/assets/shape/bacias_buffer_caatinga_49_regions',
    asset_afloramento: 'projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/Classifier/rockyoutcropcol10',
    asset_collectionId: 'LANDSAT/COMPOSITES/C02/T1_L2_32DAY',
}
var lstYears = [2020,2021,2022,2023,2024];
var layerAfloramento = ee.Image(param.asset_afloramento).selfMask();
lstYears.forEach(function(nyear){
    var visualizar_map = false;
    if(nyear === 2024){
        visualizar_map = true;
    }
    print()
    var class_especf = 4;
    // var nyear = 2023;
    var dateStart = ee.Date.fromYMD(nyear, 1, 1);
    var dateEnd = ee.Date.fromYMD(nyear, 12, 31);
    var nbasin = '765';
    var name_feat = nbasin + '_' + nyear +'_cd';
    print("loading  " + name_feat);
    
    var feat = ee.FeatureCollection(param.assetrois + name_feat);
    print(feat.aggregate_histogram('class'));
    print(feat.first())
    
    // raster com o novo mapa 
    var raster_new = ee.ImageCollection(param.asset_maps_new);
    print("processed images from new maps " , raster_new.size());
    print("show metadatas from new maps ", raster_new);
    var raster_newYear = raster_new.filter(ee.Filter.eq('year', nyear));
    
    var lstIdCod = raster_newYear.reduceColumns(ee.Reducer.toList(), ['id_bacia']).get('list');
    raster_newYear = raster_newYear.min();
    
    var baciabuffer = ee.FeatureCollection(param.asset_bacias_buffer)
                            .filter(ee.Filter.inList('nunivotto4', lstIdCod));
    
    baciabuffer = baciabuffer.map(function(f){ return f.set('id_codigo', 1)})
    var bacia_raster =  baciabuffer.reduceToImage(['id_codigo'], ee.Reducer.first()).gt(0)
    
    var mosGEEyy = ee.ImageCollection(param.asset_collectionId)
                            .filter(ee.Filter.date(dateStart, dateEnd))
                            .median().updateMask(bacia_raster)
                            .select(spectralBands);  
    print("mosaico mensal GEE no ano", mosGEEyy)
    // raster com os mapas mais antigos 
    var raster_old = ee.ImageCollection(param.asset_maps_old)
                            .filter(ee.Filter.inList('id_bacia', ee.List(lstIdCod)));
    print("processed images from old maps " , raster_old.size());
    print("show metadatas from old maps ", raster_old);
    var raster_oldYear = raster_old.filter(ee.Filter.eq('year', nyear)).min();
    
    
    Map.addLayer(mosGEEyy,   visualizar.vismosaicoGEE, 'mosEE_' + String(nyear), visualizar_map);
    if (nyear === lstYears[0]){
        Map.addLayer(baciabuffer, {color: 'yellow'}, 'bacias', false);
    }
    Map.addLayer(raster_oldYear, visualizar.visclassCC, "map old " + String(nyear), visualizar_map);
    Map.addLayer(raster_newYear, visualizar.visclassCC, "map new " + String(nyear), visualizar_map);
    
    var mapSavanaOld = raster_oldYear.eq(class_especf).unmask(0);
    var mapSavanaNew = raster_newYear.eq(class_especf).multiply(2).unmask(0);
    var mask_mudanca = mapSavanaNew.subtract(mapSavanaOld).updateMask(bacia_raster);
    // mask_mudanca = mask_mudanca.remap([2,1,0,-1], [])
    
    Map.addLayer(mask_mudanca, visualizar.presencia, "precensa " + String(nyear), visualizar_map);
})
Map.addLayer(layerAfloramento, visualizar.afloramento, 'afloramento');