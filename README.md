# 판교 테크노밸리 vs 위례 계획구역 대시보드

판교 제1테크노밸리와 위례 계획구역을 비교하는 공간분석 대시보다. 비교 축은 토지이용, 개발실현도, 직주·산업 구조, 접근성이다.

## 프로젝트 목적

- 판교의 고용·업무 중심 구조와 위례의 주거 중심 구조를 비교한다.
- 동일한 분석 경계에서 공간 데이터와 통계 데이터를 연결해 비교 가능한 지표를 만든다.
- 교수님이 처리 흐름을 추적할 수 있도록 최종 산출물과 재현 문서를 함께 제공한다.

## 비교 대상

- 판교: `pangyo_1st_technovalley`
- 위례: `wirye_plan_area`

## 대시보드 탭

- `토지이용`: 용도지역, block type, 혼합도 지표
- `개발실현도`: 건축물/필지, 업무시설 비중, 승인 시계열
- `직주·산업`: SGIS 기반 인구·가구·사업체·종사자, 직주비, 산업 LQ
- `접근성`: 역세권 버퍼, 등시간권, 누적 접근성 곡선

## 주요 지표

- 용도지역 혼합도
- block type 혼합도
- 개발실현도
- 업무시설 연면적 비중
- 직주비
- 산업 특화도 LQ
- 30/60분 접근 가능 인구·종사자

## 데이터 출처 요약

- '토지이음' 용도지역 자료
- 'SGIS' 인구·가구, 사업체·종사자, 집계구 경계
- '브이월드' 연속지적도
- '건축HUB' 건축물대장
- OpenStreetMap 기반 도로망
- 프로젝트 구축 대중교통 네트워크
- '택지정보 자료제공' 가구 및 획지 경계도

원천 데이터 대부분은 GitHub에 포함하지 않았다. 상세 목록은 [REPRODUCIBILITY.md](./REPRODUCIBILITY.md)와 [DATA_INVENTORY.md](./DATA_INVENTORY.md)를 참조하면 된다.

## 실행 방법

```bash
npm install
npm run dev
```

## 빌드 방법

```bash
npm run build
```

## 폴더 구조

```text
smart_project/
├─ README.md
├─ DATA_PREPROCESSING.md
├─ DATA_INVENTORY.md
├─ REPRODUCIBILITY.md
├─ package.json
├─ package-lock.json
├─ index.html
├─ src/
├─ public/
│  └─ data/
├─ scripts/
├─ derived_data/
├─ docs/
│  ├─ figures/
│  └─ reports/
└─ data_samples/
```

실제 저장소에는 재현 보조용 `analysis_boundaries/`, `network/`, `subway/`도 포함되어 있다. 반면 원천 대용량 데이터 폴더와 백업/임시 폴더는 `.gitignore`로 제외한다.

## 데이터 한계

- 여러 데이터의 기준시점이 동일하지 않다.
- SGIS 값은 집계구 면적비 기반 배분값이라 추정치다.
- 접근성 분석은 프로젝트 네트워크 파일 기준이다.
- 분석 경계는 행정경계가 아니라 비교 목적의 분석 경계다.

## 재현 관련 문서

- [DATA_PREPROCESSING.md](./DATA_PREPROCESSING.md)
- [DATA_INVENTORY.md](./DATA_INVENTORY.md)
- [REPRODUCIBILITY.md](./REPRODUCIBILITY.md)
- [scripts/README.md](./scripts/README.md)

## Links

- GitHub Repository: https://github.com/Jang-Minju/smart-city-pangyo-wirye
- GitHub Pages: https://jang-minju.github.io/smart-city-pangyo-wirye/

### GitHub Pages 배포 시 환경변수

VWorld 베이스맵을 사용하기 위해 GitHub 저장소의 Actions secrets에 다음 값을 등록해야 한다.

- `VITE_VWORLD_KEY`: VWorld API key

등록 위치:

`Settings → Secrets and variables → Actions → New repository secret`
