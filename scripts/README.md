# Scripts

이 폴더는 분석 경계 설정, 토지이용 처리, 개발실현도 계산, SGIS 통계 배분, 접근성 산출, 검증 문서 생성을 위한 스크립트를 담고 있다.

중요:

- GitHub에는 대용량 원천 데이터가 포함되지 않는다.
- 따라서 원천 데이터가 없는 환경에서는 아래 스크립트 대부분을 끝까지 실행할 수 없다.
- 반면 `public/data/`가 이미 포함되어 있으므로 대시보드 실행은 가능하다.

## 실행 순서

| 순서 | 스크립트 | 목적 | 입력 | 출력 |
| -: | -- | -- | -- | -- |
| 1 | `01_extract_boundaries.py` | 초기 분석 경계 후보 추출 | `가구및획지/`, 판교/위례 원천 자료 | `analysis_boundaries/` 후보 경계 |
| 2 | `02_extract_analysis_boundaries.py` | 후보 경계 정리 및 추출 | 1단계 결과, 원천 필지 | `analysis_boundaries/` 보조 산출 |
| 3 | `08_define_boundaries_from_reference_images.py` | 기준 이미지 기반 경계 보정 | 계획 이미지, 필지 자료 | `analysis_boundaries/`, 경계 보정 결과 |
| 4 | `05_refine_boundaries_from_plan_images.py` | 계획도면 기준 경계 정제 | 기준 이미지, 필지 자료 | 보정 경계, 검토 자료 |
| 5 | `06_create_final_outer_boundaries.py` | 최종 외곽 경계 생성 | 보정 경계, 후보 필지 | `derived_data/00_boundaries/` |
| 6 | `09_calculate_landuse_mix.py` | 용도지역/블록유형 혼합도 계산 | `derived_data/00_boundaries/`, `용도지역*`, `가구및획지/` | `derived_data/01_landuse_mix/`, `public/data/landuse_*` |
| 7 | `15_rebuild_landuse_2024.py` | 2024 기준 용도지역 재구성 | 용도지역 원천 자료 | 토지이용 보정 산출 |
| 8 | `10_calculate_development_realization.py` | 개발실현도와 건축물 지표 계산 | 경계, `건축물/`, `연속지적도/` | `derived_data/02_development_realization/`, `public/data/development_*` |
| 9 | `11_validate_development_join_duplicates.py` | 건축물-필지 조인 중복 검증 | 8단계 결과 | 검증 CSV/MD |
| 10 | `12_generate_accessibility_cumulative.py` | 네트워크 기반 접근성 누적 지표 생성 | `network/`, `인구가구/`, `집계구경계/` | `derived_data/04_accessibility/`, 접근성 CSV |
| 11 | 별도 SGIS 처리 스크립트/노트북 기반 | 직주 및 산업 구조 산출 | `인구가구/`, `집계구경계/`, 경계 | `derived_data/03_sgis_jobs_housing/`, `public/data/sgis_*` |
| 12 | `07_create_data_inventory.py` | 인벤토리/보고용 자료 생성 | 프로젝트 파일 목록 | 보고용 인벤토리 |

## 검증/보조 스크립트

| 순서 | 스크립트 | 목적 | 입력 | 출력 |
| -: | -- | -- | -- | -- |
| A | `03_check_landuse_zone_columns.py` | 용도지역 속성 컬럼 점검 | `용도지역*` SHP | 컬럼 점검 보고서 |
| B | `04_create_validation_maps.py` | 검증용 지도 이미지 생성 | 경계, 인구, 건축물, 용도지역 | `docs/figures/` 또는 보고 이미지 |
| C | `13_validate_zoning2.py` | 용도지역2 검증 | `용도지역2/` | 검증 보고서/이미지 |
| D | `14_validate_zoning3.py` | 용도지역3 검증 | `용도지역3/` | 검증 보고서/이미지 |
| E | `validate_user_drawn_boundary.py` | 사용자 작성 판교 경계 검증 | 수동 작성 GeoJSON | 경계 검증 결과 |
| F | `dev-server.mjs` | 로컬 개발 서버 실행 보조 | Node 환경 | 개발 서버 |

## 주의사항

- `public/data/`는 대시보드가 실제로 읽는 최종 결과 폴더다.
- `public/data/archive/` 파일은 현재 코드에서 참조하지 않으므로 제출 대상에서 제외했다.
- `derived_data/04_accessibility/accessibility_sgis_intersections.geojson`는 217MB 중간 산출물이라 `archive/`로 이동했다.
- 원천 데이터 폴더는 현재 저장소 루트의 기존 이름을 유지한다. 스크립트도 그 경로를 가정한다.

