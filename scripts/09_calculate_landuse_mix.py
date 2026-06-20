from __future__ import annotations

from pathlib import Path
import math
import warnings

import geopandas as gpd
import pandas as pd
from shapely import make_valid


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "derived_data" / "01_landuse_mix"
REPORT = OUT_DIR / "landuse_mix_report.md"

PANGYO_BOUNDARY = ROOT / "derived_data" / "00_boundaries" / "pangyo_boundary_user_drawn2_5186.geojson"
WIRYE_BOUNDARY = ROOT / "derived_data" / "00_boundaries" / "wirye_boundary.geojson"
PARCELS = ROOT / "가구및획지" / "the_geom.shp"
SEOUL_ZONING_DIR = ROOT / "서울용도지역"
GYEONGGI_ZONING_DIR = ROOT / "경기용도지역"
AREA_CRS = "EPSG:5186"

AREA_NAMES = {
    "pangyo": "pangyo_1st_technovalley",
    "wirye": "wirye_plan_area",
}

ZONE_NAME_CANDIDATES = [
    "DGM_NM",
    "dgm_nm",
    "UQ_NM",
    "uq_nm",
    "ZONE_NM",
    "zoneName",
    "용도지역명",
]


def read_file(path: Path, **kwargs) -> gpd.GeoDataFrame:
    last_error: Exception | None = None
    for enc in ["cp949", "euc-kr", "utf-8", None]:
        try:
            if enc:
                return gpd.read_file(path, encoding=enc, **kwargs)
            return gpd.read_file(path, **kwargs)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError(f"failed to read {path}: {last_error}")


def clean_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf = gdf.copy()
    gdf = gdf[~gdf.geometry.isna()].copy()
    gdf["geometry"] = gdf.geometry.apply(make_valid)
    gdf = gdf[~gdf.geometry.is_empty].copy()
    return gdf


def to_area_crs(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        raise ValueError("CRS is missing")
    return gdf.to_crs(AREA_CRS)


def find_zone_column(columns: list[str]) -> str | None:
    by_lower = {c.lower(): c for c in columns}
    for cand in ZONE_NAME_CANDIDATES:
        if cand in columns:
            return cand
        if cand.lower() in by_lower:
            return by_lower[cand.lower()]
    for col in columns:
        lower = col.lower()
        if "dgm" in lower and "nm" in lower:
            return col
        if "zone" in lower and "nm" in lower:
            return col
    return None


def read_boundary(path: Path) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    gdf = clean_geometries(to_area_crs(gdf))
    gdf["area_sqm"] = gdf.geometry.area
    return gdf[["area_sqm", "geometry"]]


def list_shps(folder: Path) -> list[Path]:
    return sorted(folder.rglob("*.shp"))


def clip_one_zoning_file(path: Path, boundary: gpd.GeoDataFrame, area_name: str, source_group: str) -> tuple[gpd.GeoDataFrame, dict]:
    meta = {
        "file": str(path.relative_to(ROOT)),
        "source_group": source_group,
        "original_crs": "",
        "zone_column": "",
        "read_rows": 0,
        "clipped_rows": 0,
        "status": "ok",
        "message": "",
    }
    try:
        gdf = read_file(path)
        meta["read_rows"] = len(gdf)
        meta["original_crs"] = str(gdf.crs)
        zone_col = find_zone_column(list(gdf.columns))
        if zone_col is None:
            meta["status"] = "skipped"
            meta["message"] = "용도지역명 컬럼 후보를 찾지 못함"
            return gpd.GeoDataFrame(columns=["area_name", "landuse_category", "source_layer", "source_group", "geometry"], crs=AREA_CRS), meta
        meta["zone_column"] = zone_col
        gdf = clean_geometries(to_area_crs(gdf))
        if gdf.empty:
            meta["clipped_rows"] = 0
            return gpd.GeoDataFrame(columns=["area_name", "landuse_category", "source_layer", "source_group", "geometry"], crs=AREA_CRS), meta
        clipped = gpd.overlay(
            gdf[[zone_col, "geometry"]],
            boundary[["geometry"]],
            how="intersection",
            keep_geom_type=False,
        )
        clipped = clean_geometries(clipped)
        if clipped.empty:
            meta["clipped_rows"] = 0
            return gpd.GeoDataFrame(columns=["area_name", "landuse_category", "source_layer", "source_group", "geometry"], crs=AREA_CRS), meta
        clipped["area_name"] = area_name
        clipped["landuse_category"] = clipped[zone_col].fillna("미분류").astype(str).str.strip()
        clipped.loc[clipped["landuse_category"].eq(""), "landuse_category"] = "미분류"
        clipped["source_layer"] = str(path.relative_to(ROOT))
        clipped["source_group"] = source_group
        clipped = clipped[["area_name", "landuse_category", "source_layer", "source_group", "geometry"]]
        meta["clipped_rows"] = len(clipped)
        return clipped, meta
    except Exception as exc:  # noqa: BLE001
        meta["status"] = "error"
        meta["message"] = str(exc)
        return gpd.GeoDataFrame(columns=["area_name", "landuse_category", "source_layer", "source_group", "geometry"], crs=AREA_CRS), meta


def clip_zoning_for_area(
    area_name: str,
    boundary: gpd.GeoDataFrame,
    folders: list[tuple[Path, str]],
) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    clips: list[gpd.GeoDataFrame] = []
    metas: list[dict] = []
    for folder, source_group in folders:
        for shp in list_shps(folder):
            clipped, meta = clip_one_zoning_file(shp, boundary, area_name, source_group)
            metas.append(meta)
            if not clipped.empty:
                clips.append(clipped)
    if clips:
        out = pd.concat(clips, ignore_index=True)
        out = gpd.GeoDataFrame(out, geometry="geometry", crs=AREA_CRS)
    else:
        out = gpd.GeoDataFrame(columns=["area_name", "landuse_category", "source_layer", "source_group", "geometry"], crs=AREA_CRS)
    return out, pd.DataFrame(metas)


def remove_exact_zoning_duplicates(gdf: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, int]:
    if gdf.empty:
        return gdf, 0
    work = gdf.copy()
    work["geom_key"] = work.geometry.normalize().to_wkb(hex=True)
    before = len(work)
    work = work.drop_duplicates(subset=["area_name", "landuse_category", "geom_key"]).copy()
    removed = before - len(work)
    return work.drop(columns=["geom_key"]), removed


def composition(
    gdf: gpd.GeoDataFrame,
    area_col: str,
    category_col: str,
    extra_cols: list[str] | None = None,
) -> pd.DataFrame:
    if gdf.empty:
        cols = ["area_name", category_col, "area_sqm", "area_ha", "area_ratio"]
        if extra_cols:
            cols = ["area_name", *extra_cols, category_col, "area_sqm", "area_ha", "area_ratio"]
        return pd.DataFrame(columns=cols)
    work = gdf.copy()
    work[area_col] = work.geometry.area
    group_cols = ["area_name", category_col] if not extra_cols else ["area_name", *extra_cols, category_col]
    out = work.groupby(group_cols, dropna=False)[area_col].sum().reset_index()
    out = out.rename(columns={area_col: "area_sqm"})
    totals = out.groupby("area_name")["area_sqm"].transform("sum")
    out["area_ha"] = out["area_sqm"] / 10000
    out["area_ratio"] = out["area_sqm"] / totals
    return out.sort_values(["area_name", "area_ratio"], ascending=[True, False])


def lum_from_composition(comp: pd.DataFrame, category_col: str, basis: str, notes: dict[str, str] | None = None) -> pd.DataFrame:
    rows: list[dict] = []
    notes = notes or {}
    for area_name, grp in comp.groupby("area_name"):
        positive = grp[grp["area_sqm"] > 0].copy()
        total = positive["area_sqm"].sum()
        n = len(positive[category_col].dropna().unique())
        if n <= 1 or total <= 0:
            lum = 0.0
        else:
            p = positive["area_sqm"] / total
            lum = float(-(p * p.apply(math.log)).sum() / math.log(n))
        rows.append(
            {
                "area_name": area_name,
                "basis": basis,
                "category_count": n,
                "total_area_sqm": total,
                "lum_index": lum,
                "note": notes.get(area_name, ""),
            }
        )
    return pd.DataFrame(rows)


def clip_blocktypes(boundaries: dict[str, gpd.GeoDataFrame]) -> tuple[gpd.GeoDataFrame, dict]:
    parcels = read_file(PARCELS)
    original_crs = str(parcels.crs)
    parcels = clean_geometries(to_area_crs(parcels))
    parcels["blockType"] = parcels["blockType"].fillna("미분류").astype(str).str.strip()
    parcels.loc[parcels["blockType"].eq(""), "blockType"] = "미분류"
    outputs: list[gpd.GeoDataFrame] = []
    for area_name, boundary in boundaries.items():
        minx, miny, maxx, maxy = boundary.total_bounds
        cand = parcels.cx[minx:maxx, miny:maxy].copy()
        clipped = gpd.overlay(cand[["blockType", "geometry"]], boundary[["geometry"]], how="intersection", keep_geom_type=False)
        clipped = clean_geometries(clipped)
        clipped["area_name"] = area_name
        clipped["area_sqm"] = clipped.geometry.area
        clipped["area_ha"] = clipped["area_sqm"] / 10000
        outputs.append(clipped[["area_name", "blockType", "area_sqm", "area_ha", "geometry"]])
    out = pd.concat(outputs, ignore_index=True)
    return gpd.GeoDataFrame(out, geometry="geometry", crs=AREA_CRS), {"file": str(PARCELS.relative_to(ROOT)), "original_crs": original_crs}


def md_table(df: pd.DataFrame, max_rows: int = 30) -> str:
    if df.empty:
        return "(없음)"
    work = df.head(max_rows).copy()
    for col in work.columns:
        if pd.api.types.is_float_dtype(work[col]):
            work[col] = work[col].map(lambda x: f"{x:.6f}")
    lines = [
        "| " + " | ".join(work.columns) + " |",
        "| " + " | ".join("---" for _ in work.columns) + " |",
    ]
    for row in work.fillna("").astype(str).values.tolist():
        lines.append("| " + " | ".join(v.replace("|", "\\|") for v in row) + " |")
    if len(df) > max_rows:
        lines.append(f"\n총 {len(df)}행 중 {max_rows}행만 표시.")
    return "\n".join(lines)


def write_report(
    boundary_areas: pd.DataFrame,
    zoning_meta: pd.DataFrame,
    zone_comp: pd.DataFrame,
    zone_lum: pd.DataFrame,
    block_comp: pd.DataFrame,
    block_lum: pd.DataFrame,
    block_meta: dict,
    duplicate_removed: int,
    wirye_ratio_before: float,
    wirye_ratio_after: float,
    warnings_list: list[str],
) -> None:
    used_zoning = zoning_meta[zoning_meta["clipped_rows"] > 0].copy()
    zone_columns = (
        zoning_meta[zoning_meta["zone_column"].astype(str).ne("")]
        .groupby(["source_group", "zone_column"])
        .size()
        .reset_index(name="file_count")
    )
    report = f"""# 토지이용 구성비 및 토지이용혼합도(LUM) 보고서

## 1. 작업 목적

판교 제1테크노밸리와 위례 계획구역의 토지이용 구조를 비교하기 위해 용도지역별 면적·면적비, 용도지역 기준 LUM, 가구획지 `blockType`별 면적·면적비, `blockType` 기준 보조 LUM을 산출했다.

이번 작업에서는 토지이용 관련 파생지표만 계산했다. 개발 실현 정도, 건축물대장, SGIS, 접근성, 역세권, 산업특화도, 업무시설밀도는 계산하지 않았다.

## 2. 사용한 분석경계 파일

- 판교: `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson`
- 위례: `derived_data/00_boundaries/wirye_boundary.geojson`
- 내부 필지 파일은 최종 clip 기준으로 사용하지 않았다.

## 3. 사용한 용도지역 원천 파일 목록

{md_table(used_zoning[["source_group", "file", "original_crs", "zone_column", "clipped_rows"]], 80)}

## 4. 사용한 가구획지 파일

- `{block_meta["file"]}`

## 5. 각 데이터의 CRS

### 경계 CRS 및 면적

{md_table(boundary_areas)}

### 용도지역 원천 CRS 요약

{md_table(zoning_meta.groupby(["source_group", "original_crs"]).size().reset_index(name="file_count"))}

### 가구획지 CRS

- 원래 CRS: `{block_meta["original_crs"]}`

## 6. 면적 계산 CRS

- `{AREA_CRS}`

## 7. 용도지역명으로 사용한 컬럼명

{md_table(zone_columns)}

## 8. blockType 기준 보조 LUM 산출 방식

`가구및획지/the_geom.shp`를 `pangyo_boundary_user_drawn2_5186.geojson`, `wirye_boundary.geojson`으로 각각 intersection한 뒤, `blockType`별 clip 면적비를 기준으로 LUM을 계산했다. `blockType` 결측 또는 공백은 `미분류`로 처리했다.

## 9. 판교 분석경계 면적

- `{boundary_areas.loc[boundary_areas["area_name"].eq("pangyo_1st_technovalley"), "boundary_area_sqm"].iloc[0]:,.3f}㎡`

## 10. 위례 분석경계 면적

- `{boundary_areas.loc[boundary_areas["area_name"].eq("wirye_plan_area"), "boundary_area_sqm"].iloc[0]:,.3f}㎡`

## 11. 판교 용도지역 구성비 요약

{md_table(zone_comp[zone_comp["area_name"].eq("pangyo_1st_technovalley")][["landuse_category", "area_sqm", "area_ha", "area_ratio"]])}

## 12. 위례 용도지역 구성비 요약

{md_table(zone_comp[zone_comp["area_name"].eq("wirye_plan_area")][["landuse_category", "area_sqm", "area_ha", "area_ratio"]])}

## 13. 판교 용도지역 기준 LUM

{md_table(zone_lum[zone_lum["area_name"].eq("pangyo_1st_technovalley")])}

## 14. 위례 용도지역 기준 LUM

{md_table(zone_lum[zone_lum["area_name"].eq("wirye_plan_area")])}

## 15. 판교 blockType 기준 LUM

{md_table(block_lum[block_lum["area_name"].eq("pangyo_1st_technovalley")])}

## 16. 위례 blockType 기준 LUM

{md_table(block_lum[block_lum["area_name"].eq("wirye_plan_area")])}

## 17. 위례 서울/경기 용도지역 중복 여부

- 중복 제거 전 위례 용도지역 clip 면적 / 위례 경계 면적: `{wirye_ratio_before:.6f}`
- 중복 제거 후 위례 용도지역 clip 면적 / 위례 경계 면적: `{wirye_ratio_after:.6f}`
- 동일 `area_name` + `landuse_category` + geometry 기준으로 제거한 중복 feature 수: `{duplicate_removed}`

## 18. 중복 처리 방식

동일한 geometry와 동일 용도지역명이 중복된 경우만 제거했다. 면적 합계가 경계 면적을 크게 초과하는 경우 임의로 수치를 보정하지 않고 한계로 기록했다.

## 19. 결측 또는 미분류 처리 방식

- 용도지역명이 결측 또는 공백인 경우 `미분류`로 처리했다.
- `blockType`이 결측 또는 공백인 경우 `미분류`로 처리했다.

## 20. 한계점

- 용도지역 원천 파일은 여러 SHP로 분리되어 있고 서울 자료에는 KLIP/UPIS 계열이 함께 존재한다. 동일 geometry 중복은 제거했지만, 미세한 경계 차이로 인한 중첩은 완전히 제거하지 못할 수 있다.
- 위례의 서울/경기 용도지역 clip 면적 합계가 경계 면적과 차이 나는 경우, 행정경계 기반 분할 자료가 없으면 임의 보정하지 않았다.
- 용도지역 기준 LUM은 법정 용도지역 혼합도를 의미하며, 실제 건축물 이용이나 개발 실현 상태를 뜻하지 않는다.
- blockType 기준 LUM은 가구획지 용도 기반 보조지표이며, 메인 지표는 용도지역 SHP 기준 LUM이다.

## 오류 또는 주의사항

{chr(10).join(f"- {w}" for w in warnings_list) if warnings_list else "- 특이 오류 없음"}
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pangyo_boundary = read_boundary(PANGYO_BOUNDARY)
    wirye_boundary = read_boundary(WIRYE_BOUNDARY)
    boundaries = {
        AREA_NAMES["pangyo"]: pangyo_boundary,
        AREA_NAMES["wirye"]: wirye_boundary,
    }
    boundary_areas = pd.DataFrame(
        [
            {"area_name": AREA_NAMES["pangyo"], "boundary_file": str(PANGYO_BOUNDARY.relative_to(ROOT)), "original_crs": str(gpd.read_file(PANGYO_BOUNDARY).crs), "area_crs": AREA_CRS, "boundary_area_sqm": pangyo_boundary.geometry.area.sum()},
            {"area_name": AREA_NAMES["wirye"], "boundary_file": str(WIRYE_BOUNDARY.relative_to(ROOT)), "original_crs": str(gpd.read_file(WIRYE_BOUNDARY).crs), "area_crs": AREA_CRS, "boundary_area_sqm": wirye_boundary.geometry.area.sum()},
        ]
    )

    pangyo_zoning, pangyo_meta = clip_zoning_for_area(
        AREA_NAMES["pangyo"],
        pangyo_boundary,
        [(GYEONGGI_ZONING_DIR, "gyeonggi")],
    )
    wirye_zoning_raw, wirye_meta = clip_zoning_for_area(
        AREA_NAMES["wirye"],
        wirye_boundary,
        [(SEOUL_ZONING_DIR, "seoul"), (GYEONGGI_ZONING_DIR, "gyeonggi")],
    )

    wirye_boundary_area = float(wirye_boundary.geometry.area.sum())
    wirye_ratio_before = float(wirye_zoning_raw.geometry.area.sum() / wirye_boundary_area) if wirye_boundary_area else 0.0
    wirye_zoning, duplicate_removed = remove_exact_zoning_duplicates(wirye_zoning_raw)
    wirye_ratio_after = float(wirye_zoning.geometry.area.sum() / wirye_boundary_area) if wirye_boundary_area else 0.0

    zone_clipped = pd.concat([pangyo_zoning, wirye_zoning], ignore_index=True)
    zone_clipped = gpd.GeoDataFrame(zone_clipped, geometry="geometry", crs=AREA_CRS)
    zone_clipped["area_sqm"] = zone_clipped.geometry.area
    zone_clipped["area_ha"] = zone_clipped["area_sqm"] / 10000
    zone_clipped_out = zone_clipped[["area_name", "landuse_category", "source_layer", "area_sqm", "area_ha", "geometry"]].copy()

    zone_comp_raw = composition(zone_clipped, "clip_area_sqm", "landuse_category", extra_cols=["source_layer"])
    zone_comp = (
        zone_clipped.assign(calc_area_sqm=zone_clipped.geometry.area)
        .groupby(["area_name", "landuse_category"], dropna=False)["calc_area_sqm"]
        .sum()
        .reset_index()
        .rename(columns={"calc_area_sqm": "area_sqm"})
    )
    zone_comp["area_ha"] = zone_comp["area_sqm"] / 10000
    zone_comp["area_ratio"] = zone_comp["area_sqm"] / zone_comp.groupby("area_name")["area_sqm"].transform("sum")
    zone_comp = zone_comp.sort_values(["area_name", "area_ratio"], ascending=[True, False])
    zone_comp_output = zone_comp.merge(
        zone_clipped.groupby(["area_name", "landuse_category"])["source_layer"]
        .apply(lambda s: "; ".join(sorted(set(s))))
        .reset_index(),
        on=["area_name", "landuse_category"],
        how="left",
    )
    zone_comp_output = zone_comp_output[["area_name", "source_layer", "landuse_category", "area_sqm", "area_ha", "area_ratio"]]

    zone_notes = {}
    if wirye_ratio_after > 1.1:
        zone_notes[AREA_NAMES["wirye"]] = "위례 서울/경기 용도지역 clip 면적 합계가 경계 면적을 크게 초과하여 중복 가능성 있음. 동일 geometry 중복만 제거하고 임의 보정하지 않음."
    zone_lum = lum_from_composition(zone_comp, "landuse_category", "zoning", zone_notes)

    block_clipped, block_meta = clip_blocktypes(boundaries)
    block_comp = (
        block_clipped.groupby(["area_name", "blockType"], dropna=False)["area_sqm"]
        .sum()
        .reset_index()
    )
    block_comp["area_ha"] = block_comp["area_sqm"] / 10000
    block_comp["area_ratio"] = block_comp["area_sqm"] / block_comp.groupby("area_name")["area_sqm"].transform("sum")
    block_comp = block_comp.sort_values(["area_name", "area_ratio"], ascending=[True, False])
    block_lum = lum_from_composition(block_comp, "blockType", "blockType")

    warnings_list: list[str] = []
    warnings_list.append(
        "일부 서울/경기 용도지역 SHP에서 polygon ring winding order 경고가 발생했으며 pyogrio가 자동 보정하여 읽었음. 면적 계산 전 make_valid를 적용했지만 원천 geometry 정비가 필요할 수 있음."
    )
    error_meta = pd.concat([pangyo_meta, wirye_meta], ignore_index=True)
    for _, row in error_meta[error_meta["status"].isin(["error", "skipped"])].iterrows():
        warnings_list.append(f"{row['file']}: {row['status']} - {row['message']}")
    if wirye_ratio_after > 1.1:
        warnings_list.append(f"위례 용도지역 면적 합계 / 위례 경계 면적 비율이 {wirye_ratio_after:.3f}로 100%를 크게 초과함. 동일 geometry 중복 {duplicate_removed}개만 제거했고 임의 보정하지 않음.")
    if wirye_ratio_after < 0.9:
        warnings_list.append(f"위례 용도지역 면적 합계 / 위례 경계 면적 비율이 {wirye_ratio_after:.3f}로 100%보다 낮음. 용도지역 자료가 경계 전체를 덮지 못할 수 있음.")

    zone_comp_output.to_csv(OUT_DIR / "landuse_zone_composition.csv", index=False, encoding="utf-8-sig")
    zone_lum.to_csv(OUT_DIR / "landuse_mix_index.csv", index=False, encoding="utf-8-sig")
    block_comp.to_csv(OUT_DIR / "landuse_blocktype_composition.csv", index=False, encoding="utf-8-sig")
    block_lum.to_csv(OUT_DIR / "landuse_blocktype_mix_index.csv", index=False, encoding="utf-8-sig")
    zone_clipped_out.to_file(OUT_DIR / "landuse_zones_clipped.geojson", driver="GeoJSON")
    block_clipped[["area_name", "blockType", "area_sqm", "area_ha", "geometry"]].to_file(
        OUT_DIR / "landuse_blocktype_clipped.geojson",
        driver="GeoJSON",
    )

    write_report(
        boundary_areas,
        pd.concat([pangyo_meta, wirye_meta], ignore_index=True),
        zone_comp,
        zone_lum,
        block_comp,
        block_lum,
        block_meta,
        duplicate_removed,
        wirye_ratio_before,
        wirye_ratio_after,
        warnings_list,
    )

    print("생성된 파일 목록")
    for p in [
        "landuse_zone_composition.csv",
        "landuse_mix_index.csv",
        "landuse_blocktype_composition.csv",
        "landuse_blocktype_mix_index.csv",
        "landuse_zones_clipped.geojson",
        "landuse_blocktype_clipped.geojson",
        "landuse_mix_report.md",
    ]:
        print(f"- {OUT_DIR / p}")
    print("\n판교 용도지역별 면적비 상위 5개")
    print(zone_comp[zone_comp["area_name"].eq(AREA_NAMES["pangyo"])][["landuse_category", "area_sqm", "area_ratio"]].head(5).to_string(index=False))
    print("\n위례 용도지역별 면적비 상위 5개")
    print(zone_comp[zone_comp["area_name"].eq(AREA_NAMES["wirye"])][["landuse_category", "area_sqm", "area_ratio"]].head(5).to_string(index=False))
    print("\nLUM")
    print(zone_lum.to_string(index=False))
    print(block_lum.to_string(index=False))
    print(f"\n위례 용도지역 면적 합계 / 위례 경계 면적 비율: {wirye_ratio_after:.6f}")
    print("\n오류 또는 주의사항")
    if warnings_list:
        for w in warnings_list:
            print(f"- {w}")
    else:
        print("- 특이 오류 없음")


if __name__ == "__main__":
    main()
