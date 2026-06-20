from __future__ import annotations

from pathlib import Path
import math

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
import pyogrio
from shapely import make_valid


ROOT = Path(__file__).resolve().parents[1]
AREA_CRS = "EPSG:5186"
LANDUSE_DIR = ROOT / "derived_data" / "01_landuse_mix"
VALIDATION_DIR = ROOT / "derived_data" / "01_landuse_validation"

PANGYO_BOUNDARY = ROOT / "derived_data" / "00_boundaries" / "pangyo_boundary_user_drawn2_5186.geojson"
WIRYE_BOUNDARY = ROOT / "derived_data" / "00_boundaries" / "wirye_boundary.geojson"

TITLE_FONT = "Malgun Gothic"

AREA_KEYS = {
    "pangyo": "pangyo_1st_technovalley",
    "wirye": "wirye_plan_area",
}

ZONE_COLORS = {
    "준주거지역": "#eec245",
    "자연녹지지역": "#409a58",
    "보전녹지지역": "#7ec25e",
    "제1종전용주거지역": "#267e48",
    "제1종일반주거지역": "#60b07a",
    "제2종일반주거지역": "#97a4b0",
    "제2종일반주거지역(7층이하)": "#ec8b48",
    "제2종일반주거지역(7층)": "#f3a958",
    "제3종일반주거지역": "#f7b967",
    "일반상업지역": "#fac574",
    "근린상업지역": "#f8cb78",
    "중심상업지역": "#fada94",
    "개발제한구역": "#ca4e61",
    "장지 도시자연공원구역": "#db6c56",
    "계획관리지역": "#9db77d",
    "생산관리지역": "#7ea85e",
    "보전관리지역": "#6f8f57",
    "관리지역미분류": "#93a06b",
    "농림지역": "#89a85e",
    "자연환경보전지역": "#76965e",
    "비도시지역": "#b6c3cd",
    "기타 도시지역": "#a74f8f",
    "미분류": "#b0b8c1",
    "기타": "#7566ac",
}


def set_korean_font() -> None:
    plt.rcParams["font.family"] = TITLE_FONT
    plt.rcParams["axes.unicode_minus"] = False


def read_boundary(path: Path) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        raise ValueError(f"CRS missing: {path}")
    gdf = gdf.to_crs(AREA_CRS)
    gdf["geometry"] = gdf.geometry.apply(make_valid)
    return gdf[~gdf.geometry.isna() & ~gdf.geometry.is_empty].copy()


def read_zoning_shp(path: Path) -> gpd.GeoDataFrame:
    gdf = pyogrio.read_dataframe(path, encoding="cp949")
    zone_col = "DGM_NM" if "DGM_NM" in gdf.columns else "dgm_nm"
    code_col = "SIGNGU_SE" if "SIGNGU_SE" in gdf.columns else "sgg_cd"
    gdf = gdf[[zone_col, code_col, "geometry"]].rename(columns={zone_col: "landuse_category", code_col: "signgu_code"})
    gdf = gdf.to_crs(AREA_CRS)
    gdf["geometry"] = gdf.geometry.apply(make_valid)
    gdf = gdf[~gdf.geometry.isna() & ~gdf.geometry.is_empty].copy()
    gdf["landuse_category"] = gdf["landuse_category"].fillna("미분류").astype(str).str.strip()
    gdf.loc[gdf["landuse_category"].eq(""), "landuse_category"] = "미분류"
    gdf["signgu_code"] = gdf["signgu_code"].fillna("").astype(str).str.strip()
    return gdf


def load_zoning_dataset(folder_suffix: str) -> tuple[gpd.GeoDataFrame, list[Path]]:
    folder = next(path for path in ROOT.iterdir() if path.is_dir() and path.name.endswith(folder_suffix))
    shp_files = sorted(folder.glob("UPIS_C_UQ11*.shp"))
    frames = [read_zoning_shp(path) for path in shp_files]
    gdf = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), geometry="geometry", crs=AREA_CRS)
    gdf["source_layer"] = gdf.get("source_layer", "")
    return gdf, shp_files


def overlay_clip(zones: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame, area_key: str, source_version: str) -> gpd.GeoDataFrame:
    clipped = gpd.overlay(zones, boundary[["geometry"]], how="intersection", keep_geom_type=False)
    clipped = clipped[~clipped.geometry.isna() & ~clipped.geometry.is_empty].copy()
    clipped["area_name"] = area_key
    clipped["source_version"] = source_version
    clipped["area_sqm"] = clipped.geometry.area
    clipped["area_ha"] = clipped["area_sqm"] / 10000
    return clipped


def compute_missing(boundary: gpd.GeoDataFrame, covered: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, float]:
    boundary_area = boundary.geometry.area.sum()
    if covered.empty:
        missing = boundary.copy()
        missing["area_sqm"] = missing.geometry.area
        return missing, boundary_area
    union_geom = covered.geometry.union_all()
    missing = gpd.overlay(
        boundary[["geometry"]],
        gpd.GeoDataFrame(geometry=[union_geom], crs=AREA_CRS),
        how="difference",
    )
    missing = missing[~missing.geometry.isna() & ~missing.geometry.is_empty].copy()
    missing["area_sqm"] = missing.geometry.area
    return missing, float(boundary_area - union_geom.area)


def composition_rows(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    if gdf.empty:
        return pd.DataFrame(columns=["area_name", "source_layer", "source_version", "landuse_category", "area_sqm", "area_ha", "area_ratio"])
    grouped = (
        gdf.groupby(["area_name", "landuse_category"], dropna=False)
        .agg(
            area_sqm=("area_sqm", "sum"),
            source_layer=("source_layer", lambda s: "; ".join(sorted(set(str(v) for v in s if str(v))))),
            source_version=("source_version", lambda s: "; ".join(sorted(set(str(v) for v in s if str(v))))),
        )
        .reset_index()
    )
    grouped["area_ha"] = grouped["area_sqm"] / 10000
    grouped["area_ratio"] = grouped["area_sqm"] / grouped.groupby("area_name")["area_sqm"].transform("sum")
    return grouped.sort_values(["area_name", "area_ratio"], ascending=[True, False])


def lum_from_composition(comp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for area_name, grp in comp.groupby("area_name"):
        total = grp["area_sqm"].sum()
        n = len(grp["landuse_category"].dropna().unique())
        if total <= 0 or n <= 1:
            lum = 0.0
        else:
            p = grp["area_sqm"] / total
            lum = float(-(p * p.apply(math.log)).sum() / math.log(n))
        rows.append({
            "area_name": area_name,
            "basis": "zoning",
            "category_count": n,
            "total_area_sqm": total,
            "lum_index": lum,
            "note": "",
        })
    return pd.DataFrame(rows)


def md_table(df: pd.DataFrame, float_digits: int = 6) -> str:
    if df.empty:
        return "(없음)"
    work = df.copy()
    for col in work.columns:
        if pd.api.types.is_float_dtype(work[col]):
            work[col] = work[col].map(lambda x: f"{x:.{float_digits}f}")
    lines = [
        "| " + " | ".join(work.columns) + " |",
        "| " + " | ".join("---" for _ in work.columns) + " |",
    ]
    for row in work.fillna("").astype(str).values.tolist():
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |")
    return "\n".join(lines)


def top_categories(gdf: gpd.GeoDataFrame, n: int = 10) -> list[str]:
    if gdf.empty:
        return []
    return gdf.groupby("landuse_category")["area_sqm"].sum().sort_values(ascending=False).head(n).index.tolist()


def plot_final_map(title: str, gdf: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame, out_path: Path) -> None:
    keep = top_categories(gdf, 10)
    plot_df = gdf.copy()
    plot_df["display_category"] = plot_df["landuse_category"].where(plot_df["landuse_category"].isin(keep), "기타")
    cats = keep + (["기타"] if (~plot_df["landuse_category"].isin(keep)).any() else [])
    fig, ax = plt.subplots(figsize=(9, 9))
    for cat in cats:
        subset = plot_df[plot_df["display_category"] == cat]
        if subset.empty:
            continue
        subset.plot(ax=ax, color=ZONE_COLORS.get(cat, ZONE_COLORS["기타"]), edgecolor="#222222", linewidth=0.35)
    boundary.plot(ax=ax, facecolor="none", edgecolor="#111111", linewidth=2.0)
    ax.set_title(title, fontsize=16, pad=14)
    ax.set_axis_off()
    patches = [Patch(facecolor=ZONE_COLORS.get(cat, ZONE_COLORS["기타"]), edgecolor="#222222", label=cat) for cat in cats]
    ax.legend(handles=patches, title="용도지역", loc="lower left", fontsize=9, title_fontsize=10, frameon=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_wirye_coverage(boundary: gpd.GeoDataFrame, original_2024_01: gpd.GeoDataFrame, gapfill_2024_02: gpd.GeoDataFrame, missing: gpd.GeoDataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 9))
    if not original_2024_01.empty:
        gpd.GeoDataFrame(geometry=[original_2024_01.geometry.union_all()], crs=AREA_CRS).plot(ax=ax, color="#7ba6d9", edgecolor="#557aa5", linewidth=0.5)
    if not gapfill_2024_02.empty:
        gpd.GeoDataFrame(geometry=[gapfill_2024_02.geometry.union_all()], crs=AREA_CRS).plot(ax=ax, color="#efb36b", edgecolor="#b97125", linewidth=0.5)
    if not missing.empty:
        missing.plot(ax=ax, color="#f2d7d7", edgecolor="#b85c5c", linewidth=0.7)
    boundary.plot(ax=ax, facecolor="none", edgecolor="#111111", linewidth=2.0)
    ax.set_title("위례 2024 조합 용도지역 coverage", fontsize=16, pad=14)
    ax.set_axis_off()
    patches = [
        Patch(facecolor="#7ba6d9", edgecolor="#557aa5", label="용도지역2 원본"),
        Patch(facecolor="#efb36b", edgecolor="#b97125", label="용도지역3 보완"),
        Patch(facecolor="#f2d7d7", edgecolor="#b85c5c", label="데이터 없음"),
    ]
    ax.legend(handles=patches, loc="lower left", fontsize=10, frameon=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def build_preprocessing_note() -> str:
    return "\n".join([
        "- 용도지역 분석은 2024년 1월 갱신본인 `용도지역2`를 기본 자료로 사용하였다.",
        "- 판교 제1테크노밸리는 `용도지역2`만으로 분석경계를 전부 덮어 해당 자료만 사용하였다.",
        "- 위례 계획구역은 `용도지역2`를 기본으로 사용하고, 이 자료가 덮지 못하는 결측 구역 일부를 2024년 2월 갱신본인 `용도지역3`으로 보완하였다.",
        "- `용도지역2`와 `용도지역3`은 결측 구역에 대해서만 순차적으로 적용했으며, 중복 면적은 허용하지 않았다.",
        "- 그래도 남는 결측 구역은 `데이터 없음`으로 유지하였다.",
        "- 따라서 용도지역 분석은 서로 다른 2024년 1월/2월 자료를 조합한 결과이며, 기준시점 차이와 잔여 결측 가능성은 데이터 한계로 해석해야 한다.",
        "- 기존 2026년 용도지역 자료는 최종 용도지역 갱신 기준에는 사용하지 않았다.",
    ])


def main() -> None:
    set_korean_font()
    LANDUSE_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    old_mix = pd.read_csv(ROOT / "public" / "data" / "landuse_mix_index.csv")
    old_comp = pd.read_csv(ROOT / "public" / "data" / "landuse_zone_composition.csv")
    old_geo = gpd.read_file(ROOT / "public" / "data" / "landuse_zones.geojson").to_crs(AREA_CRS)
    old_geo["geometry"] = old_geo.geometry.apply(make_valid)

    pangyo_old = old_geo[old_geo["area_name"] == AREA_KEYS["pangyo"]].copy()
    wirye_old = old_geo[old_geo["area_name"] == AREA_KEYS["wirye"]].copy()

    zoning2, zoning2_files = load_zoning_dataset("2")
    zoning3, zoning3_files = load_zoning_dataset("3")

    pangyo_boundary = read_boundary(PANGYO_BOUNDARY)
    wirye_boundary = read_boundary(WIRYE_BOUNDARY)

    # Pangyo: zoning2 only
    pangyo_clip = overlay_clip(zoning2, pangyo_boundary, AREA_KEYS["pangyo"], "2024_01_original")
    pangyo_clip["source_layer"] = "용도지역2"
    pangyo_missing, pangyo_missing_area = compute_missing(pangyo_boundary, pangyo_clip)
    pangyo_missing["area_name"] = AREA_KEYS["pangyo"]
    pangyo_missing["landuse_category"] = "데이터 없음"
    pangyo_missing["source_layer"] = "none"
    pangyo_missing["source_version"] = "no_data"

    # Wirye: zoning2 base + zoning3 gap fill only
    wirye_base = overlay_clip(zoning2, wirye_boundary, AREA_KEYS["wirye"], "2024_01_original")
    wirye_base["source_layer"] = "용도지역2"
    wirye_missing_stage1, _ = compute_missing(wirye_boundary, wirye_base)

    if wirye_missing_stage1.empty:
        wirye_gapfill = gpd.GeoDataFrame(columns=wirye_base.columns, geometry="geometry", crs=AREA_CRS)
    else:
        wirye_gapfill = gpd.overlay(zoning3, wirye_missing_stage1[["geometry"]], how="intersection", keep_geom_type=False)
        wirye_gapfill = wirye_gapfill[~wirye_gapfill.geometry.isna() & ~wirye_gapfill.geometry.is_empty].copy()
        wirye_gapfill["area_name"] = AREA_KEYS["wirye"]
        wirye_gapfill["source_version"] = "2024_02_gap_fill"
        wirye_gapfill["source_layer"] = "용도지역3"
        wirye_gapfill["area_sqm"] = wirye_gapfill.geometry.area
        wirye_gapfill["area_ha"] = wirye_gapfill["area_sqm"] / 10000

    wirye_combined = pd.concat([wirye_base, wirye_gapfill], ignore_index=True)
    wirye_combined = gpd.GeoDataFrame(wirye_combined, geometry="geometry", crs=AREA_CRS)
    wirye_missing_final, wirye_missing_area = compute_missing(wirye_boundary, wirye_combined)
    wirye_missing_final["area_name"] = AREA_KEYS["wirye"]
    wirye_missing_final["landuse_category"] = "데이터 없음"
    wirye_missing_final["source_layer"] = "none"
    wirye_missing_final["source_version"] = "no_data"

    final_landuse = pd.concat([pangyo_clip, wirye_combined], ignore_index=True)
    final_landuse = gpd.GeoDataFrame(final_landuse, geometry="geometry", crs=AREA_CRS)

    # Outputs
    composition = composition_rows(final_landuse)
    mix_index = lum_from_composition(composition)

    # Preserve blocktype files, overwrite zoning files only
    final_landuse.to_file(LANDUSE_DIR / "landuse_zones_clipped.geojson", driver="GeoJSON")
    composition.to_csv(LANDUSE_DIR / "landuse_zone_composition.csv", index=False, encoding="utf-8-sig")
    mix_index.to_csv(LANDUSE_DIR / "landuse_mix_index.csv", index=False, encoding="utf-8-sig")

    coverage_summary = pd.DataFrame([
        {
            "area_name": AREA_KEYS["pangyo"],
            "coverage_ratio": pangyo_clip.geometry.union_all().area / pangyo_boundary.geometry.area.sum() if not pangyo_clip.empty else 0.0,
            "missing_area_sqm": pangyo_missing_area,
            "source_2024_01_area_sqm": pangyo_clip["area_sqm"].sum() if not pangyo_clip.empty else 0.0,
            "source_2024_02_area_sqm": 0.0,
        },
        {
            "area_name": AREA_KEYS["wirye"],
            "coverage_ratio": wirye_combined.geometry.union_all().area / wirye_boundary.geometry.area.sum() if not wirye_combined.empty else 0.0,
            "missing_area_sqm": wirye_missing_area,
            "source_2024_01_area_sqm": wirye_base["area_sqm"].sum() if not wirye_base.empty else 0.0,
            "source_2024_02_area_sqm": wirye_gapfill["area_sqm"].sum() if not wirye_gapfill.empty else 0.0,
        },
    ])
    coverage_summary.to_csv(LANDUSE_DIR / "landuse_zone_coverage_summary.csv", index=False, encoding="utf-8-sig")

    missing_geo = pd.concat([pangyo_missing, wirye_missing_final], ignore_index=True)
    missing_geo = gpd.GeoDataFrame(missing_geo, geometry="geometry", crs=AREA_CRS)
    missing_geo.to_file(LANDUSE_DIR / "landuse_zones_missing.geojson", driver="GeoJSON")

    # Validation images
    plot_final_map("판교 2024 용도지역 최종", pangyo_clip, pangyo_boundary, VALIDATION_DIR / "pangyo_zoning_2024_final.png")
    plot_final_map("위례 2024 조합 용도지역 최종", wirye_combined, wirye_boundary, VALIDATION_DIR / "wirye_zoning_2024_combined_final.png")
    plot_wirye_coverage(wirye_boundary, wirye_base, wirye_gapfill, wirye_missing_final, VALIDATION_DIR / "wirye_zoning_2024_combined_coverage.png")

    # Comparison to old 2026 results
    old_mix_map = {row["area_name"]: row["lum_index"] for _, row in old_mix.iterrows()}
    new_mix_map = {row["area_name"]: row["lum_index"] for _, row in mix_index.iterrows()}
    old_cov_p = pangyo_old.geometry.union_all().area / pangyo_boundary.geometry.area.sum() if not pangyo_old.empty else 0.0
    old_cov_w = wirye_old.geometry.union_all().area / wirye_boundary.geometry.area.sum() if not wirye_old.empty else 0.0
    new_cov_p = coverage_summary.loc[coverage_summary["area_name"] == AREA_KEYS["pangyo"], "coverage_ratio"].iloc[0]
    new_cov_w = coverage_summary.loc[coverage_summary["area_name"] == AREA_KEYS["wirye"], "coverage_ratio"].iloc[0]

    compare_summary = pd.DataFrame([
        {"metric": "pangyo_zoning_lum_old_2026", "value": old_mix_map.get(AREA_KEYS["pangyo"], 0.0)},
        {"metric": "pangyo_zoning_lum_new_2024", "value": new_mix_map.get(AREA_KEYS["pangyo"], 0.0)},
        {"metric": "wirye_zoning_lum_old_2026", "value": old_mix_map.get(AREA_KEYS["wirye"], 0.0)},
        {"metric": "wirye_zoning_lum_new_2024", "value": new_mix_map.get(AREA_KEYS["wirye"], 0.0)},
        {"metric": "pangyo_coverage_old_2026", "value": old_cov_p},
        {"metric": "pangyo_coverage_new_2024", "value": new_cov_p},
        {"metric": "wirye_coverage_old_2026", "value": old_cov_w},
        {"metric": "wirye_coverage_new_2024", "value": new_cov_w},
        {"metric": "wirye_2024_01_area_sqm", "value": coverage_summary.loc[coverage_summary["area_name"] == AREA_KEYS["wirye"], "source_2024_01_area_sqm"].iloc[0]},
        {"metric": "wirye_2024_02_gap_fill_area_sqm", "value": coverage_summary.loc[coverage_summary["area_name"] == AREA_KEYS["wirye"], "source_2024_02_area_sqm"].iloc[0]},
        {"metric": "wirye_missing_area_sqm", "value": coverage_summary.loc[coverage_summary["area_name"] == AREA_KEYS["wirye"], "missing_area_sqm"].iloc[0]},
    ])
    compare_summary.to_csv(LANDUSE_DIR / "landuse_2024_vs_2026_comparison.csv", index=False, encoding="utf-8-sig")

    report_lines = [
        "# 2024 landuse mix report",
        "",
        "## 사용한 원본 파일",
        "### 용도지역2",
        *[f"- `{path.relative_to(ROOT).as_posix()}`" for path in zoning2_files],
        "",
        "### 용도지역3",
        *[f"- `{path.relative_to(ROOT).as_posix()}`" for path in zoning3_files],
        "",
        "## 적용 기준",
        "- 판교: `용도지역2` 사용",
        "- 위례: `용도지역2`를 기본으로 사용하고, 결측 구역만 `용도지역3`으로 보완",
        "- 그래도 남는 결측은 `데이터 없음`으로 유지",
        "- 기존 2026 용도지역 SHP는 최종 산출에는 사용하지 않음",
        "",
        "## coverage 요약",
        md_table(coverage_summary),
        "",
        "## zoning LUM",
        md_table(mix_index),
        "",
        "## 기존 2026 결과와 비교",
        f"- 판교 zoning LUM: `{old_mix_map.get(AREA_KEYS['pangyo'], 0.0):.6f}` -> `{new_mix_map.get(AREA_KEYS['pangyo'], 0.0):.6f}`",
        f"- 위례 zoning LUM: `{old_mix_map.get(AREA_KEYS['wirye'], 0.0):.6f}` -> `{new_mix_map.get(AREA_KEYS['wirye'], 0.0):.6f}`",
        f"- 판교 coverage: `{old_cov_p:.6f}` -> `{new_cov_p:.6f}`",
        f"- 위례 coverage: `{old_cov_w:.6f}` -> `{new_cov_w:.6f}`",
        f"- 위례 남은 결측 면적: `{coverage_summary.loc[coverage_summary['area_name'] == AREA_KEYS['wirye'], 'missing_area_sqm'].iloc[0]:.3f}㎡`",
        f"- 위례 용도지역2 사용 면적: `{coverage_summary.loc[coverage_summary['area_name'] == AREA_KEYS['wirye'], 'source_2024_01_area_sqm'].iloc[0]:.3f}㎡`",
        f"- 위례 용도지역3 보완 면적: `{coverage_summary.loc[coverage_summary['area_name'] == AREA_KEYS['wirye'], 'source_2024_02_area_sqm'].iloc[0]:.3f}㎡`",
        "",
        "## DATA_PREPROCESSING.md 반영 문구",
        build_preprocessing_note(),
    ]
    (LANDUSE_DIR / "landuse_mix_report.md").write_text("\n".join(report_lines), encoding="utf-8")

    print("done")


if __name__ == "__main__":
    main()
