// https://code.earthengine.google.com/74aac3d0d5ac8a5a8f40bc4f21059452
var param = {
    'asset_fire_monitor' : 'projects/mapbiomas-public/assets/brazil/fire/monitor/mapbiomas_fire_monthly_burned_v1',
    'asset_matopiba': 'projects/mapbiomas-fogo/assets/territories/matopiba',
    "BR_ESTADOS_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_ESTADOS_2022",
    "br_estados_raster": 'projects/mapbiomas-workspace/AUXILIAR/estados-2016-raster',
    "BR_Municipios_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_Municipios_2022",
    "BR_Pais_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_Pais_2022",
    "Im_bioma_250" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/Im_bioma_250",
    'vetor_biomas_250': 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
    'biomas_250_rasters': 'projects/mapbiomas-workspace/AUXILIAR/RASTER/Bioma250mil',
    'lstYears': [2019,2020,2021,2022,2023,2024]
}
var vis = {
    pmt_fire:  {min: 0, max: 1, palette: ['00FFFF', 'FF0000']},
    constante: {min: 0, max: 1}
};
var getInfo = false;
var biomas_raster = ee.Image(param.biomas_250_rasters).eq(2);
var shpCatinga = ee.FeatureCollection(param.vetor_biomas_250)
                        .filter(ee.Filter.eq('CD_Bioma', 2));
print("metadados biomas ", shpCatinga);
print("area Caatinga ", shpCatinga.geometry().area().divide(10000));
var shpMatopiba = ee.FeatureCollection(param.asset_matopiba);
print("area Matopiba ", shpMatopiba.geometry().area().divide(10000));
var shpEstados = ee.FeatureCollection(param.BR_ESTADOS_2022);
                      
if (getInfo){
    var estaMatopiba = shpEstados.filterBounds(shpMatopiba.geometry().buffer(-5000));
    print("show data Matopiba/estados ", estaMatopiba);

    var lstCod = estaMatopiba.reduceColumns(ee.Reducer.toList(2), ['CD_UF', 'NM_UF']).get('list');
    print("lista de infor Estados Matopiba ", lstCod);
}else{
    var lstIdsMat = ['21','22','23','24','25','26','27','28','29'];  //'17', '21',
    var dictEst = {
        '21': 'MARANHÃO',
        '22': 'PIAUÍ',
        '23': 'CEARÁ',
        '24': 'RIO GRANDE DO NORTE',
        '25': 'PARAÍBA',
        '26': 'PERNAMBUCO',
        '27': 'ALAGOAS',
        '28': 'SERGIPE',
        '29': 'BAHIA',
        '31': 'MINAS GERAIS',
        '32': 'ESPÍRITO SANTO',
        '17': 'Tocantins',
    }
    var estaMatopiba = shpEstados.filter(ee.Filter.inList('CD_UF', lstIdsMat));
    print("lista de info Estados Matopiba ", dictEst);
    
}

var imColfire = ee.ImageCollection(param.asset_fire_monitor);
print("show metadata imagecollections fire", imColfire);

Map.addLayer(ee.Image.constant(1), vis.constante, 'base');

param.lstYears.forEach(function(nyear){
    var imgFire = imColfire.filter(ee.Filter.eq('year', nyear));
    print('Fire image Collection year ' + nyear , imgFire);
    imgFire = imgFire.reduce(ee.Reducer.sum()).gt(0);
    imgFire = imgFire.clip(estaMatopiba.geometry().intersection(shpMatopiba.geometry()))//.updateMask(biomas_raster);
    Map.addLayer(imgFire.selfMask(), vis.pmt_fire, 'Fire monitor ' + nyear, false);    
})

// Paint all the polygon edges with the same number and width, display.
var outlineMat = ee.Image().byte().paint({
    featureCollection: shpMatopiba,  color: 1, width: 1.5 });
var outlineEstados = ee.Image().byte().paint({
    featureCollection: estaMatopiba,  color: 1, width: 1.5 });
var outlineCaat = ee.Image().byte().paint({
    featureCollection: shpCatinga,  color: 1, width: 1.5 });    
Map.addLayer(outlineEstados, {palette: 'green'}, 'estadosMatopiba');
Map.addLayer(outlineMat, {palette: 'black'}, 'shpMatopiba');
Map.addLayer(outlineCaat, {palette: '#0052ff'}, 'shpCaatinga');
