var param = {
    'inputAssetCol': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',  
    // 'inputAssetCol': 'projects/mapbiomas-workspace/COLECAO9/integracao',
    'inputTransicao': 'projects/mapbiomas-workspace/COLECAO8/transicao',
    'assets' : {
        "Assentamento_Brasil" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/Assentamento_Brasil",
        "BR_ESTADOS_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_ESTADOS_2022",
        // # https://code.earthengine.google.com/2536e797df4b90efcc67e3b17ebf58a2
        "br_estados_raster": 'projects/mapbiomas-workspace/AUXILIAR/estados-2016-raster',
        "BR_Municipios_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_Municipios_2022",
        "BR_Pais_2022" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/BR_Pais_2022",
        "Im_bioma_250" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/Im_bioma_250",
        'vetor_biomas_250': 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
        'biomas_250_rasters': 'projects/mapbiomas-workspace/AUXILIAR/RASTER/Bioma250mil',
        "Sigef_Brasil" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/Sigef_Brasil",
        "Sistema_Costeiro_Marinho" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/Sistema_Costeiro_Marinho",
        "aapd" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/aapd",
        "areas_Quilombolas" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/areas_Quilombolas",
        "buffer_pts_energias" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/buffer_pts_energias",
        "energias-dissolve-aneel" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/energias-dissolve-aneel",
        "florestaspublicas" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/florestaspublicas",
        "imovel_certificado_SNCI_br" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/imovel_certificado_SNCI_br",
        "macro_RH" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/macro_RH",
        "meso_RH" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/meso_RH",
        "micro_RH" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/micro_RH",
        "pnrh_asd" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/pnrh_asd",
        "areas_priori_caatinga_nova_delimi" : "projects/mapbiomas-arida/areas_priori_caatinga_nova_delimi",
        "tis_poligonais_portarias" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/tis_poligonais_portarias",
        "transposicao-cbhsf" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/transposicao-cbhsf",
        "nucleos_desertificacao" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/pnrh_nucleos_desertificacao",
        "uso_sustentaveis_caat" : "projects/mapbiomas-arida/prj_clip_caat_dif_dissolv_us_caatinga",
        "area_protecao_integral_caat" : "projects/mapbiomas-arida/prj_clip_caat_dif_dissolv_pi_caatinga",
        "unidade_gerenc_RH_SNIRH_2020" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/unidade_gerenc_RH_SNIRH_2020",
        "reserva_biosfera_2019" : "projects/mapbiomas-workspace/AUXILIAR/RESERVA_BIOSFERA/caatinga-central-2019",
        "SemiArido_2024": 'projects/mapbiomas-workspace/AUXILIAR/SemiArido_2024',
        'semiarido' : 'users/mapbiomascaatinga04/semiarido_rec',
        "polos_irrigacao_atlas": 'projects/ee-mapbiomascaatinga04/assets/polos_irrigaaco_atlas',
        "energias_renovaveis": 'projects/ee-mapbiomascaatinga04/assets/energias_renovaveis',
        "bacia_sao_francisco" : 'users/solkancengine17/shps_public/bacia_sao_francisco' 
    },   
    // # 'assetVetor': 'users/data_sets_solkan/SHPs/APA_Guarajuba_limite',
    // 'assetVetor': 'users/data_sets_solkan/SHPs/APA_R_Capivara_limite',
    assetOut: {
        'Assentamento_Brasil': "projects/ee-solkancengine17/assets/shp_publicos/Assentamento_Brasil",
        "nucleos_desertificacao": "projects/ee-solkancengine17/assets/shp_publicos/nucleos_desertificacao",
        "uso_sustentaveis_caat" : "projects/ee-solkancengine17/assets/shp_publicos/uso_sustentaveis_caat",
        "area_protecao_integral_caat": "projects/ee-solkancengine17/assets/shp_publicos/area_protecao_integral_caat",
        'areas_Quilombolas': "projects/ee-solkancengine17/assets/shp_publicos/areas_Quilombolas",  
        "macro_RH": "projects/ee-solkancengine17/assets/shp_publicos/macro_RH", 
        "meso_RH": "projects/ee-solkancengine17/assets/shp_publicos/meso_RH", 
        'micro_RH': "projects/ee-solkancengine17/assets/shp_publicos/micro_RH", 
        'areas_priori_caatinga_nova_delimi': "projects/ee-solkancengine17/assets/shp_publicos/areas_priori_caatinga_nova_delimi", 
        'tis_poligonais_portarias': "projects/ee-solkancengine17/assets/shp_publicos/tis_poligonais_portarias", 
        "reserva_biosfera_2019": "projects/ee-solkancengine17/assets/shp_publicos/reserva_biosfera_2019",
        'SemiArido_2024': 'projects/ee-solkancengine17/assets/shp_publicos/SemiArido_2024',
        "energias_renovaveis": 'projects/ee-solkancengine17/assets/shp_publicos/energias_renovaveis',    
        "polos_irrigacao_atlas": 'projects/ee-solkancengine17/assets/shp_publicos/polos_irrigacao_atlas',
        "bacia_sao_francisco": 'projects/ee-solkancengine17/assets/shp_publicos/bacia_sao_francisco',
    }
}

function processoExportar(areaFeat, nameT){      
    var optExp = {
          'collection': ee.FeatureCollection(areaFeat), 
          'description': nameT, 
          'assetId': param['assetOut'][nameT]        
        };    
    Export.table.toAsset(optExp) ;
    print(" salvando ... " + nameT + "..!")      ;
}


var lst_nameAsset = [
    'Assentamento_Brasil', 
    "nucleos_desertificacao",
    "uso_sustentaveis_caat",
    "area_protecao_integral_caat",
    'areas_Quilombolas',  
    "macro_RH", 
    "meso_RH", 
    'micro_RH', 
    'areas_priori_caatinga_nova_delimi', 
    'tis_poligonais_portarias', 
    "reserva_biosfera_2019",
    'SemiArido_2024',
    "energias_renovaveis",    
    "polos_irrigacao_atlas",
    "bacia_sao_francisco",

];   

var featPrio = ee.FeatureCollection(param.assets['areas_priori_caatinga_nova_delimi']);
Map.addLayer(featPrio)

lst_nameAsset.forEach(function(feat_name){
    print(feat_name, param['assets'][feat_name]);
    var feat = ee.FeatureCollection(param['assets'][feat_name]);
    processoExportar(feat, feat_name);
})



