# OSM Road Network Density Report

## Scope
Pangyo OSM road density was updated using `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson`. Wirye OSM values are preserved from the pre-update backup.

## Boundary Files
- Pangyo: `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson`
- Wirye: `derived_data/00_boundaries/wirye_boundary.geojson`

## Method
- Existing stored OSM road network was used. No new OSM download was performed.
- Length CRS: EPSG:5186.
- Calculation: road geometry intersection with analysis boundary, then total road length in km divided by boundary area in km2.
- Network type: `walk`.

## Results
| area_name | boundary_area_sqm | road_total_length_m | road_density_km_per_km2 |
| --- | ---: | ---: | ---: |
| pangyo_1st_technovalley | 860504.887988 | 33388.100460 | 38.800594 |
| wirye_plan_area | 6757873.520642 | 456834.205995 | 67.600289 |

## Deduplicated Reference
| area_name | deduplicated_road_total_length_m | deduplicated_road_density_km_per_km2 |
| --- | ---: | ---: |
| pangyo_1st_technovalley | 16694.050230 | 19.400297 |
| wirye_plan_area | 228405.149634 | 33.798376 |

## Outputs
- `derived_data/04_accessibility/osm_road_network/osm_roads_clipped.geojson`
- `derived_data/04_accessibility/osm_road_network/osm_roads_deduplicated.geojson`
- `derived_data/04_accessibility/osm_road_network/road_density.csv`
- `derived_data/04_accessibility/osm_road_network/road_density_validation.csv`
- `derived_data/04_accessibility/osm_road_network/osm_road_network_report.md`
- `derived_data/04_accessibility/osm_road_network/osm_road_network_validation_report.md`

## Notes
This step did not recalculate bonus analysis/LQ, business floor-area density, KPI, chart data, dashboard data, or public data.
