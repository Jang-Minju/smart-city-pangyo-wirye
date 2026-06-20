# 개발실현도 조인 중복 검증 보고서

## 검증 목적

건축물대장과 연속지적도 조인에서 `시군구코드 + 본번 + 부번` 대체 조인키를 사용했기 때문에, 경계 내부에서 동일 대체키를 가진 여러 필지가 존재할 경우 하나의 건축물대장 행이 여러 필지에 중복 조인될 수 있다. 기존 결과 파일은 덮어쓰지 않고 중복 여부와 중복 제거 후 요약값 변화를 별도 검증했다.

## 입력 자료

- 기존 조인 결과: `derived_data/02_development_realization/buildings_joined.geojson`
- 원본 개발실현도 요약: `derived_data/02_development_realization/development_realization.csv`
- 재현 스크립트: `scripts/10_calculate_development_realization.py`

## 1. 경계 내 중복 대체 조인키

| area_name | duplicate_join_key_count | parcels_in_duplicate_keys |
| --- | --- | --- |
| wirye_plan_area | 29 | 58 |

상세 목록: `duplicate_join_keys_in_boundary.csv`

## 2. 하나의 건축물대장 행이 여러 필지에 조인된 사례

| area_name | building_rows_joined_to_multiple_parcels | expanded_join_rows | candidate_parcel_total |
| --- | --- | --- | --- |
| wirye_plan_area | 20 | 40 | 40 |

상세 목록: `duplicate_building_join_cases.csv`

## 3. 동일 row_id 또는 PK 중복 사례

기존 `buildings_joined.geojson`에는 `row_id`, `PK`, `source_file`이 저장되어 있지 않아 해당 파일만으로 직접 판별할 수 없었다. 따라서 원본 건축물대장과 조인 과정을 재현하여 `building_uid = source_file + row_id`, `PK` 기준으로 검증했다.

### PK 중복 조인 요약

| area_name | duplicate_pk_count | duplicate_pk_join_rows |
| --- | --- | --- |
| wirye_plan_area | 20 | 40 |

상세 목록: `duplicate_pk_join_cases.csv`

## 4. 개발실현도 요약값 중복 집계 여부

중복 조인이 확인되었고, 원본 개발실현도 요약값 일부가 중복 집계의 영향을 받았다. 아래 표는 원본 요약과 `area_name + building_uid` 기준 중복 제거 요약의 차이다.

| area_name | metric | original | deduplicated | difference |
| --- | --- | --- | --- | --- |
| wirye_plan_area | joined_building_count | 3620.000000 | 3600.000000 | -20.000000 |
| wirye_plan_area | developed_parcel_count | 1031.000000 | 1021.000000 | -10.000000 |
| wirye_plan_area | estimated_unbuilt_parcel_count | 1445.000000 | 1455.000000 | 10.000000 |
| wirye_plan_area | developed_parcel_ratio | 0.416397 | 0.412359 | -0.004039 |
| wirye_plan_area | estimated_unbuilt_parcel_ratio | 0.583603 | 0.587641 | 0.004039 |
| wirye_plan_area | avg_far | 168.825860 | 169.804774 | 0.978915 |
| wirye_plan_area | floor_area_weighted_far | 422.521751 | 422.987444 | 0.465693 |
| wirye_plan_area | avg_bcr | 50.244079 | 50.333159 | 0.089080 |
| wirye_plan_area | total_building_floor_area_sqm | 15477051.386700 | 15470008.843700 | -7042.543000 |
| wirye_plan_area | total_building_area_sqm | 1302422.464200 | 1298160.359200 | -4262.105000 |
| wirye_plan_area | business_floor_area_ratio | 0.181312 | 0.181395 | 0.000083 |

전체 비교표: `development_realization_duplicate_comparison.csv`

## 5. 중복 제거 산출물

- `buildings_joined_deduplicated.geojson`
- `development_realization_deduplicated.csv`

중복 제거 기준은 `area_name + building_uid`이며, 하나의 건축물대장 행이 여러 필지에 조인된 경우 `parcel_area_sqm`이 가장 큰 필지를 대표 필지로 선택했다. 건축물대장에 PNU가 없고 법정동코드를 포함한 완전 조인이 불가능하므로, 이 대표 필지 선택은 보수적 검증용 처리이며 원본을 대체하는 확정 보정은 아니다.

## 6. 판단

- 중복 조인은 존재한다.
- 기존 `development_realization.csv`는 중복 조인된 건축물 행의 건축물 수, 연면적, 건축면적, 업무시설 연면적 등에 영향을 받았다.
- 따라서 보고서 본문에는 원본 결과와 함께 본 검증 결과를 참고하고, 최종 발표 또는 분석표에서는 `development_realization_deduplicated.csv`를 보조 비교값으로 함께 제시하는 것이 적절하다.
