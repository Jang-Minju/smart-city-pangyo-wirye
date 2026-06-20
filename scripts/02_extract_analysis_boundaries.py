from __future__ import annotations

import re
from pathlib import Path

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PARCEL_SHP = ROOT / "가구및획지" / "the_geom.shp"
DISTRICT_SHP = ROOT / "판교" / "지구경계_전국" / "the_geom.shp"
OUT_DIR = ROOT / "analysis_boundaries"
REPORT_PATH = ROOT / "analysis_boundary_recommendation.md"


def read_shp(path: Path) -> gpd.GeoDataFrame:
    for encoding in ("cp949", "euc-kr", "utf-8"):
        try:
            return gpd.read_file(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    return gpd.read_file(path)


def normalize_id(row: pd.Series) -> str:
    block = "" if pd.isna(row.get("blockName")) else str(row.get("blockName"))
    lot = "" if pd.isna(row.get("lotName")) else str(row.get("lotName"))
    if not lot or lot == block:
        return block
    return f"{block}-{lot}"


def first_work_number(value: str) -> int | None:
    match = re.search(r"업무\s*(\d+)", value)
    if not match:
        return None
    return int(match.group(1))


def add_metrics(gdf: gpd.GeoDataFrame, category: str) -> gpd.GeoDataFrame:
    out = gdf.copy()
    out["analysis_category"] = category
    out["parcel_id"] = out.apply(normalize_id, axis=1)
    out["area_sqm"] = out.geometry.area
    return out


def dissolve_boundary(gdf: gpd.GeoDataFrame, name: str) -> gpd.GeoDataFrame:
    dissolved = gdf.dissolve()
    dissolved = dissolved[["geometry"]].copy()
    dissolved["name"] = name
    dissolved["area_sqm"] = dissolved.geometry.area
    dissolved["source_feature_count"] = len(gdf)
    dissolved = dissolved[["name", "area_sqm", "source_feature_count", "geometry"]]
    return dissolved


def save_candidate(gdf: gpd.GeoDataFrame, basename: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gdf.to_file(OUT_DIR / f"{basename}_5186.geojson", driver="GeoJSON")
    gdf.to_crs(epsg=4326).to_file(OUT_DIR / f"{basename}_4326.geojson", driver="GeoJSON")
    gdf.to_file(OUT_DIR / f"{basename}_5186.shp", encoding="cp949")


def save_summary(gdf: gpd.GeoDataFrame, basename: str) -> pd.DataFrame:
    summary = (
        gdf.drop(columns="geometry")
        .groupby(["zoneName", "blockType", "blockName", "lotName", "parcel_id", "analysis_category"], dropna=False)
        .agg(feature_count=("area_sqm", "size"), area_sqm=("area_sqm", "sum"))
        .reset_index()
        .sort_values(["analysis_category", "blockType", "parcel_id"])
    )
    summary.to_csv(OUT_DIR / f"{basename}_summary.csv", index=False, encoding="utf-8-sig")
    return summary


def markdown_table(df: pd.DataFrame, max_rows: int = 200) -> str:
    if df.empty:
        return "(없음)"
    d = df.head(max_rows).fillna("").astype(str)
    headers = list(d.columns)
    rows = d.values.tolist()

    def clean(value: object) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")

    lines = [
        "| " + " | ".join(clean(h) for h in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(clean(v) for v in row) + " |")
    return "\n".join(lines)


def main() -> None:
    parcels = read_shp(PARCEL_SHP)
    districts = read_shp(DISTRICT_SHP)
    parcels = parcels.to_crs(epsg=5186)
    districts = districts.to_crs(epsg=5186)

    pangyo_district = districts[districts["zoneName"].astype(str).str.contains("성남판교지구", regex=False, na=False)]
    wirye_district = districts[districts["zoneName"].astype(str).str.contains("위례", regex=False, na=False)]

    pangyo_all = parcels[parcels["zoneName"].astype(str).str.contains("성남판교지구", regex=False, na=False)].copy()
    wirye_all = parcels[parcels["zoneName"].astype(str).str.contains("위례", regex=False, na=False)].copy()

    pangyo_primary = add_metrics(
        pangyo_all[pangyo_all["blockType"].astype(str).eq("도시지원시설용지")],
        "제1판교테크노밸리 후보: 도시지원시설용지",
    )
    pangyo_support = add_metrics(
        pangyo_all[pangyo_all["blockType"].astype(str).isin(["업무시설", "업무시설기타"])],
        "판교 보조 검토: 업무시설",
    )

    def is_wirye_work_target(row: pd.Series) -> bool:
        if str(row.get("blockType")) != "업무시설":
            return False
        joined = f"{row.get('blockName', '')} {row.get('lotName', '')}"
        num = first_work_number(joined)
        return num is not None and 1 <= num <= 28

    wirye_work = add_metrics(
        wirye_all[wirye_all.apply(is_wirye_work_target, axis=1)],
        "위례 업무시설 후보: 업무1~업무28",
    )
    wirye_commercial = add_metrics(
        wirye_all[wirye_all["blockType"].astype(str).isin(["일반상업", "근린상업"])],
        "위례 상업시설 후보",
    )
    wirye_self_support = add_metrics(
        wirye_all[wirye_all["blockType"].astype(str).isin(["도시지원시설용지", "복합용지"])],
        "위례 자족 대체 후보: 도시지원/복합",
    )
    wirye_candidate = pd.concat([wirye_work, wirye_commercial, wirye_self_support], ignore_index=True)
    wirye_candidate = gpd.GeoDataFrame(wirye_candidate, geometry="geometry", crs=parcels.crs)

    save_candidate(pangyo_primary, "pangyo_1st_technovalley_candidate_parcels")
    save_candidate(dissolve_boundary(pangyo_primary, "제1판교테크노밸리 후보"), "pangyo_1st_technovalley_candidate_boundary")
    pangyo_summary = save_summary(pangyo_primary, "pangyo_1st_technovalley_candidate_parcels")

    if not pangyo_support.empty:
        save_summary(pangyo_support, "pangyo_supporting_business_facility_review")

    save_candidate(wirye_candidate, "wirye_business_commercial_candidate_parcels")
    save_candidate(dissolve_boundary(wirye_candidate, "위례 업무·상업·자족 대체 후보"), "wirye_business_commercial_candidate_boundary")
    wirye_summary = save_summary(wirye_candidate, "wirye_business_commercial_candidate_parcels")

    inventory = []
    for ext in ("*.shp", "*.dbf", "*.shx", "*.dxf", "*.dwg", "*.pdf"):
        for path in ROOT.rglob(ext):
            rel_parts = path.relative_to(ROOT).parts
            if rel_parts and rel_parts[0] == OUT_DIR.name:
                continue
            inventory.append(
                {
                    "file": str(path.relative_to(ROOT)),
                    "ext": path.suffix.lower(),
                    "size_bytes": path.stat().st_size,
                }
            )
    inventory_df = pd.DataFrame(inventory).sort_values(["ext", "file"])

    pangyo_inside = bool(pangyo_primary.within(pangyo_district.geometry.union_all()).all()) if not pangyo_primary.empty else False
    wirye_inside = bool(wirye_candidate.within(wirye_district.geometry.union_all()).all()) if not wirye_candidate.empty else False

    pangyo_boundary = dissolve_boundary(pangyo_primary, "제1판교테크노밸리 후보")
    wirye_boundary = dissolve_boundary(wirye_candidate, "위례 업무·상업·자족 대체 후보")

    pangyo_blocktypes = pangyo_all["blockType"].fillna("(NA)").value_counts().reset_index()
    pangyo_blocktypes.columns = ["blockType", "count"]
    wirye_blocktypes = wirye_all["blockType"].fillna("(NA)").value_counts().reset_index()
    wirye_blocktypes.columns = ["blockType", "count"]

    report = f"""# 교수 과제 분석 경계 추천 보고서

## 목적

전체 사업지구인 성남판교지구와 위례신도시를 그대로 쓰지 않고, 교수 과제의 비교 대상인 `제1판교테크노밸리`와 `위례 업무·상업용지 또는 자족시설용지`에 가까운 실제 분석 경계를 찾는 것이 목적이다.

## 전체 파일 조사

{markdown_table(inventory_df, max_rows=200)}

## 사용한 핵심 파일

| 구분 | 파일 | CRS | 레코드 수 | 주요 컬럼 |
| --- | --- | --- | --- | --- |
| 가구및획지경계도 | `가구및획지/the_geom.shp` | {parcels.crs} | {len(parcels)} | zoneCode, zoneName, blockName, blockType, lotName |
| 지구경계 | `판교/지구경계_전국/the_geom.shp` | {districts.crs} | {len(districts)} | zoneCode, zoneName, stepCode, ar |

## 가구및획지 컬럼 검토

- 획지번호: 별도 `획지번호` 컬럼은 없지만 `blockName`, `lotName` 조합으로 획지 식별 가능
- 용도: `blockType` 컬럼으로 확인 가능
- 자족시설용지: 명칭 그대로는 없음
- 업무시설용지: `업무시설`, `업무시설기타` 존재
- 도시지원시설용지: 존재
- 연구개발용지: 명칭 그대로는 없음
- 상업시설용지: `일반상업`, `근린상업`, `중심상업`, `상업시설` 등 존재

### 성남판교지구 blockType 분포

{markdown_table(pangyo_blocktypes, max_rows=100)}

### 위례 blockType 분포

{markdown_table(wirye_blocktypes, max_rows=100)}

## 판교 최종 분석 경계 추천안

### 추천안

`성남판교지구 택지개발사업` 내부의 `도시지원시설용지`를 제1판교테크노밸리 경계 후보로 추천한다.

### 근거

- 가구및획지경계도에서 성남판교지구 내부 `도시지원시설용지`가 75개 객체로 확인됨
- 제1판교테크노밸리는 성남판교지구 전체가 아니라 판교신도시 내 도시지원시설 성격의 업무·연구·산업 기능 집적지로 보는 것이 타당함
- `테크노밸리` 또는 `제1판교`라는 직접 명칭은 속성에 없지만, 현재 데이터에서 제1판교테크노밸리를 특정할 수 있는 가장 강한 속성 근거는 `도시지원시설용지`
- 공간적으로 성남판교지구 전체 경계 내부 포함 여부: {pangyo_inside}

### 판교 후보 요약

- 후보 객체 수: {len(pangyo_primary)}
- 후보 dissolve 경계 면적: {float(pangyo_boundary.iloc[0].area_sqm):,.1f}㎡
- 사용 파일: `가구및획지/the_geom.shp`
- 저장 파일:
  - `analysis_boundaries/pangyo_1st_technovalley_candidate_parcels_5186.geojson`
  - `analysis_boundaries/pangyo_1st_technovalley_candidate_parcels_4326.geojson`
  - `analysis_boundaries/pangyo_1st_technovalley_candidate_parcels_5186.shp`
  - `analysis_boundaries/pangyo_1st_technovalley_candidate_boundary_5186.geojson`
  - `analysis_boundaries/pangyo_1st_technovalley_candidate_boundary_4326.geojson`
  - `analysis_boundaries/pangyo_1st_technovalley_candidate_boundary_5186.shp`
  - `analysis_boundaries/pangyo_1st_technovalley_candidate_parcels_summary.csv`

### 사용한 필지/획지

{markdown_table(pangyo_summary, max_rows=150)}

### 과제 적합성 판단

적합. 단, `제1판교테크노밸리`라는 명칭이 속성에 직접 들어 있지는 않으므로 보고서에는 `성남판교지구 전체가 아니라 도시지원시설용지를 추출한 제1판교테크노밸리 후보 경계`라고 명시하는 것이 안전하다.

보조 검토로 `업무시설`, `업무시설기타` 18개 객체도 별도 CSV로 저장했다. 제1판교테크노밸리 본체 경계에는 도시지원시설용지를 우선 사용하고, 업무시설은 주변 업무기능 보조 후보로만 취급하는 것을 권장한다.

## 위례 최종 분석 경계 추천안

### 추천안

`위례 택지개발사업 예정지구` 내부에서 다음 필지를 추출한 경계를 위례 업무·상업용지 분석 후보로 추천한다.

- 업무시설: `업무1~업무28`에 해당하는 객체
- 상업시설: `일반상업`, `근린상업`
- 자족 대체 후보: `도시지원시설용지`, `복합용지`

### 근거

- `자족시설용지`라는 직접 명칭은 현재 데이터에 없음
- 업무용지는 `업무시설`로 존재하며, 과제에서 언급한 `업무1~업무28` 범위에 해당하는 필지만 선별함
- 상업용지는 `일반상업`, `근린상업`으로 존재함
- 위례에서 자족 기능을 대체 검토할 수 있는 용도는 `도시지원시설용지`, `복합용지`
- 공간적으로 위례 전체 지구경계 내부 포함 여부: {wirye_inside}

### 위례 후보 요약

- 후보 객체 수: {len(wirye_candidate)}
- 후보 dissolve 경계 면적: {float(wirye_boundary.iloc[0].area_sqm):,.1f}㎡
- 사용 파일: `가구및획지/the_geom.shp`
- 저장 파일:
  - `analysis_boundaries/wirye_business_commercial_candidate_parcels_5186.geojson`
  - `analysis_boundaries/wirye_business_commercial_candidate_parcels_4326.geojson`
  - `analysis_boundaries/wirye_business_commercial_candidate_parcels_5186.shp`
  - `analysis_boundaries/wirye_business_commercial_candidate_boundary_5186.geojson`
  - `analysis_boundaries/wirye_business_commercial_candidate_boundary_4326.geojson`
  - `analysis_boundaries/wirye_business_commercial_candidate_boundary_5186.shp`
  - `analysis_boundaries/wirye_business_commercial_candidate_parcels_summary.csv`

### 사용한 필지/획지

{markdown_table(wirye_summary, max_rows=200)}

### 과제 적합성 판단

부분 적합에서 적합. `업무시설`과 `상업시설`은 직접 확인되어 과제 요구와 잘 맞는다. 다만 `자족시설용지` 명칭은 없으므로, 자족시설은 `도시지원시설용지`와 `복합용지`를 대체 후보로 제시해야 한다. 최종 보고서에는 `자족시설용지 직접 속성 없음`을 명시하는 것이 필요하다.

## 최종 결론

| 대상 | 전체 지구경계 사용 여부 | 최종 추천 경계 | 적합성 |
| --- | --- | --- | --- |
| 제1판교테크노밸리 | 사용하지 않음. 공간 검증용으로만 사용 | 성남판교지구 내부 `도시지원시설용지` | 적합. 명칭 직접 속성 부재는 한계 |
| 위례 업무·상업용지 | 사용하지 않음. 공간 검증용으로만 사용 | 위례 내부 `업무1~업무28`, `일반상업`, `근린상업`, `도시지원시설용지`, `복합용지` | 적합. 자족시설용지 직접 명칭 없음 |

## 재실행 방법

```powershell
python scripts/02_extract_analysis_boundaries.py
```
"""
    REPORT_PATH.write_text(report, encoding="utf-8-sig")

    print(f"parcels={len(parcels)}")
    print(f"pangyo_candidate_features={len(pangyo_primary)}")
    print(f"pangyo_candidate_area_sqm={float(pangyo_boundary.iloc[0].area_sqm):.1f}")
    print(f"wirye_candidate_features={len(wirye_candidate)}")
    print(f"wirye_candidate_area_sqm={float(wirye_boundary.iloc[0].area_sqm):.1f}")
    print(f"report={REPORT_PATH}")


if __name__ == "__main__":
    main()
