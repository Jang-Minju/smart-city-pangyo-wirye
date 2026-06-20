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
    if gdf.crs is None:
        raise ValueError(f"CRS missing: {path}")
    zone_col = "DGM_NM" if "DGM_NM" in gdf.columns else "dgm_nm"
    gdf = gdf[[zone_col, "geometry"]].rename(columns={zone_col: "zone_name"})
    gdf = gdf.to_crs(AREA_CRS)
    gdf["geometry"] = gdf.geometry.apply(make_valid)
    gdf = gdf[~gdf.geometry.isna() & ~gdf.geometry.is_empty].copy()
    gdf["zone_name"] = gdf["zone_name"].fillna("미분류").astype(str).str.strip()
    gdf.loc[gdf["zone_name"].eq(""), "zone_name"] = "미분류"
    gdf["source_file"] = path.name
    return gdf


def load_new_zoning() -> tuple[gpd.GeoDataFrame, list[Path]]:
    zoning_dir = next(path for path in ROOT.iterdir() if path.is_dir() and path.name.endswith("2"))
    shp_files = sorted(zoning_dir.rglob("UPIS_C_UQ11*.shp"))
    frames = [read_zoning_shp(path) for path in shp_files]
    gdf = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), geometry="geometry", crs=AREA_CRS)
    return gdf, shp_files


def clip_to_boundary(zones: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame, area_name: str) -> gpd.GeoDataFrame:
    clipped = gpd.overlay(zones, boundary[["geometry"]], how="intersection", keep_geom_type=False)
    clipped = clipped[~clipped.geometry.isna() & ~clipped.geometry.is_empty].copy()
    clipped["area_name"] = area_name
    clipped["area_sqm"] = clipped.geometry.area
    return clipped


def top_legend_categories(gdf: gpd.GeoDataFrame, top_n: int = 10) -> list[str]:
    if gdf.empty:
        return []
    totals = gdf.groupby("zone_name")["area_sqm"].sum().sort_values(ascending=False)
    return totals.head(top_n).index.tolist()


def map_zone_color(zone_name: str) -> str:
    return ZONE_COLORS.get(zone_name, ZONE_COLORS["기타"])


def apply_zone_grouping(gdf: gpd.GeoDataFrame, keep: list[str]) -> gpd.GeoDataFrame:
    work = gdf.copy()
    work["zone_group"] = work["zone_name"].where(work["zone_name"].isin(keep), "기타")
    return work


def compute_coverage(clipped: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame) -> tuple[float, gpd.GeoDataFrame]:
    boundary_area = boundary.geometry.area.sum()
    covered_geom = clipped.geometry.union_all() if not clipped.empty else None
    coverage_ratio = (covered_geom.area / boundary_area) if covered_geom is not None and not covered_geom.is_empty else 0.0
    if covered_geom is None or covered_geom.is_empty:
        missing = boundary.copy()
    else:
        missing = gpd.overlay(boundary[["geometry"]], gpd.GeoDataFrame(geometry=[covered_geom], crs=AREA_CRS), how="difference")
        missing = missing[~missing.geometry.isna() & ~missing.geometry.is_empty].copy()
    missing["area_sqm"] = missing.geometry.area
    return coverage_ratio, missing


def compute_old_coverage(area_name: str, boundary: gpd.GeoDataFrame) -> float:
    old = read_geo(OLD_LANDUSE)
    area_key = "pangyo_1st_technovalley" if area_name == "pangyo" else "wirye_plan_area"
    old = old[old["area_name"] == area_key].copy()
    if old.empty:
        return 0.0
    return old.geometry.union_all().area / boundary.geometry.area.sum()


def plot_validation_map(area_label: str, clipped: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame, out_path: Path) -> None:
    keep = top_legend_categories(clipped, top_n=10)
    plot_gdf = apply_zone_grouping(clipped, keep)
    categories = keep + (["기타"] if (~plot_gdf["zone_name"].isin(keep)).any() else [])

    fig, ax = plt.subplots(figsize=(9, 9))
    for category in categories:
        subset = plot_gdf[plot_gdf["zone_group"] == category]
        if subset.empty:
            continue
        subset.plot(ax=ax, color=map_zone_color(category), edgecolor="#222222", linewidth=0.4)
    boundary.plot(ax=ax, facecolor="none", edgecolor="#111111", linewidth=2.0)
    ax.set_title(f"{area_label} 새 용도지역 검증 지도", fontsize=16, pad=16)
    ax.set_axis_off()
    patches = [Patch(facecolor=map_zone_color(cat), edgecolor="#222222", label=cat) for cat in categories]
    ax.legend(handles=patches, title="용도지역", loc="lower left", fontsize=9, title_fontsize=10, frameon=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_coverage_map(area_label: str, clipped: gpd.GeoDataFrame, missing: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 9))
    if not clipped.empty:
        covered = gpd.GeoDataFrame(geometry=[clipped.geometry.union_all()], crs=AREA_CRS)
        covered.plot(ax=ax, color="#7ba6d9", edgecolor="#557aa5", linewidth=0.6)
    if not missing.empty:
        missing.plot(ax=ax, color="#f2d7d7", edgecolor="#b85c5c", linewidth=0.8)
    boundary.plot(ax=ax, facecolor="none", edgecolor="#111111", linewidth=2.0)
    ax.set_title(f"{area_label} 새 용도지역 coverage 검증", fontsize=16, pad=16)
    ax.set_axis_off()
    patches = [
        Patch(facecolor="#7ba6d9", edgecolor="#557aa5", label="용도지역 데이터 있음"),
        Patch(facecolor="#f2d7d7", edgecolor="#b85c5c", label="데이터 공백"),
    ]
    ax.legend(handles=patches, loc="lower left", fontsize=10, frameon=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "(없음)"
    work = df.copy()
    lines = [
        "| " + " | ".join(work.columns) + " |",
        "| " + " | ".join("---" for _ in work.columns) + " |",
    ]
    for row in work.fillna("").astype(str).values.tolist():
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |")
    return "\n".join(lines)


def write_report(
    shp_files: list[Path],
    zoning_column: str,
    crs: str,
    pangyo_clip: gpd.GeoDataFrame,
    wirye_clip: gpd.GeoDataFrame,
    pangyo_cov: float,
    wirye_cov: float,
    pangyo_old_cov: float,
    wirye_old_cov: float,
    out_path: Path,
) -> None:
    summary = pd.DataFrame(
        [
            {
                "area": "pangyo",
                "intersect_polygon_count": len(pangyo_clip),
                "coverage_ratio": f"{pangyo_cov:.6f}",
                "old_coverage_ratio": f"{pangyo_old_cov:.6f}",
            },
            {
                "area": "wirye",
                "intersect_polygon_count": len(wirye_clip),
                "coverage_ratio": f"{wirye_cov:.6f}",
                "old_coverage_ratio": f"{wirye_old_cov:.6f}",
            },
        ]
    )

    usable = "부분 사용 가능하나, 위례 coverage가 기존보다 낮아 바로 분석 교체용으로는 부적합"
    better = "판교는 기존과 유사(100%), 위례는 기존보다 악화(0.618 < 0.793)"

    pangyo_zones = pangyo_clip.groupby("zone_name")["area_sqm"].sum().sort_values(ascending=False).head(10).reset_index()
    wirye_zones = wirye_clip.groupby("zone_name")["area_sqm"].sum().sort_values(ascending=False).head(10).reset_index()
    pangyo_zones["area_sqm"] = pangyo_zones["area_sqm"].map(lambda x: f"{x:.3f}")
    wirye_zones["area_sqm"] = wirye_zones["area_sqm"].map(lambda x: f"{x:.3f}")

    out_path.write_text(
        "\n".join(
            [
                "# zoning2 validation report",
                "",
                "## 사용한 원본 파일",
                *[f"- `{path.relative_to(ROOT).as_posix()}`" for path in shp_files],
                "",
                f"- 용도지역명 컬럼: `{zoning_column}`",
                f"- 좌표계: `{crs}`",
                "",
                "## 요약",
                md_table(summary),
                "",
                f"- 판교 coverage 비율: `{pangyo_cov:.6f}`",
                f"- 위례 coverage 비율: `{wirye_cov:.6f}`",
                f"- 기존 판교 coverage 비율: `{pangyo_old_cov:.6f}`",
                f"- 기존 위례 coverage 비율: `{wirye_old_cov:.6f}`",
                "",
                f"- 실제 분석 사용 가능성: {usable}",
                f"- 기존 용도지역 데이터보다 나은지 여부: {better}",
                "",
                "## 판교 주요 용도지역",
                md_table(pangyo_zones),
                "",
                "## 위례 주요 용도지역",
                md_table(wirye_zones),
                "",
                "## 판단",
                "- 판교는 새 데이터가 분석경계를 사실상 전부 덮으며, 용도지역명도 정상적으로 읽힌다.",
                "- 위례는 새 데이터 coverage가 약 61.8%로 기존 데이터(약 79.3%)보다 낮다.",
                "- 따라서 새 용도지역2 데이터는 판교 검증용 또는 부분 보조자료로는 쓸 수 있지만, 현재 상태로는 위례를 포함한 공통 분석용 대체본으로 쓰기 어렵다.",
                "- 문제 원인은 `용도지역2` 세트가 위례 경계 내부를 충분히 덮지 못하는 점이며, 추가 서울/경기 원본 또는 누락 레이어 확인이 필요하다.",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    set_korean_font()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    zones, shp_files = load_new_zoning()
    pangyo_boundary = read_geo(PANGYO_BOUNDARY)
    wirye_boundary = read_geo(WIRYE_BOUNDARY)

    pangyo_clip = clip_to_boundary(zones, pangyo_boundary, "pangyo")
    wirye_clip = clip_to_boundary(zones, wirye_boundary, "wirye")

    pangyo_cov, pangyo_missing = compute_coverage(pangyo_clip, pangyo_boundary)
    wirye_cov, wirye_missing = compute_coverage(wirye_clip, wirye_boundary)
    pangyo_old_cov = compute_old_coverage("pangyo", pangyo_boundary)
    wirye_old_cov = compute_old_coverage("wirye", wirye_boundary)

    plot_validation_map("판교", pangyo_clip, pangyo_boundary, OUT_DIR / "pangyo_zoning2_validation.png")
    plot_validation_map("위례", wirye_clip, wirye_boundary, OUT_DIR / "wirye_zoning2_validation.png")
    plot_coverage_map("판교", pangyo_clip, pangyo_missing, pangyo_boundary, OUT_DIR / "pangyo_zoning2_coverage.png")
    plot_coverage_map("위례", wirye_clip, wirye_missing, wirye_boundary, OUT_DIR / "wirye_zoning2_coverage.png")

    write_report(
        shp_files=shp_files,
        zoning_column="DGM_NM",
        crs=AREA_CRS,
        pangyo_clip=pangyo_clip,
        wirye_clip=wirye_clip,
        pangyo_cov=pangyo_cov,
        wirye_cov=wirye_cov,
        pangyo_old_cov=pangyo_old_cov,
        wirye_old_cov=wirye_old_cov,
        out_path=OUT_DIR / "zoning2_validation_report.md",
    )

    print("done")


if __name__ == "__main__":
    main()
