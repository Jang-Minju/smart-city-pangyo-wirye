from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager
from shapely import make_valid


ROOT = Path(__file__).resolve().parents[1]
PARCELS = ROOT / "가구및획지" / "the_geom.shp"
OLD_PANGYO = ROOT / "analysis_boundaries" / "pangyo_1st_technovalley_candidate_boundary_5186.geojson"
OLD_WIRYE = ROOT / "analysis_boundaries" / "wirye_business_commercial_candidate_boundary_5186.geojson"
OUT_DIR = ROOT / "analysis_boundaries" / "refined_from_plan_images"
MAP_DIR = ROOT / "reports" / "plan_image_boundary_review"
REPORT = ROOT / "reports" / "plan_image_boundary_review_report.md"


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


def save_vector(gdf: gpd.GeoDataFrame, basename: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gdf.to_file(OUT_DIR / f"{basename}_5186.geojson", driver="GeoJSON")
    gdf.to_crs(epsg=4326).to_file(OUT_DIR / f"{basename}_4326.geojson", driver="GeoJSON")
    gdf.to_file(OUT_DIR / f"{basename}_5186.shp", encoding="cp949")


def dissolve(gdf: gpd.GeoDataFrame, name: str) -> gpd.GeoDataFrame:
    out = gdf.dissolve()
    out = out[["geometry"]].copy()
    out["name"] = name
    out["feature_count"] = len(gdf)
    out["area_sqm"] = out.geometry.area
    return out[["name", "feature_count", "area_sqm", "geometry"]]


def bounds_with_pad(gdf: gpd.GeoDataFrame, pad=0.08):
    minx, miny, maxx, maxy = gdf.total_bounds
    size = max(maxx - minx, maxy - miny)
    p = size * pad
    return minx - p, miny - p, maxx + p, maxy + p


def plot_all_and_selection(
    base: gpd.GeoDataFrame,
    selected: gpd.GeoDataFrame,
    title: str,
    filename: str,
    old_boundary: gpd.GeoDataFrame | None = None,
) -> None:
    MAP_DIR.mkdir(parents=True, exist_ok=True)
    bounds = bounds_with_pad(base)
    fig, ax = plt.subplots(figsize=(13, 13))
    base.plot(ax=ax, color="#F3F4F6", edgecolor="#D1D5DB", linewidth=0.25)
    thematic = base[base["blockType"].isin(["업무시설", "업무시설기타", "도시지원시설용지", "일반상업", "근린상업", "복합용지"])]
    if not thematic.empty:
        thematic.plot(ax=ax, color="#BFDBFE", edgecolor="#2563EB", linewidth=0.5, alpha=0.75)
    selected.plot(ax=ax, color="#EF4444", edgecolor="#7F1D1D", linewidth=0.8, alpha=0.82)
    if old_boundary is not None and not old_boundary.empty:
        old_boundary.boundary.plot(ax=ax, color="#111827", linewidth=2.2, linestyle="--")

    label_gdf = pd.concat([thematic, selected], ignore_index=True).drop_duplicates(subset=["parcel_id", "blockType"])
    label_gdf = gpd.GeoDataFrame(label_gdf, geometry="geometry", crs=base.crs)
    for _, row in label_gdf.iterrows():
        pt = row.geometry.representative_point()
        label = str(row["blockName"])
        if row["blockName"] != row["lotName"] and str(row["lotName"]) not in ["", "nan", "None"]:
            label = f"{row['blockName']}-{row['lotName']}"
        ax.text(pt.x, pt.y, label, fontsize=7, ha="center", va="center", color="#111827")

    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=16, pad=14)
    ax.grid(True, color="#E5E7EB", linewidth=0.4)
    ax.ticklabel_format(style="plain", useOffset=False)
    ax.text(
        0.01,
        0.01,
        "빨강: 최종 선택 획지 / 파랑: 업무·상업·도시지원 후보 / 검정 점선: 기존 경계",
        transform=ax.transAxes,
        fontsize=10,
        bbox={"facecolor": "white", "edgecolor": "#9CA3AF", "alpha": 0.9},
    )
    fig.savefig(MAP_DIR / filename, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_boundary_comparison(old: gpd.GeoDataFrame, new: gpd.GeoDataFrame, title: str, filename: str) -> None:
    MAP_DIR.mkdir(parents=True, exist_ok=True)
    both = pd.concat([old.assign(kind="old"), new.assign(kind="new")], ignore_index=True)
    both = gpd.GeoDataFrame(both, geometry="geometry", crs=old.crs)
    bounds = bounds_with_pad(both, 0.12)
    fig, ax = plt.subplots(figsize=(10, 10))
    old.plot(ax=ax, color="#9CA3AF", edgecolor="#111827", alpha=0.25, linewidth=2, label="기존")
    new.plot(ax=ax, color="#EF4444", edgecolor="#991B1B", alpha=0.45, linewidth=2, label="신규")
    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=15, pad=14)
    ax.grid(True, color="#E5E7EB", linewidth=0.4)
    ax.ticklabel_format(style="plain", useOffset=False)
    ax.text(
        0.01,
        0.01,
        "회색: 기존 경계 / 빨강: 계획도 기준 재선택 경계",
        transform=ax.transAxes,
        fontsize=10,
        bbox={"facecolor": "white", "edgecolor": "#9CA3AF", "alpha": 0.9},
    )
    fig.savefig(MAP_DIR / filename, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def summary(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    return (
        gdf.drop(columns="geometry")
        .groupby(["zoneName", "blockType", "blockName", "lotName", "parcel_id"], dropna=False)
        .agg(feature_count=("area_sqm", "size"), area_sqm=("area_sqm", "sum"))
        .reset_index()
        .sort_values(["blockType", "parcel_id"])
    )


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

    # Image #1 shows the Pangyo business core as business/office blocks, not the whole city.
    # Keep urban-support land because it is the official land-use class for Pangyo Techno Valley,
    # and add the explicit office blocks visible in the development plan.
    pangyo_sel = pangyo_all[
        pangyo_all["blockType"].isin(["도시지원시설용지", "업무시설", "업무시설기타"])
    ].copy()

    # Image #2 labels Wirye business/commercial lots only. Exclude residential/quasi-residential
    # and parking lots, and keep business, commercial, urban-support and mixed-use lots.
    wirye_sel = wirye_all[
        wirye_all["blockType"].isin(["업무시설", "일반상업", "근린상업", "도시지원시설용지", "복합용지"])
    ].copy()

    old_pangyo = gpd.read_file(OLD_PANGYO).to_crs(5186)
    old_wirye = gpd.read_file(OLD_WIRYE).to_crs(5186)
    new_pangyo = dissolve(pangyo_sel, "판교 계획도 기준 업무·도시지원 경계")
    new_wirye = dissolve(wirye_sel, "위례 계획도 기준 업무·상업·자족 후보 경계")

    save_vector(pangyo_sel, "pangyo_final_selected_parcels")
    save_vector(new_pangyo, "pangyo_final_boundary")
    save_vector(wirye_sel, "wirye_final_selected_parcels")
    save_vector(new_wirye, "wirye_final_boundary")

    pangyo_summary = summary(pangyo_sel)
    wirye_summary = summary(wirye_sel)
    pangyo_summary.to_csv(OUT_DIR / "pangyo_selected_parcel_ids.csv", index=False, encoding="utf-8-sig")
    wirye_summary.to_csv(OUT_DIR / "wirye_selected_parcel_ids.csv", index=False, encoding="utf-8-sig")

    plot_all_and_selection(
        pangyo_all,
        pangyo_sel,
        "판교 가구및획지 전체 + 계획도 기준 선택 획지",
        "01_pangyo_all_parcels_selected.png",
        old_pangyo,
    )
    plot_all_and_selection(
        wirye_all,
        wirye_sel,
        "위례 가구및획지 전체 + 계획도 기준 선택 획지",
        "02_wirye_all_parcels_selected.png",
        old_wirye,
    )
    plot_boundary_comparison(old_pangyo, new_pangyo, "판교 기존 경계 vs 신규 경계", "03_pangyo_old_new_boundary_compare.png")
    plot_boundary_comparison(old_wirye, new_wirye, "위례 기존 경계 vs 신규 경계", "04_wirye_old_new_boundary_compare.png")

    compare = pd.DataFrame(
        [
            {
                "target": "판교",
                "old_area_sqm": float(old_pangyo.geometry.area.sum()),
                "new_area_sqm": float(new_pangyo.geometry.area.sum()),
                "new_feature_count": len(pangyo_sel),
            },
            {
                "target": "위례",
                "old_area_sqm": float(old_wirye.geometry.area.sum()),
                "new_area_sqm": float(new_wirye.geometry.area.sum()),
                "new_feature_count": len(wirye_sel),
            },
        ]
    )
    report = f"""# 계획도 이미지 기준 분석 경계 재검토 보고서

## 작업 기준

- 기준 SHP: `가구및획지/the_geom.shp`
- 판교 참고 이미지: 판교 개발계획도. 업무/도시지원 성격의 블록을 최종 후보로 재선택.
- 위례 참고 이미지: 업무·상업용지 계획도. 업무, 일반상업, 근린상업, 도시지원, 복합용지만 선택.
- 기존 경계: `analysis_boundaries`의 기존 dissolve 경계
- 산출 폴더: `analysis_boundaries/refined_from_plan_images`

## 선택 규칙

| 대상 | 선택한 blockType | 제외한 주요 blockType |
| --- | --- | --- |
| 판교 | 도시지원시설용지, 업무시설, 업무시설기타 | 주거, 공원녹지, 학교, 주차장, 위험물저장및처리시설, 일반 상업·근린상업 |
| 위례 | 업무시설, 일반상업, 근린상업, 도시지원시설용지, 복합용지 | 준주거용지, 주차장, 주거, 학교, 공원녹지 |

판교 이미지는 `업무6`, `위4` 같은 도면 표기가 보이지만 현재 SHP 속성에는 `업무6`이 없고 `위4`는 `위험물저장및처리시설`로 확인된다. 따라서 `위4`는 업무·상업 분석구역에서 제외했다.

## 기존 경계와 신규 경계 비교

{markdown_table(compare)}

## 판교 선택 획지 ID

{markdown_table(pangyo_summary, max_rows=200)}

## 위례 선택 획지 ID

{markdown_table(wirye_summary, max_rows=200)}

## 생성 파일

- `pangyo_final_boundary_5186.shp`
- `pangyo_final_boundary_4326.geojson`
- `pangyo_final_boundary_5186.geojson`
- `pangyo_final_selected_parcels_5186.shp`
- `pangyo_selected_parcel_ids.csv`
- `wirye_final_boundary_5186.shp`
- `wirye_final_boundary_4326.geojson`
- `wirye_final_boundary_5186.geojson`
- `wirye_final_selected_parcels_5186.shp`
- `wirye_selected_parcel_ids.csv`

## 비교 지도

- `reports/plan_image_boundary_review/01_pangyo_all_parcels_selected.png`
- `reports/plan_image_boundary_review/02_wirye_all_parcels_selected.png`
- `reports/plan_image_boundary_review/03_pangyo_old_new_boundary_compare.png`
- `reports/plan_image_boundary_review/04_wirye_old_new_boundary_compare.png`

## 판단

기존 판교 경계는 `도시지원시설용지`만 사용해 계획도상 업무 관련 블록 일부가 빠질 수 있었다. 신규 판교 경계는 도시지원시설용지에 명시적 업무시설/업무시설기타를 추가하여 개발계획도상 업무 핵심 구역에 더 가깝다.

기존 위례 경계는 업무1~업무28만 제한하여 일부 계획도상 업무 블록과 상업 블록을 누락할 수 있었다. 신규 위례 경계는 도면상 업무·상업·자족 후보에 해당하는 `업무시설`, `일반상업`, `근린상업`, `도시지원시설용지`, `복합용지` 전체를 포함한다.
"""
    REPORT.write_text(report, encoding="utf-8-sig")

    print(f"pangyo_features={len(pangyo_sel)}")
    print(f"pangyo_area={float(new_pangyo.geometry.area.sum()):.1f}")
    print(f"wirye_features={len(wirye_sel)}")
    print(f"wirye_area={float(new_wirye.geometry.area.sum()):.1f}")
    print(f"out={OUT_DIR}")
    print(f"maps={MAP_DIR}")
    print(f"report={REPORT}")


if __name__ == "__main__":
    main()
