# Accessibility Cumulative Validation

- source network: `network/nodes.tsv`, `network/links.tsv`
- source SGIS raw csv: `인구가구/11_2023년_인구총괄(총인구).csv`, `인구가구/31_2023년_인구총괄(총인구).csv`, `인구가구/11_2023년_산업분류별(10차_대분류)_종사자수.csv`, `인구가구/31_2023년_산업분류별(10차_대분류)_종사자수.csv`
- source OA boundaries: `집계구경계/bnd_oa_11_2025_2Q.shp`, `집계구경계/bnd_oa_31_2025_2Q.shp`
- source 30/60 polygons reused for validation: `derived_data/04_accessibility/accessibility_isochrones.geojson`
- output cumulative: `derived_data/04_accessibility/accessibility_cumulative.csv`
- output polygons: `derived_data/04_accessibility/accessibility_isochrones_10min.geojson`

## 0-60 minute cumulative table

| area_name | station_name | time_min | reachable_station_count | reachable_population | reachable_workers |
|---|---|---:|---:|---:|---:|
| pangyo_1st_technovalley | 판교역 | 0 | 0 | 0.000 | 0.000 |
| pangyo_1st_technovalley | 판교역 | 10 | 7 | 52,313.313 | 74,153.832 |
| pangyo_1st_technovalley | 판교역 | 20 | 26 | 360,043.735 | 320,347.343 |
| pangyo_1st_technovalley | 판교역 | 30 | 91 | 2,342,410.995 | 1,917,642.269 |
| pangyo_1st_technovalley | 판교역 | 40 | 194 | 7,302,035.241 | 4,613,133.023 |
| pangyo_1st_technovalley | 판교역 | 50 | 420 | 13,022,716.269 | 6,986,771.640 |
| pangyo_1st_technovalley | 판교역 | 60 | 592 | 16,774,253.979 | 8,542,443.835 |
| wirye_plan_area | 남위례역 | 0 | 0 | 0.000 | 0.000 |
| wirye_plan_area | 남위례역 | 10 | 20 | 162,093.505 | 68,104.476 |
| wirye_plan_area | 남위례역 | 20 | 54 | 874,789.873 | 489,417.532 |
| wirye_plan_area | 남위례역 | 30 | 114 | 1,942,910.891 | 1,481,691.069 |
| wirye_plan_area | 남위례역 | 40 | 198 | 5,369,264.447 | 4,017,896.346 |
| wirye_plan_area | 남위례역 | 50 | 348 | 11,131,292.006 | 6,113,944.611 |
| wirye_plan_area | 남위례역 | 60 | 542 | 15,270,097.552 | 7,937,442.267 |

## 30/60 minute validation against current accessibility_summary.csv

| area_name | time_min | generated_population | existing_population | diff_population | generated_workers | existing_workers | diff_workers |
|---|---:|---:|---:|---:|---:|---:|---:|
| pangyo_1st_technovalley | 30 | 2,342,410.995 | 2,342,410.995 | 0.000000 | 1,917,642.269 | 1,917,642.269 | 0.000000 |
| pangyo_1st_technovalley | 60 | 16,774,253.979 | 16,774,253.979 | 0.000000 | 8,542,443.835 | 8,542,443.835 | 0.000000 |
| wirye_plan_area | 30 | 1,942,910.891 | 1,942,910.891 | 0.000000 | 1,481,691.069 | 1,481,691.069 | 0.000000 |
| wirye_plan_area | 60 | 15,270,097.552 | 15,270,097.552 | 0.000000 | 7,937,442.267 | 7,937,442.267 | 0.000000 |
