# 판교 경계 갱신 0단계 백업 및 교체 준비 보고서

작성일: 2026-06-19

## 1. 최종 판교 경계 파일

- 최종 판교 경계 파일: `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson`
- 기존 판교 경계 파일: `derived_data/00_boundaries/pangyo_boundary.geojson`
- 위례 경계 파일: `derived_data/00_boundaries/wirye_boundary.geojson`
- 위례 경계와 위례 지표는 이번 갱신 대상에서 제외하며 변경하지 않는다.

## 2. 최종 판교 경계 검증 결과

| 항목 | 기존 판교 경계 | 최종 판교 경계 |
|---|---:|---:|
| 파일 | `pangyo_boundary.geojson` | `pangyo_boundary_user_drawn2_5186.geojson` |
| CRS | EPSG:5186 | EPSG:5186 |
| feature 수 | 1 | 1 |
| geometry type | Polygon | Polygon |
| geometry validity | valid | valid |
| 면적 | 1,066,109.797 m2 | 860,504.888 m2 |

- 면적 차이: -205,604.909 m2
- 면적 차이율: -19.286%
- 최종 판교 경계는 EPSG:5186 좌표계의 단일 Polygon이며 geometry가 유효하다.

## 3. 백업 완료 여부

- 백업 완료 여부: 완료
- 백업 폴더 경로: `backup_before_pangyo_boundary_update/`
- 백업 파일 수: 125개

백업 대상별 상태:

| 대상 | 상태 |
|---|---|
| `derived_data/00_boundaries` | 백업 완료 |
| `derived_data/01_landuse_mix` | 백업 완료 |
| `derived_data/02_development_realization` | 백업 완료 |
| `derived_data/03_sgis_jobs_housing` | 백업 완료 |
| `derived_data/04_accessibility` | 백업 완료 |
| `derived_data/05_station_area` | 백업 완료 |
| `derived_data/06_bonus_analysis` | 백업 완료 |
| `derived_data/07_integrated_outputs` | 현재 폴더 없음 |
| `public/data` | 백업 완료 |

## 4. 앞으로 갱신할 파일 목록

아래 파일들은 새 파일을 추가하는 방식이 아니라, 백업 원본을 보존한 상태에서 기존 파일을 새 판교 경계 기준 값으로 갱신하는 대상으로 본다. 위례 관련 파일과 위례 지표 값은 유지한다.

### 4.1 경계 및 경계 요약

- `derived_data/00_boundaries/pangyo_boundary.geojson`
- `derived_data/00_boundaries/boundary_area_summary.csv`
- `public/data/pangyo_boundary.geojson`
- `public/data/pangyo_boundary_refined.geojson`
- `public/data/boundaries.geojson`
- `public/data/boundary_area_summary.csv`

### 4.2 토지이용 혼합도

- `derived_data/01_landuse_mix/landuse_zones_clipped.geojson`
- `derived_data/01_landuse_mix/landuse_blocktype_clipped.geojson`
- `derived_data/01_landuse_mix/landuse_zone_composition.csv`
- `derived_data/01_landuse_mix/landuse_blocktype_composition.csv`
- `derived_data/01_landuse_mix/landuse_mix_index.csv`
- `derived_data/01_landuse_mix/landuse_blocktype_mix_index.csv`
- `derived_data/01_landuse_mix/landuse_mix_report.md`
- `public/data/landuse_zones.geojson`
- `public/data/landuse_blocktype.geojson`
- `public/data/landuse_zone_composition.csv`
- `public/data/landuse_blocktype_composition.csv`
- `public/data/landuse_mix_index.csv`
- `public/data/landuse_blocktype_mix_index.csv`

### 4.3 개발실현도

- `derived_data/02_development_realization/buildings_joined.geojson`
- `derived_data/02_development_realization/buildings_joined_deduplicated.geojson`
- `derived_data/02_development_realization/building_approval_timeseries.csv`
- `derived_data/02_development_realization/building_join_failures.csv`
- `derived_data/02_development_realization/building_use_composition.csv`
- `derived_data/02_development_realization/development_realization.csv`
- `derived_data/02_development_realization/development_realization_deduplicated.csv`
- `derived_data/02_development_realization/development_realization_duplicate_comparison.csv`
- `derived_data/02_development_realization/development_realization_report.md`
- `derived_data/02_development_realization/development_realization_validation.md`
- `derived_data/02_development_realization/duplicate_building_join_cases.csv`
- `derived_data/02_development_realization/duplicate_join_keys_in_boundary.csv`
- `derived_data/02_development_realization/duplicate_pk_join_cases.csv`
- `derived_data/02_development_realization/vacant_or_unbuilt_parcels.csv`
- `public/data/buildings_or_parcels.geojson`
- `public/data/building_approval_timeseries.csv`
- `public/data/building_use_composition.csv`
- `public/data/development_summary.csv`
- `public/data/vacant_or_unbuilt_parcels.csv`

### 4.4 SGIS 일자리/주거

- `derived_data/03_sgis_jobs_housing/sgis_joined_census.geojson`
- `derived_data/03_sgis_jobs_housing/sgis_join_validation.csv`
- `derived_data/03_sgis_jobs_housing/population_business_summary.csv`
- `derived_data/03_sgis_jobs_housing/jobs_housing_ratio.csv`
- `derived_data/03_sgis_jobs_housing/industry_basic_composition.csv`
- `derived_data/03_sgis_jobs_housing/sgis_jobs_housing_report.md`
- `public/data/sgis_census.geojson`
- `public/data/population_business_summary.csv`
- `public/data/jobs_housing_ratio.csv`
- `public/data/industry_basic_composition.csv`

### 4.5 접근성 및 OSM 도로망

- `derived_data/04_accessibility/accessibility_isochrones.geojson`
- `derived_data/04_accessibility/accessibility_population_workers.csv`
- `derived_data/04_accessibility/accessibility_sgis_intersections.geojson`
- `derived_data/04_accessibility/cumulative_accessibility_curve.csv`
- `derived_data/04_accessibility/reachable_stations.csv`
- `derived_data/04_accessibility/accessibility_report.md`
- `derived_data/04_accessibility/osm_road_network/osm_roads_clipped.geojson`
- `derived_data/04_accessibility/osm_road_network/osm_roads_deduplicated.geojson`
- `derived_data/04_accessibility/osm_road_network/road_density.csv`
- `derived_data/04_accessibility/osm_road_network/road_density_validation.csv`
- `derived_data/04_accessibility/osm_road_network/osm_road_network_report.md`
- `derived_data/04_accessibility/osm_road_network/osm_road_network_validation_report.md`
- `public/data/accessibility_isochrones.geojson`
- `public/data/accessibility_summary.csv`
- `public/data/cumulative_accessibility_curve.csv`
- `public/data/reachable_stations.csv`
- `public/data/osm_roads_deduplicated.geojson`
- `public/data/road_density_validation.csv`

### 4.6 역세권

- `derived_data/05_station_area/core_stations.geojson`
- `derived_data/05_station_area/station_buffers.geojson`
- `derived_data/05_station_area/station_buffer_intersections.geojson`
- `derived_data/05_station_area/station_area_ratio.csv`
- `derived_data/05_station_area/station_area_report.md`
- `public/data/core_stations.geojson`
- `public/data/station_buffers.geojson`
- `public/data/station_area_ratio.csv`

### 4.7 보너스 분석 및 통합 공개 산출물

- `derived_data/06_bonus_analysis/bonus_analysis_summary.csv`
- `derived_data/06_bonus_analysis/business_floor_area_density.csv`
- `derived_data/06_bonus_analysis/industry_lq.csv`
- `derived_data/06_bonus_analysis/top_worker_lq_industries.csv`
- `derived_data/06_bonus_analysis/bonus_analysis_report.md`
- `public/data/bonus_analysis_summary.csv`
- `public/data/business_floor_area_density.csv`
- `public/data/industry_lq.csv`
- `public/data/top_worker_lq_industries.csv`
- `public/data/dashboard_indicators.json`
- `public/data/final_comparison_table.csv`

### 4.8 현재 없음

- `derived_data/07_integrated_outputs/`

## 5. 권장 작업 순서

1. `pangyo_boundary_user_drawn2_5186.geojson`을 기준으로 `derived_data/00_boundaries/pangyo_boundary.geojson`와 판교 면적 요약만 먼저 갱신한다.
2. 토지이용 클리핑 및 혼합도 산출물을 새 판교 경계 기준으로 재계산한다.
3. 개발실현도 산출물을 새 판교 경계 기준 필지/건축물 집합으로 재계산한다.
4. SGIS 집계구 교차 및 일자리/주거 지표를 새 판교 경계 기준으로 재계산한다.
5. OSM 도로망, 접근성, 역세권 지표를 새 판교 경계 기준으로 재계산한다.
6. 보너스 분석과 통합 비교표/대시보드용 공개 데이터(`public/data`)를 마지막에 갱신한다.
7. 모든 단계에서 위례 경계와 위례 지표는 기존 값을 유지하고, 판교 값만 새 경계 기준으로 교체한다.

## 6. 이번 0단계에서 하지 않은 작업

- 토지이용 재계산하지 않음
- 개발실현도 재계산하지 않음
- SGIS 재계산하지 않음
- OSM/접근성 재계산하지 않음
- `public/data` 덮어쓰기하지 않음
- 대시보드 코드 수정하지 않음
