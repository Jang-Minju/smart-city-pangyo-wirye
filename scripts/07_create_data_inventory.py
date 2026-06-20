from __future__ import annotations

import json
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = ["인구가구", "건축물", "서울용도지역", "경기용도지역", "가구및획지", "subway"]
REPORT = ROOT / "reports" / "data_inventory.md"
ASSIGNMENT_MD = ROOT / "제목 없음 382094d6351280b08f8fde699320004e.md"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_shp(path: Path) -> gpd.GeoDataFrame:
    for encoding in ["cp949", "euc-kr", "utf-8"]:
        try:
            return gpd.read_file(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    return gpd.read_file(path)


def csv_inventory(path: Path) -> dict[str, object]:
    # SGIS files in this project are headerless 4-column CSVs.
    for encoding in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            sample = pd.read_csv(path, encoding=encoding, header=None, nrows=5)
            rows = sum(1 for _ in path.open("r", encoding=encoding, errors="ignore"))
            columns = infer_csv_columns(path, sample)
            return {
                "records": rows,
                "columns": columns,
                "geometry": "No",
                "geometry_type": "",
                "crs": "",
                "main_columns": describe_columns(path, columns),
            }
        except Exception:
            continue
    return base_error("CSV read failed")


def infer_csv_columns(path: Path, sample: pd.DataFrame) -> list[str]:
    if path.parent.name == "인구가구" and sample.shape[1] == 4:
        return ["year", "spatial_id", "item_code", "value"]
    return [f"col_{i + 1}" for i in range(sample.shape[1])]


def xlsx_inventory(path: Path) -> dict[str, object]:
    try:
        headers, records = xlsx_headers_and_count(path)
        return {
            "records": records,
            "columns": headers,
            "geometry": "No",
            "geometry_type": "",
            "crs": "",
            "main_columns": describe_columns(path, headers),
        }
    except Exception as exc:
        return base_error(f"XLSX inspect failed: {type(exc).__name__}")


def xlsx_headers_and_count(path: Path) -> tuple[list[str], int]:
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        shared: list[str] = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("a:si", ns):
                shared.append("".join(t.text or "" for t in si.findall(".//a:t", ns)))
        sheet_name = [n for n in names if n.startswith("xl/worksheets/sheet")][0]
        sheet = ET.fromstring(z.read(sheet_name))
        rows = sheet.findall(".//a:row", ns)
        headers = row_values(rows[0], shared, ns) if rows else []
        nonempty = 0
        for row in rows[1:]:
            vals = row_values(row, shared, ns)
            if any(str(v).strip() for v in vals):
                nonempty += 1
        return headers, nonempty


def row_values(row, shared: list[str], ns: dict[str, str]) -> list[str]:
    values: dict[int, str] = {}
    for cell in row.findall("a:c", ns):
        ref = cell.get("r", "A1")
        idx = col_index(ref)
        value_node = cell.find("a:v", ns)
        value = "" if value_node is None else value_node.text or ""
        if cell.get("t") == "s" and value:
            value = shared[int(value)]
        elif cell.get("t") == "inlineStr":
            value = "".join(t.text or "" for t in cell.findall(".//a:t", ns))
        values[idx] = value
    if not values:
        return []
    out = [""] * (max(values) + 1)
    for idx, value in values.items():
        out[idx] = value
    return out


def col_index(cell_ref: str) -> int:
    letters = ""
    for char in cell_ref:
        if char.isalpha():
            letters += char
        else:
            break
    n = 0
    for char in letters:
        n = n * 26 + ord(char.upper()) - 64
    return max(n - 1, 0)


def tsv_inventory(path: Path) -> dict[str, object]:
    try:
        df = pd.read_csv(path, sep="\t", nrows=5)
        rows = max(sum(1 for _ in path.open("r", encoding="utf-8", errors="ignore")) - 1, 0)
        columns = list(df.columns)
        return {
            "records": rows,
            "columns": columns,
            "geometry": "No",
            "geometry_type": "",
            "crs": "",
            "main_columns": describe_columns(path, columns),
        }
    except Exception as exc:
        return base_error(f"TSV inspect failed: {type(exc).__name__}")


def parquet_inventory(path: Path) -> dict[str, object]:
    try:
        df = pd.read_parquet(path)
        columns = list(df.columns)
        return {
            "records": len(df),
            "columns": columns,
            "geometry": "No",
            "geometry_type": "",
            "crs": "",
            "main_columns": describe_columns(path, columns),
        }
    except Exception as exc:
        return base_error(f"Parquet inspect failed: {type(exc).__name__}")


def ipynb_inventory(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        cells = data.get("cells", [])
        return {
            "records": len(cells),
            "columns": ["cell_type", "source", "metadata", "outputs"],
            "geometry": "No",
            "geometry_type": "",
            "crs": "",
            "main_columns": "전처리/네트워크 생성 노트북. 데이터 테이블이 아니라 코드 문서.",
        }
    except Exception as exc:
        return base_error(f"Notebook inspect failed: {type(exc).__name__}")


def shp_inventory(path: Path) -> dict[str, object]:
    try:
        gdf = read_shp(path)
        attr_cols = [c for c in gdf.columns if c != gdf.geometry.name]
        geom_types = ", ".join(sorted(gdf.geom_type.dropna().astype(str).unique()))
        return {
            "records": len(gdf),
            "columns": attr_cols + [gdf.geometry.name],
            "geometry": "Yes",
            "geometry_type": geom_types,
            "crs": str(gdf.crs) if gdf.crs is not None else "",
            "main_columns": describe_columns(path, attr_cols),
        }
    except Exception as exc:
        return base_error(f"SHP read failed: {type(exc).__name__}")


def sidecar_inventory(path: Path) -> dict[str, object]:
    shp = path.with_suffix(".shp")
    if shp.exists():
        note = f"SHP sidecar file. 주 데이터 구조는 `{rel(shp)}` 참조."
    else:
        note = "Auxiliary/non-tabular file."
    return {
        "records": "",
        "columns": [],
        "geometry": "Sidecar",
        "geometry_type": "",
        "crs": "",
        "main_columns": note,
    }


def base_error(message: str) -> dict[str, object]:
    return {
        "records": "",
        "columns": [],
        "geometry": "",
        "geometry_type": "",
        "crs": "",
        "main_columns": message,
    }


def describe_columns(path: Path, columns: list[str]) -> str:
    name = path.name
    parent = path.parent.name
    colset = set(columns)

    if parent == "인구가구":
        if "인구총괄" in name:
            return "`year`, `spatial_id`, `value`: 집계구/격자 단위 총인구. geometry는 별도 필요."
        if "가구총괄" in name:
            return "`year`, `spatial_id`, `value`: 집계구/격자 단위 가구수. geometry는 별도 필요."
        if "사업체수" in name:
            return "`item_code`, `value`: 산업분류별 사업체 수. 공간 ID와 결합 필요."
        if "종사자수" in name:
            return "`item_code`, `value`: 산업분류별 종사자 수. 공간 ID와 결합 필요."

    if parent == "건축물":
        useful = [c for c in ["시도", "시군구", "법정동", "번", "지", "대지면적(㎡)", "건축면적(㎡)", "연면적(㎡)", "용적률(%)", "주용도", "기타용도", "용도지역코드명정보"] if c in colset]
        return "건축물 용도·면적·용적률 분석 가능. 주요 컬럼: " + ", ".join(f"`{c}`" for c in useful) + ". 좌표/PNU 없음."

    if parent in ["서울용도지역", "경기용도지역"]:
        useful = [c for c in ["DGM_NM", "dgm_nm", "ATRB_SE", "atrb_se", "DGM_AR", "dgm_ar", "SIGNGU_SE", "sgg_cd"] if c in colset]
        if useful:
            return "용도지역 구성비 산출 가능. 주요 컬럼: " + ", ".join(f"`{c}`" for c in useful)
        return "용도지역/도시계획 계열 SHP. 파일명 UQ 코드와 속성명을 함께 확인 필요."

    if parent == "가구및획지":
        return "`zoneName`: 사업지구, `blockName`/`lotName`: 획지 식별, `blockType`: 용도. 경계 정의와 획지 선택에 사용."

    if parent == "subway":
        if name.endswith(".tsv"):
            return "개통일/노선 메타데이터. 지하철 시점 필터링에 사용 가능."
        if name.endswith(".parquet"):
            return "노선별 대기시간 데이터. 네트워크 소요시간 보정에 사용 가능."
        if name.endswith(".ipynb"):
            return "지하철 네트워크 생성/가공 노트북."

    return "구조 확인 필요."


def inventory_file(path: Path) -> dict[str, object]:
    ext = path.suffix.lower()
    if ext == ".shp":
        info = shp_inventory(path)
    elif ext == ".csv":
        info = csv_inventory(path)
    elif ext == ".xlsx":
        info = xlsx_inventory(path)
    elif ext == ".tsv":
        info = tsv_inventory(path)
    elif ext == ".parquet":
        info = parquet_inventory(path)
    elif ext == ".ipynb":
        info = ipynb_inventory(path)
    elif ext in [".dbf", ".shx", ".prj", ".fix", ".cpg", ".cst"]:
        info = sidecar_inventory(path)
    else:
        info = base_error("Unsupported/auxiliary file type")

    return {
        "folder": path.parent.name,
        "file": rel(path),
        "extension": ext,
        "records": info["records"],
        "columns": ", ".join(info["columns"]) if isinstance(info["columns"], list) else str(info["columns"]),
        "geometry": info["geometry"],
        "geometry_type": info["geometry_type"],
        "crs": info["crs"],
        "main_columns": info["main_columns"],
    }


def markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if df.empty:
        return "(없음)"
    d = df.copy()
    if max_rows is not None:
        d = d.head(max_rows)
    d = d.fillna("").astype(str)
    lines = [
        "| " + " | ".join(d.columns) + " |",
        "| " + " | ".join("---" for _ in d.columns) + " |",
    ]
    for row in d.values.tolist():
        lines.append("| " + " | ".join(str(v).replace("|", "\\|").replace("\n", " ") for v in row) + " |")
    return "\n".join(lines)


def assignment_summary() -> str:
    if not ASSIGNMENT_MD.exists():
        return "과제 MD 파일을 찾지 못함."
    text = ASSIGNMENT_MD.read_text(encoding="utf-8", errors="ignore")
    return """- 과제는 판교테크노밸리와 실패/저조 업무지구 1곳을 공공데이터로 비교하는 시스템 및 보고서를 요구한다.
- 필수 데이터는 SGIS 인구·종사자, 토지이용계획/건축물대장, 도로망, 수도권 지하철 네트워크다.
- 필수 지표는 용도지역 구성비, 건축물 주용도 구성비, 토지이용 혼합도, 개발 실현 정도, 등시간권 접근성, 도달가능 인구·종사자, 인구·가구·사업체·종사자 및 직주 지표다.
- 모든 분석은 시간범위, 공간범위, 공간단위, 시간단위를 명시해야 한다.
- 현재 데이터 인벤토리는 이 요구사항에 맞춰 어떤 원자료가 어느 지표에 투입 가능한지 확인하기 위한 사전 단계다."""


def main() -> None:
    rows = []
    for dirname in TARGET_DIRS:
        folder = ROOT / dirname
        if not folder.exists():
            rows.append(
                {
                    "folder": dirname,
                    "file": f"{dirname} (missing)",
                    "extension": "",
                    "records": "",
                    "columns": "",
                    "geometry": "",
                    "geometry_type": "",
                    "crs": "",
                    "main_columns": "폴더 없음",
                }
            )
            continue
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                rows.append(inventory_file(path))

    df = pd.DataFrame(rows)
    folder_summary = (
        df.groupby("folder")
        .agg(file_count=("file", "count"), spatial_files=("geometry", lambda s: int((s == "Yes").sum())))
        .reset_index()
    )

    report = f"""# 데이터 인벤토리

## 과제 MD 요구사항 요약

{assignment_summary()}

## 현재 데이터의 역할 요약

- `가구및획지`: 판교/위례 분석 경계 정의, 획지 용도 확인, 업무·상업·도시지원 후보 선별에 사용 가능.
- `서울용도지역`, `경기용도지역`: 용도지역 구성비 산출에 사용 가능. `DGM_NM`/`dgm_nm` 계열이 용도지역명 컬럼이다.
- `건축물`: 건축물 주용도, 연면적, 대지면적, 용적률, 사용승인일 등 토지이용·개발 실현 정도 분석에 사용 가능. 좌표/PNU가 없어 공간 결합에는 지번 정제 또는 필지 도형 결합이 필요하다.
- `인구가구`: SGIS 집계구/격자 ID별 인구·가구·사업체·종사자 값. 공간 분석에는 동일 ID의 geometry 파일이 추가로 필요하다.
- `subway`: 현재 폴더에는 개통/대기시간/생성 노트북만 있고 역·링크 TSV 본체는 보이지 않는다. 등시간권 분석에는 `nodes.tsv`, `links.tsv` 또는 이에 준하는 네트워크 산출물이 필요하다.

## 폴더별 요약

{markdown_table(folder_summary)}

## 전체 파일 인벤토리

{markdown_table(df)}
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8-sig")
    print(f"files={len(df)}")
    print(f"report={REPORT}")


if __name__ == "__main__":
    main()
