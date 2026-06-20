# 30분/60분 대중교통 접근성 및 도달 인구·종사자수 산출 보고서

## 작업 목적
판교 제1테크노밸리와 위례 계획구역의 핵심역 기준 대중교통 접근성을 비교하기 위해 지하철 네트워크 최단시간 기반 30분/60분 도달권을 산출하고, 도달권 내부의 SGIS 인구·종사자수를 면적비례 방식으로 추정했다.

이번 작업에서는 접근성 및 도달 인구·종사자수만 계산했다. 역세권 면적비율, 보너스 분석, 대시보드용 통합 GeoJSON/JSON은 생성하지 않았다.

## 사용한 핵심역
- 판교: 판교역, `network/nodes.tsv` node id `824`, 신분당선 판교
- 위례: 남위례역, `network/nodes.tsv` node id `735`, 서울8호선 남위례
- 핵심역 좌표는 `derived_data/05_station_area/core_stations.geojson`를 확인용으로 읽었고, 네트워크 최단시간 origin은 위 node id를 사용했다.
- 동일 명칭의 위례선 남위례 node는 이번 분석 origin에서 제외했다.

## 사용한 분석경계
- `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson` 읽기 전용
- `derived_data/00_boundaries/wirye_boundary.geojson` 읽기 전용
- 경계 파일은 수정하거나 덮어쓰지 않았다.

## 사용한 지하철 네트워크 파일
- nodes: `network/nodes.tsv`
- links: `network/links.tsv`

### nodes.tsv 컬럼 구조
`id`, `linenm`, `statnm`, `x_5179`, `y_5179`, `lng`, `lat`, `begin`, `effective_begin`, `geometry_wkt`

### links.tsv 컬럼 구조
`id`, `fromNode`, `toNode`, `timeFT`, `timeTF`, `kind`, `begin`, `linenm_from`, `linenm_to`, `length_m`, `geometry_wkt`

## 링크 시간 처리 방식
`links.tsv`의 `timeFT`, `timeTF`를 초 단위 소요시간으로 보고 60으로 나누어 분 단위 비용으로 변환했다.

- `fromNode -> toNode`: `timeFT`
- `toNode -> fromNode`: `timeTF`
- 총 방향성 링크 수: 3,026개

## 최단시간 계산 방식
각 핵심역 node id를 origin으로 하여 Dijkstra 최단시간을 계산했다. 30분, 60분 이내 도달 가능한 역을 추출했고, 누적 접근성 곡선은 10/20/30/40/50/60분 기준으로 별도 집계했다.

## 도달권 polygon 생성 방식
도달 가능한 역 point를 EPSG:5186으로 변환한 뒤 concave hull을 적용했다. concave hull 생성이 불가능한 경우 convex hull 또는 단일 point buffer를 보조적으로 사용하도록 처리했다.

이 도달권은 실제 보행 접근권이 아니라 지하철역 기반 근사 도달권이다.

## SGIS 인구·종사자수 결합
`derived_data/03_sgis_jobs_housing/sgis_joined_census.geojson`는 분석경계 내부 집계구만 포함하고 있어 30/60분 도달권 전체 인구·종사자 산정에는 부족했다.

따라서 03 폴더의 기존 결과는 덮어쓰지 않고, 원천 SGIS CSV와 서울·경기 집계구 경계를 읽어 04 접근성 작업 내부에서만 결합했다.

- 인구 원천: `인구가구/11_2023년_인구총괄(총인구).csv`, `인구가구/31_2023년_인구총괄(총인구).csv`
- 종사자 원천: `인구가구/11_2023년_산업분류별(10차_대분류)_종사자수.csv`, `인구가구/31_2023년_산업분류별(10차_대분류)_종사자수.csv`
- 집계구 경계: `집계구경계/bnd_oa_11_2025_2Q.shp`, `집계구경계/bnd_oa_31_2025_2Q.shp`
- 집계구 CRS: 원천 EPSG:5179로 읽어 EPSG:5186으로 변환
- 면적 계산 CRS: EPSG:5186

## 면적비례 배분 방식
집계구 원래 면적을 `original_area_sqm`, 도달권과 겹친 면적을 `intersect_area_sqm`로 계산하고 `allocation_ratio = intersect_area_sqm / original_area_sqm`를 적용했다. 인구와 종사자수는 해당 비율만큼 배분했다.

## 30분/60분 결과 요약
- 판교역 30분: 도달 가능 역 91개, 도달 가능 인구 2,342,411.0명, 도달 가능 종사자수 1,917,642.3명
- 판교역 60분: 도달 가능 역 592개, 도달 가능 인구 16,774,254.0명, 도달 가능 종사자수 8,542,443.8명
- 남위례역 30분: 도달 가능 역 114개, 도달 가능 인구 1,942,910.9명, 도달 가능 종사자수 1,481,691.1명
- 남위례역 60분: 도달 가능 역 542개, 도달 가능 인구 15,270,097.6명, 도달 가능 종사자수 7,937,442.3명

## 누적 접근성 곡선 요약
| area_name | origin_station | time_min | reachable_station_count | reachable_population | reachable_workers |
|---|---:|---:|---:|---:|---:|
| pangyo_1st_technovalley | 판교역 | 10 | 7 | 52,313.3 | 74,153.8 |
| pangyo_1st_technovalley | 판교역 | 20 | 26 | 360,043.7 | 320,347.3 |
| pangyo_1st_technovalley | 판교역 | 30 | 91 | 2,342,411.0 | 1,917,642.3 |
| pangyo_1st_technovalley | 판교역 | 40 | 194 | 7,302,035.2 | 4,613,133.1 |
| pangyo_1st_technovalley | 판교역 | 50 | 420 | 13,022,718.0 | 6,986,772.3 |
| pangyo_1st_technovalley | 판교역 | 60 | 592 | 16,774,254.0 | 8,542,443.8 |
| wirye_plan_area | 남위례역 | 10 | 20 | 162,093.5 | 68,104.5 |
| wirye_plan_area | 남위례역 | 20 | 54 | 874,789.9 | 489,417.5 |
| wirye_plan_area | 남위례역 | 30 | 114 | 1,942,910.9 | 1,481,691.1 |
| wirye_plan_area | 남위례역 | 40 | 198 | 5,369,264.0 | 4,017,895.8 |
| wirye_plan_area | 남위례역 | 50 | 348 | 11,131,292.1 | 6,113,945.2 |
| wirye_plan_area | 남위례역 | 60 | 542 | 15,270,097.6 | 7,937,442.3 |

## 생성 파일
- `derived_data/04_accessibility/reachable_stations.csv`
- `derived_data/04_accessibility/accessibility_isochrones.geojson`
- `derived_data/04_accessibility/accessibility_population_workers.csv`
- `derived_data/04_accessibility/cumulative_accessibility_curve.csv`
- `derived_data/04_accessibility/accessibility_sgis_intersections.geojson`
- `derived_data/04_accessibility/accessibility_report.md`

## 한계점
- 도달권 polygon은 지하철역 point의 hull 기반 근사치이며, 실제 보행 접근권·환승 대기시간·배차간격·출입구 위치·버스 연계는 반영하지 않았다.
- 네트워크 링크의 `timeFT/timeTF` 값을 그대로 사용했으므로 데이터 구축 시점과 실제 운행시간 차이가 있을 수 있다.
- SGIS 값은 집계구 단위 자료를 면적비례로 배분한 추정치이며, 실제 인구·종사자 분포가 집계구 내부에서 균등하다고 가정한다.
- 03 결과 파일은 분석경계 내부 집계구만 포함되어 접근성 분석 범위에는 부족했으므로, 원천 SGIS와 서울·경기 집계구 경계를 04 작업에서만 재결합했다.
