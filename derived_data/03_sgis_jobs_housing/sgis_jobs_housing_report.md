# SGIS Population, Household, Business, Worker, and Jobs-Housing Report

## 1. Scope
This report updates the SGIS 2023 indicators for Pangyo using `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson`. Wirye boundary and Wirye SGIS results are preserved from the pre-update backup. LQ is not calculated in this step.

## 2. Boundary Files
- Pangyo: `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson`
- Wirye: `derived_data/00_boundaries/wirye_boundary.geojson`

## 3. Source Data and Method
- SGIS CSV: `????/*_2023?_*.csv`
- Pangyo source CSV group: `31_2023?_*`
- Output-area boundary: `?????/bnd_oa_31_2025_2Q.shp` and `?????/bnd_oa_11_2025_2Q.shp`
- Join key: `spatial_id -> TOT_OA_CD`
- Area CRS: `EPSG:5186`
- Allocation: area-proportional intersection, `intersect_area_sqm / original_area_sqm`

## 4. Summary Indicators
| area_name | boundary_area_sqm | boundary_area_km2 | population | households | business_count | worker_count | population_density_per_km2 | household_density_per_km2 | business_density_per_km2 | worker_density_per_km2 | allocation_method | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pangyo_1st_technovalley | 860504.887988 | 0.860505 | 341.813835 | 294.762628 | 1469.745708 | 52567.396762 | 397.224746 | 342.546140 | 1708.003904 | 61089.015874 | area_proportional_intersection | SGIS 2023 values allocated by intersect_area_sqm / original_area_sqm using EPSG:5186; industry missing values treated as 0. |
| wirye_plan_area | 6757873.520642 | 6.757874 | 119487.045671 | 42435.125732 | 5481.525409 | 25566.812993 | 17681.160398 | 6279.360749 | 811.131696 | 3783.263021 | area_proportional_intersection | SGIS 2023 values allocated by intersect_area_sqm / original_area_sqm using EPSG:5186; industry missing values treated as 0. |

## 5. Jobs-Housing Ratio
| area_name | population | worker_count | jobs_housing_ratio | interpretation_note |
| --- | --- | --- | --- | --- |
| pangyo_1st_technovalley | 341.813835 | 52567.396762 | 153.789553 | worker_count / resident population; area-proportional allocation from SGIS output area data |
| wirye_plan_area | 119487.045671 | 25566.812993 | 0.213971 | worker_count / resident population; area-proportional allocation from SGIS output area data |

Jobs-housing ratio is `worker_count / resident population`.

## 6. Top Industry Composition
| area_name | metric_type | industry_code | industry_name | value | ratio |
| --- | --- | --- | --- | --- | --- |
| pangyo_1st_technovalley | business_count | 10 | 정보통신업 | 393.817090 | 0.267949 |
| pangyo_1st_technovalley | business_count | 9 | 숙박 및 음식점업 | 308.544745 | 0.209931 |
| pangyo_1st_technovalley | business_count | 7 | 도매 및 소매업 | 222.641159 | 0.151483 |
| pangyo_1st_technovalley | business_count | 13 | 전문, 과학 및 기술 서비스업 | 176.477296 | 0.120073 |
| pangyo_1st_technovalley | business_count | 12 | 부동산업 | 85.721948 | 0.058324 |
| pangyo_1st_technovalley | worker_count | 10 | 정보통신업 | 23488.585189 | 0.446828 |
| pangyo_1st_technovalley | worker_count | 13 | 전문, 과학 및 기술 서비스업 | 10235.267902 | 0.194708 |
| pangyo_1st_technovalley | worker_count | 14 | 사업시설 관리, 사업 지원 및 임대 서비스업 | 7145.348379 | 0.135927 |
| pangyo_1st_technovalley | worker_count | 7 | 도매 및 소매업 | 4273.336734 | 0.081293 |
| pangyo_1st_technovalley | worker_count | 3 | 제조업 | 2388.994093 | 0.045446 |
| wirye_plan_area | business_count | 7 | 도매 및 소매업 | 2011.758808 | 0.367007 |
| wirye_plan_area | business_count | 9 | 숙박 및 음식점업 | 832.651684 | 0.151901 |
| wirye_plan_area | business_count | 16 | 교육 서비스업 | 631.169639 | 0.115145 |
| wirye_plan_area | business_count | 19 | 협회 및 단체, 수리 및 기타 개인 서비스업 | 398.440757 | 0.072688 |
| wirye_plan_area | business_count | 12 | 부동산업 | 381.014253 | 0.069509 |
| wirye_plan_area | worker_count | 7 | 도매 및 소매업 | 4368.078060 | 0.170850 |
| wirye_plan_area | worker_count | 16 | 교육 서비스업 | 3746.290652 | 0.146529 |
| wirye_plan_area | worker_count | 17 | 보건업 및 사회복지 서비스업 | 3297.945134 | 0.128993 |
| wirye_plan_area | worker_count | 9 | 숙박 및 음식점업 | 2874.491154 | 0.112431 |
| wirye_plan_area | worker_count | 6 | 건설업 | 1979.068184 | 0.077408 |

## 7. Join Validation
| source_file | source_region_code | metric_type | csv_rows | boundary_rows | joined_rows | join_failed_rows | join_success_rate | join_key | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 11_2023년_가구총괄.csv | 11 | household | 38194 | 19097 | 38194 | 0 | 1.000000 | spatial_id -> TOT_OA_CD | validated against 11 output-area boundary; CSV has no header, parsed as year/spatial_id/item_code/value |
| 11_2023년_산업분류별(10차_대분류)_사업체수.csv | 11 | business_count | 153840 | 19097 | 153840 | 0 | 1.000000 | spatial_id -> TOT_OA_CD | validated against 11 output-area boundary; CSV has no header, parsed as year/spatial_id/item_code/value |
| 11_2023년_산업분류별(10차_대분류)_종사자수.csv | 11 | worker_count | 153840 | 19097 | 153840 | 0 | 1.000000 | spatial_id -> TOT_OA_CD | validated against 11 output-area boundary; CSV has no header, parsed as year/spatial_id/item_code/value |
| 11_2023년_인구총괄(총인구).csv | 11 | population | 57291 | 19097 | 57291 | 0 | 1.000000 | spatial_id -> TOT_OA_CD | validated against 11 output-area boundary; CSV has no header, parsed as year/spatial_id/item_code/value |
| 31023_2023년_가구총괄.csv | 31023 | household | 1852 | 28394 | 1852 | 0 | 1.000000 | spatial_id -> TOT_OA_CD | validated against 31 output-area boundary; CSV has no header, parsed as year/spatial_id/item_code/value |
| 31023_2023년_산업분류별(10차_대분류)_사업체수.csv | 31023 | business_count | 6326 | 28394 | 6326 | 0 | 1.000000 | spatial_id -> TOT_OA_CD | validated against 31 output-area boundary; CSV has no header, parsed as year/spatial_id/item_code/value |
| 31023_2023년_산업분류별(10차_대분류)_종사자수.csv | 31023 | worker_count | 6326 | 28394 | 6326 | 0 | 1.000000 | spatial_id -> TOT_OA_CD | validated against 31 output-area boundary; CSV has no header, parsed as year/spatial_id/item_code/value |
| 31023_2023년_인구총괄(총인구).csv | 31023 | population | 2778 | 28394 | 2778 | 0 | 1.000000 | spatial_id -> TOT_OA_CD | validated against 31 output-area boundary; CSV has no header, parsed as year/spatial_id/item_code/value |
| 31_2023년_가구총괄.csv | 31 | household | 56788 | 28394 | 56788 | 0 | 1.000000 | spatial_id -> TOT_OA_CD | validated against 31 output-area boundary; CSV has no header, parsed as year/spatial_id/item_code/value |
| 31_2023년_산업분류별(10차_대분류)_사업체수.csv | 31 | business_count | 216573 | 28394 | 216573 | 0 | 1.000000 | spatial_id -> TOT_OA_CD | validated against 31 output-area boundary; CSV has no header, parsed as year/spatial_id/item_code/value |
| 31_2023년_산업분류별(10차_대분류)_종사자수.csv | 31 | worker_count | 216573 | 28394 | 216573 | 0 | 1.000000 | spatial_id -> TOT_OA_CD | validated against 31 output-area boundary; CSV has no header, parsed as year/spatial_id/item_code/value |
| 31_2023년_인구총괄(총인구).csv | 31 | population | 85182 | 28394 | 85182 | 0 | 1.000000 | spatial_id -> TOT_OA_CD | validated against 31 output-area boundary; CSV has no header, parsed as year/spatial_id/item_code/value |

## 8. Notes
Population uses `to_in_001`; households use `to_ga_001`. Missing industry values are treated as 0. This step does not calculate LQ, station-area indicators, accessibility, OSM metrics, bonus analysis, KPI, chart data, or dashboard data.
