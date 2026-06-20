# derived_data

이 폴더는 판교 제1테크노밸리와 위례 업무·상업용지 비교 분석에서 생성될 파생 데이터를 저장하기 위한 작업 공간이다.

이번 단계에서는 폴더 구조와 저장 계획만 정리한다. 실제 지표 계산, 공간조인, 지도 생성, CSV 산출은 수행하지 않는다.

## 파생 데이터 저장 구조

| 폴더명 | 저장할 파생 데이터 | 사용할 원천 데이터 | 관련 교수님 필수/추가 지표 | 예상 산출 파일명 | 시스템에서 사용할 화면 또는 기능 |
| --- | --- | --- | --- | --- | --- |
| `00_boundaries/` | 판교·위례 최종 분석 경계, 핵심역 위치 | `analysis_boundaries`, `가구및획지`, `subway` | 모든 지표의 공간 기준 | `pangyo_boundary.geojson`, `wirye_boundary.geojson`, `core_stations.geojson` | 분석구역 선택, 기본 지도, 비교 화면 |
| `01_landuse_mix/` | 용도지역 구성비, LUM 토지이용혼합도, 가구및획지 `blockType` 기준 보조 혼합도 | `서울용도지역`, `경기용도지역`, `가구및획지`, `00_boundaries` | 필수: 토지이용혼합도, 용도지역 구성비 | `landuse_zone_composition.csv`, `landuse_mix_index.csv`, `landuse_blocktype_mix_index.csv`, `landuse_zones_clipped.geojson` | 토지이용 구성 차트, 혼합도 비교, 용도지역 지도 |
| `02_development_realization/` | 건축물 주용도 구성비, 평균 용적률, 연면적 가중 평균 용적률, 평균 건폐율, 공지 또는 미건축 필지 비율, 사용승인일 기반 개발 시계열 | `건축물`, `가구및획지`, `00_boundaries` | 필수: 개발 실현 정도, 건축물 주용도 구성비 | `building_use_composition.csv`, `development_realization.csv`, `building_approval_timeseries.csv`, `vacant_or_unbuilt_parcels.csv`, `buildings_joined.geojson` | 개발 실현도 대시보드, 건축물 용도 차트, 개발 시계열 |
| `03_sgis_jobs_housing/` | 인구, 가구, 사업체, 종사자, 직주비, 인구밀도, 고용밀도, 산업 기본 구성 | `인구가구`, `집계구경계`, `00_boundaries` | 필수: 직주지표, 인구·가구·사업체·종사자, 인구밀도, 고용밀도 | `population_business_summary.csv`, `jobs_housing_ratio.csv`, `industry_basic_composition.csv`, `sgis_joined_census.geojson` | 직주 비교 카드, 인구·고용 지도, SGIS 통계 차트 |
| `04_accessibility/` | 핵심역 기준 30분/60분 등시간권, 도달가능 인구, 도달가능 종사자, 누적 접근성 곡선, 역 선택 민감도 | `subway`, `network`, `인구가구`, `집계구경계`, `00_boundaries` | 필수: 접근성 분석, 등시간권, 도달가능 인구·종사자 | `isochrones_30_60.geojson`, `reachable_population_workers.csv`, `cumulative_accessibility_curve.csv`, `accessibility_station_sensitivity.csv` | 등시간권 지도, 접근성 비교, 누적 접근성 그래프 |
| `05_station_area/` | 역세권 500m/1km 버퍼, 분석구역 대비 역세권 면적비율 | `subway`, `00_boundaries` | 필수 보조 교통지표: 역세권 500m/1km 면적비율 | `station_area_ratio.csv`, `station_buffers.geojson` | 역세권 지도, 역세권 면적비율 비교 |
| `06_bonus_analysis/` | 산업별 사업체 비율, 산업별 종사자 비율, 산업별 LQ 또는 상대특화도, 업무시설밀도 | `인구가구`, `건축물`, `집계구경계`, `00_boundaries` | 추가분석: 산업특화도, 업무시설밀도 | `industry_specialization_lq.csv`, `industry_composition_detail.csv`, `business_facility_density.csv`, `bonus_analysis_summary.json` | 추가분석 탭, 산업특화도 차트, 업무시설밀도 비교 |
| `geojson/` | 웹 시스템에서 직접 읽을 통합 GeoJSON | 각 파생 데이터 폴더의 최종 공간 산출물 | 시스템 표시용 공간 데이터 | `system_boundaries.geojson`, `system_landuse.geojson`, `system_buildings.geojson`, `system_sgis.geojson`, `system_isochrones.geojson`, `system_station_buffers.geojson` | 지도 레이어, 레이어 토글, 지역 선택 |
| `stats/` | 웹 시스템에서 직접 읽을 통합 JSON 통계 | 각 파생 데이터 폴더의 최종 통계 산출물 | 시스템 표시용 차트·요약 데이터 | `summary_stats.json`, `chart_landuse.json`, `chart_development.json`, `chart_jobs_housing.json`, `chart_accessibility.json`, `chart_bonus.json` | 대시보드 카드, 차트, 비교 표 |
| `reports/` | 파생지표 처리 보고서, 처리 로그, 누락 데이터 및 한계 정리 | 전체 원천 데이터와 파생 데이터 | 보고서 재현성, 데이터 한계 설명 | `derived_metrics_report.md`, `data_processing_log.md`, `missing_data_and_limitations.md` | 보고서 다운로드, 분석 근거 확인 |

## 포함할 필수 파생지표

### 1. 토지이용혼합도

- 용도지역 구성비
- LUM 토지이용혼합도
- 가구및획지 `blockType` 기준 보조 혼합도

### 2. 개발 실현 정도

- 건축물 주용도 구성비
- 평균 용적률
- 연면적 가중 평균 용적률
- 평균 건폐율
- 공지 또는 미건축 필지 비율
- 사용승인일 기반 개발 시계열

### 3. 직주지표

- 인구
- 가구
- 사업체
- 종사자
- 직주비
- 인구밀도
- 고용밀도

### 4. 접근성 분석

- 핵심역 기준 30분/60분 등시간권
- 도달가능 인구
- 도달가능 종사자
- 누적 접근성 곡선

### 5. 보조 교통지표

- 역세권 500m/1km 면적비율

## 포함할 추가분석 지표

### 1. 산업특화도

- 산업별 사업체 비율
- 산업별 종사자 비율
- 산업별 LQ 또는 상대특화도

### 2. 업무시설밀도

- 업무시설 총연면적 / 분석구역 면적
- 업무시설 연면적 / 전체 연면적
- 업무시설 건축물 수 / 분석구역 면적

## 제외 지표

기업규모구조 분석은 이번 프로젝트에서 제외한다.

## 앞으로의 작업 순서

1. 경계 정리
2. 토지이용혼합도 산출
3. 개발 실현 정도 산출
4. SGIS 인구·사업체·종사자 및 직주지표 산출
5. 접근성 및 등시간권 산출
6. 역세권 면적비율 산출
7. 추가분석: 산업특화도, 업무시설밀도 산출
8. 시스템용 GeoJSON/JSON 통합
