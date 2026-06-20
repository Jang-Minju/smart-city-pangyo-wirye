from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
LANDUSE_DIR = ROOT / "경기용도지역"
REPORT_DIR = ROOT / "reports"
REPORT_PATH = REPORT_DIR / "landuse_zone_column_check.md"

PANGYO_BOUNDARY = ROOT / "analysis_boundaries" / "pangyo_1st_technovalley_candidate_boundary_5186.geojson"
WIRYE_BOUNDARY = ROOT / "analysis_boundaries" / "wirye_business_commercial_candidate_boundary_5186.geojson"

TARGET_VALUES = [
    "주거지역",
    "제1종일반주거지역",
    "제2종일반주거지역",
    "제3종일반주거지역",
    "준주거지역",
    "상업지역",
    "일반상업지역",
    "근린상업지역",
    "자연녹지지역",
    "보전녹지지역",
    "생산녹지지역",
    "공업지역",
    "준공업지역",
]


def read_shp(path: Path) -> tuple[gpd.GeoDataFrame, str]:
    for encoding in ("cp949", "euc-kr", "utf-8"):
        try:
            return gpd.read_file(path, encoding=encoding), encoding
        except UnicodeDecodeError:
            continue
    return gpd.read_file(path), "driver-default"


def markdown_table(df: pd.DataFrame, max_rows: int = 100) -> str:
    if df.empty:
        return "(없음)"
    d = df.head(max_rows).fillna("").astype(str)
    headers = list(d.columns)

    def clean(value: object) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")

    lines = [
        "| " + " | ".join(clean(h) for h in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in d.values.tolist():
        lines.append("| " + " | ".join(clean(v) for v in row) + " |")
    return "\n".join(lines)


def text_columns(gdf: gpd.GeoDataFrame) -> list[str]:
    cols: list[str] = []
    for col in gdf.columns:
        if col == gdf.geometry.name:
            continue
        if pd.api.types.is_object_dtype(gdf[col]) or pd.api.types.is_string_dtype(gdf[col]):
            cols.append(col)
    return cols


def unique_samples(gdf: gpd.GeoDataFrame, columns: list[str], limit: int = 30) -> pd.DataFrame:
    rows = []
    for col in columns:
        values = (
            gdf[col]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .head(limit)
            .tolist()
        )
        rows.append(
            {
                "column": col,
                "unique_count": int(gdf[col].dropna().astype(str).nunique()),
                "sample_values": ", ".join(values),
            }
        )
    return pd.DataFrame(rows)


def find_target_columns(gdf: gpd.GeoDataFrame, columns: list[str]) -> pd.DataFrame:
    rows = []
    for col in columns:
        series = gdf[col].fillna("").astype(str)
        hits = []
        for value in TARGET_VALUES:
            if series.str.contains(value, regex=False, na=False).any():
                hits.append(value)
        if hits:
            matched_rows = int(series.apply(lambda x: any(v in x for v in TARGET_VALUES)).sum())
            rows.append(
                {
                    "column": col,
                    "matched_values": ", ".join(hits),
                    "matched_row_count": matched_rows,
                }
            )
    return pd.DataFrame(rows)


def bounds_overlap(bounds_a, bounds_b) -> bool:
    minx_a, miny_a, maxx_a, maxy_a = bounds_a
    minx_b, miny_b, maxx_b, maxy_b = bounds_b
    return not (
        maxx_a < minx_b
        or maxx_b < minx_a
        or maxy_a < miny_b
        or maxy_b < miny_a
    )


def clip_feasibility(landuse: gpd.GeoDataFrame) -> pd.DataFrame:
    rows = []
    landuse_5186 = landuse.to_crs(epsg=5186) if landuse.crs is not None else landuse
    for name, path in [("판교 분석 경계", PANGYO_BOUNDARY), ("위례 분석 경계", WIRYE_BOUNDARY)]:
        if not path.exists():
            rows.append(
                {
                    "boundary": name,
                    "boundary_file": str(path.relative_to(ROOT)),
                    "exists": False,
                    "crs": "",
                    "bounds_overlap": False,
                    "intersects": False,
                    "judgement": "분석 경계 파일이 없어 clip 가능 여부를 판단할 수 없음",
                }
            )
            continue

        boundary = gpd.read_file(path)
        boundary_5186 = boundary.to_crs(epsg=5186) if boundary.crs is not None else boundary
        bbox_overlap = bounds_overlap(landuse_5186.total_bounds, boundary_5186.total_bounds)
        intersects = False
        if bbox_overlap:
            intersects = bool(landuse_5186.intersects(boundary_5186.geometry.union_all()).any())

        if landuse.crs is None:
            judgement = "용도지역 SHP의 CRS가 없어 좌표계 지정 전에는 clip 판단이 불완전함"
        elif intersects:
            judgement = "clip 및 면적 구성비 계산 가능"
        elif bbox_overlap:
            judgement = "bbox는 겹치지만 실제 geometry 교차가 확인되지 않음"
        else:
            judgement = "공간 범위가 겹치지 않아 현재 파일만으로는 clip 불가"

        rows.append(
            {
                "boundary": name,
                "boundary_file": str(path.relative_to(ROOT)),
                "exists": True,
                "crs": str(boundary.crs),
                "bounds_overlap": bbox_overlap,
                "intersects": intersects,
                "judgement": judgement,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    shp_files = sorted(LANDUSE_DIR.rglob("*.shp"))
    file_rows = []
    sample_tables = []
    hit_tables = []
    feasibility_tables = []

    for shp in shp_files:
        gdf, encoding = read_shp(shp)
        cols = [col for col in gdf.columns if col != gdf.geometry.name]
        txt_cols = text_columns(gdf)
        hits = find_target_columns(gdf, txt_cols)
        samples = unique_samples(gdf, txt_cols)
        feasibility = clip_feasibility(gdf)

        rel = str(shp.relative_to(ROOT))
        file_rows.append(
            {
                "file": rel,
                "read_encoding": encoding,
                "crs": str(gdf.crs),
                "record_count": len(gdf),
                "geometry_type": ", ".join(sorted(gdf.geom_type.dropna().unique())),
                "bounds": ", ".join(f"{v:.3f}" for v in gdf.total_bounds),
                "columns": ", ".join(cols),
                "text_columns": ", ".join(txt_cols),
            }
        )
        samples.insert(0, "file", rel)
        sample_tables.append(samples)
        if not hits.empty:
            hits.insert(0, "file", rel)
        hit_tables.append(hits)
        feasibility.insert(0, "landuse_file", rel)
        feasibility_tables.append(feasibility)

    file_df = pd.DataFrame(file_rows)
    samples_df = pd.concat(sample_tables, ignore_index=True) if sample_tables else pd.DataFrame()
    hits_df = pd.concat(hit_tables, ignore_index=True) if hit_tables else pd.DataFrame()
    feasibility_df = (
        pd.concat(feasibility_tables, ignore_index=True) if feasibility_tables else pd.DataFrame()
    )

    if hits_df.empty:
        target_judgement = "지정한 용도지역 명칭이 포함된 문자형 컬럼을 찾지 못했다."
    else:
        target_cols = ", ".join(sorted(hits_df["column"].unique()))
        target_judgement = f"지정한 용도지역 명칭이 포함된 컬럼: {target_cols}"

    clip_possible = (
        not hits_df.empty
        and not feasibility_df.empty
        and bool(feasibility_df["intersects"].all())
    )
    if clip_possible:
        clip_judgement = "판교/위례 분석 경계와 공간적으로 교차하며 용도지역 컬럼도 확인되어 구성비 계산이 가능하다."
    elif hits_df.empty:
        clip_judgement = "공간 clip은 별도 검토 가능하지만 용도지역 명칭 컬럼이 확인되지 않아 구성비 계산 기준 컬럼을 먼저 확정해야 한다."
    else:
        clip_judgement = "용도지역 컬럼은 확인됐지만 일부 분석 경계와 공간 교차가 확인되지 않아 현재 파일 범위를 확인해야 한다."

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = f"""# 경기용도지역 SHP 컬럼 점검 보고서

## 작업 개요

- 조사 폴더: `경기용도지역`
- 발견된 SHP 파일 수: {len(shp_files)}
- 목표: 용도지역 명칭이 들어 있는 컬럼을 찾고 판교/위례 분석 경계와 clip하여 구성비 계산이 가능한지 판단

## SHP 파일 목록 및 기본 정보

{markdown_table(file_df, max_rows=50)}

## 전체 컬럼명

{chr(10).join(f"- `{row['file']}`: {row['columns']}" for _, row in file_df.iterrows()) if not file_df.empty else "(없음)"}

## 문자형 컬럼 고유값 샘플

{markdown_table(samples_df, max_rows=100)}

## 지정 용도지역 값 포함 컬럼 확인

검색 값:

{chr(10).join(f"- {value}" for value in TARGET_VALUES)}

### 검색 결과

{markdown_table(hits_df, max_rows=100)}

판단: {target_judgement}

## 판교/위례 분석 경계와 Clip 가능성

{markdown_table(feasibility_df, max_rows=50)}

판단: {clip_judgement}

## 다음 단계

- 용도지역 컬럼이 확인되면 `geopandas.overlay(..., how="intersection")` 방식으로 분석 경계와 교차 면적을 계산한다.
- 면적은 EPSG:5186에서 계산하고, `용도지역별 교차면적 / 분석경계 전체면적`으로 구성비를 산출한다.
- 공간 교차가 없으면 경기용도지역 파일이 판교/위례 위치를 포함하는지, 또는 행정구역/시군 단위 파일이 누락됐는지 확인한다.
"""
    REPORT_PATH.write_text(report, encoding="utf-8-sig")

    print(f"shp_files={len(shp_files)}")
    print(f"target_columns={', '.join(sorted(hits_df['column'].unique())) if not hits_df.empty else ''}")
    print(f"clip_possible={clip_possible}")
    print(f"report={REPORT_PATH}")


if __name__ == "__main__":
    main()
