# 최종 분석용 외곽 경계 생성 보고서

## 핵심 변경

기존 `analysis_boundaries` 산출물은 업무용지/획지의 집합이어서 내부 필지 경계와 도로 틈이 남아 있었다. 이번 작업에서는 분석에 사용할 수 있도록 내부 필지 경계를 제거하고 하나의 외곽 Polygon 또는 MultiPolygon으로 재생성했다.

## 생성 방식

| 대상 | 생성 방식 |
| --- | --- |
| 판교 제1테크노밸리 | `도시지원시설용지(지원)` + 지원 경계에서 450m 이내 인접 `업무시설/업무시설기타`를 원천 획지로 선택한 뒤 `concave_hull(ratio=0.10, allow_holes=False)` 적용 |
| 위례신도시 | `위례 택지개발사업 예정지구`의 모든 가구및획지를 dissolve한 뒤 내부 hole 제거 |

## 결과 요약

| target | source_features | source_area_sqm | outer_area_sqm | geometry_type |
| --- | --- | --- | --- | --- |
| 판교 제1테크노밸리 | 81 | 440577.85019051936 | 766655.835113822 | Polygon |
| 위례신도시 | 1170 | 6753734.259406522 | 6753734.609664464 | Polygon |

## 산출 파일

### SHP

- `analysis_boundaries/final_outer_boundaries/pangyo_1st_technovalley_outer_boundary_5186.shp`
- `analysis_boundaries/final_outer_boundaries/wirye_newtown_outer_boundary_5186.shp`

### GeoJSON

- `analysis_boundaries/final_outer_boundaries/pangyo_1st_technovalley_outer_boundary_5186.geojson`
- `analysis_boundaries/final_outer_boundaries/pangyo_1st_technovalley_outer_boundary_4326.geojson`
- `analysis_boundaries/final_outer_boundaries/wirye_newtown_outer_boundary_5186.geojson`
- `analysis_boundaries/final_outer_boundaries/wirye_newtown_outer_boundary_4326.geojson`

### 원천 획지 ID

- `analysis_boundaries/final_outer_boundaries/pangyo_1st_technovalley_outer_boundary_source_parcel_ids.csv`
- `analysis_boundaries/final_outer_boundaries/wirye_newtown_outer_boundary_source_parcel_ids.csv`

## PNG 검증 지도

- `reports/final_outer_boundary_maps/01_pangyo_outer_boundary_validation.png`
- `reports/final_outer_boundary_maps/02_wirye_outer_boundary_validation.png`
- `reports/final_outer_boundary_maps/03_pangyo_plan_image_overlap_check.png`
- `reports/final_outer_boundary_maps/04_wirye_plan_image_overlap_check.png`

## 계획도 이미지 중첩 검증 한계

사용자가 제공한 계획도 이미지는 좌표계, 축척, 기준점이 없는 스크린샷이다. 따라서 GIS 레이어처럼 실제 좌표 기반으로 지오리퍼런싱하여 픽셀 단위 중첩 검증을 수행할 수는 없다. 대신 SHP의 블록명, 용도, 상대 위치, 외곽 형상을 계획도 이미지와 시각적으로 대조했다.

판교는 이미지의 업무·도시지원 핵심 구역과 대응되는 `지원` 블록 및 인접 업무 블록만 사용했다. SHP에는 이미지에 보이는 `업무6` 명칭이 없고, `위4`는 `위험물저장및처리시설`로 확인되어 제1테크노밸리 외곽 원천에서 제외했다.

위례는 이번 요구가 `위례신도시 전체 외곽 경계`이므로 업무·상업 획지만이 아니라 위례 사업지구의 모든 가구획지를 사용했다. 내부 업무·상업용지 분석은 별도 레이어로 유지해야 한다.

## 판교 원천 획지 ID

| zoneName | blockType | blockName | lotName | parcel_id | feature_count | area_sqm |
| --- | --- | --- | --- | --- | --- | --- |
| 성남판교지구 택지개발사업 | 도시지원시설용지 | 지원 | 지원 | 지원 | 75 | 433241.41618483356 |
| 성남판교지구 택지개발사업 | 업무시설 | 업무5 | 1 | 업무5-1 | 1 | 1000.7566025060177 |
| 성남판교지구 택지개발사업 | 업무시설기타 | 공3 | 1 | 공3-1 | 1 | 1646.7109922413533 |
| 성남판교지구 택지개발사업 | 업무시설기타 | 공4 | 1 | 공4-1 | 1 | 1108.4347451746166 |
| 성남판교지구 택지개발사업 | 업무시설기타 | 공5 | 1 | 공5-1 | 1 | 925.6829017452103 |
| 성남판교지구 택지개발사업 | 업무시설기타 | 공6 | 1 | 공6-1 | 1 | 1001.0726977341368 |
| 성남판교지구 택지개발사업 | 업무시설기타 | 동3 | 1 | 동3-1 | 1 | 1653.7760662843862 |

## 위례 원천 획지 ID

위례는 전체 사업지구 외곽이므로 원천 획지가 많다. 전체 목록은 CSV로 저장했다.
