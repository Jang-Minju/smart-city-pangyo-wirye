from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PREFERRED_RAW_DIR = ROOT / "판교" / "data" / "raw" / "지구경계_전국"
FALLBACK_RAW_DIRS = [
    ROOT / "판교" / "지구경계_전국",
    ROOT / "판교",
]

PANGYO_KEYWORDS = ["판교", "판교테크노밸리", "제1판교", "제1판교테크노밸리", "Pangyo"]
WIRYE_KEYWORDS = ["위례", "Wirye"]
LAND_USE_KEYWORDS = ["업무", "상업", "자족"]

PANGYO_OUT_DIR = ROOT / "판교" / "data" / "processed" / "boundary"
WIRYE_OUT_DIR = ROOT / "위례" / "data" / "processed" / "candidates"
REPORT_PATH = ROOT / "boundary_extraction_report.md"
SHAPEFILE_ENCODINGS = ["cp949", "euc-kr", "utf-8"]


def find_shp_files() -> tuple[Path, list[Path]]:
    if PREFERRED_RAW_DIR.exists():
        raw_dir = PREFERRED_RAW_DIR
        shp_files = sorted(raw_dir.rglob("*.shp"))
        return raw_dir, shp_files

    for raw_dir in FALLBACK_RAW_DIRS:
        if raw_dir.exists():
            shp_files = sorted(raw_dir.rglob("*.shp"))
            if shp_files:
                return raw_dir, shp_files

    return PREFERRED_RAW_DIR, []


def text_columns(gdf: gpd.GeoDataFrame) -> list[str]:
    cols: list[str] = []
    for col in gdf.columns:
        if col == gdf.geometry.name:
            continue
        if pd.api.types.is_object_dtype(gdf[col]) or pd.api.types.is_string_dtype(gdf[col]):
            cols.append(col)
    return cols


def read_shp(path: Path) -> tuple[gpd.GeoDataFrame, str]:
    last_error: Exception | None = None
    for encoding in SHAPEFILE_ENCODINGS:
        try:
            return gpd.read_file(path, encoding=encoding), encoding
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    return gpd.read_file(path), "driver-default"


def find_keyword_matches(
    gdf: gpd.GeoDataFrame, keywords: list[str], source_file: str
) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    cols = text_columns(gdf)
    if not cols:
        empty = gdf.iloc[0:0].copy()
        return empty, pd.DataFrame()

    row_mask = pd.Series(False, index=gdf.index)
    used_cols_by_row: dict[int, set[str]] = {idx: set() for idx in gdf.index}
    keywords_by_row: dict[int, set[str]] = {idx: set() for idx in gdf.index}

    for col in cols:
        text = gdf[col].fillna("").astype(str)
        for keyword in keywords:
            mask = text.str.contains(keyword, case=False, regex=False, na=False)
            if mask.any():
                row_mask = row_mask | mask
                for idx in gdf.index[mask]:
                    used_cols_by_row[idx].add(col)
                    keywords_by_row[idx].add(keyword)

    matches = gdf.loc[row_mask].copy()
    if matches.empty:
        return matches, pd.DataFrame()

    summary = pd.DataFrame(
        {
            "_source_index": matches.index,
            "matched_columns": [
                ", ".join(sorted(used_cols_by_row[idx])) for idx in matches.index
            ],
            "matched_keywords": [
                ", ".join(sorted(keywords_by_row[idx])) for idx in matches.index
            ],
            "source_file": source_file,
        }
    )
    summary.index = matches.index
    return matches, summary


def best_column(columns: list[str], candidates: list[str]) -> str | None:
    lowered = {col.lower(): col for col in columns}
    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    for col in columns:
        for candidate in candidates:
            if candidate.lower() in col.lower():
                return col
    return None


def ensure_5186(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        raise ValueError("CRS is missing; cannot calculate area in EPSG:5186.")
    if gdf.crs.to_epsg() == 5186:
        return gdf.copy()
    return gdf.to_crs(epsg=5186)


def add_summary_fields(
    gdf: gpd.GeoDataFrame, match_summary: pd.DataFrame, source_crs: str
) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    gdf_5186 = ensure_5186(gdf)
    cols = list(gdf_5186.columns)
    zone_col = best_column(cols, ["zoneName", "지구명", "지구", "name", "zone"])
    project_col = best_column(cols, ["사업명", "projectName", "project", "bsnsNm", "bizName"])
    source_area_col = best_column(cols, ["ar", "area", "면적"])

    enriched = gdf_5186.copy()
    enriched["calc_area_sqm"] = enriched.geometry.area
    enriched["source_crs"] = source_crs
    enriched["matched_columns"] = match_summary["matched_columns"].values
    enriched["matched_keywords"] = match_summary["matched_keywords"].values
    enriched["source_file"] = match_summary["source_file"].values

    summary = pd.DataFrame(
        {
            "used_columns": enriched["matched_columns"],
            "matched_keywords": enriched["matched_keywords"],
            "zone_name": enriched[zone_col].astype(str) if zone_col else "",
            "project_name": enriched[project_col].astype(str) if project_col else "",
            "area_sqm_calc_epsg5186": enriched["calc_area_sqm"],
            "area_sqm_source_attr": enriched[source_area_col] if source_area_col else "",
            "source_file": enriched["source_file"],
            "source_crs": enriched["source_crs"],
        }
    )
    return enriched, summary


def save_outputs(
    gdf_5186: gpd.GeoDataFrame,
    summary: pd.DataFrame,
    out_dir: Path,
    basename: str,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    gdf_5186.to_file(out_dir / f"{basename}_5186.geojson", driver="GeoJSON")
    gdf_5186.to_crs(epsg=4326).to_file(out_dir / f"{basename}_4326.geojson", driver="GeoJSON")
    summary.to_csv(out_dir / f"{basename}_summary.csv", index=False, encoding="utf-8-sig")


def sample_records(gdf: gpd.GeoDataFrame, n: int = 20) -> pd.DataFrame:
    attrs = gdf.drop(columns=[gdf.geometry.name], errors="ignore").head(n).copy()
    return attrs


def dataframe_markdown(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "(없음)"
    markdown_df = df.head(max_rows).copy()
    markdown_df = markdown_df.fillna("").astype(str)
    headers = list(markdown_df.columns)
    rows = markdown_df.values.tolist()

    def clean(value: object) -> str:
        return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")

    header_line = "| " + " | ".join(clean(col) for col in headers) + " |"
    separator_line = "| " + " | ".join("---" for _ in headers) + " |"
    row_lines = [
        "| " + " | ".join(clean(value) for value in row) + " |" for row in rows
    ]
    return "\n".join([header_line, separator_line, *row_lines])


def infer_pangyo_judgement(summary: pd.DataFrame) -> str:
    if summary.empty:
        return "판교 후보가 없어 판단할 수 없음."
    names = " ".join(summary["zone_name"].fillna("").astype(str).tolist())
    projects = " ".join(summary["project_name"].fillna("").astype(str).tolist())
    text = f"{names} {projects}"
    if "제1판교" in text or "제1판교테크노밸리" in text:
        return "속성명에 제1판교/제1판교테크노밸리 표현이 직접 포함되어 제1판교테크노밸리 경계로 볼 근거가 있음."
    if "판교테크노밸리" in text:
        return "속성명에 판교테크노밸리가 포함되어 관련 경계로 보이나, 제1판교 여부는 추가 원자료 확인이 필요함."
    if "판교" in text:
        return "속성명에는 판교가 포함되지만 제1판교테크노밸리 표현은 확인되지 않아 제1판교테크노밸리로 확정하기 어려움."
    return "매칭 키워드는 발견됐지만 지구명/사업명에서 판교 식별 표현이 약해 추가 확인이 필요함."


def infer_wirye_judgement(summary: pd.DataFrame, gdf: gpd.GeoDataFrame) -> tuple[str, str]:
    if summary.empty:
        return "위례 후보가 없어 판단할 수 없음.", "업무/상업/자족 관련 속성 확인 불가."

    attrs = gdf.drop(columns=[gdf.geometry.name], errors="ignore")
    all_text = " ".join(attrs.fillna("").astype(str).agg(" ".join, axis=1).tolist())
    has_land_use = [kw for kw in LAND_USE_KEYWORDS if kw in all_text]

    names = " ".join(summary["zone_name"].fillna("").astype(str).tolist())
    if "위례" in names and ("택지" in names or "신도시" in names):
        district = "지구명 기준으로 위례신도시/위례택지개발사업 전체 사업지구일 가능성이 높음."
    elif "위례" in names:
        district = "지구명에 위례가 포함되지만 전체 사업지구인지 세부 용지 경계인지는 속성만으로 확정하기 어려움."
    else:
        district = "위례 후보이나 지구명에서 전체 사업지구 여부를 판단하기 어려움."

    if has_land_use:
        land_use = "업무/상업/자족 관련 표현 확인: " + ", ".join(has_land_use)
    else:
        land_use = "현재 SHP 속성에는 업무용지/상업용지/자족용지 구분 표현이 확인되지 않음."
    return district, land_use


def main() -> None:
    raw_dir, shp_files = find_shp_files()
    all_frames: list[gpd.GeoDataFrame] = []
    metadata: list[dict[str, object]] = []
    pangyo_frames: list[gpd.GeoDataFrame] = []
    pangyo_summaries: list[pd.DataFrame] = []
    wirye_frames: list[gpd.GeoDataFrame] = []
    wirye_summaries: list[pd.DataFrame] = []
    no_result_samples: list[pd.DataFrame] = []
    all_columns: set[str] = set()

    for shp in shp_files:
        gdf, read_encoding = read_shp(shp)
        source_file = str(shp.relative_to(ROOT))
        crs = str(gdf.crs) if gdf.crs is not None else "None"
        metadata.append(
            {
                "file": source_file,
                "crs": crs,
                "read_encoding": read_encoding,
                "records": len(gdf),
                "columns": [col for col in gdf.columns if col != gdf.geometry.name],
                "text_columns": text_columns(gdf),
            }
        )
        all_columns.update([col for col in gdf.columns if col != gdf.geometry.name])
        all_frames.append(gdf.assign(source_file=source_file))

        pangyo_matches, pangyo_match_summary = find_keyword_matches(gdf, PANGYO_KEYWORDS, source_file)
        if not pangyo_matches.empty:
            enriched, summary = add_summary_fields(pangyo_matches, pangyo_match_summary, crs)
            pangyo_frames.append(enriched)
            pangyo_summaries.append(summary)

        wirye_matches, wirye_match_summary = find_keyword_matches(gdf, WIRYE_KEYWORDS, source_file)
        if not wirye_matches.empty:
            enriched, summary = add_summary_fields(wirye_matches, wirye_match_summary, crs)
            wirye_frames.append(enriched)
            wirye_summaries.append(summary)

        if pangyo_matches.empty and wirye_matches.empty:
            sample = sample_records(gdf)
            sample.insert(0, "source_file", source_file)
            no_result_samples.append(sample)

    pangyo_gdf = pd.concat(pangyo_frames, ignore_index=True) if pangyo_frames else gpd.GeoDataFrame()
    pangyo_summary = pd.concat(pangyo_summaries, ignore_index=True) if pangyo_summaries else pd.DataFrame()
    wirye_gdf = pd.concat(wirye_frames, ignore_index=True) if wirye_frames else gpd.GeoDataFrame()
    wirye_summary = pd.concat(wirye_summaries, ignore_index=True) if wirye_summaries else pd.DataFrame()

    if not pangyo_gdf.empty:
        pangyo_gdf = gpd.GeoDataFrame(pangyo_gdf, geometry="geometry", crs="EPSG:5186")
        save_outputs(pangyo_gdf, pangyo_summary, PANGYO_OUT_DIR, "pangyo_boundary")

    if not wirye_gdf.empty:
        wirye_gdf = gpd.GeoDataFrame(wirye_gdf, geometry="geometry", crs="EPSG:5186")
        save_outputs(wirye_gdf, wirye_summary, WIRYE_OUT_DIR, "wirye_candidates")

    all_gdf = pd.concat(all_frames, ignore_index=True) if all_frames else gpd.GeoDataFrame()
    total_records = int(sum(item["records"] for item in metadata))
    crs_values = sorted({str(item["crs"]) for item in metadata})
    wirye_district_judgement, wirye_land_use_judgement = infer_wirye_judgement(
        wirye_summary, wirye_gdf
    )

    metadata_df = pd.DataFrame(metadata)
    metadata_for_report = metadata_df.copy()
    if not metadata_for_report.empty:
        metadata_for_report["columns"] = metadata_for_report["columns"].apply(lambda x: ", ".join(x))
        metadata_for_report["text_columns"] = metadata_for_report["text_columns"].apply(
            lambda x: ", ".join(x)
        )

    all_sample = pd.concat(no_result_samples, ignore_index=True) if no_result_samples else pd.DataFrame()
    if all_sample.empty and not all_gdf.empty:
        all_sample = sample_records(gpd.GeoDataFrame(all_gdf, geometry="geometry", crs=all_gdf.crs))

    report = f"""# 지구경계 SHP 검색 및 추출 결과 보고서

## 작업 개요

- 실행 스크립트: `scripts/01_extract_boundaries.py`
- 원천 탐색 우선 경로: `{PREFERRED_RAW_DIR.relative_to(ROOT)}`
- 실제 사용 경로: `{raw_dir.relative_to(ROOT) if raw_dir.exists() else raw_dir}`
- 판교 검색 키워드: {", ".join(PANGYO_KEYWORDS)}
- 위례 검색 키워드: {", ".join(WIRYE_KEYWORDS)}
- 면적 계산 좌표계: EPSG:5186
- 웹 지도용 변환 좌표계: EPSG:4326

## 전체 요약

- SHP 파일 개수: {len(shp_files)}
- 좌표계(CRS): {", ".join(crs_values) if crs_values else "없음"}
- 총 레코드 수: {total_records}
- 전체 속성 컬럼명: {", ".join(sorted(all_columns)) if all_columns else "없음"}
- 판교 후보 개수: {len(pangyo_summary)}
- 위례 후보 개수: {len(wirye_summary)}

## SHP 파일별 속성 확인

{dataframe_markdown(metadata_for_report)}

## 판교 검색 결과

- 발견된 레코드 수: {len(pangyo_summary)}
- 저장 폴더: `{PANGYO_OUT_DIR.relative_to(ROOT)}`{"" if not pangyo_summary.empty else " (후보 없음으로 미생성)"}
- 저장 파일:
  - `pangyo_boundary_5186.geojson`
  - `pangyo_boundary_4326.geojson`
  - `pangyo_boundary_summary.csv`

{dataframe_markdown(pangyo_summary)}

### 판교 경계 판단

{infer_pangyo_judgement(pangyo_summary)}

## 위례 검색 결과

- 발견된 레코드 수: {len(wirye_summary)}
- 저장 폴더: `{WIRYE_OUT_DIR.relative_to(ROOT)}`{"" if not wirye_summary.empty else " (후보 없음으로 미생성)"}
- 저장 파일:
  - `wirye_candidates_5186.geojson`
  - `wirye_candidates_4326.geojson`
  - `wirye_candidates_summary.csv`

{dataframe_markdown(wirye_summary)}

### 위례 경계 판단

- 전체 사업지구 여부: {wirye_district_judgement}
- 업무/상업/자족용지 속성 여부: {wirye_land_use_judgement}
- 결론: 위례 후보는 아직 업무·상업용지 경계로 확정하지 않는다.

## 결과가 없을 때 확인용 컬럼 및 샘플

아래 표는 후보가 없는 파일이 있을 경우 해당 파일의 샘플을 보여준다. 모든 파일에서 후보가 발견된 경우에는 전체 데이터의 앞 20개 속성 레코드를 참고용으로 표시한다.

### 전체 컬럼명 목록

{", ".join(sorted(all_columns)) if all_columns else "없음"}

### 샘플 레코드 20개

{dataframe_markdown(all_sample, max_rows=20)}

## 다음 단계 제안

- 위례 업무·상업용지 확정을 위해 토지이용계획도 또는 토지이용계획 SHP/DWG/PDF를 확보한다.
- 자족용지 여부 확인을 위해 가구획지계획도, 획지별 용도/면적 조서, 공급대상 토지 목록을 확보한다.
- 판교 제1테크노밸리 확정을 위해 산업단지/도시첨단산업단지 고시 경계, 지구단위계획 결정도, 필지 또는 획지 단위 도면을 대조한다.
- 현재 택지정보시스템 지구경계는 사업지구 단위 경계일 가능성이 있으므로, 업무·상업·자족용지 분석에는 세부 토지이용 또는 획지 경계 데이터가 필요하다.

## 재실행 방법

```powershell
python scripts/01_extract_boundaries.py
```

## 기계 판독용 메타데이터

```json
{json.dumps({"metadata": metadata, "pangyo_count": len(pangyo_summary), "wirye_count": len(wirye_summary)}, ensure_ascii=False, indent=2)}
```
"""
    REPORT_PATH.write_text(report, encoding="utf-8-sig")
    print(f"report={REPORT_PATH}")
    print(f"shp_files={len(shp_files)}")
    print(f"total_records={total_records}")
    print(f"pangyo_candidates={len(pangyo_summary)}")
    print(f"wirye_candidates={len(wirye_summary)}")


if __name__ == "__main__":
    main()
