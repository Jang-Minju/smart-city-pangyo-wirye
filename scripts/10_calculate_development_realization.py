from __future__ import annotations

from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET
import warnings

import geopandas as gpd
import pandas as pd
from shapely import make_valid


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "derived_data" / "02_development_realization"
REPORT = OUT_DIR / "development_realization_report.md"
AREA_CRS = "EPSG:5186"
REFERENCE_DATE = pd.Timestamp("2023-12-31")

DATE_SOURCE_COLUMNS = {
    "use_approval_date": "사용승인일",
    "start_date": "착공일",
    "permit_date": "허가일",
}

PANGYO_BOUNDARY = ROOT / "derived_data" / "00_boundaries" / "pangyo_boundary_user_drawn2_5186.geojson"
WIRYE_BOUNDARY = ROOT / "derived_data" / "00_boundaries" / "wirye_boundary.geojson"
BUILDING_DIR = ROOT / "건축물"
CADASTRAL_CANDIDATE_DIRS = ["연속지적도", "연속지적도_송파_하남_수정_분당", "cadastral", "parcel", "지적도"]

AREA_NAMES = {
    "pangyo": "pangyo_1st_technovalley",
    "wirye": "wirye_plan_area",
}

SIGUNGU_CODE = {
    "송파구": "11710",
    "성남시 수정구": "41131",
    "성남시 분당구": "41135",
    "하남시": "41450",
}
TARGET_SIGUNGU = set(SIGUNGU_CODE)

BUSINESS_KEYWORDS = ["업무시설", "사무소", "지식산업센터", "연구소", "벤처기업"]
RESEARCH_KEYWORDS = ["교육연구시설", "연구"]


def col_idx(cell_ref: str) -> int:
    letters = "".join(re.findall(r"[A-Z]+", cell_ref))
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_xlsx_xml(path: Path) -> pd.DataFrame:
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rows: list[list[str]] = []
    with zipfile.ZipFile(path) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("a:si", ns):
                shared.append("".join(t.text or "" for t in si.findall(".//a:t", ns)))
        sheet_path = "xl/worksheets/sheet1.xml"
        for _, elem in ET.iterparse(z.open(sheet_path), events=("end",)):
            if not elem.tag.endswith("row"):
                continue
            vals: dict[int, str] = {}
            max_col = -1
            for cell in list(elem):
                if not cell.tag.endswith("c"):
                    continue
                idx = col_idx(cell.attrib.get("r", "A1"))
                max_col = max(max_col, idx)
                cell_type = cell.attrib.get("t")
                value = ""
                v = cell.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
                if v is not None and v.text is not None:
                    value = v.text
                    if cell_type == "s":
                        value = shared[int(value)]
                elif cell_type == "inlineStr":
                    value = "".join(
                        t.text or "" for t in cell.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
                    )
                vals[idx] = value
            rows.append([vals.get(i, "") for i in range(max_col + 1)])
            elem.clear()
    if not rows:
        return pd.DataFrame()
    header = rows[0]
    width = len(header)
    data = [r + [""] * (width - len(r)) if len(r) < width else r[:width] for r in rows[1:]]
    return pd.DataFrame(data, columns=header)


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


def normalize_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False).str.strip(), errors="coerce")


def parse_date(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.replace(r"[^0-9]", "", regex=True)
    s = s.where(s.str.len() >= 8, None)
    return pd.to_datetime(s.str[:8], format="%Y%m%d", errors="coerce")


def list_building_files() -> list[Path]:
    files = sorted(BUILDING_DIR.glob("*.xlsx")) + sorted(BUILDING_DIR.glob("*.csv"))
    return [path for path in files if not path.name.startswith("~$")]


def apply_reference_date_filter(buildings: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    work = buildings.copy()
    work["effective_date"] = work["use_approval_date"]
    work["date_basis"] = "사용승인일"

    missing_effective = work["effective_date"].isna() & work["start_date"].notna()
    work.loc[missing_effective, "effective_date"] = work.loc[missing_effective, "start_date"]
    work.loc[missing_effective, "date_basis"] = "착공일"

    missing_effective = work["effective_date"].isna() & work["permit_date"].notna()
    work.loc[missing_effective, "effective_date"] = work.loc[missing_effective, "permit_date"]
    work.loc[missing_effective, "date_basis"] = "허가일"

    work.loc[work["effective_date"].isna(), "date_basis"] = "날짜없음"
    work["effective_year"] = work["effective_date"].dt.year
    work["is_post_reference_date"] = work["effective_date"].gt(REFERENCE_DATE)

    excluded = work[work["is_post_reference_date"]].copy()
    kept = work[~work["is_post_reference_date"]].copy()

    stats = {
        "reference_date": REFERENCE_DATE.strftime("%Y-%m-%d"),
        "total_rows_before_filter": int(len(work)),
        "kept_rows_after_filter": int(len(kept)),
        "excluded_rows_post_reference_date": int(len(excluded)),
        "missing_all_dates_rows_kept": int(kept["effective_date"].isna().sum()),
        "date_basis_counts_all": work["date_basis"].value_counts(dropna=False).to_dict(),
        "date_basis_counts_kept": kept["date_basis"].value_counts(dropna=False).to_dict(),
        "excluded_year_counts": excluded["effective_year"].value_counts(dropna=False).sort_index().to_dict(),
        "excluded_floor_area_sqm_total": float(excluded["total_floor_area_sqm"].fillna(0).sum()),
    }
    return kept, stats


def normalize_bunji(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    digits = re.sub(r"[^0-9]", "", text)
    if digits == "":
        digits = "0"
    return f"{int(digits):04d}"


def make_building_join_key(df: pd.DataFrame) -> pd.Series:
    sigungu_code = df["시군구"].map(SIGUNGU_CODE).fillna("")
    bun = df["번"].map(normalize_bunji)
    ji = df["지"].map(normalize_bunji)
    return sigungu_code + "_" + bun + "_" + ji


def make_parcel_join_key(pnu: pd.Series) -> pd.Series:
    s = pnu.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(19)
    return s.str[:5] + "_" + s.str[11:15] + "_" + s.str[15:19]


def read_boundaries() -> dict[str, gpd.GeoDataFrame]:
    out = {}
    for area_name, path in [
        (AREA_NAMES["pangyo"], PANGYO_BOUNDARY),
        (AREA_NAMES["wirye"], WIRYE_BOUNDARY),
    ]:
        gdf = clean_geometries(to_area_crs(gpd.read_file(path)))
        out[area_name] = gdf[["geometry"]].copy()
    return out


def find_cadastral_files() -> list[Path]:
    files: list[Path] = []
    for name in CADASTRAL_CANDIDATE_DIRS:
        folder = ROOT / name
        if folder.exists():
            files.extend(sorted(folder.rglob("*.shp")))
    return files


def read_cadastral(boundaries: dict[str, gpd.GeoDataFrame]) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    files = find_cadastral_files()
    metas: list[dict] = []
    frames: list[gpd.GeoDataFrame] = []
    for path in files:
        gdf = read_file(path)
        metas.append(
            {
                "file": str(path.relative_to(ROOT)),
                "original_crs": str(gdf.crs),
                "columns": ", ".join(gdf.columns),
                "row_count": len(gdf),
            }
        )
        if "PNU" not in gdf.columns:
            continue
        gdf = clean_geometries(to_area_crs(gdf))
        gdf["pnu"] = gdf["PNU"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(19)
        gdf["jibun"] = gdf.get("JIBUN", "").astype(str)
        gdf["join_key"] = make_parcel_join_key(gdf["pnu"])
        gdf["parcel_id"] = gdf["pnu"]
        gdf["source_file"] = str(path.relative_to(ROOT))
        frames.append(gdf[["pnu", "jibun", "join_key", "parcel_id", "source_file", "geometry"]])
    if not frames:
        return gpd.GeoDataFrame(columns=["pnu", "jibun", "join_key", "parcel_id", "source_file", "geometry"], crs=AREA_CRS), pd.DataFrame(metas)
    parcels = pd.concat(frames, ignore_index=True)
    parcels = gpd.GeoDataFrame(parcels, geometry="geometry", crs=AREA_CRS)
    parcels = parcels.drop_duplicates(subset=["pnu"]).copy()
    return parcels, pd.DataFrame(metas)


def read_buildings() -> tuple[pd.DataFrame, pd.DataFrame]:
    files = sorted(BUILDING_DIR.glob("*.xlsx")) + sorted(BUILDING_DIR.glob("*.csv"))
    frames: list[pd.DataFrame] = []
    metas: list[dict] = []
    for path in files:
        if path.suffix.lower() == ".xlsx":
            df = read_xlsx_xml(path)
        else:
            df = pd.read_csv(path, encoding="cp949")
        df["source_file"] = str(path.relative_to(ROOT))
        df["row_id"] = range(1, len(df) + 1)
        metas.append({"file": str(path.relative_to(ROOT)), "row_count": len(df), "columns": ", ".join(df.columns)})
        frames.append(df)
    if not frames:
        return pd.DataFrame(), pd.DataFrame(metas)
    buildings = pd.concat(frames, ignore_index=True)
    buildings = buildings[buildings["시군구"].isin(TARGET_SIGUNGU)].copy()
    buildings["building_uid"] = buildings["source_file"].astype(str) + "#" + buildings["row_id"].astype(str)
    buildings["join_key"] = make_building_join_key(buildings)
    buildings["sido"] = buildings["시도"]
    buildings["sigungu"] = buildings["시군구"]
    buildings["bjdong"] = buildings["법정동"]
    buildings["bun"] = buildings["번"]
    buildings["ji"] = buildings["지"]
    buildings["address"] = (
        buildings["시도"].fillna("").astype(str)
        + " "
        + buildings["시군구"].fillna("").astype(str)
        + " "
        + buildings["법정동"].fillna("").astype(str)
        + " "
        + buildings["번"].fillna("").astype(str)
        + "-"
        + buildings["지"].fillna("").astype(str)
    )
    numeric_map = {
        "대지면적(㎡)": "site_area_sqm",
        "건축면적(㎡)": "building_area_sqm",
        "연면적(㎡)": "total_floor_area_sqm",
        "용적률(%)": "far",
        "건폐율(%)": "bcr",
        "용적률산정연면적(㎡)": "far_calc_floor_area_sqm",
    }
    for src, dst in numeric_map.items():
        buildings[dst] = normalize_number(buildings[src]) if src in buildings.columns else pd.NA
    buildings["main_use"] = buildings["주용도"].fillna("미분류").astype(str).str.strip()
    buildings.loc[buildings["main_use"].eq(""), "main_use"] = "미분류"
    buildings["other_use"] = buildings.get("기타용도", "").fillna("").astype(str)
    buildings["approval_date"] = parse_date(buildings["사용승인일"]) if "사용승인일" in buildings.columns else pd.NaT
    buildings["approval_year"] = buildings["approval_date"].dt.year
    buildings["is_business"] = buildings.apply(classify_business, axis=1)
    return buildings, pd.DataFrame(metas)


def read_buildings_filtered_2023() -> tuple[pd.DataFrame, pd.DataFrame]:
    files = list_building_files()
    frames: list[pd.DataFrame] = []
    metas: list[dict] = []
    for path in files:
        if path.suffix.lower() == ".xlsx":
            df = read_xlsx_xml(path)
        else:
            df = pd.read_csv(path, encoding="cp949")
        df["source_file"] = str(path.relative_to(ROOT))
        df["row_id"] = range(1, len(df) + 1)
        metas.append({"file": str(path.relative_to(ROOT)), "row_count": len(df), "columns": ", ".join(df.columns)})
        frames.append(df)
    if not frames:
        return pd.DataFrame(), pd.DataFrame(metas)

    buildings = pd.concat(frames, ignore_index=True)
    buildings = buildings[buildings["시군구"].isin(["송파구", "성남시 수정구", "성남시 분당구", "하남시"])].copy()
    buildings["building_uid"] = buildings["source_file"].astype(str) + "#" + buildings["row_id"].astype(str)
    buildings["join_key"] = make_building_join_key(buildings)
    buildings["sido"] = buildings["시도"]
    buildings["sigungu"] = buildings["시군구"]
    buildings["bjdong"] = buildings["법정동"]
    buildings["bun"] = buildings["번"]
    buildings["ji"] = buildings["지"]
    buildings["address"] = (
        buildings["시도"].fillna("").astype(str)
        + " "
        + buildings["시군구"].fillna("").astype(str)
        + " "
        + buildings["법정동"].fillna("").astype(str)
        + " "
        + buildings["번"].fillna("").astype(str)
        + "-"
        + buildings["지"].fillna("").astype(str)
    )
    numeric_map = {
        "대지면적(㎡)": "site_area_sqm",
        "건축면적(㎡)": "building_area_sqm",
        "연면적(㎡)": "total_floor_area_sqm",
        "용적률(%)": "far",
        "건폐율(%)": "bcr",
        "용적률산정연면적(㎡)": "far_calc_floor_area_sqm",
    }
    for src, dst in numeric_map.items():
        buildings[dst] = normalize_number(buildings[src]) if src in buildings.columns else pd.NA
    buildings["main_use"] = buildings["주용도"].fillna("미분류").astype(str).str.strip()
    buildings.loc[buildings["main_use"].eq(""), "main_use"] = "미분류"
    buildings["other_use"] = buildings.get("기타용도", "").fillna("").astype(str)
    for dst, src in DATE_SOURCE_COLUMNS.items():
        buildings[dst] = parse_date(buildings[src]) if src in buildings.columns else pd.NaT
    buildings["approval_date"] = buildings["use_approval_date"]
    buildings["approval_year"] = buildings["approval_date"].dt.year
    buildings["is_business"] = buildings.apply(classify_business, axis=1)

    filtered, filter_stats = apply_reference_date_filter(buildings)
    filtered["approval_date"] = filtered["effective_date"]
    filtered["approval_year"] = filtered["effective_year"]

    metas_df = pd.DataFrame(metas)
    metas_df.attrs["filter_stats"] = filter_stats
    return filtered, metas_df


def classify_business(row: pd.Series) -> bool:
    text = f"{row.get('main_use', '')} {row.get('other_use', '')}"
    if any(k in text for k in BUSINESS_KEYWORDS):
        return True
    if "공장" in text and "지식산업센터" in text:
        return True
    return False


def parcels_by_area(parcels: gpd.GeoDataFrame, boundaries: dict[str, gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
    out: list[gpd.GeoDataFrame] = []
    for area_name, boundary in boundaries.items():
        minx, miny, maxx, maxy = boundary.total_bounds
        cand = parcels.cx[minx:maxx, miny:maxy].copy()
        cent = cand.copy()
        cent["geometry"] = cent.geometry.representative_point()
        inside_idx = gpd.sjoin(cent, boundary, predicate="within", how="inner").index.unique()
        selected = cand.loc[inside_idx].copy()
        selected["area_name"] = area_name
        selected["parcel_area_sqm"] = selected.geometry.area
        out.append(selected)
    if not out:
        return gpd.GeoDataFrame(columns=[*parcels.columns, "area_name", "parcel_area_sqm"], crs=AREA_CRS)
    return gpd.GeoDataFrame(pd.concat(out, ignore_index=True), geometry="geometry", crs=AREA_CRS)


def join_buildings_to_parcels(
    buildings: pd.DataFrame,
    parcels: gpd.GeoDataFrame,
    area_parcels: gpd.GeoDataFrame,
) -> tuple[gpd.GeoDataFrame, pd.DataFrame, dict]:
    parcel_join = parcels[["pnu", "jibun", "join_key", "parcel_id", "geometry"]].copy()
    counts = parcel_join.groupby("join_key")["pnu"].nunique().reset_index(name="parcel_key_count")
    parcel_join = parcel_join.merge(counts, on="join_key", how="left")
    joined_all = buildings.merge(parcel_join, on="join_key", how="left", suffixes=("", "_parcel"))
    joined_all["join_status"] = joined_all["pnu"].notna().map({True: "joined", False: "failed"})

    success_uids = set(joined_all.loc[joined_all["join_status"].eq("joined"), "building_uid"])
    failures = buildings[~buildings["building_uid"].isin(success_uids)].copy()
    failures["reason"] = "대체 조인키(시군구코드+본번+부번)에 대응하는 연속지적도 필지를 찾지 못함"

    area_lookup = area_parcels[["area_name", "pnu", "parcel_area_sqm"]].drop_duplicates(subset=["area_name", "pnu"])
    joined_area = joined_all[joined_all["join_status"].eq("joined")].merge(area_lookup, on="pnu", how="inner")
    joined_area = joined_area.drop_duplicates(subset=["building_uid", "area_name", "pnu"]).copy()
    joined_gdf = gpd.GeoDataFrame(joined_area, geometry="geometry", crs=AREA_CRS)
    join_stats = {
        "total_building_rows": len(buildings),
        "join_success_rows": len(success_uids),
        "join_failure_rows": len(failures),
        "join_success_rate": len(success_uids) / len(buildings) if len(buildings) else 0,
        "joined_all_rows_after_duplicate_expansion": len(joined_all[joined_all["join_status"].eq("joined")]),
    }
    return joined_gdf, failures, join_stats


def valid_far(series: pd.Series) -> pd.Series:
    return series.where((series > 0) & (series <= 3000))


def valid_bcr(series: pd.Series) -> pd.Series:
    return series.where((series > 0) & (series <= 100))


def build_outputs(
    buildings: pd.DataFrame,
    parcels_area: gpd.GeoDataFrame,
    joined: gpd.GeoDataFrame,
    failures: pd.DataFrame,
    boundaries: dict[str, gpd.GeoDataFrame],
    join_stats: dict,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, gpd.GeoDataFrame, pd.DataFrame]:
    joined = joined.copy()
    joined["far_valid"] = valid_far(joined["far"])
    joined["bcr_valid"] = valid_bcr(joined["bcr"])

    use = (
        joined.groupby(["area_name", "main_use"], dropna=False)
        .agg(building_count=("row_id", "count"), total_floor_area_sqm=("total_floor_area_sqm", "sum"))
        .reset_index()
    )
    use["building_count_ratio"] = use["building_count"] / use.groupby("area_name")["building_count"].transform("sum")
    use["floor_area_ratio"] = use["total_floor_area_sqm"] / use.groupby("area_name")["total_floor_area_sqm"].transform("sum")
    use = use[["area_name", "main_use", "building_count", "building_count_ratio", "total_floor_area_sqm", "floor_area_ratio"]]

    rows: list[dict] = []
    for area_name in boundaries:
        b = joined[joined["area_name"].eq(area_name)].copy()
        p = parcels_area[parcels_area["area_name"].eq(area_name)].copy()
        parcel_count = p["pnu"].nunique()
        developed = b["pnu"].nunique()
        unbuilt = max(parcel_count - developed, 0)
        total_floor = b["total_floor_area_sqm"].fillna(0).sum()
        business = b[b["is_business"].fillna(False)]
        far_weighted = pd.NA
        far_weight_source = b[b["far_valid"].notna() & b["total_floor_area_sqm"].gt(0)]
        if far_weight_source["total_floor_area_sqm"].sum() > 0:
            far_weighted = (far_weight_source["far_valid"] * far_weight_source["total_floor_area_sqm"]).sum() / far_weight_source["total_floor_area_sqm"].sum()
        join_success_rate = join_stats["join_success_rate"]
        note_parts = []
        if len(b) == 0:
            note_parts.append("경계 내 조인 건축물 없음")
        dup_keys = p["join_key"].duplicated().sum()
        if dup_keys:
            note_parts.append(f"경계 내 대체 조인키 중복 필지 {dup_keys}건 존재")
        rows.append(
            {
                "area_name": area_name,
                "boundary_area_sqm": float(boundaries[area_name].geometry.area.sum()),
                "parcel_count": int(parcel_count),
                "joined_building_count": int(len(b)),
                "developed_parcel_count": int(developed),
                "estimated_unbuilt_parcel_count": int(unbuilt),
                "developed_parcel_ratio": developed / parcel_count if parcel_count else 0,
                "estimated_unbuilt_parcel_ratio": unbuilt / parcel_count if parcel_count else 0,
                "avg_far": b["far_valid"].mean(),
                "floor_area_weighted_far": far_weighted,
                "avg_bcr": b["bcr_valid"].mean(),
                "total_building_floor_area_sqm": total_floor,
                "total_building_area_sqm": b["building_area_sqm"].fillna(0).sum(),
                "business_building_count": int(len(business)),
                "business_floor_area_sqm": business["total_floor_area_sqm"].fillna(0).sum(),
                "business_floor_area_ratio": business["total_floor_area_sqm"].fillna(0).sum() / total_floor if total_floor else 0,
                "business_floor_area_density_sqm_per_ha": (
                    business["total_floor_area_sqm"].fillna(0).sum()
                    / (float(boundaries[area_name].geometry.area.sum()) / 10000)
                    if float(boundaries[area_name].geometry.area.sum()) > 0
                    else 0
                ),
                "join_success_rate": join_success_rate,
                "note": "; ".join(note_parts),
            }
        )
    summary = pd.DataFrame(rows)

    ts_rows: list[pd.DataFrame] = []
    for area_name, b in joined[joined["effective_year"].notna()].groupby("area_name"):
        ts = (
            b.groupby("effective_year")
            .agg(approved_building_count=("row_id", "count"), approved_floor_area_sqm=("total_floor_area_sqm", "sum"))
            .reset_index()
            .sort_values("effective_year")
        )
        ts["area_name"] = area_name
        ts["cumulative_building_count"] = ts["approved_building_count"].cumsum()
        ts["cumulative_floor_area_sqm"] = ts["approved_floor_area_sqm"].cumsum()
        ts = ts.rename(columns={"effective_year": "approval_year"})
        ts_rows.append(ts[["area_name", "approval_year", "approved_building_count", "approved_floor_area_sqm", "cumulative_building_count", "cumulative_floor_area_sqm"]])
    timeseries = pd.concat(ts_rows, ignore_index=True) if ts_rows else pd.DataFrame(columns=["area_name", "approval_year", "approved_building_count", "approved_floor_area_sqm", "cumulative_building_count", "cumulative_floor_area_sqm"])
    if not timeseries.empty:
        timeseries["approval_year"] = timeseries["approval_year"].astype(int)

    developed_pnu = set(joined["pnu"].dropna().astype(str))
    vacant = parcels_area[~parcels_area["pnu"].astype(str).isin(developed_pnu)].copy()
    vacant["join_status"] = "not_joined_to_building_register"
    vacant["estimated_status"] = "미건축/공지 추정"
    vacant["note"] = "건축물대장 조인 실패와 실제 미건축 필지가 혼재될 수 있음"
    vacant_out = pd.DataFrame(vacant.drop(columns="geometry"))[
        ["area_name", "parcel_id", "pnu", "jibun", "parcel_area_sqm", "join_status", "estimated_status", "note"]
    ]

    joined_out = joined.copy()
    joined_out["approval_date"] = joined_out["approval_date"].dt.strftime("%Y-%m-%d")
    joined_out["use_approval_date"] = joined_out["use_approval_date"].dt.strftime("%Y-%m-%d")
    joined_out["start_date"] = joined_out["start_date"].dt.strftime("%Y-%m-%d")
    joined_out["permit_date"] = joined_out["permit_date"].dt.strftime("%Y-%m-%d")
    joined_out["effective_date"] = joined_out["effective_date"].dt.strftime("%Y-%m-%d")
    joined_out = joined_out[
        [
            "area_name",
            "pnu",
            "main_use",
            "total_floor_area_sqm",
            "building_area_sqm",
            "far",
            "bcr",
            "approval_date",
            "approval_year",
            "use_approval_date",
            "start_date",
            "permit_date",
            "effective_date",
            "effective_year",
            "date_basis",
            "join_status",
            "geometry",
        ]
    ]

    fail_out = failures[["source_file", "row_id", "sido", "sigungu", "bjdong", "bun", "ji", "address", "main_use", "reason"]].copy()
    return use, summary, timeseries, vacant_out, joined_out, fail_out


def md_table(df: pd.DataFrame, max_rows: int = 30) -> str:
    if df.empty:
        return "(없음)"
    work = df.head(max_rows).copy()
    for col in work.columns:
        if pd.api.types.is_float_dtype(work[col]):
            work[col] = work[col].map(lambda x: "" if pd.isna(x) else f"{x:.6f}")
    lines = ["| " + " | ".join(work.columns) + " |", "| " + " | ".join("---" for _ in work.columns) + " |"]
    for row in work.fillna("").astype(str).values.tolist():
        lines.append("| " + " | ".join(v.replace("|", "\\|") for v in row) + " |")
    if len(df) > max_rows:
        lines.append(f"\n총 {len(df)}행 중 {max_rows}행만 표시.")
    return "\n".join(lines)


def write_report(
    building_meta: pd.DataFrame,
    cadastral_meta: pd.DataFrame,
    buildings: pd.DataFrame,
    parcels: gpd.GeoDataFrame,
    joined: gpd.GeoDataFrame,
    failures: pd.DataFrame,
    join_stats: dict,
    use_comp: pd.DataFrame,
    summary: pd.DataFrame,
    timeseries: pd.DataFrame,
    warnings_list: list[str],
) -> None:
    total_rows = join_stats["total_building_rows"]
    success_rows = join_stats["join_success_rows"]
    fail_rows = join_stats["join_failure_rows"]
    success_rate = join_stats["join_success_rate"]
    report = f"""# 개발 실현 정도 보고서

## 1. 작업 목적

판교 제1테크노밸리와 위례 계획구역에서 계획된 업무·상업·도시지원 기능이 실제 건축물로 얼마나 실현되었는지 비교하기 위해 건축물대장과 연속지적도를 조인하여 개발 실현 정도 지표를 산출했다.

이번 작업에서는 개발 실현 정도 관련 지표만 계산했다. 토지이용혼합도 LUM, SGIS, 접근성, 역세권, 산업특화도, 대시보드는 계산하지 않았다.

## 2. 사용한 분석경계 파일

- 판교: `derived_data/00_boundaries/pangyo_boundary_user_drawn2_5186.geojson`
- 위례: `derived_data/00_boundaries/wirye_boundary.geojson`
- 내부 필지 파일은 최종 clip 기준으로 사용하지 않았다.

## 3. 사용한 건축물대장 파일 목록

{md_table(building_meta)}

## 4. 사용한 연속지적도 파일 목록

{md_table(cadastral_meta[["file", "original_crs", "row_count"]])}

## 5. 각 데이터 CRS

- 분석경계 CRS: `EPSG:5186`
- 연속지적도 원본 CRS: {", ".join(sorted(cadastral_meta["original_crs"].dropna().unique()))}
- 건축물대장: 비공간 속성자료, CRS 없음

## 6. 면적 계산 CRS

- `{AREA_CRS}`

## 7. 건축물대장 주요 컬럼명

- 대지면적: `대지면적(㎡)`
- 건축면적: `건축면적(㎡)`
- 연면적: `연면적(㎡)`
- 용적률: `용적률(%)`
- 건폐율: `건폐율(%)`
- 용적률산정연면적: `용적률산정연면적(㎡)`
- 주용도: `주용도`
- 기타용도: `기타용도`
- 사용승인일: `사용승인일`
- 허가일: `허가일`
- 착공일: `착공일`
- 주소 조인 컬럼: `시도`, `시군구`, `법정동`, `번`, `지`

## 8. 연속지적도 주요 컬럼명

- PNU: `PNU`
- 지번: `JIBUN`
- 행정구역 코드: `COL_ADM_SE`

## 9. PNU 또는 대체 조인키 생성 방식

연속지적도에는 `PNU`가 있으나 건축물대장에는 PNU가 직접 존재하지 않았다. 따라서 건축물대장에서는 `시군구`를 코드로 매핑한 뒤 `시군구코드 + 본번 + 부번` 대체 조인키를 생성했다. 연속지적도에서는 `PNU`의 앞 5자리 시군구코드와 본번·부번 부분을 이용해 같은 형식의 대체 조인키를 생성했다.

이 방식은 법정동코드를 조인키에 포함하지 못하므로 같은 시군구 안에서 같은 본번·부번이 여러 법정동에 존재하면 오조인 가능성이 있다. 분석경계 안으로 필지를 먼저 제한한 뒤 중심점 포함 방식으로 경계 내 필지를 선택하여 위험을 줄였다.

## 10. 건축물대장-연속지적도 조인 성공률

- 전체 건축물대장 행 수: `{total_rows:,}`
- 조인 성공 행 수: `{success_rows:,}`
- 조인 실패 행 수: `{fail_rows:,}`
- 조인 성공률: `{success_rate:.6f}`

## 11. 판교 경계 내 건축물 수

- `{len(joined[joined["area_name"].eq("pangyo_1st_technovalley")]):,}`

## 12. 위례 경계 내 건축물 수

- `{len(joined[joined["area_name"].eq("wirye_plan_area")]):,}`

## 13. 주용도 구성비 요약

{md_table(use_comp.sort_values(["area_name", "floor_area_ratio"], ascending=[True, False]), 40)}

## 14. 평균 용적률

{md_table(summary[["area_name", "avg_far"]])}

## 15. 연면적 가중 평균 용적률

{md_table(summary[["area_name", "floor_area_weighted_far"]])}

## 16. 평균 건폐율

{md_table(summary[["area_name", "avg_bcr"]])}

## 17. 개발 필지 비율

{md_table(summary[["area_name", "parcel_count", "developed_parcel_count", "developed_parcel_ratio"]])}

## 18. 미건축/공지 추정 비율

{md_table(summary[["area_name", "estimated_unbuilt_parcel_count", "estimated_unbuilt_parcel_ratio"]])}

## 19. 업무시설 연면적 비율

{md_table(summary[["area_name", "business_building_count", "business_floor_area_sqm", "business_floor_area_ratio"]])}

## 20. 업무시설밀도

{md_table(summary[["area_name", "business_floor_area_density_sqm_per_ha"]])}

## 21. 사용승인일 기반 개발 시계열 요약

{md_table(timeseries.groupby("area_name").tail(5), 20)}

## 22. 결측 처리 방식

- 용적률, 건폐율, 연면적, 건축면적은 숫자형으로 변환했고 변환 실패는 결측으로 처리했다.
- 사용승인일은 `YYYYMMDD` 형식으로 파싱 가능한 값만 날짜로 변환했다.
- 주용도 결측 또는 공백은 `미분류`로 처리했다.
- 사용승인일이 없는 건축물은 개발 시계열 계산에서 제외했다.

## 23. 이상값 처리 방식

- 평균 용적률 계산에서는 0 이하 또는 3000% 초과 값을 제외했다.
- 평균 건폐율 계산에서는 0 이하 또는 100% 초과 값을 제외했다.
- 원본 값은 `buildings_joined.geojson`에 유지했다.

## 24. 한계점

- 건축물대장에 PNU가 없어 법정동코드를 포함한 완전한 PNU 조인은 불가능했다.
- 대체 조인키는 `시군구코드 + 본번 + 부번`이므로 동일 시군구 내 법정동 중복 지번이 있을 경우 오조인 가능성이 있다.
- 미건축/공지 추정 필지는 실제 미건축 필지와 건축물대장 조인 실패가 섞일 수 있으므로 공지율로 단정하지 않는다.
- 건축물대장 행은 동/건축물 단위가 혼재될 수 있어 건축물 수 해석에 주의가 필요하다.

## 오류 또는 주의사항

{chr(10).join(f"- {w}" for w in warnings_list) if warnings_list else "- 특이 오류 없음"}
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    boundaries = read_boundaries()
    parcels, cadastral_meta = read_cadastral(boundaries)
    buildings, building_meta = read_buildings_filtered_2023()
    area_parcels = parcels_by_area(parcels, boundaries)
    joined, failures, join_stats = join_buildings_to_parcels(buildings, parcels, area_parcels)
    use_comp, summary, timeseries, vacant, joined_out, fail_out = build_outputs(
        buildings, area_parcels, joined, failures, boundaries, join_stats
    )

    warnings_list: list[str] = []
    total_rows = len(buildings)
    join_success = join_stats["join_success_rate"]
    if join_success < 0.2:
        warnings_list.append(f"건축물대장-연속지적도 조인 성공률이 {join_success:.3f}로 낮음. 지표 해석 신뢰도 낮음.")
    warnings_list.append("건축물대장에 PNU가 없어 시군구코드+본번+부번 대체 조인키를 사용함.")
    if area_parcels["join_key"].duplicated().any():
        warnings_list.append("경계 내 연속지적도에 중복 대체 조인키가 존재하여 일부 건축물이 복수 필지와 연결될 수 있음.")

    use_comp.to_csv(OUT_DIR / "building_use_composition.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT_DIR / "development_realization.csv", index=False, encoding="utf-8-sig")
    timeseries.to_csv(OUT_DIR / "building_approval_timeseries.csv", index=False, encoding="utf-8-sig")
    vacant.to_csv(OUT_DIR / "vacant_or_unbuilt_parcels.csv", index=False, encoding="utf-8-sig")
    joined_out.to_file(OUT_DIR / "buildings_joined.geojson", driver="GeoJSON")
    fail_out.to_csv(OUT_DIR / "building_join_failures.csv", index=False, encoding="utf-8-sig")

    write_report(
        building_meta,
        cadastral_meta,
        buildings,
        area_parcels,
        joined,
        failures,
        join_stats,
        use_comp,
        summary,
        timeseries,
        warnings_list,
    )

    print("생성된 파일 목록")
    for name in [
        "building_use_composition.csv",
        "development_realization.csv",
        "building_approval_timeseries.csv",
        "vacant_or_unbuilt_parcels.csv",
        "buildings_joined.geojson",
        "building_join_failures.csv",
        "development_realization_report.md",
    ]:
        print(f"- {OUT_DIR / name}")
    print(f"\n건축물대장 전체 행 수: {len(buildings):,}")
    print(f"연속지적도 전체 필지 수: {len(parcels):,}")
    print(f"건축물대장-연속지적도 조인 성공률: {join_success:.6f}")
    for area_name in [AREA_NAMES["pangyo"], AREA_NAMES["wirye"]]:
        row = summary[summary["area_name"].eq(area_name)].iloc[0]
        print(f"\n{area_name}")
        print(f"경계 내 건축물 수: {int(row['joined_building_count']):,}")
        print(f"평균 용적률: {row['avg_far']}")
        print(f"연면적 가중 평균 용적률: {row['floor_area_weighted_far']}")
        print(f"평균 건폐율: {row['avg_bcr']}")
        print(f"업무시설 연면적 비율: {row['business_floor_area_ratio']}")
        print(f"미건축/공지 추정 비율: {row['estimated_unbuilt_parcel_ratio']}")
    print("\n오류 또는 주의사항")
    for w in warnings_list:
        print(f"- {w}")


if __name__ == "__main__":
    main()
