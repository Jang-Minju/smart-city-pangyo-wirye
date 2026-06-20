# Bonus Analysis Report: Industry LQ and Business Floor-Area Density

## 1. Inputs
- LQ input: `derived_data/03_sgis_jobs_housing/industry_basic_composition.csv`
- Business floor-area density input: `derived_data/02_development_realization/development_realization_deduplicated.csv`

The Pangyo inputs reflect the final boundary update. Wirye inputs are preserved from the previous boundary results where requested in upstream steps.

## 2. LQ Method
`LQ = area industry share / combined Pangyo+Wirye industry share`.

Both `worker_count` and `business_count` LQ are retained. Worker-count LQ is the primary interpretation value; business-count LQ is a supporting value.

## 3. Top Worker-Count LQ Industries
| area_name | rank | industry_code | industry_name | worker_count | worker_ratio | lq |
| --- | --- | --- | --- | --- | --- | --- |
| pangyo_1st_technovalley | 1 | 5 | 수도, 하수 및 폐기물 처리, 원료 재생업 | 16.914240 | 0.000322 | 1.483835 |
| pangyo_1st_technovalley | 2 | 10 | 정보통신업 | 23488.585189 | 0.446828 | 1.450955 |
| pangyo_1st_technovalley | 3 | 3 | 제조업 | 2388.994093 | 0.045446 | 1.322720 |
| pangyo_1st_technovalley | 4 | 13 | 전문, 과학 및 기술 서비스업 | 10235.267902 | 0.194708 | 1.280805 |
| pangyo_1st_technovalley | 5 | 14 | 사업시설 관리, 사업 지원 및 임대 서비스업 | 7145.348379 | 0.135927 | 1.195603 |
| wirye_plan_area | 1 | 1 | 농업, 임업 및 어업 | 10.000000 | 0.000391 | 3.056079 |
| wirye_plan_area | 2 | 16 | 교육 서비스업 | 3746.290652 | 0.146529 | 3.005329 |
| wirye_plan_area | 3 | 8 | 운수 및 창고업 | 1953.898279 | 0.076423 | 2.936966 |
| wirye_plan_area | 4 | 17 | 보건업 및 사회복지 서비스업 | 3297.945134 | 0.128993 | 2.647495 |
| wirye_plan_area | 5 | 18 | 예술, 스포츠 및 여가관련 서비스업 | 545.797536 | 0.021348 | 2.629022 |

## 4. Worker-Count LQ Full Ranking
| area_name | industry_code | industry_name | area_value | area_industry_ratio | combined_industry_ratio | lq | specialization_level |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pangyo_1st_technovalley | 5 | 수도, 하수 및 폐기물 처리, 원료 재생업 | 16.914240 | 0.000322 | 0.000217 | 1.483835 | specialized |
| pangyo_1st_technovalley | 10 | 정보통신업 | 23488.585189 | 0.446828 | 0.307955 | 1.450955 | specialized |
| pangyo_1st_technovalley | 3 | 제조업 | 2388.994093 | 0.045446 | 0.034358 | 1.322720 | specialized |
| pangyo_1st_technovalley | 13 | 전문, 과학 및 기술 서비스업 | 10235.267902 | 0.194708 | 0.152020 | 1.280805 | specialized |
| pangyo_1st_technovalley | 14 | 사업시설 관리, 사업 지원 및 임대 서비스업 | 7145.348379 | 0.135927 | 0.113689 | 1.195603 | specialized |
| pangyo_1st_technovalley | 11 | 금융 및 보험업 | 502.236237 | 0.009554 | 0.010468 | 0.912727 | under_specialized |
| pangyo_1st_technovalley | 7 | 도매 및 소매업 | 4273.336734 | 0.081293 | 0.110597 | 0.735033 | under_specialized |
| pangyo_1st_technovalley | 12 | 부동산업 | 1025.489500 | 0.019508 | 0.027656 | 0.705392 | under_specialized |
| pangyo_1st_technovalley | 15 | 공공행정, 국방 및 사회보장 행정 | 116.274014 | 0.002212 | 0.003994 | 0.553760 | under_specialized |
| pangyo_1st_technovalley | 6 | 건설업 | 1034.867998 | 0.019686 | 0.038574 | 0.510359 | under_specialized |
| pangyo_1st_technovalley | 9 | 숙박 및 음식점업 | 1402.748394 | 0.026685 | 0.054742 | 0.487462 | under_specialized |
| pangyo_1st_technovalley | 19 | 협회 및 단체, 수리 및 기타 개인 서비스업 | 188.501048 | 0.003586 | 0.013279 | 0.270050 | under_specialized |
| pangyo_1st_technovalley | 4 | 전기, 가스, 증기 및 공기조절 공급업 | 8.699821 | 0.000165 | 0.000703 | 0.235268 | under_specialized |
| pangyo_1st_technovalley | 18 | 예술, 스포츠 및 여가관련 서비스업 | 88.659104 | 0.001687 | 0.008120 | 0.207705 | under_specialized |
| pangyo_1st_technovalley | 17 | 보건업 및 사회복지 서비스업 | 508.967265 | 0.009682 | 0.048723 | 0.198720 | under_specialized |
| pangyo_1st_technovalley | 8 | 운수 및 창고업 | 79.243669 | 0.001507 | 0.026021 | 0.057932 | under_specialized |
| pangyo_1st_technovalley | 16 | 교육 서비스업 | 63.263175 | 0.001203 | 0.048757 | 0.024683 | under_specialized |
| pangyo_1st_technovalley | 1 | 농업, 임업 및 어업 | 0.000000 | 0.000000 | 0.000128 | 0.000000 | under_specialized |
| wirye_plan_area | 1 | 농업, 임업 및 어업 | 10.000000 | 0.000391 | 0.000128 | 3.056079 | specialized |
| wirye_plan_area | 16 | 교육 서비스업 | 3746.290652 | 0.146529 | 0.048757 | 3.005329 | specialized |
| wirye_plan_area | 8 | 운수 및 창고업 | 1953.898279 | 0.076423 | 0.026021 | 2.936966 | specialized |
| wirye_plan_area | 17 | 보건업 및 사회복지 서비스업 | 3297.945134 | 0.128993 | 0.048723 | 2.647495 | specialized |
| wirye_plan_area | 18 | 예술, 스포츠 및 여가관련 서비스업 | 545.797536 | 0.021348 | 0.008120 | 2.629022 | specialized |
| wirye_plan_area | 4 | 전기, 가스, 증기 및 공기조절 공급업 | 46.263337 | 0.001810 | 0.000703 | 2.572349 | specialized |
| wirye_plan_area | 19 | 협회 및 단체, 수리 및 기타 개인 서비스업 | 849.013835 | 0.033208 | 0.013279 | 2.500835 | specialized |
| wirye_plan_area | 9 | 숙박 및 음식점업 | 2874.491154 | 0.112431 | 0.054742 | 2.053818 | specialized |
| wirye_plan_area | 6 | 건설업 | 1979.068184 | 0.077408 | 0.038574 | 2.006741 | specialized |
| wirye_plan_area | 15 | 공공행정, 국방 및 사회보장 행정 | 195.820363 | 0.007659 | 0.003994 | 1.917505 | specialized |
| wirye_plan_area | 12 | 부동산업 | 1135.365766 | 0.044408 | 0.027656 | 1.605738 | specialized |
| wirye_plan_area | 7 | 도매 및 소매업 | 4368.078060 | 0.170850 | 0.110597 | 1.544793 | specialized |
| wirye_plan_area | 11 | 금융 및 보험업 | 315.648529 | 0.012346 | 0.010468 | 1.179441 | specialized |
| wirye_plan_area | 14 | 사업시설 관리, 사업 지원 및 임대 서비스업 | 1737.679602 | 0.067966 | 0.113689 | 0.597824 | under_specialized |
| wirye_plan_area | 13 | 전문, 과학 및 기술 서비스업 | 1642.667362 | 0.064250 | 0.152020 | 0.422643 | under_specialized |
| wirye_plan_area | 3 | 제조업 | 295.558446 | 0.011560 | 0.034358 | 0.336462 | under_specialized |
| wirye_plan_area | 10 | 정보통신업 | 573.197945 | 0.022420 | 0.307955 | 0.072802 | under_specialized |
| wirye_plan_area | 5 | 수도, 하수 및 폐기물 처리, 원료 재생업 | 0.028809 | 0.000001 | 0.000217 | 0.005196 | under_specialized |

## 5. Business-Count LQ Full Ranking
| area_name | industry_code | industry_name | area_value | area_industry_ratio | combined_industry_ratio | lq | specialization_level |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pangyo_1st_technovalley | 15 | 공공행정, 국방 및 사회보장 행정 | 1.691424 | 0.001151 | 0.000243 | 4.729574 | specialized |
| pangyo_1st_technovalley | 10 | 정보통신업 | 393.817090 | 0.267949 | 0.072389 | 3.701496 | specialized |
| pangyo_1st_technovalley | 11 | 금융 및 보험업 | 44.795023 | 0.030478 | 0.009589 | 3.178312 | specialized |
| pangyo_1st_technovalley | 3 | 제조업 | 66.046656 | 0.044937 | 0.019045 | 2.359538 | specialized |
| pangyo_1st_technovalley | 13 | 전문, 과학 및 기술 서비스업 | 176.477296 | 0.120073 | 0.066654 | 1.801449 | specialized |
| pangyo_1st_technovalley | 14 | 사업시설 관리, 사업 지원 및 임대 서비스업 | 26.855241 | 0.018272 | 0.013596 | 1.343973 | specialized |
| pangyo_1st_technovalley | 9 | 숙박 및 음식점업 | 308.544745 | 0.209931 | 0.164171 | 1.278733 | specialized |
| pangyo_1st_technovalley | 8 | 운수 및 창고업 | 40.702053 | 0.027693 | 0.027917 | 0.991977 | under_specialized |
| pangyo_1st_technovalley | 12 | 부동산업 | 85.721948 | 0.058324 | 0.067144 | 0.868645 | under_specialized |
| pangyo_1st_technovalley | 17 | 보건업 및 사회복지 서비스업 | 31.772806 | 0.021618 | 0.034867 | 0.620007 | under_specialized |
| pangyo_1st_technovalley | 18 | 예술, 스포츠 및 여가관련 서비스업 | 21.985522 | 0.014959 | 0.026738 | 0.559453 | under_specialized |
| pangyo_1st_technovalley | 7 | 도매 및 소매업 | 222.641159 | 0.151483 | 0.321438 | 0.471266 | under_specialized |
| pangyo_1st_technovalley | 19 | 협회 및 단체, 수리 및 기타 개인 서비스업 | 29.050848 | 0.019766 | 0.061498 | 0.321405 | under_specialized |
| pangyo_1st_technovalley | 6 | 건설업 | 9.366507 | 0.006373 | 0.022432 | 0.284092 | under_specialized |
| pangyo_1st_technovalley | 16 | 교육 서비스업 | 10.277389 | 0.006993 | 0.092278 | 0.075778 | under_specialized |
| pangyo_1st_technovalley | 1 | 농업, 임업 및 어업 | 0.000000 | 0.000000 | 0.000000 |  | not_calculable |
| pangyo_1st_technovalley | 4 | 전기, 가스, 증기 및 공기조절 공급업 | 0.000000 | 0.000000 | 0.000000 |  | not_calculable |
| pangyo_1st_technovalley | 5 | 수도, 하수 및 폐기물 처리, 원료 재생업 | 0.000000 | 0.000000 | 0.000000 |  | not_calculable |
| wirye_plan_area | 16 | 교육 서비스업 | 631.169639 | 0.115145 | 0.092278 | 1.247809 | specialized |
| wirye_plan_area | 6 | 건설업 | 146.567570 | 0.026738 | 0.022432 | 1.191954 | specialized |
| wirye_plan_area | 19 | 협회 및 단체, 수리 및 기타 개인 서비스업 | 398.440757 | 0.072688 | 0.061498 | 1.181950 | specialized |
| wirye_plan_area | 7 | 도매 및 소매업 | 2011.758808 | 0.367007 | 0.321438 | 1.141768 | specialized |
| wirye_plan_area | 18 | 예술, 스포츠 및 여가관련 서비스업 | 163.878544 | 0.029897 | 0.026738 | 1.118123 | specialized |
| wirye_plan_area | 17 | 보건업 및 사회복지 서비스업 | 210.598523 | 0.038420 | 0.034867 | 1.101887 | specialized |
| wirye_plan_area | 12 | 부동산업 | 381.014253 | 0.069509 | 0.067144 | 1.035220 | specialized |
| wirye_plan_area | 8 | 운수 및 창고업 | 153.358213 | 0.027977 | 0.027917 | 1.002151 | specialized |
| wirye_plan_area | 9 | 숙박 및 음식점업 | 832.651684 | 0.151901 | 0.164171 | 0.925264 | under_specialized |
| wirye_plan_area | 14 | 사업시설 관리, 사업 지원 및 임대 서비스업 | 67.651018 | 0.012342 | 0.013596 | 0.907772 | under_specialized |
| wirye_plan_area | 13 | 전문, 과학 및 기술 서비스업 | 286.851066 | 0.052331 | 0.066654 | 0.785110 | under_specialized |
| wirye_plan_area | 3 | 제조업 | 66.340527 | 0.012103 | 0.019045 | 0.635471 | under_specialized |
| wirye_plan_area | 11 | 금융 및 보험업 | 21.863442 | 0.003989 | 0.009589 | 0.415936 | under_specialized |
| wirye_plan_area | 10 | 정보통신업 | 109.381364 | 0.019955 | 0.072389 | 0.275656 | under_specialized |
| wirye_plan_area | 15 | 공공행정, 국방 및 사회보장 행정 | 0.000000 | 0.000000 | 0.000243 | 0.000000 | under_specialized |
| wirye_plan_area | 1 | 농업, 임업 및 어업 | 0.000000 | 0.000000 | 0.000000 |  | not_calculable |
| wirye_plan_area | 4 | 전기, 가스, 증기 및 공기조절 공급업 | 0.000000 | 0.000000 | 0.000000 |  | not_calculable |
| wirye_plan_area | 5 | 수도, 하수 및 폐기물 처리, 원료 재생업 | 0.000000 | 0.000000 | 0.000000 |  | not_calculable |

## 6. Business Floor-Area Density
| area_name | boundary_area_sqm | boundary_area_ha | boundary_area_km2 | business_floor_area_sqm | business_floor_area_ratio | business_floor_area_density_sqm_per_sqm | business_floor_area_density_sqm_per_ha | business_floor_area_density_sqm_per_km2 | source_file | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pangyo_1st_technovalley | 860504.887988 | 86.050489 | 0.860505 | 2613788.187400 | 0.737547 | 3.037505 | 30375.053342 | 3037505.334238 | C:\Users\go123\Documents\4-1\smart_project\derived_data\02_development_realization\development_realization_deduplicated.csv | Used development_realization_deduplicated.csv as the preferred duplicate-checked source. |
| wirye_plan_area | 6757873.520642 | 675.787352 | 6.757874 | 2806179.344800 | 0.181395 | 0.415246 | 4152.459107 | 415245.910748 | C:\Users\go123\Documents\4-1\smart_project\derived_data\02_development_realization\development_realization_deduplicated.csv | Used development_realization_deduplicated.csv as the preferred duplicate-checked source. |

## 7. Summary
| area_name | top_specialized_industry_1 | top_specialized_industry_1_lq | top_specialized_industry_2 | top_specialized_industry_2_lq | top_specialized_industry_3 | top_specialized_industry_3_lq | business_floor_area_sqm | business_floor_area_density_sqm_per_ha | business_floor_area_ratio | interpretation_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pangyo_1st_technovalley | 수도, 하수 및 폐기물 처리, 원료 재생업 | 1.483835 | 정보통신업 | 1.450955 | 제조업 | 1.322720 | 2613788.187400 | 30375.053342 | 0.737547 | Worker-based LQ and high business-floor-area density indicate a strong office/employment function relative to the two-area benchmark. |
| wirye_plan_area | 농업, 임업 및 어업 | 3.056079 | 교육 서비스업 | 3.005329 | 운수 및 창고업 | 2.936966 | 2806179.344800 | 4152.459107 | 0.181395 | Worker-based LQ highlights relatively stronger local-service industries, while business-floor-area density is lower than Pangyo. |

## 8. Notes
No KPI, chart, dashboard, public data, final comparison table, accessibility, OSM, or station-area outputs were updated in this step.
