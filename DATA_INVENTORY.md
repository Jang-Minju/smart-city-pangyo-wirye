# DATA_INVENTORY

정리 기준일: 2026-06-20

원칙:

- 대시보드 실행에 직접 필요한 `src/`, `public/data/`, `package*.json`, `index.html`은 포함
- 데이터 재현 설명에 필요한 `scripts/`, `derived_data/`, 문서는 포함
- 원천 대용량 데이터, 백업, 로그, 임시 산출물은 GitHub 제외
- 코드에서 참조하지 않는 `public/data` 파일은 `public/data/archive/`로 이동 후 GitHub 제외

| 경로 | 파일/폴더 | 용도 | GitHub 포함 여부 | 비고 |
| -- | -- | -- | -- | -- |
| `/README.md` | 파일 | 제출용 프로젝트 개요 | 포함 | 실행, 구조, 문서 링크 정리 |
| `/DATA_PREPROCESSING.md` | 파일 | 전처리 방법 상세 설명 | 포함 | 기존 분석 문서 유지 |
| `/DATA_INVENTORY.md` | 파일 | 현재 파일 인벤토리 | 포함 | 본 문서 |
| `/REPRODUCIBILITY.md` | 파일 | 재현 및 실행 안내 | 포함 | 원천 데이터 획득 경로 포함 |
| `/.gitignore` | 파일 | GitHub 제외 규칙 | 포함 | 원천/임시/백업 제외 |
| `/package.json` | 파일 | Vite/React 실행 설정 | 포함 | `npm run dev`, `npm run build` |
| `/package-lock.json` | 파일 | 의존성 잠금 파일 | 포함 | 재현성 확보 |
| `/index.html` | 파일 | Vite 진입 HTML | 포함 | 대시보드 실행 필수 |
| `/src/` | 폴더 | React 대시보드 코드 | 포함 | 실행 필수 |
| `/public/data/` | 폴더 | 대시보드가 fetch하는 최종 데이터 | 포함 | 사용 파일만 유지 |
| `/public/data/archive/` | 폴더 | 코드에서 참조하지 않는 공개 데이터 백업 | 제외 | `.gitignore`로 제외 |
| `/scripts/` | 폴더 | 데이터 처리 및 검증 스크립트 | 포함 | 실행 순서는 `scripts/README.md` 참조 |
| `/scripts/archive/` | 폴더 | 향후 실험용/비핵심 스크립트 보관용 | 포함 가능 | 현재 비어 있음 |
| `/scripts/dev-server.mjs` | 파일 | 로컬 개발 서버 실행 보조 | 포함 | `npm run dev` 사용 |
| `/scripts/README.md` | 파일 | 스크립트 역할/입출력/순서 | 포함 | 제출용 문서 |
| `/derived_data/00_boundaries/` | 폴더 | 최종 분석 경계 및 요약 | 포함 | 핵심 산출물 |
| `/derived_data/01_landuse_mix/` | 폴더 | 토지이용 혼합도 최종 산출 | 포함 | 대시보드/보고서 사용 |
| `/derived_data/01_landuse_validation/` | 폴더 | 토지이용 검증용 이미지/보조 산출 | 포함 가능 | 검증 자료, 대시보드 직접 사용 아님 |
| `/derived_data/02_development_realization/` | 폴더 | 개발실현도 산출물 | 포함 | 일부 중간 GeoJSON 포함 |
| `/derived_data/03_sgis_jobs_housing/` | 폴더 | SGIS 기반 직주/산업 산출물 | 포함 | 실제 구조 유지 |
| `/derived_data/04_accessibility/` | 폴더 | 접근성 최종 산출물 | 포함 | 217MB 중간 GeoJSON은 제외 이동 |
| `/derived_data/05_station_area/` | 폴더 | 역세권 비율 산출 | 포함 | 접근성 탭 보조 |
| `/derived_data/06_bonus_analysis/` | 폴더 | 보조 비교 지표 산출 | 포함 가능 | 대시보드 직접 참조는 아님 |
| `/derived_data/reports/` | 폴더 | 초기 경계 검증 보고서 | 포함 | 기존 산출 기록 유지 |
| `/docs/figures/` | 폴더 | 검증 이미지, 도식, 캡처 | 포함 | 보고용 자료 정리 |
| `/docs/reports/` | 폴더 | 경계/검증 관련 보고서 | 포함 | 제출용 참고자료 |
| `/data_samples/README.md` | 파일 | 원천 데이터 샘플/획득 안내 | 포함 | 실제 원천 데이터는 제외 |
| `/analysis_boundaries/` | 폴더 | 경계 추출/편집에 사용한 후보 GeoJSON | 포함 일부 | GeoJSON/CSV는 유지, SHP 계열은 ignore |
| `/network/` | 폴더 | 접근성 분석용 가공 네트워크 | 포함 | `nodes.tsv`, `links.tsv` 등 |
| `/subway/` | 폴더 | 네트워크 생성 노트북과 보조 파일 | 포함 | 재현 참고용 |
| `/.node-portable/` | 폴더 | 로컬 Node 실행 파일 | 제외 | 환경 의존, 대용량 |
| `/.npm-cache/` | 폴더 | npm 캐시 | 제외 | 재생성 가능 |
| `/node_modules/` | 폴더 | 설치된 프런트엔드 의존성 | 제외 | `npm install`로 재생성 |
| `/dist/` | 폴더 | 빌드 결과물 | 제외 | `npm run build`로 재생성, 현재 삭제 |
| `/cache/` | 폴더 | 임시 캐시 | 제외 | 재생성 가능 |
| `/archive/` | 폴더 | 로그, 임시 내보내기, 큰 중간파일 백업 | 제외 | 제출 대상 아님 |
| `/backup_before_pangyo_boundary_update/` | 폴더 | 이전 상태 백업 | 제외 | 중복 백업, 현재 위치 유지 |
| `/dashboard/` | 폴더 | 개발 중 생성된 로그/점검 파일 | 제외 | 실행 필수 아님, 현재 위치 유지 |
| `/edit/` | 폴더 | QGIS 편집 원본 레이어 | 제외 권장 | 접근성 원천 편집 데이터 |
| `/용도지역/` | 폴더 | 토지이음 전국 원천 ZIP/CSV | 제외 | 대용량 원천 데이터 |
| `/용도지역2/` | 폴더 | 토지이음 2024-01 경기/서울 원천 SHP | 제외 | 대용량 원천 데이터 |
| `/용도지역3/` | 폴더 | 토지이음 2024-02 원천 SHP | 제외 | 대용량 원천 데이터 |
| `/경기용도지역/` | 폴더 | 용도지역 보조 원천 SHP | 제외 | 원천 데이터 |
| `/서울용도지역/` | 폴더 | 용도지역 보조 원천 SHP | 제외 | 원천 데이터 |
| `/연속지적도/` | 폴더 | 공공데이터 기반 연속지적도 원천 SHP | 제외 | 원천 데이터 |
| `/건축물/` | 폴더 | 건축물대장 원천 Excel | 제외 | 원천 데이터, 엑셀 대용량 |
| `/인구가구/` | 폴더 | SGIS 인구/가구/사업체/종사자 원천 CSV | 제외 | 원천 통계 데이터 |
| `/집계구경계/` | 폴더 | SGIS 집계구 경계 SHP | 제외 | 원천 공간 데이터 |
| `/가구및획지/` | 폴더 | 가구 및 획지 원천 SHP | 제외 | 경계 추출 원천 데이터 |
| `/판교/` | 폴더 | 판교 DWG 및 원천 자료 | 제외 | 대용량 원천 자료 |
| `/위례/` | 폴더 | 위례 원천/가공 후보 자료 | 제외 권장 | 대용량 또는 보조 원천 |
| `/.env` | 파일 | VWorld API 키 | 제외 | 민감 정보 |

## `public/data` 정리 결과

포함 유지:

- `accessibility_cumulative.csv`
- `accessibility_isochrones.geojson`
- `accessibility_summary.csv`
- `boundaries.geojson`
- `buildings_or_parcels.geojson`
- `building_approval_timeseries.csv`
- `building_use_composition.csv`
- `core_stations.geojson`
- `development_summary.csv`
- `industry_basic_composition.csv`
- `industry_lq.csv`
- `jobs_housing_ratio.csv`
- `landuse_blocktype.geojson`
- `landuse_blocktype_composition.csv`
- `landuse_blocktype_mix_index.csv`
- `landuse_mix_index.csv`
- `landuse_zone_composition.csv`
- `landuse_zone_coverage_summary.csv`
- `landuse_zones.geojson`
- `landuse_zones_missing.geojson`
- `pangyo_boundary.geojson`
- `population_business_summary.csv`
- `sgis_census.geojson`
- `station_area_ratio.csv`
- `station_buffers.geojson`
- `top_worker_lq_industries.csv`
- `wirye_boundary.geojson`

`public/data/archive/` 이동:

- `accessibility_isochrones_10min.geojson`
- `bonus_analysis_summary.csv`
- `boundary_area_summary.csv`
- `business_floor_area_density.csv`
- `cumulative_accessibility_curve.csv`
- `dashboard_indicators.json`
- `final_comparison_table.csv`
- `osm_roads_deduplicated.geojson`
- `pangyo_boundary_refined.geojson`
- `reachable_stations.csv`
- `road_density_validation.csv`
- `vacant_or_unbuilt_parcels.csv`

이유: 현재 `src/` 코드에서 직접 fetch하지 않음.

