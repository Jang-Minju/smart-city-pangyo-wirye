from __future__ import annotations

import re
import textwrap
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager
from shapely import make_valid
from shapely.geometry import box


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "validation_maps"
REPORT_PATH = ROOT / "reports" / "data_validation_report.md"

PANGYO_BOUNDARY = ROOT / "analysis_boundaries" / "pangyo_1st_technovalley_candidate_boundary_5186.geojson"
WIRYE_BOUNDARY = ROOT / "analysis_boundaries" / "wirye_business_commercial_candidate_boundary_5186.geojson"

SEOUL_LANDUSE = ROOT / "서울용도지역" / "UPIS_C_UQ111.shp"
GYEONGGI_LANDUSE = ROOT / "경기용도지역" / "UPIS_C_UQ111.shp"
BUILDING_DIR = ROOT / "건축물"
POP_DIR = ROOT / "인구가구"


def set_korean_font() -> None:
    for font in ["Malgun Gothic", "AppleGothic", "NanumGothic"]:
        if any(font in f.name for f in font_manager.fontManager.ttflist):
            plt.rcParams["font.family"] = font
            break
    plt.rcParams["axes.unicode_minus"] = False


def read_shp(path: Path) -> gpd.GeoDataFrame:
    for encoding in ["cp949", "euc-kr", "utf-8"]:
        try:
            return gpd.read_file(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    return gpd.read_file(path)


def expand_bounds(bounds, pad_ratio: float = 0.12):
    minx, miny, maxx, maxy = bounds
    width = maxx - minx
    height = maxy - miny
    pad = max(width, height) * pad_ratio
    return minx - pad, miny - pad, maxx + pad, maxy + pad


def bbox_gdf(bounds, crs="EPSG:5186") -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(geometry=[box(*bounds)], crs=crs)


def save_fig(fig, filename: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / filename, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def setup_ax(title: str, bounds):
    fig, ax = plt.subplots(figsize=(9, 9))
    ax.set_title(title, fontsize=15, pad=14)
    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.4, color="#E5E7EB")
    ax.ticklabel_format(style="plain", useOffset=False)
    ax.set_xlabel("X (EPSG:5186)")
    ax.set_ylabel("Y (EPSG:5186)")
    return fig, ax


def add_note(ax, text: str) -> None:
    wrapped = "\n".join(textwrap.wrap(text, width=54))
    ax.text(
        0.02,
        0.02,
        wrapped,
        transform=ax.transAxes,
        fontsize=10,
        va="bottom",
        ha="left",
        bbox={"boxstyle": "round,pad=0.45", "facecolor": "white", "edgecolor": "#9CA3AF", "alpha": 0.92},
    )


def load_boundaries() -> dict[str, gpd.GeoDataFrame]:
    return {
        "pangyo": gpd.read_file(PANGYO_BOUNDARY).to_crs(epsg=5186),
        "wirye": gpd.read_file(WIRYE_BOUNDARY).to_crs(epsg=5186),
    }


def load_landuse() -> tuple[gpd.GeoDataFrame, list[dict[str, object]]]:
    frames = []
    rows = []
    for source, path in [("서울용도지역", SEOUL_LANDUSE), ("경기용도지역", GYEONGGI_LANDUSE)]:
        if not path.exists():
            rows.append({"source": source, "file": str(path.relative_to(ROOT)), "exists": False})
            continue
        gdf = read_shp(path)
        name_col = "DGM_NM" if "DGM_NM" in gdf.columns else "dgm_nm" if "dgm_nm" in gdf.columns else None
        code_col = "ATRB_SE" if "ATRB_SE" in gdf.columns else "atrb_se" if "atrb_se" in gdf.columns else None
        rows.append(
            {
                "source": source,
                "file": str(path.relative_to(ROOT)),
                "exists": True,
                "crs": str(gdf.crs),
                "records": len(gdf),
                "name_col": name_col or "",
                "code_col": code_col or "",
            }
        )
        gdf = gdf.to_crs(epsg=5186)
        gdf["geometry"] = gdf.geometry.apply(make_valid)
        gdf["source"] = source
        gdf["zone_name"] = gdf[name_col].astype(str) if name_col else ""
        gdf["zone_code"] = gdf[code_col].astype(str) if code_col else ""
        frames.append(gdf[["source", "zone_name", "zone_code", "geometry"]])
    if frames:
        return gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), geometry="geometry", crs="EPSG:5186"), rows
    return gpd.GeoDataFrame(geometry=[], crs="EPSG:5186"), rows


def clip_to_bounds(gdf: gpd.GeoDataFrame, bounds) -> gpd.GeoDataFrame:
    if gdf.empty:
        return gdf
    fixed = gdf.copy()
    fixed["geometry"] = fixed.geometry.apply(make_valid)
    return gpd.clip(fixed, bbox_gdf(bounds, gdf.crs))


def overlay_boundary_map(name: str, boundary: gpd.GeoDataFrame, filename: str) -> dict[str, object]:
    bounds = expand_bounds(boundary.total_bounds)
    fig, ax = setup_ax(f"{name} 분석 경계", bounds)
    boundary.boundary.plot(ax=ax, color="#111827", linewidth=2.4)
    boundary.plot(ax=ax, color="#60A5FA", alpha=0.28, edgecolor="#111827", linewidth=1.5)
    add_note(ax, f"경계 파일: analysis_boundaries. 면적: {boundary.geometry.area.sum():,.1f}㎡")
    save_fig(fig, filename)
    return {"map": filename, "boundary_area_sqm": float(boundary.geometry.area.sum())}


def building_metadata() -> tuple[pd.DataFrame, bool]:
    rows = []
    spatial_columns = []
    for path in sorted(BUILDING_DIR.glob("*.xlsx")):
        headers, row_count = read_xlsx_headers_and_count(path)
        lower_headers = [h.lower() for h in headers]
        spatial_hits = [
            h for h in headers
            if any(token in h.lower() for token in ["x", "y", "경도", "위도", "좌표", "pnu", "geometry", "geom"])
        ]
        rows.append(
            {
                "file": str(path.relative_to(ROOT)),
                "records_estimate": row_count,
                "column_count": len(headers),
                "spatial_columns": ", ".join(spatial_hits),
                "has_address": all(col in headers for col in ["시도", "시군구", "법정동", "번", "지"]),
            }
        )
        spatial_columns.extend(spatial_hits)
    return pd.DataFrame(rows), bool(spatial_columns)


def read_xlsx_headers_and_count(path: Path) -> tuple[list[str], int]:
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        shared = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("a:si", ns):
                shared.append("".join(t.text or "" for t in si.findall(".//a:t", ns)))
        sheet = [n for n in names if n.startswith("xl/worksheets/sheet")][0]
        root = ET.fromstring(z.read(sheet))
        rows = root.findall(".//a:row", ns)
        headers = row_values(rows[0], shared, ns) if rows else []
        nonempty_count = 0
        for row in rows[1:]:
            vals = row_values(row, shared, ns)
            if any(str(v).strip() for v in vals):
                nonempty_count += 1
        return headers, nonempty_count


def col_to_idx(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref)
    if not match:
        return 0
    n = 0
    for ch in match.group(1):
        n = n * 26 + ord(ch) - 64
    return n - 1


def row_values(row, shared, ns) -> list[str]:
    vals = {}
    for cell in row.findall("a:c", ns):
        value_node = cell.find("a:v", ns)
        value = "" if value_node is None else value_node.text or ""
        if cell.get("t") == "s" and value:
            value = shared[int(value)]
        elif cell.get("t") == "inlineStr":
            value = "".join(t.text or "" for t in cell.findall(".//a:t", ns))
        vals[col_to_idx(cell.get("r", "A1"))] = value
    if not vals:
        return []
    out = [""] * (max(vals) + 1)
    for idx, value in vals.items():
        out[idx] = value
    return out


def population_metadata() -> tuple[pd.DataFrame, bool]:
    rows = []
    has_spatial_file = any(POP_DIR.rglob("*.shp")) or any(POP_DIR.rglob("*.geojson"))
    for path in sorted(POP_DIR.glob("*인구총괄*.csv")):
        df = pd.read_csv(path, encoding="cp949", header=None, names=["year", "grid_id", "item", "value"])
        rows.append(
            {
                "file": str(path.relative_to(ROOT)),
                "records": len(df),
                "value_sum": float(pd.to_numeric(df["value"], errors="coerce").fillna(0).sum()),
                "has_geometry_file": has_spatial_file,
            }
        )
    return pd.DataFrame(rows), has_spatial_file


def overlay_building_map(name: str, boundary: gpd.GeoDataFrame, filename: str, has_spatial: bool, building_df: pd.DataFrame) -> None:
    bounds = expand_bounds(boundary.total_bounds)
    fig, ax = setup_ax(f"{name} 경계 + 건축물 검증", bounds)
    boundary.plot(ax=ax, color="#93C5FD", alpha=0.35, edgecolor="#1D4ED8", linewidth=2)
    if has_spatial:
        add_note(ax, "건축물 공간 좌표 컬럼이 확인됨.")
    else:
        total = int(building_df["records_estimate"].sum()) if not building_df.empty else 0
        add_note(ax, f"건축물대장 {len(building_df)}개 파일, 약 {total:,}개 레코드 확인. 좌표/PNU/geometry 컬럼이 없어 지도에 건축물 위치를 표시하지 못함.")
    save_fig(fig, filename)


def overlay_population_map(name: str, boundary: gpd.GeoDataFrame, filename: str, has_spatial: bool, pop_df: pd.DataFrame) -> None:
    bounds = expand_bounds(boundary.total_bounds, 0.35)
    fig, ax = setup_ax(f"{name} 주변 인구분포 검증", bounds)
    boundary.plot(ax=ax, color="#FDE68A", alpha=0.4, edgecolor="#92400E", linewidth=2)
    if has_spatial:
        add_note(ax, "인구 공간 도형 파일이 확인됨.")
    else:
        total_records = int(pop_df["records"].sum()) if not pop_df.empty else 0
        add_note(ax, f"인구 CSV {len(pop_df)}개, {total_records:,}개 레코드 확인. grid_id별 도형/SHP가 없어 공간 분포를 지도화할 수 없음.")
    save_fig(fig, filename)


def landuse_map(name: str, boundary: gpd.GeoDataFrame, landuse: gpd.GeoDataFrame, filename: str) -> tuple[pd.DataFrame, int]:
    bounds = expand_bounds(boundary.total_bounds, 0.18)
    lu = clip_to_bounds(landuse, bounds)
    intersect_count = 0
    clipped = gpd.GeoDataFrame(geometry=[], crs="EPSG:5186")
    if not lu.empty:
        clipped = gpd.overlay(lu, boundary[["geometry"]], how="intersection")
        if not clipped.empty:
            clipped["area_sqm"] = clipped.geometry.area
            intersect_count = len(clipped)

    fig, ax = setup_ax(f"{name} 경계 + 용도지역", bounds)
    if not lu.empty:
        lu.plot(ax=ax, column="zone_name", categorical=True, alpha=0.45, linewidth=0.25, edgecolor="#6B7280", legend=True)
    boundary.boundary.plot(ax=ax, color="#111827", linewidth=2.4)
    note = f"용도지역 주변 객체: {len(lu):,}건, 경계 교차 객체: {intersect_count:,}건"
    if clipped.empty:
        note += ". 경계와 교차하는 용도지역이 없거나 데이터 범위가 누락됨."
    add_note(ax, note)
    save_fig(fig, filename)

    if clipped.empty:
        return pd.DataFrame(), intersect_count
    summary = (
        clipped.groupby(["source", "zone_name"], dropna=False)["area_sqm"]
        .sum()
        .reset_index()
        .sort_values("area_sqm", ascending=False)
    )
    summary["ratio_pct"] = summary["area_sqm"] / float(boundary.geometry.area.sum()) * 100
    return summary, intersect_count


def markdown_table(df: pd.DataFrame, max_rows: int = 100) -> str:
    if df.empty:
        return "(없음)"
    d = df.head(max_rows).fillna("").astype(str)
    headers = list(d.columns)

    def clean(value):
        return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")

    lines = [
        "| " + " | ".join(clean(h) for h in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in d.values.tolist():
        lines.append("| " + " | ".join(clean(v) for v in row) + " |")
    return "\n".join(lines)


def main() -> None:
    set_korean_font()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    boundaries = load_boundaries()
    landuse, landuse_meta = load_landuse()
    building_df, building_spatial = building_metadata()
    pop_df, pop_spatial = population_metadata()

    map_rows = []
    map_rows.append({"map": "01_pangyo_boundary.png", **overlay_boundary_map("판교", boundaries["pangyo"], "01_pangyo_boundary.png")})
    map_rows.append({"map": "02_wirye_boundary.png", **overlay_boundary_map("위례", boundaries["wirye"], "02_wirye_boundary.png")})

    overlay_building_map("판교", boundaries["pangyo"], "03_pangyo_boundary_buildings.png", building_spatial, building_df)
    overlay_building_map("위례", boundaries["wirye"], "04_wirye_boundary_buildings.png", building_spatial, building_df)
    map_rows.extend([
        {"map": "03_pangyo_boundary_buildings.png", "boundary_area_sqm": float(boundaries["pangyo"].geometry.area.sum())},
        {"map": "04_wirye_boundary_buildings.png", "boundary_area_sqm": float(boundaries["wirye"].geometry.area.sum())},
    ])

    pangyo_lu_summary, pangyo_lu_count = landuse_map("판교", boundaries["pangyo"], landuse, "05_pangyo_boundary_landuse.png")
    wirye_lu_summary, wirye_lu_count = landuse_map("위례", boundaries["wirye"], landuse, "06_wirye_boundary_landuse.png")
    map_rows.extend([
        {"map": "05_pangyo_boundary_landuse.png", "landuse_intersect_features": pangyo_lu_count},
        {"map": "06_wirye_boundary_landuse.png", "landuse_intersect_features": wirye_lu_count},
    ])

    overlay_population_map("판교", boundaries["pangyo"], "07_pangyo_population.png", pop_spatial, pop_df)
    overlay_population_map("위례", boundaries["wirye"], "08_wirye_population.png", pop_spatial, pop_df)
    map_rows.extend([
        {"map": "07_pangyo_population.png", "population_spatialized": pop_spatial},
        {"map": "08_wirye_population.png", "population_spatialized": pop_spatial},
    ])

    crs_rows = [
        {"dataset": "판교 분석 경계", "crs": str(boundaries["pangyo"].crs), "status": "OK"},
        {"dataset": "위례 분석 경계", "crs": str(boundaries["wirye"].crs), "status": "OK"},
        *[
            {"dataset": row["source"], "crs": row.get("crs", ""), "status": "좌표계 변환 후 사용" if row.get("exists") else "파일 없음"}
            for row in landuse_meta
        ],
        {"dataset": "건축물대장", "crs": "없음", "status": "좌표/geometry 없음"},
        {"dataset": "인구가구 CSV", "crs": "없음", "status": "grid_id 도형 없음"},
    ]
    crs_df = pd.DataFrame(crs_rows)

    outside_rows = [
        {"dataset": "판교 용도지역", "outside_or_missing": pangyo_lu_count == 0, "detail": f"교차 객체 {pangyo_lu_count}건"},
        {"dataset": "위례 용도지역", "outside_or_missing": wirye_lu_count == 0, "detail": f"교차 객체 {wirye_lu_count}건"},
        {"dataset": "건축물", "outside_or_missing": True, "detail": "좌표/PNU/geometry 없음. 경계 밖 여부 판정 불가"},
        {"dataset": "인구", "outside_or_missing": True, "detail": "grid_id 도형 없음. 경계 밖 여부 판정 불가"},
    ]
    outside_df = pd.DataFrame(outside_rows)
    pangyo_lu_ratio_sum = float(pangyo_lu_summary["ratio_pct"].sum()) if not pangyo_lu_summary.empty else 0.0
    wirye_lu_ratio_sum = float(wirye_lu_summary["ratio_pct"].sum()) if not wirye_lu_summary.empty else 0.0
    landuse_overlap_df = pd.DataFrame(
        [
            {
                "target": "판교",
                "raw_ratio_sum_pct": pangyo_lu_ratio_sum,
                "overlap_warning": pangyo_lu_ratio_sum > 100.5,
            },
            {
                "target": "위례",
                "raw_ratio_sum_pct": wirye_lu_ratio_sum,
                "overlap_warning": wirye_lu_ratio_sum > 100.5,
            },
        ]
    )

    report = f"""# 데이터 검증용 시각화 및 품질 점검 보고서

## 생성 PNG

{markdown_table(pd.DataFrame(map_rows), max_rows=20)}

저장 폴더: `reports/validation_maps/`

## 좌표계 검토

{markdown_table(crs_df, max_rows=50)}

판교/위례 분석 경계는 EPSG:5186이다. 용도지역 SHP는 EPSG:5174로 들어오며, 지도 생성과 clip 계산에서 EPSG:5186으로 변환했다.

## 경계 밖 데이터 및 누락 데이터 검토

{markdown_table(outside_df, max_rows=50)}

## 건축물 데이터 검토

{markdown_table(building_df, max_rows=20)}

건축물대장에는 주소, 용도, 면적, 층수 등 속성은 있으나 좌표, PNU, geometry 컬럼이 없어 현재 데이터만으로는 경계와 공간 결합하거나 건축물 위치를 지도에 표시할 수 없다.

## 인구 데이터 검토

{markdown_table(pop_df, max_rows=20)}

인구 CSV는 `year`, `grid_id`, `item`, `value` 형태의 집계값이다. `인구가구` 폴더에는 grid_id에 대응되는 격자 또는 집계구 도형 파일이 없어 현재 데이터만으로는 공간 분포도를 생성할 수 없다.

## 판교 용도지역 Clip 결과

{markdown_table(pangyo_lu_summary, max_rows=50)}

## 위례 용도지역 Clip 결과

{markdown_table(wirye_lu_summary, max_rows=50)}

## 용도지역 중복 검토

{markdown_table(landuse_overlap_df, max_rows=10)}

위례는 서울용도지역과 경기용도지역 원시 교차 면적을 단순 합산하면 100%를 초과한다. 이는 행정경계 인접부에서 두 자료가 일부 중첩되거나, 동일 경계 영역을 양쪽 자료가 동시에 덮는 구간이 있다는 뜻이다. 최종 구성비 산정 단계에서는 서울/경기 행정경계로 분석 경계를 먼저 분할하거나, 중복 영역의 우선순위를 정해 한쪽 자료만 사용해야 한다. 현재 PNG는 검증용 겹침 확인 지도이며, 위 표는 원시 교차 결과다.

## 종합 판단

- 경계 데이터: 판교/위례 모두 정상 로드 및 PNG 생성 완료.
- 용도지역 데이터: 서울/경기 `UPIS_C_UQ111.shp`를 사용해 clip 가능. 좌표계는 EPSG:5174에서 EPSG:5186으로 변환했다.
- 건축물 데이터: 속성 테이블은 존재하지만 공간 좌표가 없어 지도화와 경계 내외 검증이 불가하다. 지번 기반 필지 SHP 또는 PNU 좌표/필지 도형이 필요하다.
- 인구 데이터: 인구 값은 존재하지만 격자/집계구 geometry가 없어 지도화와 경계 내외 검증이 불가하다. 동일 grid_id 기준의 인구격자 SHP/GeoJSON이 필요하다.
"""
    REPORT_PATH.write_text(report, encoding="utf-8-sig")
    print(f"maps={OUT_DIR}")
    print(f"report={REPORT_PATH}")
    print(f"pangyo_landuse_intersections={pangyo_lu_count}")
    print(f"wirye_landuse_intersections={wirye_lu_count}")
    print(f"building_spatial={building_spatial}")
    print(f"population_spatial={pop_spatial}")


if __name__ == "__main__":
    main()
