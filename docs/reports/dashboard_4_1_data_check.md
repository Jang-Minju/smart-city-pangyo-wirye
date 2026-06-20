# Dashboard 4-1 Data Check

## Boundary Source

- Dashboard boundary file: `public/data/boundaries.geojson`
- Final Pangyo boundary source: `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson`
- Pangyo geometry in `public/data/boundaries.geojson` matches final drawn2 boundary: `True`
- Pangyo boundary hash: `f4896c6c1971f44a`
- Wirye geometry changed during this update: `False`
- Wirye boundary hash: `f7505561072c3335`

## 4-1 Map Layer Data Paths

- Pangyo boundary: `public/data/boundaries.geojson`
- Wirye boundary: `public/data/boundaries.geojson`
- Core stations: `public/data/core_stations.geojson`
- Dashboard map component: `src/components/DashboardMap.jsx`
- Boundary fetch path in dashboard map: `/data/boundaries.geojson`
- Core station fetch path in dashboard map: `/data/core_stations.geojson`
- Boundary editor reference boundary path: `/data/pangyo_boundary.geojson`
- Boundary editor reference parcels path: `/data/buildings_or_parcels.geojson`

## Map View Check

- Pangyo split map initial view: lon `127.111`, lat `37.394`, zoom `13.5`
- Wirye split map initial view: lon `127.140`, lat `37.462`, zoom `13.2`
- Comparison/detail map initial view: lon `127.126`, lat `37.428`, zoom `11.2`
- Detail map Pangyo/Wirye/comparison switching source: `ControlledDashboardMap` view mode in `src/components/DashboardMap.jsx`
- 4-1 map layer references to deleted or obsolete Pangyo boundary files: `None found`

## Public Data Updated From Latest Derived Outputs

Existing `public/data` filenames were kept. No `_final_boundary` file was added.

- `public/data/boundaries.geojson`
- `public/data/pangyo_boundary.geojson`
- `public/data/pangyo_boundary_refined.geojson`
- `public/data/boundary_area_summary.csv`
- `public/data/landuse_zones.geojson`
- `public/data/landuse_blocktype.geojson`
- `public/data/landuse_zone_composition.csv`
- `public/data/landuse_blocktype_composition.csv`
- `public/data/landuse_mix_index.csv`
- `public/data/landuse_blocktype_mix_index.csv`
- `public/data/buildings_or_parcels.geojson`
- `public/data/building_approval_timeseries.csv`
- `public/data/building_use_composition.csv`
- `public/data/development_summary.csv`
- `public/data/vacant_or_unbuilt_parcels.csv`
- `public/data/sgis_census.geojson`
- `public/data/industry_basic_composition.csv`
- `public/data/jobs_housing_ratio.csv`
- `public/data/population_business_summary.csv`
- `public/data/accessibility_isochrones.geojson`
- `public/data/accessibility_summary.csv`
- `public/data/cumulative_accessibility_curve.csv`
- `public/data/reachable_stations.csv`
- `public/data/osm_roads_deduplicated.geojson`
- `public/data/road_density_validation.csv`
- `public/data/core_stations.geojson`
- `public/data/station_buffers.geojson`
- `public/data/station_area_ratio.csv`
- `public/data/bonus_analysis_summary.csv`
- `public/data/business_floor_area_density.csv`
- `public/data/industry_lq.csv`
- `public/data/top_worker_lq_industries.csv`

## Latest Pangyo Values Available In `public/data`

- Boundary area: `860,504.888 sqm`
- Zoning LUM: `0.2855777139873423`
- BlockType LUM: `0.5748418806421138`
- Developed parcel ratio: `0.5533333333333333`
- Estimated unbuilt/vacant ratio: `0.4466666666666666`
- Business floor area ratio: `0.7371095545404406`
- Business floor area density: `30,375.053342376224 sqm/ha`
- Population: `341.8138352226815`
- Worker count: `52,567.39676218949`
- Jobs-housing ratio: `153.78955251458268`
- 1 km station area ratio: `0.3729237886905336`
- OSM deduplicated road density: `19.400296806020062 km/km2`
- ICT worker LQ: `1.450954533130501`
- Professional/scientific/technical services worker LQ: `1.2808049995522242`

## Not Updated In This Step

- KPI card design and binding were not redesigned.
- Chart binding was not newly implemented.
- Final comparison table UI was not redesigned.
- VWorld map settings were not changed.
- Dashboard layout was not refactored.
