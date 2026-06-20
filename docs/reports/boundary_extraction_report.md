# 지구경계 SHP 검색 및 추출 결과 보고서

## 작업 개요

- 실행 스크립트: `scripts/01_extract_boundaries.py`
- 원천 탐색 우선 경로: `판교\data\raw\지구경계_전국`
- 실제 사용 경로: `판교\지구경계_전국`
- 판교 검색 키워드: 판교, 판교테크노밸리, 제1판교, 제1판교테크노밸리, Pangyo
- 위례 검색 키워드: 위례, Wirye
- 면적 계산 좌표계: EPSG:5186
- 웹 지도용 변환 좌표계: EPSG:4326

## 전체 요약

- SHP 파일 개수: 1
- 좌표계(CRS): EPSG:5186
- 총 레코드 수: 1328
- 전체 속성 컬럼명: ar, stepCode, zoneCode, zoneName
- 판교 후보 개수: 2
- 위례 후보 개수: 1

## SHP 파일별 속성 확인

| file | crs | read_encoding | records | columns | text_columns |
| --- | --- | --- | --- | --- | --- |
| 판교\지구경계_전국\the_geom.shp | EPSG:5186 | cp949 | 1328 | zoneCode, zoneName, stepCode, ar | zoneCode, zoneName, stepCode, ar |

## 판교 검색 결과

- 발견된 레코드 수: 2
- 저장 폴더: `판교\data\processed\boundary`
- 저장 파일:
  - `pangyo_boundary_5186.geojson`
  - `pangyo_boundary_4326.geojson`
  - `pangyo_boundary_summary.csv`

| used_columns | matched_keywords | zone_name | project_name | area_sqm_calc_epsg5186 | area_sqm_source_attr | source_file | source_crs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zoneName | 판교 | 성남판교지구 택지개발사업 |  | 8921646.202927612 | 8,921,788.2 | 판교\지구경계_전국\the_geom.shp | EPSG:5186 |
| zoneName | 판교 | 성남 판교대장 도시개발구역 |  | 917055.3350600078 | 917,068.8 | 판교\지구경계_전국\the_geom.shp | EPSG:5186 |

### 판교 경계 판단

속성명에는 판교가 포함되지만 제1판교테크노밸리 표현은 확인되지 않아 제1판교테크노밸리로 확정하기 어려움.

## 위례 검색 결과

- 발견된 레코드 수: 1
- 저장 폴더: `위례\data\processed\candidates`
- 저장 파일:
  - `wirye_candidates_5186.geojson`
  - `wirye_candidates_4326.geojson`
  - `wirye_candidates_summary.csv`

| used_columns | matched_keywords | zone_name | project_name | area_sqm_calc_epsg5186 | area_sqm_source_attr | source_file | source_crs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zoneName | 위례 | 위례 택지개발사업 예정지구 |  | 6753738.598234524 | 6,755,172.9 | 판교\지구경계_전국\the_geom.shp | EPSG:5186 |

### 위례 경계 판단

- 전체 사업지구 여부: 지구명 기준으로 위례신도시/위례택지개발사업 전체 사업지구일 가능성이 높음.
- 업무/상업/자족용지 속성 여부: 현재 SHP 속성에는 업무용지/상업용지/자족용지 구분 표현이 확인되지 않음.
- 결론: 위례 후보는 아직 업무·상업용지 경계로 확정하지 않는다.

## 결과가 없을 때 확인용 컬럼 및 샘플

아래 표는 후보가 없는 파일이 있을 경우 해당 파일의 샘플을 보여준다. 모든 파일에서 후보가 발견된 경우에는 전체 데이터의 앞 20개 속성 레코드를 참고용으로 표시한다.

### 전체 컬럼명 목록

ar, stepCode, zoneCode, zoneName

### 샘플 레코드 20개

| zoneCode | zoneName | stepCode | ar | source_file |
| --- | --- | --- | --- | --- |
| 27290KH1986001 | 대구월성 | CP | 487,938.5 | 판교\지구경계_전국\the_geom.shp |
| 27230KH2001001 | 대구매천 | CP | 399,189.0 | 판교\지구경계_전국\the_geom.shp |
| 27200KH1981001 | 대구송현 | CP | 212,719.6 | 판교\지구경계_전국\the_geom.shp |
| 26260KH1984001 | 부산망미 | CP | 249,951.0 | 판교\지구경계_전국\the_geom.shp |
| 27290DA1989001 | 대구상인 | CP | 944,971.6 | 판교\지구경계_전국\the_geom.shp |
| 27260DA1989001 | 대구시지 | CP | 868,471.7 | 판교\지구경계_전국\the_geom.shp |
| 48220KL1987001 | 충무도남 | CP | 180,924.6 | 판교\지구경계_전국\the_geom.shp |
| 29200DA2006007 | 광주하남2 | CP | 989,891.6 | 판교\지구경계_전국\the_geom.shp |
| 31200KL1989001 | 울산화봉 | CP | 1,060,700.4 | 판교\지구경계_전국\the_geom.shp |
| 29170KL1989002 | 광주일곡 | CP | 1,473,172.5 | 판교\지구경계_전국\the_geom.shp |
| 27290DA1989002 | 대구장기 | CP | 397,937.9 | 판교\지구경계_전국\the_geom.shp |
| 31110KL1987001 | 울산태화 | CP | 577,979.0 | 판교\지구경계_전국\the_geom.shp |
| 30170KL1985001 | 대전둔산 | CP | 7,434,839.2 | 판교\지구경계_전국\the_geom.shp |
| 27230KL1981001 | 대구월배 | CP | 872,571.5 | 판교\지구경계_전국\the_geom.shp |
| 45111DA1985001 | 전주아중 | CP | 2,042,585.2 | 판교\지구경계_전국\the_geom.shp |
| 42110DA1989001 | 춘천사우 | CP | 122,004.4 | 판교\지구경계_전국\the_geom.shp |
| 42110DC2010001 | 춘천 온의2지구 도시개발사업 | CP | 43,982.4 | 판교\지구경계_전국\the_geom.shp |
| 47290KL1994001 | 경산백천 | CP | 327,830.0 | 판교\지구경계_전국\the_geom.shp |
| 47290KL1998001 | 경산사동2지구 택지개발사업 | CP | 936,176.6 | 판교\지구경계_전국\the_geom.shp |
| 47290DA1991001 | 경산옥산2 | CP | 339,980.6 | 판교\지구경계_전국\the_geom.shp |

## 다음 단계 제안

- 위례 업무·상업용지 확정을 위해 토지이용계획도 또는 토지이용계획 SHP/DWG/PDF를 확보한다.
- 자족용지 여부 확인을 위해 가구획지계획도, 획지별 용도/면적 조서, 공급대상 토지 목록을 확보한다.
- 판교 제1테크노밸리 확정을 위해 산업단지/도시첨단산업단지 고시 경계, 지구단위계획 결정도, 필지 또는 획지 단위 도면을 대조한다.
- 현재 택지정보시스템 지구경계는 사업지구 단위 경계일 가능성이 있으므로, 업무·상업·자족용지 분석에는 세부 토지이용 또는 획지 경계 데이터가 필요하다.

## 재실행 방법

```powershell
python scripts/01_extract_boundaries.py
```

## 기계 판독용 메타데이터

```json
{
  "metadata": [
    {
      "file": "판교\\지구경계_전국\\the_geom.shp",
      "crs": "EPSG:5186",
      "read_encoding": "cp949",
      "records": 1328,
      "columns": [
        "zoneCode",
        "zoneName",
        "stepCode",
        "ar"
      ],
      "text_columns": [
        "zoneCode",
        "zoneName",
        "stepCode",
        "ar"
      ]
    }
  ],
  "pangyo_count": 2,
  "wirye_count": 1
}
```
