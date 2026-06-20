from __future__ import annotations

import csv
import heapq
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import shapely
from pyproj import Transformer
from shapely.geometry import MultiPoint, Point, mapping, shape


ROOT = Path(__file__).resolve().parents[1]
ACCESS_DIR = ROOT / "derived_data" / "04_accessibility"
PUBLIC_DIR = ROOT / "public" / "data"
NETWORK_DIR = ROOT / "network"
POP_DIR = ROOT / "인구가구"
OA_DIR = ROOT / "집계구경계"

TIME_BINS = [10, 20, 30, 40, 50, 60]
ORIGINS = {
    "pangyo_1st_technovalley": {"station_name": "판교역", "node_id": 824},
    "wirye_plan_area": {"station_name": "남위례역", "node_id": 735},
}
TRANSFORMER = Transformer.from_crs(5179, 5186, always_xy=True)


def read_csv_rows(path: Path, *, delimiter=",", fieldnames=None) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        if fieldnames is None:
            return list(csv.DictReader(fp, delimiter=delimiter))
        return list(csv.DictReader(fp, delimiter=delimiter, fieldnames=fieldnames))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False)


def load_network():
    node_rows = read_csv_rows(
        NETWORK_DIR / "nodes.tsv",
        delimiter="\t",
    )
    nodes = {}
    for row in node_rows:
        node_id = int(row["id"])
        x_5186, y_5186 = TRANSFORMER.transform(float(row["x_5179"]), float(row["y_5179"]))
        nodes[node_id] = {
            "station_name": row["statnm"],
            "line_name": row["linenm"],
            "x_5186": x_5186,
            "y_5186": y_5186,
        }

    adjacency: dict[int, list[tuple[int, float]]] = {}
    link_rows = read_csv_rows(NETWORK_DIR / "links.tsv", delimiter="\t")
    for row in link_rows:
        from_node = int(row["fromNode"])
        to_node = int(row["toNode"])
        time_ft = float(row["timeFT"]) / 60.0
        time_tf = float(row["timeTF"]) / 60.0
        adjacency.setdefault(from_node, []).append((to_node, time_ft))
        adjacency.setdefault(to_node, []).append((from_node, time_tf))

    return nodes, adjacency


def dijkstra(adjacency: dict[int, list[tuple[int, float]]], origin: int, max_time: float = 60.0) -> dict[int, float]:
    dist = {origin: 0.0}
    heap = [(0.0, origin)]
    while heap:
        current_time, node = heapq.heappop(heap)
        if current_time > max_time:
            continue
        if current_time > dist.get(node, float("inf")):
            continue
        for neighbor, edge_cost in adjacency.get(node, []):
            next_time = current_time + edge_cost
            if next_time > max_time:
                continue
            if next_time < dist.get(neighbor, float("inf")):
                dist[neighbor] = next_time
                heapq.heappush(heap, (next_time, neighbor))
    return dist


def build_hull(points_xy: list[tuple[float, float]]):
    if len(points_xy) == 1:
        return Point(points_xy[0]).buffer(600)
    if len(points_xy) == 2:
        return MultiPoint(points_xy).convex_hull.buffer(500)
    hull = shapely.concave_hull(MultiPoint(points_xy), ratio=0.35)
    if hull.is_empty:
        hull = MultiPoint(points_xy).convex_hull
    if hull.geom_type in {"Point", "LineString", "MultiLineString"}:
        hull = hull.buffer(500)
    if hull.geom_type == "MultiPolygon":
        hull = max(hull.geoms, key=lambda geom: geom.area)
    return hull


def build_reachable_station_rows(nodes: dict[int, dict[str, object]], adjacency: dict[int, list[tuple[int, float]]]):
    rows = []
    polygons = {}
    for area_name, origin in ORIGINS.items():
        distances = dijkstra(adjacency, origin["node_id"], max_time=60.0)
        for threshold in TIME_BINS:
            reached = [
                {
                    "node_id": node_id,
                    "travel_time_min": travel_time,
                    **nodes[node_id],
                }
                for node_id, travel_time in distances.items()
                if travel_time <= threshold and node_id in nodes
            ]
            rows.extend(
                {
                    "area_name": area_name,
                    "origin_station": origin["station_name"],
                    "time_threshold_min": threshold,
                    "station_id": item["node_id"],
                    "station_name": item["station_name"],
                    "line_name": item["line_name"],
                    "travel_time_min": item["travel_time_min"],
                    "x": item["x_5186"],
                    "y": item["y_5186"],
                }
                for item in reached
            )
            polygons[(area_name, threshold)] = build_hull([(item["x_5186"], item["y_5186"]) for item in reached])
    return rows, polygons


def load_sgis_totals() -> gpd.GeoDataFrame:
    pop_cols = ["year", "spatial_id", "item_code", "value"]
    worker_cols = ["year", "spatial_id", "item_code", "value"]

    def load_population_csv(path: Path):
        df = pd.read_csv(path, header=None, names=pop_cols, encoding="utf-8-sig")
        df["spatial_id"] = df["spatial_id"].astype(str)
        return df[df["item_code"] == "to_in_001"][["spatial_id", "value"]].rename(columns={"value": "population"})

    def load_worker_csv(path: Path):
        df = pd.read_csv(path, header=None, names=worker_cols, encoding="utf-8-sig")
        df["spatial_id"] = df["spatial_id"].astype(str)
        df["value"] = pd.to_numeric(df["value"], errors="coerce").fillna(0.0)
        return df.groupby("spatial_id", as_index=False)["value"].sum().rename(columns={"value": "worker_count"})

    pop_11 = load_population_csv(POP_DIR / "11_2023년_인구총괄(총인구).csv")
    pop_31 = load_population_csv(POP_DIR / "31_2023년_인구총괄(총인구).csv")
    worker_11 = load_worker_csv(POP_DIR / "11_2023년_산업분류별(10차_대분류)_종사자수.csv")
    worker_31 = load_worker_csv(POP_DIR / "31_2023년_산업분류별(10차_대분류)_종사자수.csv")

    gdf_11 = gpd.read_file(OA_DIR / "bnd_oa_11_2025_2Q.shp")[["TOT_OA_CD", "geometry"]].rename(columns={"TOT_OA_CD": "spatial_id"})
    gdf_31 = gpd.read_file(OA_DIR / "bnd_oa_31_2025_2Q.shp")[["TOT_OA_CD", "geometry"]].rename(columns={"TOT_OA_CD": "spatial_id"})
    gdf = pd.concat([gdf_11, gdf_31], ignore_index=True)
    gdf = gpd.GeoDataFrame(gdf, geometry="geometry", crs=5179).to_crs(5186)
    gdf["spatial_id"] = gdf["spatial_id"].astype(str)
    gdf["original_area_sqm"] = gdf.geometry.area

    pop_df = pd.concat([pop_11, pop_31], ignore_index=True)
    worker_df = pd.concat([worker_11, worker_31], ignore_index=True)
    pop_df["population"] = pd.to_numeric(pop_df["population"], errors="coerce").fillna(0.0)
    worker_df["worker_count"] = pd.to_numeric(worker_df["worker_count"], errors="coerce").fillna(0.0)

    merged = gdf.merge(pop_df, on="spatial_id", how="left").merge(worker_df, on="spatial_id", how="left")
    merged["population"] = merged["population"].fillna(0.0)
    merged["worker_count"] = merged["worker_count"].fillna(0.0)
    return merged


def calculate_accessibility(polygons: dict[tuple[str, int], object], sgis_gdf: gpd.GeoDataFrame):
    rows = []
    features = []

    existing_iso = load_json(ACCESS_DIR / "accessibility_isochrones.geojson")
    existing_geo_by_key = {
        (f["properties"]["area_name"], int(f["properties"]["time_threshold_min"])): shape(f["geometry"])
        for f in existing_iso["features"]
    }

    for area_name, origin in ORIGINS.items():
        rows.append(
            {
                "area_name": area_name,
                "station_name": origin["station_name"],
                "time_min": 0,
                "reachable_station_count": 0,
                "reachable_population": 0.0,
                "reachable_workers": 0.0,
            }
        )
        for threshold in TIME_BINS:
            polygon = existing_geo_by_key.get((area_name, threshold), polygons[(area_name, threshold)])
            subset = sgis_gdf[sgis_gdf.intersects(polygon)].copy()
            if subset.empty:
                reachable_population = 0.0
                reachable_workers = 0.0
            else:
                intersections = subset.geometry.intersection(polygon)
                subset["intersect_area_sqm"] = intersections.area
                subset["allocation_ratio"] = subset["intersect_area_sqm"] / subset["original_area_sqm"]
                reachable_population = float((subset["population"] * subset["allocation_ratio"]).sum())
                reachable_workers = float((subset["worker_count"] * subset["allocation_ratio"]).sum())

            reachable_station_count = sum(
                1 for key_area, key_time in polygons.keys() if key_area == area_name and key_time == threshold
            )
            # station count comes from reachable station rows, not polygon dict cardinality
            rows.append(
                {
                    "area_name": area_name,
                    "station_name": origin["station_name"],
                    "time_min": threshold,
                    "reachable_station_count": 0,  # patched later
                    "reachable_population": reachable_population,
                    "reachable_workers": reachable_workers,
                }
            )
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "area_name": area_name,
                        "origin_station": origin["station_name"],
                        "time_threshold_min": threshold,
                        "reachable_population": reachable_population,
                        "reachable_workers": reachable_workers,
                    },
                    "geometry": mapping(polygon),
                }
            )
    return rows, features


def apply_station_counts(rows: list[dict[str, object]], reachable_station_rows: list[dict[str, object]]) -> None:
    counts = {}
    for row in reachable_station_rows:
        key = (row["area_name"], int(row["time_threshold_min"]))
        counts[key] = counts.get(key, 0) + 1
    for row in rows:
        key = (row["area_name"], int(row["time_min"]))
        row["reachable_station_count"] = counts.get(key, 0)


def build_validation(rows: list[dict[str, object]]) -> str:
    existing = read_csv_rows(PUBLIC_DIR / "accessibility_summary.csv")
    existing_map = {
        (row["area_name"], int(float(row["time_threshold_min"]))): row
        for row in existing
    }
    lines = [
        "# Accessibility Cumulative Validation",
        "",
        "- source network: `network/nodes.tsv`, `network/links.tsv`",
        "- source SGIS raw csv: `인구가구/11_2023년_인구총괄(총인구).csv`, `인구가구/31_2023년_인구총괄(총인구).csv`, `인구가구/11_2023년_산업분류별(10차_대분류)_종사자수.csv`, `인구가구/31_2023년_산업분류별(10차_대분류)_종사자수.csv`",
        "- source OA boundaries: `집계구경계/bnd_oa_11_2025_2Q.shp`, `집계구경계/bnd_oa_31_2025_2Q.shp`",
        "- source 30/60 polygons reused for validation: `derived_data/04_accessibility/accessibility_isochrones.geojson`",
        "- output cumulative: `derived_data/04_accessibility/accessibility_cumulative.csv`",
        "- output polygons: `derived_data/04_accessibility/accessibility_isochrones_10min.geojson`",
        "",
        "## 0-60 minute cumulative table",
        "",
        "| area_name | station_name | time_min | reachable_station_count | reachable_population | reachable_workers |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['area_name']} | {row['station_name']} | {row['time_min']} | {row['reachable_station_count']} | "
            f"{float(row['reachable_population']):,.3f} | {float(row['reachable_workers']):,.3f} |"
        )

    lines.extend(
        [
            "",
            "## 30/60 minute validation against current accessibility_summary.csv",
            "",
            "| area_name | time_min | generated_population | existing_population | diff_population | generated_workers | existing_workers | diff_workers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in rows:
        if int(row["time_min"]) not in {30, 60}:
            continue
        existing_row = existing_map[(row["area_name"], int(row["time_min"]))]
        gp = float(row["reachable_population"])
        ep = float(existing_row["reachable_population"])
        gw = float(row["reachable_workers"])
        ew = float(existing_row["reachable_workers"])
        lines.append(
            f"| {row['area_name']} | {row['time_min']} | {gp:,.3f} | {ep:,.3f} | {gp - ep:,.6f} | "
            f"{gw:,.3f} | {ew:,.3f} | {gw - ew:,.6f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    nodes, adjacency = load_network()
    reachable_station_rows, generated_polygons = build_reachable_station_rows(nodes, adjacency)
    sgis_gdf = load_sgis_totals()
    cumulative_rows, polygon_features = calculate_accessibility(generated_polygons, sgis_gdf)
    apply_station_counts(cumulative_rows, reachable_station_rows)

    write_csv(
        ACCESS_DIR / "accessibility_cumulative.csv",
        cumulative_rows,
        [
            "area_name",
            "station_name",
            "time_min",
            "reachable_station_count",
            "reachable_population",
            "reachable_workers",
        ],
    )

    isochrone_fc = {
        "type": "FeatureCollection",
        "name": "accessibility_isochrones_10min",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::5186"}},
        "features": polygon_features,
    }
    write_json(ACCESS_DIR / "accessibility_isochrones_10min.geojson", isochrone_fc)

    validation_text = build_validation(cumulative_rows)
    (ACCESS_DIR / "accessibility_cumulative_validation.md").write_text(validation_text, encoding="utf-8")


if __name__ == "__main__":
    main()
