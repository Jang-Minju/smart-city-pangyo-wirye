# 경기용도지역 SHP 컬럼 점검 보고서

## 작업 개요

- 조사 폴더: `경기용도지역`
- 발견된 SHP 파일 수: 1
- 목표: 용도지역 명칭이 들어 있는 컬럼을 찾고 판교/위례 분석 경계와 clip하여 구성비 계산이 가능한지 판단

## SHP 파일 목록 및 기본 정보

| file | read_encoding | crs | record_count | geometry_type | bounds | columns | text_columns |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 경기용도지역\LSMD_CONT_UM211_41_202606.shp | cp949 | EPSG:5186 | 2 | Polygon | 231667.685, 590719.208, 241484.778, 595174.717 | ALIAS, REMARK, NTFDATE, SGG_OID, COL_ADM_SE, MNUM | ALIAS, REMARK, NTFDATE, COL_ADM_SE, MNUM |

## 전체 컬럼명

- `경기용도지역\LSMD_CONT_UM211_41_202606.shp`: ALIAS, REMARK, NTFDATE, SGG_OID, COL_ADM_SE, MNUM

## 문자형 컬럼 고유값 샘플

| file | column | unique_count | sample_values |
| --- | --- | --- | --- |
| 경기용도지역\LSMD_CONT_UM211_41_202606.shp | ALIAS | 0 |  |
| 경기용도지역\LSMD_CONT_UM211_41_202606.shp | REMARK | 0 |  |
| 경기용도지역\LSMD_CONT_UM211_41_202606.shp | NTFDATE | 0 |  |
| 경기용도지역\LSMD_CONT_UM211_41_202606.shp | COL_ADM_SE | 2 | 41650, 41820 |
| 경기용도지역\LSMD_CONT_UM211_41_202606.shp | MNUM | 2 | 64100004165020085171UMC5100001001, 64100004182020085171UMC5100001000 |

## 지정 용도지역 값 포함 컬럼 확인

검색 값:

- 주거지역
- 제1종일반주거지역
- 제2종일반주거지역
- 제3종일반주거지역
- 준주거지역
- 상업지역
- 일반상업지역
- 근린상업지역
- 자연녹지지역
- 보전녹지지역
- 생산녹지지역
- 공업지역
- 준공업지역

### 검색 결과

(없음)

판단: 지정한 용도지역 명칭이 포함된 문자형 컬럼을 찾지 못했다.

## 판교/위례 분석 경계와 Clip 가능성

| landuse_file | boundary | boundary_file | exists | crs | bounds_overlap | intersects | judgement |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 경기용도지역\LSMD_CONT_UM211_41_202606.shp | 판교 분석 경계 | analysis_boundaries\pangyo_1st_technovalley_candidate_boundary_5186.geojson | True | EPSG:5186 | False | False | 공간 범위가 겹치지 않아 현재 파일만으로는 clip 불가 |
| 경기용도지역\LSMD_CONT_UM211_41_202606.shp | 위례 분석 경계 | analysis_boundaries\wirye_business_commercial_candidate_boundary_5186.geojson | True | EPSG:5186 | False | False | 공간 범위가 겹치지 않아 현재 파일만으로는 clip 불가 |

판단: 공간 clip은 별도 검토 가능하지만 용도지역 명칭 컬럼이 확인되지 않아 구성비 계산 기준 컬럼을 먼저 확정해야 한다.

## 다음 단계

- 용도지역 컬럼이 확인되면 `geopandas.overlay(..., how="intersection")` 방식으로 분석 경계와 교차 면적을 계산한다.
- 면적은 EPSG:5186에서 계산하고, `용도지역별 교차면적 / 분석경계 전체면적`으로 구성비를 산출한다.
- 공간 교차가 없으면 경기용도지역 파일이 판교/위례 위치를 포함하는지, 또는 행정구역/시군 단위 파일이 누락됐는지 확인한다.
