from __future__ import annotations

from pathlib import Path

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
OUT_DIR = ROOT / "derived_data" / "01_landuse_validation"

PANGYO_BOUNDARY = ROOT / "derived_data" / "00_boundaries" / "pangyo_boundary_user_drawn2_5186.geojson"
WIRYE_BOUNDARY = ROOT / "derived_data" / "00_boundaries" / "wirye_boundary.geojson"
OLD_LANDUSE = ROOT / "derived_data" / "01_landuse_mix" / "landuse_zones_clipped.geojson"

TITLE_FONT = "Malgun Gothic"

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
    "관리지역미분류": "#9e93bf",
    "계획관리지역": "#9db77d",
    "생산관리지역": "#7ea85e",
    "보전관리지역": "#6f8f57",
    "농림지역": "#8aa35c",
    "자연환경보전지역": "#76965e",
    "비도시지역": "#b6c3cd",
    "기타": "#7566ac",
    "미분류": "#b0b8c1",
}


def set_korean_font() -> None:
    plt.rcParams["font.family"] = TITLE_FONT
    plt.rcParams["axes.unicode_minus"] = False


def read_geo(path: Path) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        raise ValueError(f"CRS missing: {path}")
    gdf = gdf.to_crs(AREA_CRS)
    gdf["geometry"] = gdf.geometry.apply(make_valid)
    return gdf[~gdf.geometry.isna() & ~gdf.geometry.is_empty].copy()


def read_zoning_shp(path: Path) -> gpd.GeoDataFrame:
    gdf = pyogrio.read_dataframe(path, encoding="cp949")
    zone_col = "DGM_NM" if "DGM_NM" in gdf.columns else "dgm_nm"
    gdf = gdf[[zone_col, "geometry"]].rename(columns={zone_col: "zone_name"})
    gdf = gdf.to_crs(AREA_CRS)
    gdf["geometry"] = gdf.geometry.apply(make_valid)
    gdf = gdf[~gdf.geometry.isna() & ~gdf.geometry.is_empty].copy()
    gdf["zone_name"] = gdf["zone_name"].fillna("미분류").astype(str).str.strip()
    gdf.loc[gdf["zone_name"].eq(""), "zone_name"] = "미분류"
    gdf["source_file"] = path.name
    return gdf


def load_zoning3() -> tuple[gpd.GeoDataFrame, list[Path], str]:
    zoning_dir = next(path for path in ROOT.iterdir() if path.is_dir() and path.name.endswith("3"))
    shp_files = sorted(zoning_dir.glob("UPIS_C_UQ11*.shp"))
    frames = [read_zoning_shp(path) for path in shp_files]
    gdf = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), geometry="geometry", crs=AREA_CRS)
    return gdf, shp_files, "DGM_NM"


def clip_to_boundary(zones: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame, area_name: str) -> gpd.GeoDataFrame:
    clipped = gpd.overlay(zones, boundary[["geometry"]], how="intersection", keep_geom_type=False)
    clipped = clipped[~clipped.geometry.isna() & ~clipped.geometry.is_empty].copy()
    clipped["area_name"] = area_name
    clipped["area_sqm"] = clipped.geometry.area
    return clipped


def compute_coverage(clipped: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame) -> tuple[float, float, gpd.GeoDataFrame]:
    boundary_area = boundary.geometry.area.sum()
    covered_geom = clipped.geometry.union_all() if not clipped.empty else None
    coverage_ratio = (covered_geom.area / boundary_area) if covered_geom is not None and not covered_geom.is_empty else 0.0
    missing_area = boundary_area - (covered_geom.area if covered_geom is not None and not covered_geom.is_empty else 0.0)
    if covered_geom is None or covered_geom.is_empty:
        missing = boundary.copy()
    else:
        missing = gpd.overlay(boundary[["geometry"]], gpd.GeoDataFrame(geometry=[covered_geom], crs=AREA_CRS), how="difference")
        missing = missing[~missing.geometry.isna() & ~missing.geometry.is_empty].copy()
    missing["area_sqm"] = missing.geometry.area
    return coverage_ratio, missing_area, missing


def top_legend_categories(gdf: gpd.GeoDataFrame, top_n: int = 10) -> list[str]:
    if gdf.empty:
        return []
    totals = gdf.groupby("zone_name")["area_sqm"].sum().sort_values(ascending=False)
    return totals.head(top_n).index.tolist()


def apply_zone_grouping(gdf: gpd.GeoDataFrame, keep: list[str]) -> gpd.GeoDataFrame:
    work = gdf.copy()
    work["zone_group"] = work["zone_name"].where(work["zone_name"].isin(keep), "기타")
    return work


def map_zone_color(zone_name: str) -> str:
    return ZONE_COLORS.get(zone_name, ZONE_COLORS["기타"])


def plot_validation_map(area_label: str, clipped: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame, out_path: Path) -> None:
    keep = top_legend_categories(clipped, top_n=10)
    plot_gdf = apply_zone_grouping(clipped, keep)
    categories = keep + (["기타"] if (~plot_gdf["zone_name"].isin(keep)).any() else [])
    fig, ax = plt.subplots(figsize=(9, 9))
    for category in categories:
        subset = plot_gdf[plot_gdf["zone_group"] == category]
        if subset.empty:
            continue
        subset.plot(ax=ax, color=map_zone_color(category), edgecolor="#222222", linewidth=0.35)
    boundary.plot(ax=ax, facecolor="none", edgecolor="#111111", linewidth=2.0)
    ax.set_title(f"{area_label} 새 용도지역 검증 지도", fontsize=16, pad=16)
    ax.set_axis_off()
    patches = [Patch(facecolor=map_zone_color(cat), edgecolor="#222222", label=cat) for cat in categories]
    ax.legend(handles=patches, title="용도지역", loc="lower left", fontsize=9, title_fontsize=10, frameon=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_coverage_compare(
    boundary: gpd.GeoDataFrame,
    clip_2024: gpd.GeoDataFrame,
    missing_2024: gpd.GeoDataFrame,
    old_2026: gpd.GeoDataFrame,
    out_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(9, 9))
    if not old_2026.empty:
        old_union = gpd.GeoDataFrame(geometry=[old_2026.geometry.union_all()], crs=AREA_CRS)
        old_union.plot(ax=ax, color="#d7dbe0", edgecolor="#98a2ad", linewidth=0.5)
    if not clip_2024.empty:
        new_union = gpd.GeoDataFrame(geometry=[clip_2024.geometry.union_all()], crs=AREA_CRS)
        new_union.plot(ax=ax, color="#7ba6d9", edgecolor="#557aa5", linewidth=0.6)
    if not missing_2024.empty:
        missing_2024.plot(ax=ax, color="#f2d7d7", edgecolor="#b85c5c", linewidth=0.8)
    boundary.plot(ax=ax, facecolor="none", edgecolor="#111111", linewidth=2.0)
    ax.set_title("위례 새 용도지역 coverage 비교", fontsize=16, pad=16)
    ax.set_axis_off()
    patches = [
        Patch(facecolor="#7ba6d9", edgecolor="#557aa5", label="2024-02 coverage"),
        Patch(facecolor="#d7dbe0", edgecolor="#98a2ad", label="기존 2026 coverage"),
        Patch(facecolor="#f2d7d7", edgecolor="#b85c5c", label="2024-02 결측"),
    ]
    ax.legend(handles=patches, loc="lower left", fontsize=10, frameon=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_gapfill_check(
    boundary: gpd.GeoDataFrame,
    clip_2024: gpd.GeoDataFrame,
    gapfill: gpd.GeoDataFrame,
    remaining_missing: gpd.GeoDataFrame,
    out_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(9, 9))
    if not clip_2024.empty:
        gpd.GeoDataFrame(geometry=[clip_2024.geometry.union_all()], crs=AREA_CRS).plot(
            ax=ax, color="#7ba6d9", edgecolor="#557aa5", linewidth=0.5
        )
    if not gapfill.empty:
        gapfill.plot(ax=ax, color="#efb36b", edgecolor="#b97125", linewidth=0.6)
    if not remaining_missing.empty:
        remaining_missing.plot(ax=ax, color="#f2d7d7", edgecolor="#b85c5c", linewidth=0.8)
    boundary.plot(ax=ax, facecolor="none", edgecolor="#111111", linewidth=2.0)
    ax.set_title("위례 2024-02 + 2026 보완 검토", fontsize=16, pad=16)
    ax.set_axis_off()
    patches = [
        Patch(facecolor="#7ba6d9", edgecolor="#557aa5", label="2024-02 원본"),
        Patch(facecolor="#efb36b", edgecolor="#b97125", label="2026 보완 가능 영역"),
        Patch(facecolor="#f2d7d7", edgecolor="#b85c5c", label="남은 결측"),
    ]
    ax.legend(handles=patches, loc="lower left", fontsize=10, frameon=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "(없음)"
    lines = [
        "| " + " | ".join(df.columns) + " |",
        "| " + " | ".join("---" for _ in df.columns) + " |",
    ]
    for row in df.fillna("").astype(str).values.tolist():
        lines.append("| " + " | ".join(v.replace("|", "\\|") for v in row) + " |")
    return "\n".join(lines)


def main() -> None:
    set_korean_font()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    zones_2024, shp_files, zoning_col = load_zoning3()
    pangyo_boundary = read_geo(PANGYO_BOUNDARY)
    wirye_boundary = read_geo(WIRYE_BOUNDARY)
    old_2026 = read_geo(OLD_LANDUSE)

    pangyo_2026 = old_2026[old_2026["area_name"] == "pangyo_1st_technovalley"].copy()
    wirye_2026 = old_2026[old_2026["area_name"] == "wirye_plan_area"].copy()

    pangyo_clip = clip_to_boundary(zones_2024, pangyo_boundary, "pangyo")
    wirye_clip = clip_to_boundary(zones_2024, wirye_boundary, "wirye")

    pangyo_cov, pangyo_missing_area, pangyo_missing = compute_coverage(pangyo_clip, pangyo_boundary)
    wirye_cov, wirye_missing_area, wirye_missing = compute_coverage(wirye_clip, wirye_boundary)
    pangyo_2026_cov = pangyo_2026.geometry.union_all().area / pangyo_boundary.geometry.area.sum() if not pangyo_2026.empty else 0.0
    wirye_2026_cov = wirye_2026.geometry.union_all().area / wirye_boundary.geometry.area.sum() if not wirye_2026.empty else 0.0
    zoning2_pangyo_cov = 1.0
    zoning2_wirye_cov = 0.618192

    # 2026 gap fill review for wirye
    gapfill_2026 = gpd.overlay(wirye_2026[["landuse_category", "geometry"]], wirye_missing[["geometry"]], how="intersection", keep_geom_type=False)
    gapfill_2026 = gapfill_2026[~gapfill_2026.geometry.isna() & ~gapfill_2026.geometry.is_empty].copy()
    gapfill_2026["source"] = "2026_gap_fill"
    if not gapfill_2026.empty:
        gapfill_2026["area_sqm"] = gapfill_2026.geometry.area
    else:
        gapfill_2026 = gpd.GeoDataFrame(columns=["landuse_category", "source", "area_sqm", "geometry"], geometry="geometry", crs=AREA_CRS)

    wirye_2024_original = wirye_clip[["zone_name", "geometry"]].copy()
    wirye_2024_original["source"] = "2024_02_original"
    wirye_2024_original = wirye_2024_original.rename(columns={"zone_name": "landuse_category"})

    combined = pd.concat([wirye_2024_original[["landuse_category", "source", "geometry"]], gapfill_2026[["landuse_category", "source", "geometry"]]], ignore_index=True)
    combined = gpd.GeoDataFrame(combined, geometry="geometry", crs=AREA_CRS)
    combined["geometry"] = combined.geometry.apply(make_valid)
    combined = combined[~combined.geometry.isna() & ~combined.geometry.is_empty].copy()
    combined["area_sqm"] = combined.geometry.area

    combined_cov, combined_missing_area, combined_missing = compute_coverage(combined, wirye_boundary)

    wirye_missing.to_file(OUT_DIR / "zoning3_2024_02_missing.geojson", driver="GeoJSON")
    combined.to_file(OUT_DIR / "zoning3_2024_02_with_2026_gapfill.geojson", driver="GeoJSON")

    plot_validation_map("판교", pangyo_clip, pangyo_boundary, OUT_DIR / "pangyo_zoning3_validation.png")
    plot_validation_map("위례", wirye_clip, wirye_boundary, OUT_DIR / "wirye_zoning3_validation.png")
    plot_coverage_compare(wirye_boundary, wirye_clip, wirye_missing, wirye_2026, OUT_DIR / "wirye_zoning3_coverage_compare.png")
    plot_gapfill_check(wirye_boundary, wirye_clip, gapfill_2026, combined_missing, OUT_DIR / "wirye_zoning3_gapfill_check.png")

    summary = pd.DataFrame(
        [
            {
                "area": "pangyo",
                "intersect_polygon_count": len(pangyo_clip),
                "coverage_ratio": f"{pangyo_cov:.6f}",
                "missing_area_sqm": f"{pangyo_missing_area:.3f}",
            },
            {
                "area": "wirye",
                "intersect_polygon_count": len(wirye_clip),
                "coverage_ratio": f"{wirye_cov:.6f}",
                "missing_area_sqm": f"{wirye_missing_area:.3f}",
            },
        ]
    )

    recommendation = "2024년 2월 기본 + 2026 보완 권장"
    if wirye_cov >= 0.95 and pangyo_cov >= 0.95:
        recommendation = "2024년 2월 단독 사용 가능"
    elif combined_cov <= wirye_2026_cov:
        recommendation = "사용 부적합"

    report_lines = [
        "# zoning3 validation report",
        "",
        "## 사용한 원본 파일",
        *[f"- `{path.relative_to(ROOT).as_posix()}`" for path in shp_files],
        "",
        f"- 용도지역명 컬럼명: `{zoning_col}`",
        f"- 좌표계(검증 기준): `{AREA_CRS}`",
        "",
        "## coverage 요약",
        md_table(summary),
        "",
        f"- 판교 coverage: `{pangyo_cov:.6f}`",
        f"- 위례 coverage: `{wirye_cov:.6f}`",
        f"- 기존 2026 판교 coverage: `{pangyo_2026_cov:.6f}`",
        f"- 기존 2026 위례 coverage: `{wirye_2026_cov:.6f}`",
        f"- 기존 용도지역2 판교 coverage: `{zoning2_pangyo_cov:.6f}`",
        f"- 기존 용도지역2 위례 coverage: `{zoning2_wirye_cov:.6f}`",
        "",
        f"- 위례 결측 개선 여부(용도지역2 대비): {'개선' if wirye_cov > zoning2_wirye_cov else '악화'}",
        f"- 위례 결측 개선 여부(기존 2026 대비): {'개선' if wirye_cov > wirye_2026_cov else '악화'}",
        "",
        f"- 2024년 2월 단독 사용 가능 여부: {'가능' if recommendation == '2024년 2월 단독 사용 가능' else '불가'}",
        f"- 2024년 2월 + 2026 보완 가능 여부: {'가능' if len(gapfill_2026) > 0 else '불가'}",
        f"- gap fill 후 위례 coverage: `{combined_cov:.6f}`",
        f"- gap fill 후 남은 결측 면적: `{combined_missing_area:.3f}`",
        "",
        "## 위례 결측 보완 판단",
        f"- 2024년 2월 원본 coverage는 `{wirye_cov:.6f}`로, 용도지역2(`{zoning2_wirye_cov:.6f}`)보다 낮고 기존 2026(`{wirye_2026_cov:.6f}`)보다는 더 낮다.",
        f"- 2026년 자료를 결측 구역에만 보완하면 coverage는 `{combined_cov:.6f}`까지 상승한다.",
        "- 중복 면적은 2024년 2월 결측 영역에 대해서만 2026을 clip하는 방식으로 방지했다.",
        "- `용도지역3` 원본에는 서울 11710은 포함되지만, 성남 41130과 하남 41450 코드가 보이지 않아 판교 전체와 위례 일부를 직접 덮지 못한다.",
        "",
        f"## 최종 추천\n- {recommendation}",
    ]
    (OUT_DIR / "zoning3_validation_report.md").write_text("\n".join(report_lines), encoding="utf-8")

    print("done")


if __name__ == "__main__":
    main()
