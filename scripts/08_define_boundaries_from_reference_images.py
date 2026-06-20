from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager
from shapely import concave_hull
from shapely import make_valid
from shapely.geometry import MultiPolygon, Polygon


ROOT = Path(__file__).resolve().parents[1]
PARCELS = ROOT / "가구및획지" / "the_geom.shp"
OUT_DIR = ROOT / "derived_data" / "00_boundaries"
REPORT_DIR = ROOT / "derived_data" / "reports"
REPORT = REPORT_DIR / "boundary_validation_report.md"
AREA_SUMMARY = OUT_DIR / "boundary_area_summary.csv"


def set_korean_font() -> None:
    for font in ["Malgun Gothic", "NanumGothic", "AppleGothic"]:
        if any(font in f.name for f in font_manager.fontManager.ttflist):
            plt.rcParams["font.family"] = font
            break
    plt.rcParams["axes.unicode_minus"] = False


def parcel_id(row: pd.Series) -> str:
    block = "" if pd.isna(row.get("blockName")) else str(row.get("blockName"))
    lot = "" if pd.isna(row.get("lotName")) else str(row.get("lotName"))
    if not lot or lot.lower() == "nan" or lot == block:
        return block
    return f"{block}-{lot}"


def read_parcels() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(PARCELS, encoding="cp949")
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=5186)
    else:
        gdf = gdf.to_crs(epsg=5186)
    gdf["geometry"] = gdf.geometry.apply(make_valid)
    gdf["parcel_id"] = gdf.apply(parcel_id, axis=1)
    gdf["area_sqm"] = gdf.geometry.area
    for col in ["zoneName", "blockName", "blockType", "lotName"]:
        gdf[col] = gdf[col].fillna("").astype(str)
    return gdf


def select_pangyo(parcels: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    pangyo_all = parcels[parcels["zoneName"].str.contains("성남판교지구", regex=False)].copy()
    centroid = pangyo_all.geometry.centroid
    pangyo_all["centroid_x"] = centroid.x
    pangyo_all["centroid_y"] = centroid.y

    candidate = pangyo_all[
        pangyo_all["blockType"].isin(["도시지원시설용지", "업무시설", "업무시설기타", "일반상업", "근린상업"])
    ].copy()

    # The reference image for Pangyo Techno Valley first phase is the office/urban-support
    # cluster in the northeast, not all business parcels in Seongnam Pangyo district.
    selected = candidate[
        candidate["blockType"].isin(["도시지원시설용지", "업무시설", "업무시설기타"])
        & (candidate["centroid_x"] >= 208500)
        & (candidate["centroid_x"] <= 209950)
        & (candidate["centroid_y"] >= 533250)
    ].copy()

    excluded = candidate.loc[~candidate.index.isin(selected.index)].copy()
    excluded["exclude_reason"] = "제1판교테크노밸리 기준 이미지의 핵심 구역과 위치가 불일치하거나 동쪽 돌출부를 형성"
    return pangyo_all, selected, excluded


def select_wirye(parcels: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    wirye_all = parcels[parcels["zoneName"].str.contains("위례", regex=False)].copy()
    centroid = wirye_all.geometry.centroid
    wirye_all["centroid_x"] = centroid.x
    wirye_all["centroid_y"] = centroid.y

    # The reference image uses SA/SB/SC/SD labels, while the SHP stores the same
    # business/commercial area with Korean block names such as 업무, 일상, 근상,
    # 지원, and E1 mixed-use blocks. Keep those business/commercial land-use
    # classes, not the whole Wirye newtown boundary.
    allowed_types = {
        "업무시설",
        "일반상업",
        "근린상업",
        "중심상업",
        "도시지원시설용지",
        "복합용지",
        "상업시설",
        "상업업무용지",
    }
    candidate = wirye_all[wirye_all["blockType"].isin(list(allowed_types))].copy()
    selected = candidate.copy()

    excluded = candidate.loc[~candidate.index.isin(selected.index)].copy()
    excluded["exclude_reason"] = "위례 업무·상업 관련 허용 용도와 불일치"
    return wirye_all, selected, excluded


def remove_holes(geom):
    if isinstance(geom, Polygon):
        return Polygon(geom.exterior)
    if isinstance(geom, MultiPolygon):
        return MultiPolygon([Polygon(part.exterior) for part in geom.geoms])
    return geom


def make_outer_boundary(
    selected: gpd.GeoDataFrame,
    name: str,
    buffer_m: float,
    shrink_m: float,
    concave_ratio: float,
    simplify_m: float,
) -> gpd.GeoDataFrame:
    parcel_union = selected.geometry.union_all()

    # Expand selected parcels enough to absorb internal roads and small gaps,
    # then shrink partway back so the result is an analysis envelope rather than
    # a parcel-by-parcel dissolve.
    envelope = parcel_union.buffer(buffer_m, join_style="round").buffer(-shrink_m, join_style="round")
    envelope = make_valid(envelope).buffer(0)
    envelope = concave_hull(envelope, ratio=concave_ratio, allow_holes=False)
    envelope = remove_holes(envelope)
    envelope = envelope.simplify(simplify_m, preserve_topology=True)
    envelope = make_valid(envelope).buffer(0)

    boundary = gpd.GeoDataFrame({"geometry": [envelope]}, crs=selected.crs)
    boundary["name"] = name
    boundary["source"] = "reference_image_and_parcel_matching_outer_envelope"
    boundary["parcel_count"] = len(selected)
    boundary["internal_parcels_area_sqm"] = selected.geometry.area.sum()
    boundary["area_sqm"] = boundary.geometry.area
    boundary["boundary_method"] = (
        f"buffer({buffer_m}) -> dissolve -> buffer(-{shrink_m}) -> "
        f"concave_hull({concave_ratio}) -> simplify({simplify_m})"
    )
    return boundary[
        [
            "name",
            "source",
            "parcel_count",
            "internal_parcels_area_sqm",
            "area_sqm",
            "boundary_method",
            "geometry",
        ]
    ]


def make_plan_area_boundary(
    all_parcels: gpd.GeoDataFrame,
    internal_parcels: gpd.GeoDataFrame,
    name: str,
    simplify_m: float,
) -> gpd.GeoDataFrame:
    plan_geom = all_parcels.geometry.union_all()
    plan_geom = make_valid(plan_geom).buffer(0)
    plan_geom = remove_holes(plan_geom)
    plan_geom = plan_geom.simplify(simplify_m, preserve_topology=True)
    plan_geom = make_valid(plan_geom).buffer(0)

    boundary = gpd.GeoDataFrame({"geometry": [plan_geom]}, crs=all_parcels.crs)
    boundary["name"] = name
    boundary["source"] = "wirye_plan_area_outer_boundary"
    boundary["parcel_count"] = len(internal_parcels)
    boundary["internal_parcels_area_sqm"] = internal_parcels.geometry.area.sum()
    boundary["area_sqm"] = boundary.geometry.area
    boundary["boundary_method"] = f"all Wirye plan parcels dissolve -> remove holes -> simplify({simplify_m})"
    return boundary[
        [
            "name",
            "source",
            "parcel_count",
            "internal_parcels_area_sqm",
            "area_sqm",
            "boundary_method",
            "geometry",
        ]
    ]


def save_outputs(
    pangyo_selected: gpd.GeoDataFrame,
    wirye_selected: gpd.GeoDataFrame,
    pangyo_boundary: gpd.GeoDataFrame,
    wirye_boundary: gpd.GeoDataFrame,
) -> pd.DataFrame:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    keep_cols = ["zoneName", "blockName", "blockType", "lotName", "parcel_id", "area_sqm", "geometry"]
    pangyo_selected[keep_cols].to_file(OUT_DIR / "pangyo_internal_parcels.geojson", driver="GeoJSON")
    wirye_selected[keep_cols].to_file(
        OUT_DIR / "wirye_business_commercial_internal_parcels.geojson", driver="GeoJSON"
    )
    pangyo_boundary.to_file(OUT_DIR / "pangyo_boundary.geojson", driver="GeoJSON")
    wirye_boundary.to_file(OUT_DIR / "wirye_boundary.geojson", driver="GeoJSON")

    summary = pd.DataFrame(
        [
            {
                "area_name": "pangyo_1st_technovalley",
                "boundary_file": "pangyo_boundary.geojson",
                "internal_parcels_file": "pangyo_internal_parcels.geojson",
                "parcel_count": int(pangyo_boundary.iloc[0]["parcel_count"]),
                "internal_parcels_area_sqm": float(pangyo_boundary.iloc[0]["internal_parcels_area_sqm"]),
                "boundary_area_sqm": float(pangyo_boundary.iloc[0]["area_sqm"]),
                "boundary_area_ha": float(pangyo_boundary.iloc[0]["area_sqm"]) / 10000,
                "area_difference_sqm": float(pangyo_boundary.iloc[0]["area_sqm"])
                - float(pangyo_boundary.iloc[0]["internal_parcels_area_sqm"]),
                "definition_note": "제1판교테크노밸리 기준 이미지와 맞지 않는 동쪽/우측 돌출 업무 후보를 제외하고 핵심 업무·도시지원 구역의 외곽으로 정의",
            },
            {
                "area_name": "wirye_plan_area",
                "boundary_file": "wirye_boundary.geojson",
                "internal_parcels_file": "wirye_business_commercial_internal_parcels.geojson",
                "parcel_count": int(wirye_boundary.iloc[0]["parcel_count"]),
                "internal_parcels_area_sqm": float(wirye_boundary.iloc[0]["internal_parcels_area_sqm"]),
                "boundary_area_sqm": float(wirye_boundary.iloc[0]["area_sqm"]),
                "boundary_area_ha": float(wirye_boundary.iloc[0]["area_sqm"]) / 10000,
                "area_difference_sqm": float(wirye_boundary.iloc[0]["area_sqm"])
                - float(wirye_boundary.iloc[0]["internal_parcels_area_sqm"]),
                "definition_note": "업무·상업용지가 여러 곳에 분산되어 있으므로 업무·상업 필지를 억지로 연결하지 않고 위례 계획구역 전체 외곽을 분석경계로 정의",
            },
        ]
    )
    summary.to_csv(AREA_SUMMARY, index=False, encoding="utf-8-sig")
    return summary


def bounds_with_pad(gdf: gpd.GeoDataFrame, pad_ratio: float = 0.08) -> tuple[float, float, float, float]:
    minx, miny, maxx, maxy = gdf.total_bounds
    x_pad = (maxx - minx) * pad_ratio
    y_pad = (maxy - miny) * pad_ratio
    return minx - x_pad, miny - y_pad, maxx + x_pad, maxy + y_pad


def label_rows(ax, gdf: gpd.GeoDataFrame, fontsize: int = 7) -> None:
    for _, row in gdf.iterrows():
        pt = row.geometry.representative_point()
        label = row["blockName"] if row["blockName"] else row["parcel_id"]
        if row["lotName"] and row["lotName"] != row["blockName"]:
            label = f"{row['blockName']}-{row['lotName']}"
        ax.text(pt.x, pt.y, str(label), fontsize=fontsize, ha="center", va="center", color="#111827")


def plot_validation(
    all_parcels: gpd.GeoDataFrame,
    selected: gpd.GeoDataFrame,
    excluded: gpd.GeoDataFrame,
    boundary: gpd.GeoDataFrame,
    title: str,
    note: str,
    filename: str,
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(13, 13))
    whole = all_parcels.dissolve()[["geometry"]]
    whole.plot(ax=ax, color="#DBEAFE", edgecolor="#60A5FA", linewidth=1.4, alpha=0.18)
    all_parcels.plot(ax=ax, color="#F8FAFC", edgecolor="#CBD5E1", linewidth=0.25)
    if not excluded.empty:
        excluded.plot(ax=ax, color="#FCD34D", edgecolor="#92400E", linewidth=0.5, alpha=0.7)
    selected.plot(ax=ax, color="#EF4444", edgecolor="#7F1D1D", linewidth=0.7, alpha=0.45)
    boundary.plot(ax=ax, color="none", edgecolor="#111827", linewidth=3.2)
    label_source = pd.concat([selected, excluded.head(80)], ignore_index=True)
    label_gdf = gpd.GeoDataFrame(label_source, geometry="geometry", crs=selected.crs)
    label_rows(ax, label_gdf)
    extent_source = pd.concat([all_parcels, selected, excluded, boundary], ignore_index=True)
    extent_gdf = gpd.GeoDataFrame(extent_source, geometry="geometry", crs=boundary.crs)
    minx, miny, maxx, maxy = bounds_with_pad(extent_gdf, 0.08)
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=16, pad=14)
    ax.grid(True, color="#E5E7EB", linewidth=0.4)
    ax.ticklabel_format(style="plain", useOffset=False)
    ax.text(
        0.01,
        0.01,
        note,
        transform=ax.transAxes,
        fontsize=10,
        bbox={"facecolor": "white", "edgecolor": "#94A3B8", "alpha": 0.92},
    )
    fig.savefig(REPORT_DIR / filename, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def table(df: pd.DataFrame, max_rows: int = 120) -> str:
    if df.empty:
        return "(없음)"
    work = df.head(max_rows).copy().fillna("")
    lines = [
        "| " + " | ".join(work.columns) + " |",
        "| " + " | ".join("---" for _ in work.columns) + " |",
    ]
    for row in work.astype(str).values.tolist():
        lines.append("| " + " | ".join(v.replace("|", "\\|") for v in row) + " |")
    if len(df) > max_rows:
        lines.append(f"\n표시는 {max_rows}개까지만 했으며 전체 {len(df)}개 항목은 GeoJSON에 저장되어 있음.")
    return "\n".join(lines)


def selection_summary(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    return (
        gdf.groupby(["zoneName", "blockName", "blockType"], dropna=False)
        .agg(parcel_count=("parcel_id", "count"), area_sqm=("area_sqm", "sum"))
        .reset_index()
        .sort_values(["zoneName", "blockName", "blockType"])
    )


def excluded_summary(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    if gdf.empty:
        return pd.DataFrame()
    return (
        gdf.groupby(["zoneName", "blockName", "blockType", "exclude_reason"], dropna=False)
        .agg(parcel_count=("parcel_id", "count"), area_sqm=("area_sqm", "sum"))
        .reset_index()
        .sort_values(["zoneName", "blockName", "blockType"])
    )


def write_report(
    parcels: gpd.GeoDataFrame,
    pangyo_selected: gpd.GeoDataFrame,
    wirye_selected: gpd.GeoDataFrame,
    pangyo_excluded: gpd.GeoDataFrame,
    wirye_excluded: gpd.GeoDataFrame,
    area_summary: pd.DataFrame,
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    pg_summary = selection_summary(pangyo_selected)
    wr_summary = selection_summary(wirye_selected)
    pg_ex = excluded_summary(pangyo_excluded)
    wr_ex = excluded_summary(wirye_excluded)

    report = f"""# 경계 생성 및 검증 보고서

## 작업 범위

공식 경계 SHP를 확보하지 못했기 때문에, 업로드한 기준 이미지와 `가구및획지` 필지 데이터를 대조하여 분석경계를 직접 정의했다.

이번 작업은 경계 생성 및 검증만 수행했다. 토지이용혼합도, 개발실현정도, 접근성, 직주지표 등 파생지표 계산은 수행하지 않았다.

`*_internal_parcels.geojson`은 최종 분석경계가 아니라 경계 생성의 근거와 검증을 위한 내부 선택 필지 레이어다. 실제 후속 분석에서는 `*_boundary.geojson`만 분석용 경계로 사용한다.

최종 `*_boundary.geojson`은 내부 선택 필지를 일정 거리 buffer로 확장하고 dissolve한 뒤, 내부 도로·공지·필지 사이 공간을 포함하도록 외곽을 정리한 분석용 외곽 Polygon이다. 따라서 내부 선택 필지 총면적과 최종 외곽 경계 면적은 다르며, 차이는 도로, 공지, 필지 사이 공간을 포함했기 때문에 발생한다.

## 이번 수정 사항

1. 기존 위례 경계는 북부 업무·상업 클러스터만 포함하여 위례신도시 업무·상업용지 전체를 대표하기에는 너무 좁았다.
2. 이후 업무·상업 필지를 하나의 큰 Polygon으로 억지로 연결한 경계를 검토했으나, 업무·상업용지가 위례신도시 내부 여러 곳에 분산되어 있어 분석경계로 부적절하다고 판단했다.
3. 수정 후 위례 경계는 위례 계획도 이미지의 전체 계획구역 외곽을 공간적 분석경계로 설정했다.
4. 내부의 업무·상업·도시지원·복합용지는 자족기능 분석 대상으로 별도 식별하여 `wirye_business_commercial_internal_parcels.geojson`에 유지했다.
5. 기존 판교 경계에는 기준 이미지에 없는 동쪽/우측 돌출부가 있었다.
6. 수정 후 판교 경계에서는 기준 이미지와 맞지 않는 동쪽/우측 돌출 업무 후보를 제외하고, 판교역 북측·동측의 제1판교테크노밸리 핵심 업무·연구·도시지원 구역 중심으로 외곽을 재생성했다.
7. 위례 검증 이미지에서 검정 경계가 오른쪽 화면 밖으로 잘려 보인 것은 경계 geometry 오류가 아니라 검증 이미지 표시 범위가 내부 선택·제외 후보 필지 중심으로 좁게 잡힌 문제였다. `wirye_boundary.geojson`의 `total_bounds`와 위례 전체 가구획지를 기준으로 x/y 방향 8% 여백을 주어 검증 이미지 표시 범위를 보정했다.

## 위례 검증 이미지 표시 범위 보정

- `wirye_boundary.geojson` total_bounds 기준으로 검증 이미지 extent를 다시 설정했다.
- x/y 방향에 각각 8% margin을 추가했다.
- 위례 전체 외곽 검정선이 이미지 안에 완전히 들어오도록 `wirye_boundary_validation.png`를 다시 저장했다.
- 확인 결과, 오른쪽으로 잘려 보인 현상은 실제 geometry가 비정상적으로 튀어나간 문제가 아니라 검증 이미지 표시 범위 문제였다.

## 사용 데이터

- 기준 필지 데이터: `가구및획지/the_geom.shp`
- CRS: `{parcels.crs}`
- 전체 레코드 수: `{len(parcels):,}`
- 사용한 가구및획지 컬럼: `zoneName`, `blockName`, `blockType`, `lotName`, `geometry`
- 판교 기준 이미지: `판교테크노밸리제1.png`
- 위례 기준 이미지: `위례지도.png`

## 판교 경계 정의 기준

- 판교 전체 택지지구가 아니라 제1판교테크노밸리 기준 이미지의 외곽을 분석경계로 사용했다.
- `zoneName`이 `성남판교지구 택지개발사업`인 필지 중 기준 이미지와 일치하는 도시지원시설·업무시설 중심 블록을 선택했다.
- `blockType` 기준으로 `도시지원시설용지`, `업무시설`, `업무시설기타`를 1차 후보로 잡았다.
- 기준 이미지와 대조했을 때 제1판교테크노밸리 외곽은 판교역 북측·동측의 핵심 업무·연구·도시지원 구역에 해당하므로, 중심점 위치가 해당 클러스터와 맞는 필지만 최종 선택했다.
- 기준 이미지에 없는 동쪽/우측 돌출부를 만드는 소규모 공공·업무 후보는 제외했다.
- 일반상업·근린상업 후보와 남서쪽·남쪽의 분산 업무시설 후보도 기준 이미지의 제1판교테크노밸리 외곽과 위치가 맞지 않아 제외했다.

### 판교 선택 blockName/blockType 목록

{table(pg_summary)}

### 판교 제외 후보 및 제외 이유

{table(pg_ex)}

## 위례 경계 정의 기준

- 위례 업무·상업용지는 단일 블록이 아니라 위례신도시 계획구역 내부 여러 곳에 분산되어 있다.
- 따라서 업무·상업 필지를 하나의 큰 Polygon으로 억지로 연결한 경계는 사용하지 않는다.
- 위례 계획도 이미지의 전체 계획구역 외곽을 공간적 분석경계로 설정했다.
- 기준 이미지에는 `SA`, `SB`, `SC`, `SD` 등으로 표시되어 있으나, SHP에서는 같은 업무·상업 일대가 `업무`, `일상`, `근상`, `지원`, `E1` 계열 명칭으로 저장되어 있었다.
- 내부의 업무·상업·도시지원·복합용지는 자족기능 분석 대상으로 별도 식별했다.
- 내부 분석용 선택 용도는 `업무시설`, `일반상업`, `근린상업`, `중심상업`, `도시지원시설용지`, `복합용지`, `상업시설`, `상업업무용지`로 제한했다.
- 업무21, 업무22, 업무23, 업무26, 업무35, E1 계열 복합용지 등 분산된 업무·상업 후보도 내부 분석용 필지에 포함했다.
- 최종 공간 분석경계는 `wirye_boundary.geojson`이며, 내부 업무·상업 관련 필지는 `wirye_business_commercial_internal_parcels.geojson`으로 유지한다.

### 위례 선택 blockName/blockType 목록

{table(wr_summary)}

### 위례 제외 후보 및 제외 이유

{table(wr_ex)}

## 최종 면적

{table(area_summary)}

- `internal_parcels_area_sqm`: 기준 이미지와 대조해 선택한 내부 필지의 순수 합계 면적이다.
- `boundary_area_sqm`: 후속 분석에 사용할 최종 분석용 외곽 Polygon 면적이다.
- `area_difference_sqm`: 외곽 경계가 내부 도로, 공지, 필지 사이 공간을 포함하면서 증가한 면적이다.

## 산출 파일

- `derived_data/00_boundaries/pangyo_boundary.geojson`
- `derived_data/00_boundaries/pangyo_internal_parcels.geojson`
- `derived_data/00_boundaries/wirye_boundary.geojson`
- `derived_data/00_boundaries/wirye_business_commercial_internal_parcels.geojson`
- `derived_data/00_boundaries/boundary_area_summary.csv`
- `derived_data/reports/pangyo_boundary_validation.png`
- `derived_data/reports/wirye_boundary_validation.png`

## 한계

- 기준 이미지는 좌표를 가진 도면이 아니므로, 필지명·용도·상대 위치를 이용해 대조했다.
- 따라서 본 경계는 공식 고시 경계가 아니라 과제 분석을 위한 재현 가능한 작업 경계다.
- 내부 선택 필지는 경계 생성의 근거 및 자족기능 분석 대상 식별용이며, 최종 공간 분석에서는 `pangyo_boundary.geojson`과 `wirye_boundary.geojson`을 사용해야 한다.
- 향후 좌표가 있는 지구단위계획도, 가구획지계획도 원본 CAD/SHP, 또는 공식 고시도면을 확보하면 경계 보정이 필요하다.
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    set_korean_font()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    parcels = read_parcels()
    pangyo_all, pangyo_selected, pangyo_excluded = select_pangyo(parcels)
    wirye_all, wirye_selected, wirye_excluded = select_wirye(parcels)

    if pangyo_selected.empty:
        raise RuntimeError("판교 선택 필지가 비어 있습니다.")
    if wirye_selected.empty:
        raise RuntimeError("위례 선택 필지가 비어 있습니다.")

    pangyo_boundary = make_outer_boundary(
        pangyo_selected,
        "제1판교테크노밸리 분석용 외곽 경계",
        buffer_m=95,
        shrink_m=45,
        concave_ratio=0.70,
        simplify_m=35,
    )
    wirye_boundary = make_plan_area_boundary(
        wirye_all,
        wirye_selected,
        "위례 계획구역 분석경계",
        simplify_m=25,
    )
    area_summary = save_outputs(pangyo_selected, wirye_selected, pangyo_boundary, wirye_boundary)

    plot_validation(
        pangyo_all,
        pangyo_selected,
        pangyo_excluded,
        pangyo_boundary,
        "판교 제1테크노밸리 최종 분석용 외곽 경계 검증",
        "반투명 빨강: 내부 선택 필지(근거용) / 노랑: 제외 후보 / 검정선: 최종 분석용 외곽 경계",
        "pangyo_boundary_validation.png",
    )
    plot_validation(
        wirye_all,
        wirye_selected,
        wirye_excluded,
        wirye_boundary,
        "위례 계획구역 최종 분석경계 + 내부 업무·상업 필지 검증",
        "반투명 빨강: 내부 업무·상업 필지(자족기능 분석용) / 노랑: 제외 후보 / 검정선: 위례 계획구역 분석경계",
        "wirye_boundary_validation.png",
    )
    write_report(parcels, pangyo_selected, wirye_selected, pangyo_excluded, wirye_excluded, area_summary)

    print("created")
    print(AREA_SUMMARY)
    print(REPORT)
    print(area_summary.to_string(index=False))


if __name__ == "__main__":
    main()
