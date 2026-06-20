# Station-Area Ratio Report

## 1. Scope
This report updates Pangyo station-area ratios using `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson`. Wirye station-area values are preserved from the pre-update backup.

## 2. Boundary Files
- Pangyo: `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson`
- Wirye: `derived_data/00_boundaries/wirye_boundary.geojson`

## 3. Station Source and Selection
- Source: `network/nodes.tsv`
- Coordinate columns: `lng`, `lat`
- Input CRS: EPSG:4326
- Area/buffer CRS: EPSG:5186
- Pangyo station: 판교역, line 신분당선
- Wirye station: 남위례역, line 서울8호선
- Buffer distances: 500m, 1000m
- Calculation: `buffer ? analysis boundary area / analysis boundary area`

## 4. Selected Core Stations
| area_name | station_name | line_name | lon | lat | x | y | source_file |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| pangyo_1st_technovalley | 판교역 | 신분당선 | 127.111157 | 37.394569 | 209842.876605 | 532808.604460 | network/nodes.tsv |
| wirye_plan_area | 남위례역 | 서울8호선 | preserved | preserved | preserved | preserved | network/nodes.tsv |

## 5. Summary
| area_name | station_name | boundary_area_sqm | buffer_500m_area_ratio | buffer_1km_area_ratio |
| --- | --- | ---: | ---: | ---: |
| pangyo_1st_technovalley | 판교역 | 860504.887988 | 0.000000 | 0.372924 |
| wirye_plan_area | 남위례역 | 6757873.520642 | 0.046117 | 0.198627 |

## 6. Station Inside Boundary
| area_name | station_name | station_inside_or_on_boundary |
| --- | --- | --- |
| pangyo_1st_technovalley | 판교역 | False |
| wirye_plan_area | 남위례역 | preserved |

## 7. Notes
This step does not recalculate 30/60-minute accessibility, OSM metrics, bonus/LQ analysis, KPI, chart data, or dashboard data.
