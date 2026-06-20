# 판교 경계 폴더 정리 보고서

작성일: 2026-06-19

## 1. 백업 확인

- 백업 폴더 존재 여부: 존재 확인 완료
- 백업 폴더 경로: `backup_before_pangyo_boundary_update/`
- 백업 폴더 내 기존 판교 경계 보존 확인: `backup_before_pangyo_boundary_update/derived_data/00_boundaries/pangyo_boundary.geojson` 존재
- 백업 폴더는 수정하지 않았다.

## 2. 최종 판교 경계

- 최종 판교 경계 파일명: `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson`
- 파일명 유지 방식: `pangyo_boundary.geojson`으로 변경하거나 덮어쓰지 않음
- CRS: EPSG:5186
- feature 수: 1
- geometry type: Polygon
- geometry validity: valid
- 최종 판교 경계 면적: 860,504.888 m2

## 3. 삭제한 판교 후보 파일

다음 파일은 `derived_data/00_boundaries`에서 삭제했다. 삭제 전 원본은 `backup_before_pangyo_boundary_update/`에 보존되어 있다.

- `pangyo_boundary.geojson`
- `pangyo_boundary_manual_reference.geojson`
- `pangyo_boundary_manual_reference_report.md`
- `pangyo_boundary_manual_reference_validation.png`
- `pangyo_boundary_pnu_based.geojson`
- `pangyo_boundary_pnu_based_report.md`
- `pangyo_boundary_pnu_based_validation.png`
- `pangyo_boundary_refined.geojson`
- `pangyo_boundary_refined_final_manual.gpkg`
- `pangyo_boundary_refined_final_manual_5186.geojson`
- `pangyo_boundary_refined_final_manual_5186.gpkg`
- `pangyo_boundary_refined_final_manual_5186_report.md`
- `pangyo_boundary_refined_final_manual_5186_validation.png`
- `pangyo_boundary_refined_manual_adjusted.geojson`
- `pangyo_boundary_refined_manual_adjusted_report.md`
- `pangyo_boundary_refined_manual_adjusted_validation.png`
- `pangyo_boundary_refined_manual_like.geojson`
- `pangyo_boundary_refined_manual_like_report.md`
- `pangyo_boundary_refined_manual_like_validation.png`
- `pangyo_boundary_refined_outer.geojson`
- `pangyo_boundary_refined_outer_report.md`
- `pangyo_boundary_refined_outer_validation.png`
- `pangyo_boundary_user_drawn.geojson`
- `pangyo_boundary_user_drawn2.geojson`
- `pangyo_boundary_user_drawn2_validation.png`
- `pangyo_boundary_user_drawn_5186.geojson`
- `pangyo_boundary_user_drawn_validation.png`
- `_manual_like_candidates.png`

삭제 중 일부 파일이 QGIS에서 잠겨 있어 QGIS 프로세스를 종료한 뒤 삭제를 완료했다.

## 4. 유지한 파일

현재 `derived_data/00_boundaries`에 유지한 파일은 다음과 같다.

- `.gitkeep`
- `boundary_area_summary.csv`
- `pangyo_boundary_user_drawn2_5186.geojson`
- `pangyo_internal_parcels.geojson`
- `wirye_boundary.geojson`
- `wirye_business_commercial_boundary.geojson`
- `wirye_business_commercial_internal_parcels.geojson`

`pangyo_internal_parcels.geojson`은 경계 후보 파일이 아니라 기존 경계 산출의 근거 필지 자료이므로 삭제 대상에서 제외했다.

## 5. 위례 경계 변경 여부

- 위례 경계 파일 변경 여부: 변경하지 않음
- 유지한 위례 파일:
  - `wirye_boundary.geojson`
  - `wirye_business_commercial_boundary.geojson`
  - `wirye_business_commercial_internal_parcels.geojson`
- 대시보드용 `public/data/boundaries.geojson`의 위례 geometry와 `derived_data/00_boundaries/wirye_boundary.geojson`의 대칭차 면적: 0.0 m2

## 6. 분석 코드의 판교 경계 참조 경로 정리

활성 분석 스크립트의 판교 경계 참조 경로를 최종 파일명 기준으로 수정했다.

- `scripts/09_calculate_landuse_mix.py`
  - 기존: `derived_data/00_boundaries/pangyo_boundary.geojson`
  - 변경: `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson`
- `scripts/10_calculate_development_realization.py`
  - 기존: `derived_data/00_boundaries/pangyo_boundary.geojson`
  - 변경: `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson`

현재 저장소의 `scripts/` 폴더에서는 SGIS, 역세권, OSM 도로망, 접근성, `public/data` 생성 전용 실행 스크립트가 별도로 확인되지 않았다. 해당 단계의 재계산이나 공개 데이터 갱신은 수행하지 않았다.

다음 항목의 과거 `pangyo_boundary.geojson` 문자열은 이번 1단계에서 수정하지 않았다.

- `scripts/08_define_boundaries_from_reference_images.py`: 과거 자동 경계 생성 후보 스크립트이며, 이번 최종 경계 확정 이후 실행 대상이 아니다.
- `scripts/validate_user_drawn_boundary.py`: 과거 사용자 작성 경계 검증 보조 스크립트이며, 이번 분석 재계산 경로가 아니다.
- `derived_data/**/_report.md`, `dashboard/*.md`, `derived_data/README.md`: 기존 산출물 또는 문서성 기록이며, 아직 지표 재계산 전이므로 내용 갱신하지 않았다.

## 7. 대시보드 경계 확인

- 대시보드 지도 컴포넌트는 `src/components/DashboardMap.jsx`에서 `/data/boundaries.geojson`을 읽는다.
- 대시보드 코드는 수정하지 않았다.
- `public/data/boundaries.geojson`의 판교 geometry와 `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson`의 대칭차 면적: 0.0 m2
- `public/data/boundaries.geojson`의 위례 geometry와 `derived_data/00_boundaries/wirye_boundary.geojson`의 대칭차 면적: 0.0 m2
- 따라서 현재 대시보드 지도 소스 기준으로 판교는 drawn2 최종 경계와 일치하고, 위례 경계는 변경되지 않았다.

## 8. 이번 단계에서 하지 않은 작업

- 토지이용 재계산하지 않음
- 개발실현도 재계산하지 않음
- SGIS 재계산하지 않음
- 역세권 재계산하지 않음
- OSM 도로밀도 재계산하지 않음
- 접근성 재계산하지 않음
- `public/data` 전체 갱신하지 않음
- KPI와 차트 데이터 갱신하지 않음
- 대시보드 코드 수정하지 않음
