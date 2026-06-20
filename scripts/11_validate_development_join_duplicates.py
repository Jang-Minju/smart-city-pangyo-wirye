from __future__ import annotations

from pathlib import Path
import importlib.util

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "derived_data" / "02_development_realization"
REPORT = OUT_DIR / "development_realization_validation.md"
DEV_SCRIPT = ROOT / "scripts" / "10_calculate_development_realization.py"


def load_dev_module():
    spec = importlib.util.spec_from_file_location("dev_realization", DEV_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def safe_float(value):
    if pd.isna(value):
        return pd.NA
    return float(value)


def deduplicate_joined(joined: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    work = joined.copy()
    work["dedup_rank_area"] = work["parcel_area_sqm"].fillna(0)
    work = work.sort_values(
        ["area_name", "building_uid", "dedup_rank_area", "pnu"],
        ascending=[True, True, False, True],
    )
    dup_groups = (
        joined.groupby(["area_name", "building_uid"], dropna=False)
        .agg(
            joined_parcel_count=("pnu", "nunique"),
            joined_rows=("pnu", "size"),
            pk=("PK", "first"),
            source_file=("source_file", "first"),
            row_id=("row_id", "first"),
            main_use=("main_use", "first"),
            total_floor_area_sqm=("total_floor_area_sqm", "first"),
            candidate_pnus=("pnu", lambda s: "; ".join(sorted(set(map(str, s))))),
        )
        .reset_index()
    )
    dup_groups = dup_groups[dup_groups["joined_parcel_count"] > 1].copy()
    deduped = work.drop_duplicates(subset=["area_name", "building_uid"], keep="first").copy()
    deduped = deduped.drop(columns=["dedup_rank_area"])
    return deduped, dup_groups


def compare_summary(original: pd.DataFrame, dedup: pd.DataFrame) -> pd.DataFrame:
    merged = original.merge(dedup, on="area_name", suffixes=("_original", "_deduplicated"))
    rows = []
    metrics = [
        "joined_building_count",
        "developed_parcel_count",
        "estimated_unbuilt_parcel_count",
        "developed_parcel_ratio",
        "estimated_unbuilt_parcel_ratio",
        "avg_far",
        "floor_area_weighted_far",
        "avg_bcr",
        "total_building_floor_area_sqm",
        "total_building_area_sqm",
        "business_building_count",
        "business_floor_area_sqm",
        "business_floor_area_ratio",
        "business_floor_area_density_sqm_per_ha",
    ]
    for _, row in merged.iterrows():
        for metric in metrics:
            old = safe_float(row[f"{metric}_original"])
            new = safe_float(row[f"{metric}_deduplicated"])
            diff = pd.NA if pd.isna(old) or pd.isna(new) else new - old
            rows.append(
                {
                    "area_name": row["area_name"],
                    "metric": metric,
                    "original": old,
                    "deduplicated": new,
                    "difference": diff,
                }
            )
    return pd.DataFrame(rows)


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


def main() -> None:
    dev = load_dev_module()
    boundaries = dev.read_boundaries()
    parcels, _ = dev.read_cadastral(boundaries)
    buildings, _ = dev.read_buildings_filtered_2023()
    area_parcels = dev.parcels_by_area(parcels, boundaries)
    joined, failures, join_stats = dev.join_buildings_to_parcels(buildings, parcels, area_parcels)

    duplicate_keys = (
        area_parcels.groupby(["area_name", "join_key"], dropna=False)
        .agg(parcel_count=("pnu", "nunique"), pnus=("pnu", lambda s: "; ".join(sorted(set(map(str, s))))))
        .reset_index()
    )
    duplicate_keys = duplicate_keys[duplicate_keys["parcel_count"] > 1].copy()
    duplicate_key_summary = (
        duplicate_keys.groupby("area_name")
        .agg(duplicate_join_key_count=("join_key", "count"), parcels_in_duplicate_keys=("parcel_count", "sum"))
        .reset_index()
    )

    deduped, duplicate_building_rows = deduplicate_joined(joined)
    duplicate_pk = (
        joined[joined["PK"].astype(str).ne("")]
        .groupby(["area_name", "PK"], dropna=False)
        .agg(joined_rows=("pnu", "size"), joined_parcel_count=("pnu", "nunique"))
        .reset_index()
    )
    duplicate_pk = duplicate_pk[(duplicate_pk["joined_rows"] > 1) | (duplicate_pk["joined_parcel_count"] > 1)].copy()

    _, original_summary, _, _, _, _ = dev.build_outputs(buildings, area_parcels, joined, failures, boundaries, join_stats)
    _, dedup_summary, _, _, dedup_joined_out, _ = dev.build_outputs(buildings, area_parcels, deduped, failures, boundaries, join_stats)
    comparison = compare_summary(original_summary, dedup_summary)

    dedup_joined_out.to_file(OUT_DIR / "buildings_joined_deduplicated.geojson", driver="GeoJSON")
    dedup_summary.to_csv(OUT_DIR / "development_realization_deduplicated.csv", index=False, encoding="utf-8-sig")
    comparison.to_csv(OUT_DIR / "development_realization_duplicate_comparison.csv", index=False, encoding="utf-8-sig")
    duplicate_keys.to_csv(OUT_DIR / "duplicate_join_keys_in_boundary.csv", index=False, encoding="utf-8-sig")
    duplicate_building_rows.to_csv(OUT_DIR / "duplicate_building_join_cases.csv", index=False, encoding="utf-8-sig")
    duplicate_pk.to_csv(OUT_DIR / "duplicate_pk_join_cases.csv", index=False, encoding="utf-8-sig")

    duplicate_building_summary = (
        duplicate_building_rows.groupby("area_name")
        .agg(
            building_rows_joined_to_multiple_parcels=("building_uid", "count"),
            expanded_join_rows=("joined_rows", "sum"),
            candidate_parcel_total=("joined_parcel_count", "sum"),
        )
        .reset_index()
    )
    duplicate_pk_summary = (
        duplicate_pk.groupby("area_name")
        .agg(duplicate_pk_count=("PK", "count"), duplicate_pk_join_rows=("joined_rows", "sum"))
        .reset_index()
    )

    affected = comparison[comparison["difference"].fillna(0).abs() > 1e-9].copy()
    report = f"""# 개발실현도 조인 중복 검증 보고서

## 검증 목적

건축물대장과 연속지적도 조인에서 `시군구코드 + 본번 + 부번` 대체 조인키를 사용했기 때문에, 경계 내부에서 동일 대체키를 가진 여러 필지가 존재할 경우 하나의 건축물대장 행이 여러 필지에 중복 조인될 수 있다. 기존 결과 파일은 덮어쓰지 않고 중복 여부와 중복 제거 후 요약값 변화를 별도 검증했다.

## 입력 자료

- 기존 조인 결과: `derived_data/02_development_realization/buildings_joined.geojson`
- 원본 개발실현도 요약: `derived_data/02_development_realization/development_realization.csv`
- 재현 스크립트: `scripts/10_calculate_development_realization.py`

## 1. 경계 내 중복 대체 조인키

{md_table(duplicate_key_summary)}

상세 목록: `duplicate_join_keys_in_boundary.csv`

## 2. 하나의 건축물대장 행이 여러 필지에 조인된 사례

{md_table(duplicate_building_summary)}

상세 목록: `duplicate_building_join_cases.csv`

## 3. 동일 row_id 또는 PK 중복 사례

기존 `buildings_joined.geojson`에는 `row_id`, `PK`, `source_file`이 저장되어 있지 않아 해당 파일만으로 직접 판별할 수 없었다. 따라서 원본 건축물대장과 조인 과정을 재현하여 `building_uid = source_file + row_id`, `PK` 기준으로 검증했다.

### PK 중복 조인 요약

{md_table(duplicate_pk_summary)}

상세 목록: `duplicate_pk_join_cases.csv`

## 4. 개발실현도 요약값 중복 집계 여부

중복 조인이 확인되었고, 원본 개발실현도 요약값 일부가 중복 집계의 영향을 받았다. 아래 표는 원본 요약과 `area_name + building_uid` 기준 중복 제거 요약의 차이다.

{md_table(affected, 80)}

전체 비교표: `development_realization_duplicate_comparison.csv`

## 5. 중복 제거 산출물

- `buildings_joined_deduplicated.geojson`
- `development_realization_deduplicated.csv`

중복 제거 기준은 `area_name + building_uid`이며, 하나의 건축물대장 행이 여러 필지에 조인된 경우 `parcel_area_sqm`이 가장 큰 필지를 대표 필지로 선택했다. 건축물대장에 PNU가 없고 법정동코드를 포함한 완전 조인이 불가능하므로, 이 대표 필지 선택은 보수적 검증용 처리이며 원본을 대체하는 확정 보정은 아니다.

## 6. 판단

- 중복 조인은 존재한다.
- 기존 `development_realization.csv`는 중복 조인된 건축물 행의 건축물 수, 연면적, 건축면적, 업무시설 연면적 등에 영향을 받았다.
- 따라서 보고서 본문에는 원본 결과와 함께 본 검증 결과를 참고하고, 최종 발표 또는 분석표에서는 `development_realization_deduplicated.csv`를 보조 비교값으로 함께 제시하는 것이 적절하다.
"""
    REPORT.write_text(report, encoding="utf-8")

    print("생성된 검증 파일")
    for name in [
        "buildings_joined_deduplicated.geojson",
        "development_realization_deduplicated.csv",
        "development_realization_duplicate_comparison.csv",
        "duplicate_join_keys_in_boundary.csv",
        "duplicate_building_join_cases.csv",
        "duplicate_pk_join_cases.csv",
        "development_realization_validation.md",
    ]:
        print(f"- {OUT_DIR / name}")
    print("\n경계 내 중복 대체 조인키")
    print(duplicate_key_summary.to_string(index=False))
    print("\n복수 필지에 조인된 건축물대장 행")
    print(duplicate_building_summary.to_string(index=False))
    print("\n중복 집계 영향이 있는 요약값 수:", len(affected))


if __name__ == "__main__":
    main()
