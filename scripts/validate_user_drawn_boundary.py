from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import matplotlib
from matplotlib.lines import Line2D

matplotlib.use("Agg")
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "pangyo_boundary_user_drawn.geojson"
OUTPUT_DIR = PROJECT_ROOT / "derived_data" / "00_boundaries"
EXISTING_BOUNDARY = OUTPUT_DIR / "pangyo_boundary.geojson"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a dashboard-drawn Pangyo boundary GeoJSON."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=str(DEFAULT_INPUT),
        help="Path to pangyo_boundary_user_drawn.geojson exported from /boundary-editor.",
    )
    parser.add_argument(
        "--prefix",
        default="pangyo_boundary_user_drawn",
        help="Output filename prefix.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = PROJECT_ROOT / input_path

    if not input_path.exists():
        raise FileNotFoundError(f"Input GeoJSON not found: {input_path}")

    drawn = gpd.read_file(input_path)
    if drawn.empty:
        raise ValueError("Input GeoJSON has no features.")

    if drawn.crs is None:
        drawn = drawn.set_crs(4326)
    else:
        drawn = drawn.to_crs(4326)

    geom = drawn.geometry.iloc[0]
    if len(drawn) != 1:
        raise ValueError(f"Expected exactly one feature, found {len(drawn)}.")
    if geom.geom_type != "Polygon":
        raise ValueError(f"Expected Polygon geometry, found {geom.geom_type}.")
    if not geom.is_valid:
        raise ValueError("Input Polygon is invalid. Check for self-intersection.")

    drawn_5186 = drawn.to_crs(5186)
    drawn_geom = drawn_5186.geometry.iloc[0]
    if drawn_geom.geom_type != "Polygon" or not drawn_geom.is_valid:
        raise ValueError("Converted geometry is not a valid single Polygon.")

    existing = gpd.read_file(EXISTING_BOUNDARY).to_crs(5186)
    existing_geom = existing.geometry.iloc[0]

    drawn_area = float(drawn_geom.area)
    existing_area = float(existing_geom.area)
    diff_area = drawn_area - existing_area
    diff_pct = diff_area / existing_area * 100 if existing_area else 0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    converted_path = OUTPUT_DIR / f"{args.prefix}_5186.geojson"
    validation_path = OUTPUT_DIR / f"{args.prefix}_validation.png"

    drawn_5186.to_file(converted_path, driver="GeoJSON")

    fig, ax = plt.subplots(figsize=(12, 9), dpi=180)
    ax.set_aspect("equal")
    ax.set_facecolor("#f6f4ef")

    existing.plot(
        ax=ax,
        facecolor="none",
        edgecolor="#2459d6",
        linewidth=2.5,
        zorder=2,
    )
    drawn_5186.plot(
        ax=ax,
        facecolor=(0.92, 0.1, 0.06, 0.14),
        edgecolor="#e31a1c",
        linewidth=3,
        zorder=3,
    )

    minx, miny, maxx, maxy = drawn_5186.total_bounds
    ex_minx, ex_miny, ex_maxx, ex_maxy = existing.total_bounds
    minx = min(minx, ex_minx)
    miny = min(miny, ex_miny)
    maxx = max(maxx, ex_maxx)
    maxy = max(maxy, ex_maxy)
    pad_x = (maxx - minx) * 0.08
    pad_y = (maxy - miny) * 0.08
    ax.set_xlim(minx - pad_x, maxx + pad_x)
    ax.set_ylim(miny - pad_y, maxy + pad_y)

    ax.text(
        0.012,
        0.986,
        "\n".join(
            [
                "input CRS: EPSG:4326",
                "converted CRS: EPSG:5186",
                f"user area: {drawn_area:,.1f} sqm",
                f"existing area: {existing_area:,.1f} sqm",
                f"diff: {diff_area:+,.1f} sqm ({diff_pct:+.2f}%)",
            ]
        ),
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=10,
        bbox=dict(
            boxstyle="round,pad=0.35",
            facecolor="white",
            edgecolor="#d0d0d0",
            alpha=0.96,
        ),
    )
    ax.legend(
        handles=[
            Line2D([0], [0], color="#2459d6", lw=2.5, label="Existing pangyo_boundary"),
            Line2D([0], [0], color="#e31a1c", lw=3, label="User drawn boundary"),
        ],
        loc="lower left",
        frameon=True,
        framealpha=0.96,
        facecolor="white",
        edgecolor="#d0d0d0",
    )
    ax.set_title("Pangyo user drawn boundary validation", fontsize=15, pad=14)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.savefig(validation_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    print(f"Input: {input_path}")
    print("Geometry: Polygon, valid=True, parts=1")
    print(f"Converted GeoJSON: {converted_path}")
    print(f"Validation PNG: {validation_path}")
    print(f"User area sqm: {drawn_area:,.2f}")
    print(f"Existing area sqm: {existing_area:,.2f}")
    print(f"Difference sqm: {diff_area:+,.2f} ({diff_pct:+.2f}%)")


if __name__ == "__main__":
    main()
