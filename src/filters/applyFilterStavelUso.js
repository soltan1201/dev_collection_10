





var param = {
    'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV3/',
    'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/FrequencyV3',
    'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',            
    anos: ['1985','1986','1987','1988','1989','1990','1991','1992','1993','1994',
           '1995','1996','1997','1998','1999','2000','2001','2002','2003','2004',
           '2005','2006','2007','2008','2009','2010','2011','2012','2013','2014',
           '2015','2016','2017','2018','2019','2020','2021','2022', '2023'],
    'last_year' : 2023,
    'first_year': 1985,
    'janela' : 5,
    'step': 1
}
var banda_act, band_before, class_output, mask_Uso_kernel;
var change_uso_YY;
var listaNameBacias = [
    '7616','744','741','7422','745','746','7492','751','752','753',
    '755','759','7621','7622', '763','764','765','766',
    '767', '771', '772','773','7741','776','7742','775', 
    '777', '778','76111','76116','7612','7613','7615',
    '7617','7618','7619','756','757','758','754', '7614', '7421'
]
var janela = 3;
var classe_uso = 21;
var imgColFreq = ee.ImageCollection(param.input_asset)
                        .filter(ee.Filter.eq('version', 20))
                        .filter(ee.Filter.eq('janela', janela))

print("comprovando Frequancia ", imgColFreq);



listaNameBacias.forEach(function(name_bacia){
    var geomBacia = ee.FeatureCollection(param['asset_bacias_buffer']).filter(
                            ee.Filter.eq('nunivotto3', name_bacia)).first().geometry();

    var imgClass = ee.ImageCollection(param['input_asset'])
                        .filter(ee.Filter.eq('id_bacia', name_bacia )).first();
    print("know metadata ", imgClass);
    param.anos.forEach(function(yyear){
        banda_act = 'classification_' + yyear;
        band_before = 'classification_' + String(parseInt(yyear) - 1);

        if (yyear == '1985'){
            class_output = imgClass.select(banda_act)
        }else{
            change_uso_YY = imgClass.select(band_before).eq(classe_uso).subtract(
                                    imgClass.select(banda_act).eq(classe_uso));
            mask_Uso_kernel = change_uso_YY.eq(1).focalMin(2).focalMax(4)
            maskPixelsRem = change_uso_YY.updateMask(mask_Uso_kernel.eq(0))
            if (yband_name == 'classification_2023'){ 
                print("run 2023")               
                class_tmp = imgClass.select(yband_name).where(change_uso_YY.eq(1), classe_uso)
            }else{
                class_tmp = imgClass.select(yband_name).where(maskPixelsRem.eq(1), classe_uso)
            }
            class_output = class_output.addBands(class_tmp.rename(yband_name))
        }

        nameExp = 'filterSPU_BACIA_'+ str(name_bacia) + "_GTB_V20_step1"
        class_output = class_output.clip(geomBacia).set(
            'version', param['versionOut'], 'biome', 'CAATINGA',
            'collection', '9.0', 'id_bacia', name_bacia,
            'sensor', 'Landsat', 'source','geodatin', 
            'filter', 'spatial_use',
            'model', nmodel, 'step', param['step'], 
            'system:footprint', geomBacia
        )
    })


})



