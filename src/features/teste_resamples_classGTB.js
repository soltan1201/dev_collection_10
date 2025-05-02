
var asset = 'projects/earthengine-legacy/assets/projects/mapbiomas-workspace/AMOSTRAS/col10/CAATINGA/ROIs/ROIs_merged_IndAllv3C/rois_grade_7411';
var fc_tmp = ee.FeatureCollection(asset);
var fcYY = fc_tmp.filter(ee.Filter.eq('year', 1985));

print("in year 1985 o tamanho é  ", fcYY.size());
var dictGroup = {
            'vegetation' : [3,4,12],
            'agropecuaria': [15,18,21],
            'outros': [22,33,29]
        };
            
var pmtros_GTB= {
            'numberOfTrees': 50, 
            'shrinkage': 0.1,         
            'samplingRate': 0.8, 
            'loss': "LeastSquares", //#'Huber',#'LeastAbsoluteDeviation', 
            'seed': 0
        };  
var bandas_imports = [
        'gli_median_wet', 'ri_median', 'osavi_median', 'shape_median', 'iia_median_wet', 'nir_median', 
        'lswi_median_wet', 'ndvi_median', 'rvi_median', 'nddi_median', 'ui_median_wet', 'red_median_wet', 
        'gemi_median', 'ratio_median', 'wetness_median', 'green_median_wet', 'evi_median', 'blue_median_wet', 
        'dswi5_median_wet', 'afvi_median', 'ndwi_median', 'gli_median', 'evi_median_wet', 'cvi_median_wet', 
        'gvmi_median', 'iia_median', 'ndwi_median_dry', 'ri_median_dry', 'osavi_median_wet', 'nddi_median_wet', 
        'swir1_median_wet', 'bsi_median', 'swir1_median', 'swir2_median', 'red_median', 'gemi_median_wet', 
        'lswi_median', 'awei_median_wet', 'ndvi_median_wet', 'afvi_median_wet', 'nir_median_wet', 'ndwi_median_wet', 
        'ratio_median_wet', 'gcvi_median', 'ui_median', 'rvi_median_wet', 'avi_median_dry', 'gvmi_median_wet', 
        'wetness_median_wet', 'dswi5_median', 'awei_median', 'mbi_median_wet', 'gemi_median_dry', 'bsi_median_1', 
        'bsi_median_2', 'brightness_median', 'green_median'
];
        
        
var fcYYtipo = fcYY.filter(ee.Filter.inList('class', dictGroup.vegetation));
print("nas classes naturais o tamanho é  ", fcYYtipo.size());
var classifierGTB = ee.Classifier.smileGradientTreeBoost(pmtros_GTB)
                                    .train(fcYYtipo, 'class', bandas_imports)
                                    .setOutputMode('MULTIPROBABILITY');

// dictGroup.vegetation.forEach(function(nclass){
//     print(" classe " + nclass);
//     var fcYYbyClass = fcYYtipo.filter(ee.Filter.eq('class', nclass));
//     print("first feat ", fcYYbyClass.first().propertyNames());
//     var classROIsGTB = fcYYbyClass.limit(5).classify(classifierGTB, 'label');
//     print("first feat classif ", classROIsGTB.first().propertyNames());
    
// })            

var classROIsGTB = fcYYtipo.classify(classifierGTB, 'label');
var asset_output = 'projects/geo-datasciencessol/assets/ROIsCol10';
var name_exp = 'rois_grade_7411_veg';
Export.table.toAsset({
    collection: classROIsGTB, 
    description: name_exp, 
    assetId: asset_output + "/" + name_exp
})
    
    
    
    
    
    

