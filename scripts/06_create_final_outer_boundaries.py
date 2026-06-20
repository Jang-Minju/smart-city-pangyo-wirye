from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager
from shapely import concave_hull, make_valid
from shapely.geometry import MultiPolygon, Polygon


ROOT = Path(__file__).resolve().parents[1]
PARCELS = ROOT / "가구및획지" / "the_geom.shp"
OUT_DIR = ROOT / "analysis_boundaries" / "final_outer_boundaries"
MAP_DIR = ROOT / "reports" / "final_outer_boundary_maps"
REPORT = ROOT / "reports" / "final_outer_boundary_report.md"


def set_font() -> None:
    for font in ["Malgun Gothic", "NanumGothic", "AppleGothic"]:
        if any(font in f.name for f in font_manager.fontManager.ttflist):
            plt.rcParams["font.family"] = font
            break
    plt.rcParams["axes.unicode_minus"] = False


def read_parcels() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(PARCELS, encoding="cp949").to_crs(epsg=5186)
    gdf["geometry"] = gdf.geometry.apply(make_valid)
    gdf["parcel_id"] = gdf.apply(parcel_id, axis=1)
    gdf["area_sqm"] = gdf.geometry.area
    return gdf


def parcel_id(row: pd.Series) -> str:
    block = "" if pd.isna(row.get("blockName")) else str(row.get("blockName"))
    lot = "" if pd.isna(row.get("lotName")) else str(row.get("lotName"))
    if not lot or lot == block:
        return block
    return f"{block}-{lot}"


def remove_holes(geom):
    geom = make_valid(geom)
    if isinstance(geom, Polygon):
        return Polygon(geom.exterior)
    if isinstance(geom, MultiPolygon):
        return MultiPolygon([Polygon(poly.exterior) for poly in geom.geoms])
    return geom


def as_boundary_gdf(geom, name: str, source_count: int, method: str) -> gpd.GeoDataFrame:
    geom = make_valid(geom)
    return gpd.GeoDataFrame(
        [{"name": name, "source_count": source_count, "method": method, "area_sqm": geom.area}],
        geometry=[geom],
        crs="EPSG:5186",
    )


def save_boundary(gdf: gpd.GeoDataFrame, basename: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gdf.to_file(OUT_DIR / f"{basename}_5186.shp", encoding="cp949")
    gdf.to_file(OUT_DIR / f"{basename}_5186.geojson", driver="GeoJSON")
    gdf.to_crs(epsg=4326).to_file(OUT_DIR / f"{basename}_4326.geojson", driver="GeoJSON")


def save_ids(gdf: gpd.GeoDataFrame, basename: str) -> pd.DataFrame:
    summary = (
        gdf.drop(columns="geometry")
        .groupby(["zoneName", "blockType", "blockName", "lotName", "parcel_id"], dropna=False)
        .agg(feature_count=("area_sqm", "size"), area_sqm=("area_sqm", "sum"))
        .reset_index()
        .sort_values(["blockType", "parcel_id"])
    )
    summary.to_csv(OUT_DIR / f"{basename}_source_parcel_ids.csv", index=False, encoding="utf-8-sig")
    return summary


def bounds_with_pad(gdf: gpd.GeoDataFrame, pad=0.1):
    minx, miny, maxx, maxy = gdf.total_bounds
    p = max(maxx - minx, maxy - miny) * pad
    return minx - p, miny - p, maxx + p, maxy + p


def plot_validation(
    all_parcels: gpd.GeoDataFrame,
    source_parcels: gpd.GeoDataFrame,
    final_boundary: gpd.GeoDataFrame,
    title: str,
    filename: str,
    note: str,
) -> None:
    MAP_DIR.mkdir(parents=True, exist_ok=True)
    bounds = bounds_with_pad(gpd.GeoDataFrame(pd.concat([all_parcels, final_boundary], ignore_index=True), geometry="geometry", crs="EPSG:5186"), 0.08)
    fig, ax = plt.subplots(figsize=(13, 13))
    all_parcels.boundary.plot(ax=ax, color="#D1D5DB", linewidth=0.25)
    source_parcels.plot(ax=ax, color="#FCA5A5", edgecolor="#B91C1C", linewidth=0.35, alpha=0.55)
    final_boundary.boundary.plot(ax=ax, color="#111827", linewidth=3.0)
    final_boundary.plot(ax=ax, color="#F97316", alpha=0.15, edgecolor="#111827", linewidth=2.0)

    for _, row in source_parcels.iterrows():
        if row.geometry.area < 900:
            continue
        pt = row.geometry.representative_point()
        ax.text(pt.x, pt.y, str(row["blockName"]), fontsize=6.5, ha="center", va="center", color="#111827")

    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    ax.set_aspect("equal")
    ax.grid(True, color="#E5E7EB", linewidth=0.35)
    ax.ticklabel_format(style="plain", useOffset=False)
    ax.set_title(title, fontsize=16, pad=14)
    ax.text(
        0.01,
        0.01,
        note,
        transform=ax.transAxes,
        fontsize=10,
        va="bottom",
        bbox={"facecolor": "white", "edgecolor": "#9CA3AF", "alpha": 0.92},
    )
    fig.savefig(MAP_DIR / filename, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_plan_check(
    source_parcels: gpd.GeoDataFrame,
    final_boundary: gpd.GeoDataFrame,
    title: str,
    filename: str,
    image_note: str,
) -> None:
    MAP_DIR.mkdir(parents=True, exist_ok=True)
    bounds = bounds_with_pad(final_boundary, 0.15)
    fig, ax = plt.subplots(figsize=(10, 10))
    source_parcels.plot(ax=ax, color="#93C5FD", edgecolor="#1D4ED8", linewidth=0.35, alpha=0.6)
    final_boundary.boundary.plot(ax=ax, color="#DC2626", linewidth=3.0)
    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    ax.set_aspect("equal")
    ax.grid(True, color="#E5E7EB", linewidth=0.35)
    ax.ticklabel_format(style="plain", useOffset=False)
    ax.set_title(title, fontsize=15, pad=14)
    ax.text(
        0.01,
        0.01,
        image_note,
        transform=ax.transAxes,
        fontsize=10,
        va="bottom",
        bbox={"facecolor": "white", "edgecolor": "#9CA3AF", "alpha": 0.92},
    )
    fig.savefig(MAP_DIR / filename, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def markdown_table(df: pd.DataFrame, max_rows=200) -> str:
    if df.empty:
        return "(없음)"
    d = df.head(max_rows).fillna("").astype(str)
    lines = [
        "| " + " | ".join(d.columns) + " |",
        "| " + " | ".join("---" for _ in d.columns) + " |",
    ]
    for row in d.values.tolist():
        lines.append("| " + " | ".join(str(v).replace("|", "\\|") for v in row) + " |")
    return "\n".join(lines)


def main() -> None:
    set_font()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MAP_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    parcels = read_parcels()
    pangyo_all = parcels[parcels["zoneName"].fillna("").str.contains("성남판교지구", regex=False)].copy()
    wirye_all = parcels[parcels["zoneName"].fillna("").str.contains("위례", regex=False)].copy()

    pangyo_support = pangyo_all[pangyo_all["blockType"].eq("도시지원시설용지")].copy()
    support_union = pangyo_support.union_all()
    pangyo_office = pangyo_all[pangyo_all["blockType"].isin(["업무시설", "업무시설기타"])].copy()
    pangyo_adjacent_office = pangyo_office[pangyo_office.geometry.distance(support_union) <= 450].copy()
    pangyo_source = gpd.GeoDataFrame(
        pd.concat([pangyo_support, pangyo_adjacent_office], ignore_index=True),
        geometry="geometry",
        crs="EPSG:5186",
    )

    # Concave hull removes internal parcel boundaries and bridges the road gaps inside
    # the Techno Valley block without expanding to the whole Pangyo district.
    pangyo_outer_geom = concave_hull(pangyo_source.union_all(), ratio=0.10, allow_holes=False)
    pangyo_outer = as_boundary_gdf(
        pangyo_outer_geom,
        "판교 제1테크노밸리 전체 외곽 경계",
        len(pangyo_source),
        "도시지원시설용지 + 인접 업무시설 concave_hull(ratio=0.10)",
    )

    # Wirye whole new town outer boundary: dissolve every lot in the Wirye project,
    # then remove interior rings so only the outer analysis shell remains.
    wirye_outer_geom = remove_holes(wirye_all.union_all())
    wirye_outer = as_boundary_gdf(
        wirye_outer_geom,
        "위례신도시 전체 외곽 경계",
        len(wirye_all),
        "위례 전체 가구및획지 dissolve + 내부 hole 제거",
    )

    save_boundary(pangyo_outer, "pangyo_1st_technovalley_outer_boundary")
    save_boundary(wirye_outer, "wirye_newtown_outer_boundary")
    pangyo_ids = save_ids(pangyo_source, "pangyo_1st_technovalley_outer_boundary")
    wirye_ids = save_ids(wirye_all, "wirye_newtown_outer_boundary")

    plot_validation(
        pangyo_all,
        pangyo_source,
        pangyo_outer,
        "판교 제1테크노밸리 외곽 경계 생성 검증",
        "01_pangyo_outer_boundary_validation.png",
        "회색: 성남판교 가구획지 전체 / 붉은 면: 외곽화 원천 획지 / 검정선: 최종 외곽 Polygon",
    )
    plot_validation(
        wirye_all,
        wirye_all,
        wirye_outer,
        "위례신도시 전체 외곽 경계 생성 검증",
        "02_wirye_outer_boundary_validation.png",
        "회색: 위례 가구획지 전체 / 붉은 면: 외곽화 원천 전체 획지 / 검정선: 최종 외곽 Polygon",
    )
    plot_plan_check(
        pangyo_source,
        pangyo_outer,
        "판교 계획도 이미지 대조용 외곽 경계",
        "03_pangyo_plan_image_overlap_check.png",
        "업로드 계획도는 좌표가 없어 직접 지오리퍼런싱 중첩은 불가. 도면상 업무·도시지원 핵심 블록과 SHP의 지원 및 인접 업무 블록 형상·위치를 대조했다.",
    )
    plot_plan_check(
        wirye_all,
        wirye_outer,
        "위례 계획도 이미지 대조용 외곽 경계",
        "04_wirye_plan_image_overlap_check.png",
        "업로드 계획도는 좌표가 없어 직접 지오리퍼런싱 중첩은 불가. 위례 전체 사업지구 외곽은 가구획지 전체 dissolve로 생성하고 업무·상업 위치는 내부 검토 대상으로 유지했다.",
    )

    summary_df = pd.DataFrame(
        [
            {
                "target": "판교 제1테크노밸리",
                "source_features": len(pangyo_source),
                "source_area_sqm": pangyo_source.geometry.area.sum(),
                "outer_area_sqm": pangyo_outer.geometry.area.sum(),
                "geometry_type": pangyo_outer.geometry.iloc[0].geom_type,
            },
            {
                "target": "위례신도시",
                "source_features": len(wirye_all),
                "source_area_sqm": wirye_all.geometry.area.sum(),
                "outer_area_sqm": wirye_outer.geometry.area.sum(),
                "geometry_type": wirye_outer.geometry.iloc[0].geom_type,
            },
        ]
    )

    report = f"""# 최종 분석용 외곽 경계 생성 보고서

## 핵심 변경

기존 `analysis_boundaries` 산출물은 업무용지/획지의 집합이어서 내부 필지 경계와 도로 틈이 남아 있었다. 이번 작업에서는 분석에 사용할 수 있도록 내부 필지 경계를 제거하고 하나의 외곽 Polygon 또는 MultiPolygon으로 재생성했다.

## 생성 방식

| 대상 | 생성 방식 |
| --- | --- |
| 판교 제1테크노밸리 | `도시지원시설용지(지원)` + 지원 경계에서 450m 이내 인접 `업무시설/업무시설기타`를 원천 획지로 선택한 뒤 `concave_hull(ratio=0.10, allow_holes=False)` 적용 |
| 위례신도시 | `위례 택지개발사업 예정지구`의 모든 가구및획지를 dissolve한 뒤 내부 hole 제거 |

## 결과 요약

{markdown_table(summary_df)}

## 산출 파일

### SHP

- `analysis_boundaries/final_outer_boundaries/pangyo_1st_technovalley_outer_boundary_5186.shp`
- `analysis_boundaries/final_outer_boundaries/wirye_newtown_outer_boundary_5186.shp`

### GeoJSON

- `analysis_boundaries/final_outer_boundaries/pangyo_1st_technovalley_outer_boundary_5186.geojson`
- `analysis_boundaries/final_outer_boundaries/pangyo_1st_technovalley_outer_boundary_4326.geojson`
- `analysis_boundaries/final_outer_boundaries/wirye_newtown_outer_boundary_5186.geojson`
- `analysis_boundaries/final_outer_boundaries/wirye_newtown_outer_boundary_4326.geojson`

### 원천 획지 ID

- `analysis_boundaries/final_outer_boundaries/pangyo_1st_technovalley_outer_boundary_source_parcel_ids.csv`
- `analysis_boundaries/final_outer_boundaries/wirye_newtown_outer_boundary_source_parcel_ids.csv`

## PNG 검증 지도

- `reports/final_outer_boundary_maps/01_pangyo_outer_boundary_validation.png`
- `reports/final_outer_boundary_maps/02_wirye_outer_boundary_validation.png`
- `reports/final_outer_boundary_maps/03_pangyo_plan_image_overlap_check.png`
- `reports/final_outer_boundary_maps/04_wirye_plan_image_overlap_check.png`

## 계획도 이미지 중첩 검증 한계

사용자가 제공한 계획도 이미지는 좌표계, 축척, 기준점이 없는 스크린샷이다. 따라서 GIS 레이어처럼 실제 좌표 기반으로 지오리퍼런싱하여 픽셀 단위 중첩 검증을 수행할 수는 없다. 대신 SHP의 블록명, 용도, 상대 위치, 외곽 형상을 계획도 이미지와 시각적으로 대조했다.

판교는 이미지의 업무·도시지원 핵심 구역과 대응되는 `지원` 블록 및 인접 업무 블록만 사용했다. SHP에는 이미지에 보이는 `업무6` 명칭이 없고, `위4`는 `위험물저장및처리시설`로 확인되어 제1테크노밸리 외곽 원천에서 제외했다.

위례는 이번 요구가 `위례신도시 전체 외곽 경계`이므로 업무·상업 획지만이 아니라 위례 사업지구의 모든 가구획지를 사용했다. 내부 업무·상업용지 분석은 별도 레이어로 유지해야 한다.

## 판교 원천 획지 ID

{markdown_table(pangyo_ids, max_rows=120)}

## 위례 원천 획지 ID

위례는 전체 사업지구 외곽이므로 원천 획지가 많다. 전체 목록은 CSV로 저장했다.
"""
    REPORT.write_text(report, encoding="utf-8-sig")

    print(f"pangyo_outer_area={pangyo_outer.geometry.area.sum():.1f}")
    print(f"wirye_outer_area={wirye_outer.geometry.area.sum():.1f}")
    print(f"out={OUT_DIR}")
    print(f"maps={MAP_DIR}")
    print(f"report={REPORT}")


if __name__ == "__main__":
    main()
