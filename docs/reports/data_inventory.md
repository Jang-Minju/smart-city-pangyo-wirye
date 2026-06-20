# 데이터 인벤토리

## 과제 MD 요구사항 요약

- 과제는 판교테크노밸리와 실패/저조 업무지구 1곳을 공공데이터로 비교하는 시스템 및 보고서를 요구한다.
- 필수 데이터는 SGIS 인구·종사자, 토지이용계획/건축물대장, 도로망, 수도권 지하철 네트워크다.
- 필수 지표는 용도지역 구성비, 건축물 주용도 구성비, 토지이용 혼합도, 개발 실현 정도, 등시간권 접근성, 도달가능 인구·종사자, 인구·가구·사업체·종사자 및 직주 지표다.
- 모든 분석은 시간범위, 공간범위, 공간단위, 시간단위를 명시해야 한다.
- 현재 데이터 인벤토리는 이 요구사항에 맞춰 어떤 원자료가 어느 지표에 투입 가능한지 확인하기 위한 사전 단계다.

## 현재 데이터의 역할 요약

- `가구및획지`: 판교/위례 분석 경계 정의, 획지 용도 확인, 업무·상업·도시지원 후보 선별에 사용 가능.
- `서울용도지역`, `경기용도지역`: 용도지역 구성비 산출에 사용 가능. `DGM_NM`/`dgm_nm` 계열이 용도지역명 컬럼이다.
- `건축물`: 건축물 주용도, 연면적, 대지면적, 용적률, 사용승인일 등 토지이용·개발 실현 정도 분석에 사용 가능. 좌표/PNU가 없어 공간 결합에는 지번 정제 또는 필지 도형 결합이 필요하다.
- `인구가구`: SGIS 집계구/격자 ID별 인구·가구·사업체·종사자 값. 공간 분석에는 동일 ID의 geometry 파일이 추가로 필요하다.
- `subway`: 현재 폴더에는 개통/대기시간/생성 노트북만 있고 역·링크 TSV 본체는 보이지 않는다. 등시간권 분석에는 `nodes.tsv`, `links.tsv` 또는 이에 준하는 네트워크 산출물이 필요하다.

## 폴더별 요약

| folder | file_count | spatial_files |
| --- | --- | --- |
| subway | 3 | 0 |
| 가구및획지 | 5 | 1 |
| 건축물 | 2 | 0 |
| 경기용도지역 | 95 | 19 |
| 서울용도지역 | 170 | 34 |
| 인구가구 | 12 | 0 |

## 전체 파일 인벤토리

| folder | file | extension | records | columns | geometry | geometry_type | crs | main_columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 인구가구 | 인구가구\11_2023년_가구총괄.csv | .csv | 38194 | year, spatial_id, item_code, value | No |  |  | `year`, `spatial_id`, `value`: 집계구/격자 단위 가구수. geometry는 별도 필요. |
| 인구가구 | 인구가구\11_2023년_산업분류별(10차_대분류)_사업체수.csv | .csv | 153840 | year, spatial_id, item_code, value | No |  |  | `item_code`, `value`: 산업분류별 사업체 수. 공간 ID와 결합 필요. |
| 인구가구 | 인구가구\11_2023년_산업분류별(10차_대분류)_종사자수.csv | .csv | 153840 | year, spatial_id, item_code, value | No |  |  | `item_code`, `value`: 산업분류별 종사자 수. 공간 ID와 결합 필요. |
| 인구가구 | 인구가구\11_2023년_인구총괄(총인구).csv | .csv | 57291 | year, spatial_id, item_code, value | No |  |  | `year`, `spatial_id`, `value`: 집계구/격자 단위 총인구. geometry는 별도 필요. |
| 인구가구 | 인구가구\31023_2023년_가구총괄.csv | .csv | 1852 | year, spatial_id, item_code, value | No |  |  | `year`, `spatial_id`, `value`: 집계구/격자 단위 가구수. geometry는 별도 필요. |
| 인구가구 | 인구가구\31023_2023년_산업분류별(10차_대분류)_사업체수.csv | .csv | 6326 | year, spatial_id, item_code, value | No |  |  | `item_code`, `value`: 산업분류별 사업체 수. 공간 ID와 결합 필요. |
| 인구가구 | 인구가구\31023_2023년_산업분류별(10차_대분류)_종사자수.csv | .csv | 6326 | year, spatial_id, item_code, value | No |  |  | `item_code`, `value`: 산업분류별 종사자 수. 공간 ID와 결합 필요. |
| 인구가구 | 인구가구\31023_2023년_인구총괄(총인구).csv | .csv | 2778 | year, spatial_id, item_code, value | No |  |  | `year`, `spatial_id`, `value`: 집계구/격자 단위 총인구. geometry는 별도 필요. |
| 인구가구 | 인구가구\31_2023년_가구총괄.csv | .csv | 56788 | year, spatial_id, item_code, value | No |  |  | `year`, `spatial_id`, `value`: 집계구/격자 단위 가구수. geometry는 별도 필요. |
| 인구가구 | 인구가구\31_2023년_산업분류별(10차_대분류)_사업체수.csv | .csv | 216573 | year, spatial_id, item_code, value | No |  |  | `item_code`, `value`: 산업분류별 사업체 수. 공간 ID와 결합 필요. |
| 인구가구 | 인구가구\31_2023년_산업분류별(10차_대분류)_종사자수.csv | .csv | 216573 | year, spatial_id, item_code, value | No |  |  | `item_code`, `value`: 산업분류별 종사자 수. 공간 ID와 결합 필요. |
| 인구가구 | 인구가구\31_2023년_인구총괄(총인구).csv | .csv | 85182 | year, spatial_id, item_code, value | No |  |  | `year`, `spatial_id`, `value`: 집계구/격자 단위 총인구. geometry는 별도 필요. |
| 건축물 | 건축물\건축물대장_go12385_20260617220540.xlsx | .xlsx | 51773 | PK, 대장구분, 시도, 시군구, 법정동, 번, 지, 대지구분, 특수지명, 블록, 로트, 외필지수, 건물명, 동명, 대지면적(㎡), 건축면적(㎡), 연면적(㎡), 건폐율(%), 용적률(%), 용적률산정연면적(㎡), 주구조, 기타구조, 주용도, 기타용도, 주지붕, 기타지붕, 높이, 지상층수, 지하층수, 총동연면적, 세대수, 가구수, 호수, 허가일, 착공일, 사용승인일, 부속건축물수, 승용승강기(대), 비상용승강기(대), 옥내자주식대수, 옥외자주식대수, 인근자주식대수, 옥내기계식대수, 옥외기계식대수, 인근기계식대수, 옥내전기차대수, 옥외전기차대수, 인근전기차대수, 면제대수, 특수공법여부, 용도지역코드명정보, 용도지구코드명정보, 용도구역코드명정보 | No |  |  | 건축물 용도·면적·용적률 분석 가능. 주요 컬럼: `시도`, `시군구`, `법정동`, `번`, `지`, `대지면적(㎡)`, `건축면적(㎡)`, `연면적(㎡)`, `용적률(%)`, `주용도`, `기타용도`, `용도지역코드명정보`. 좌표/PNU 없음. |
| 건축물 | 건축물\건축물대장_go12385_20260617220650.xlsx | .xlsx | 24211 | PK, 대장구분, 시도, 시군구, 법정동, 번, 지, 대지구분, 특수지명, 블록, 로트, 외필지수, 건물명, 동명, 대지면적(㎡), 건축면적(㎡), 연면적(㎡), 건폐율(%), 용적률(%), 용적률산정연면적(㎡), 주구조, 기타구조, 주용도, 기타용도, 주지붕, 기타지붕, 높이, 지상층수, 지하층수, 총동연면적, 세대수, 가구수, 호수, 허가일, 착공일, 사용승인일, 부속건축물수, 승용승강기(대), 비상용승강기(대), 옥내자주식대수, 옥외자주식대수, 인근자주식대수, 옥내기계식대수, 옥외기계식대수, 인근기계식대수, 옥내전기차대수, 옥외전기차대수, 인근전기차대수, 면제대수, 특수공법여부, 용도지역코드명정보, 용도지구코드명정보, 용도구역코드명정보 | No |  |  | 건축물 용도·면적·용적률 분석 가능. 주요 컬럼: `시도`, `시군구`, `법정동`, `번`, `지`, `대지면적(㎡)`, `건축면적(㎡)`, `연면적(㎡)`, `용적률(%)`, `주용도`, `기타용도`, `용도지역코드명정보`. 좌표/PNU 없음. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ111.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ111.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ111.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ111.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ111.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ111.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ111.shp | .shp | 3307 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ111.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ111.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ112.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ112.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ112.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ112.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ112.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ112.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ112.shp | .shp | 3938 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ112.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ112.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ113.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ113.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ113.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ113.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ113.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ113.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ113.shp | .shp | 795 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ113.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ113.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ114.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ114.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ114.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ114.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ114.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ114.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ114.shp | .shp | 9 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ114.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ114.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ115.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ115.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ115.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ115.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ115.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ115.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ115.shp | .shp | 157 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ115.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ115.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ121.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ121.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ121.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ121.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ121.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ121.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ121.shp | .shp | 64 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ121.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ121.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ122.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ122.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ122.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ122.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ122.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ122.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ122.shp | .shp | 1 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ122.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ122.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ123.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ123.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ123.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ123.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ123.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ123.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ123.shp | .shp | 44 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ123.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ123.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ124.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ124.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ124.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ124.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ124.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ124.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ124.shp | .shp | 127 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ124.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ124.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ126.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ126.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ126.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ126.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ126.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ126.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ126.shp | .shp | 31 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ126.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ126.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ128.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ128.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ128.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ128.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ128.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ128.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ128.shp | .shp | 15 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ128.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ128.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ129.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ129.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ129.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ129.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ129.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ129.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ129.shp | .shp | 39 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ129.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ129.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ131.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ131.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ131.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ131.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ131.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ131.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ131.shp | .shp | 6 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ131.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ131.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ141.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ141.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ141.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ141.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ141.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ141.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ141.shp | .shp | 51 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ141.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ141.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ142.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ142.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ142.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ142.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ142.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ142.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ142.shp | .shp | 8 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ142.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ142.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ145.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ145.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ145.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ145.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ145.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ145.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ145.shp | .shp | 18 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ145.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ145.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ171.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ171.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ171.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ171.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ171.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ171.shp` 참조. |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ171.shp | .shp | 6 | present_sn, lclas_cl, mlsfc_cl, sclas_cl, atrb_se, wtnnc_sn, ntfc_sn, dgm_nm, dgm_ar, dgm_lt, sgg_cd, drawing_no, create_dat, mnum, alias, remark, ntfdate, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `dgm_nm`, `atrb_se`, `dgm_ar`, `sgg_cd` |
| 서울용도지역 | 서울용도지역\KLIP_C_UQ171.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\KLIP_C_UQ171.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ111.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ111.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ111.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ111.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ111.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ111.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ111.shp | .shp | 8158 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ111.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ111.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ112.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ112.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ112.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ112.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ112.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ112.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ112.shp | .shp | 2116 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ112.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ112.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ113.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ113.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ113.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ113.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ113.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ113.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ113.shp | .shp | 399 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ113.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ113.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ114.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ114.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ114.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ114.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ114.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ114.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ114.shp | .shp | 4 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ114.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ114.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ121.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ121.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ121.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ121.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ121.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ121.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ121.shp | .shp | 41 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ121.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ121.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ122.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ122.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ122.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ122.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ122.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ122.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ122.shp | .shp | 560 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ122.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ122.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ123.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ123.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ123.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ123.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ123.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ123.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ123.shp | .shp | 42 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ123.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ123.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ124.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ124.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ124.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ124.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ124.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ124.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ124.shp | .shp | 24 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ124.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ124.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ125.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ125.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ125.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ125.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ125.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ125.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ125.shp | .shp | 7 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ125.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ125.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ126.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ126.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ126.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ126.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ126.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ126.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ126.shp | .shp | 7 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ126.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ126.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ128.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ128.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ128.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ128.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ128.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ128.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ128.shp | .shp | 38 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ128.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ128.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ129.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ129.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ129.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ129.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ129.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ129.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ129.shp | .shp | 12 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ129.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ129.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ130.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ130.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ130.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ130.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ130.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ130.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ130.shp | .shp | 2 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ130.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ130.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ131.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ131.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ131.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ131.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ131.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ131.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ131.shp | .shp | 39 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ131.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ131.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ141.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ141.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ141.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ141.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ141.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ141.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ141.shp | .shp | 2 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ141.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ141.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ142.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ142.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ142.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ142.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ142.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ142.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ142.shp | .shp | 69 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ142.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ142.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ145.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ145.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ145.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ145.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ145.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ145.shp` 참조. |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ145.shp | .shp | 1 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 서울용도지역 | 서울용도지역\UPIS_C_UQ145.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `서울용도지역\UPIS_C_UQ145.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ111.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ111.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ111.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ111.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ111.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ111.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ111.shp | .shp | 6866 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ111.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ111.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ112.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ112.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ112.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ112.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ112.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ112.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ112.shp | .shp | 25818 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ112.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ112.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ113.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ113.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ113.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ113.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ113.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ113.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ113.shp | .shp | 5214 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ113.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ113.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ114.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ114.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ114.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ114.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ114.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ114.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ114.shp | .shp | 19 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ114.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ114.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ115.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ115.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ115.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ115.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ115.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ115.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ115.shp | .shp | 30 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ115.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ115.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ121.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ121.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ121.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ121.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ121.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ121.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ121.shp | .shp | 496 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ121.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ121.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ122.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ122.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ122.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ122.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ122.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ122.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ122.shp | .shp | 89 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ122.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ122.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ123.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ123.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ123.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ123.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ123.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ123.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ123.shp | .shp | 33 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ123.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ123.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ124.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ124.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ124.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ124.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ124.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ124.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ124.shp | .shp | 50 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ124.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ124.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ126.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ126.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ126.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ126.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ126.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ126.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ126.shp | .shp | 33 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ126.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ126.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ127.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ127.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ127.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ127.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ127.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ127.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ127.shp | .shp | 7 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ127.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ127.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ128.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ128.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ128.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ128.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ128.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ128.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ128.shp | .shp | 1044 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ128.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ128.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ129.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ129.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ129.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ129.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ129.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ129.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ129.shp | .shp | 261 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ129.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ129.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ130.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ130.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ130.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ130.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ130.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ130.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ130.shp | .shp | 42 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ130.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ130.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ131.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ131.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ131.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ131.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ131.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ131.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ131.shp | .shp | 2 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ131.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ131.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ141.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ141.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ141.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ141.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ141.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ141.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ141.shp | .shp | 106 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ141.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ141.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ142.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ142.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ142.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ142.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ142.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ142.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ142.shp | .shp | 15 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ142.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ142.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ144.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ144.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ144.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ144.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ144.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ144.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ144.shp | .shp | 2 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ144.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ144.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ145.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ145.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ145.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ145.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ145.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ145.shp` 참조. |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ145.shp | .shp | 1819 | PRESENT_SN, LCLAS_CL, MLSFC_CL, SCLAS_CL, ATRB_SE, WTNNC_SN, NTFC_SN, DGM_NM, DGM_AR, DGM_LT, SIGNGU_SE, DRAWING_NO, CREATE_DAT, geometry | Yes | MultiPolygon, Polygon | EPSG:5174 | 용도지역 구성비 산출 가능. 주요 컬럼: `DGM_NM`, `ATRB_SE`, `DGM_AR`, `SIGNGU_SE` |
| 경기용도지역 | 경기용도지역\UPIS_C_UQ145.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `경기용도지역\UPIS_C_UQ145.shp` 참조. |
| 가구및획지 | 가구및획지\the_geom.dbf | .dbf |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `가구및획지\the_geom.shp` 참조. |
| 가구및획지 | 가구및획지\the_geom.fix | .fix |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `가구및획지\the_geom.shp` 참조. |
| 가구및획지 | 가구및획지\the_geom.prj | .prj |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `가구및획지\the_geom.shp` 참조. |
| 가구및획지 | 가구및획지\the_geom.shp | .shp | 275483 | zoneCode, zoneName, blockName, blockType, lotName, geometry | Yes | MultiPolygon, Polygon | EPSG:5186 | `zoneName`: 사업지구, `blockName`/`lotName`: 획지 식별, `blockType`: 용도. 경계 정의와 획지 선택에 사용. |
| 가구및획지 | 가구및획지\the_geom.shx | .shx |  |  | Sidecar |  |  | SHP sidecar file. 주 데이터 구조는 `가구및획지\the_geom.shp` 참조. |
| subway | subway\line_waits.parquet | .parquet | 42 | linenm, waittm | No |  |  | 노선별 대기시간 데이터. 네트워크 소요시간 보정에 사용 가능. |
| subway | subway\make_network.ipynb | .ipynb | 17 | cell_type, source, metadata, outputs | No |  |  | 전처리/네트워크 생성 노트북. 데이터 테이블이 아니라 코드 문서. |
| subway | subway\opening.tsv | .tsv | 24 | date, desc | No |  |  | 개통일/노선 메타데이터. 지하철 시점 필터링에 사용 가능. |
