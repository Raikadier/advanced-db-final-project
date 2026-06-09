"""Pulido visual PBIR: tipografía, etiquetas duplicadas, ejes y posición de slicers."""
from __future__ import annotations

import json
from pathlib import Path

REPORT_PAGES = (
    Path(__file__).resolve().parents[1]
    / "proyecto-bi"
    / "northwind_bi.Report"
    / "definition"
    / "pages"
)
THEME_PATH = (
    Path(__file__).resolve().parents[1]
    / "proyecto-bi"
    / "northwind_bi.Report"
    / "StaticResources"
    / "SharedResources"
    / "CustomThemes"
    / "BIBB.json"
)

FONT = "''Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif'"
FONT_SEMIBOLD = "''Segoe UI Semibold', wf_segoe-ui_semibold, helvetica, arial, sans-serif'"

CHART_TYPES = {
    "lineChart",
    "clusteredColumnChart",
    "clusteredBarChart",
    "stackedAreaChart",
    "donutChart",
    "scatterChart",
    "gauge",
    "azureMap",
}
TABLE_TYPES = {"tableEx", "pivotTable"}


def lit_bool(value: bool) -> dict:
    return {"expr": {"Literal": {"Value": "true" if value else "false"}}}


def lit_str(value: str) -> dict:
    return {"expr": {"Literal": {"Value": f"'{value}'"}}}


def dbl(value: float | int) -> dict:
    return {"expr": {"Literal": {"Value": f"{value}D"}}}


def int_lit(value: int) -> dict:
    return {"expr": {"Literal": {"Value": f"{value}L"}}}


def font_family(semibold: bool = False) -> dict:
    return {"expr": {"Literal": {"Value": FONT_SEMIBOLD if semibold else FONT}}}


def color_hex(value: str) -> dict:
    return {"solid": {"color": {"expr": {"Literal": {"Value": f"'{value}'"}}}}}


def obj_props(objects: dict, category: str) -> dict:
    entries = objects.setdefault(category, [{"properties": {}}])
    return entries[0].setdefault("properties", {})


def container_props(container: dict, category: str) -> dict:
    entries = container.setdefault(category, [{"properties": {}}])
    return entries[0].setdefault("properties", {})


def set_font(props: dict, size: float, *, text_size: bool = False) -> None:
    key = "textSize" if text_size else "fontSize"
    props[key] = dbl(size)
    props.setdefault("fontFamily", font_family())


def hide_axis_titles(objects: dict) -> None:
    for axis in ("categoryAxis", "valueAxis", "y2Axis"):
        if axis in objects or axis == "categoryAxis":
            props = obj_props(objects, axis)
            props["showAxisTitle"] = lit_bool(False)


def polish_shape(data: dict) -> list[str]:
    visual = data["visual"]
    objects = visual.setdefault("objects", {})
    text_blocks = objects.get("text", [])
    if len(text_blocks) >= 2:
        props = text_blocks[1].setdefault("properties", {})
        set_font(props, 18)
        props["fontFamily"] = font_family(True)
        props["leftMargin"] = int_lit(16)
        props["rightMargin"] = int_lit(16)
        props["topMargin"] = int_lit(8)
        props["bottomMargin"] = int_lit(8)
    pos = data.get("position", {})
    if pos.get("height", 52) != 52:
        pos["height"] = 52
    return ["banner 18pt, márgenes corregidos"]


def polish_card(data: dict) -> list[str]:
    visual = data["visual"]
    height = data.get("position", {}).get("height", 85)
    objects = visual.setdefault("objects", {})
    container = visual.setdefault("visualContainerObjects", {})

    value_size = 20 if height >= 80 else 18
    set_font(obj_props(objects, "labels"), value_size)
    obj_props(objects, "categoryLabels")["show"] = lit_bool(False)

    title = container_props(container, "title")
    set_font(title, 10)
    title["show"] = lit_bool(True)
    return [f"card {value_size}pt, sin etiqueta duplicada"]


def polish_slicer(data: dict) -> list[str]:
    visual = data["visual"]
    objects = visual.setdefault("objects", {})
    container = visual.setdefault("visualContainerObjects", {})
    pos = data.setdefault("position", {})

    pos["y"] = 8
    pos["height"] = 38
    pos["z"] = max(pos.get("z", 0), 11000)

    set_font(obj_props(objects, "items"), 9, text_size=True)
    header = obj_props(objects, "header")
    header["show"] = lit_bool(False)

    title = container_props(container, "title")
    set_font(title, 9)
    title["fontColor"] = color_hex("#FFFFFF")

    bg = obj_props(objects, "background")
    bg["show"] = lit_bool(False)

    return ["slicer en banner, header oculto, título blanco"]


def polish_table(data: dict) -> list[str]:
    visual = data["visual"]
    height = data.get("position", {}).get("height", 200)
    objects = visual.setdefault("objects", {})
    container = visual.setdefault("visualContainerObjects", {})

    compact = height <= 130
    title_size = 10 if compact else 11
    cell_size = 8 if compact else 9

    title = container_props(container, "title")
    set_font(title, title_size)
    title["fontFamily"] = font_family(True)

    for cat in ("columnHeaders", "rowHeaders", "values"):
        props = obj_props(objects, cat)
        set_font(props, cell_size)
        if cat == "columnHeaders":
            props["wordWrap"] = lit_bool(True)
        if cat == "values":
            props["wordWrap"] = lit_bool(False)

    grid = obj_props(objects, "grid")
    grid["rowPadding"] = dbl(2 if compact else 3)

    return [f"tabla título {title_size}pt / celdas {cell_size}pt"]


def polish_chart(data: dict) -> list[str]:
    visual = data["visual"]
    vtype = visual.get("visualType", "")
    height = data.get("position", {}).get("height", 280)
    objects = visual.setdefault("objects", {})
    container = visual.setdefault("visualContainerObjects", {})

    compact = height <= 120
    medium = height <= 180
    title_size = 9 if compact else (10 if medium else 11)
    axis_size = 8 if compact else 9

    title = container_props(container, "title")
    set_font(title, title_size)
    title["fontFamily"] = font_family(True)

    hide_axis_titles(objects)

    for cat in ("categoryAxis", "valueAxis"):
        set_font(obj_props(objects, cat), axis_size)

    if "legend" in objects or vtype != "donutChart":
        legend = obj_props(objects, "legend")
        set_font(legend, axis_size)
        legend["showTitle"] = lit_bool(False)
        if compact:
            legend["show"] = lit_bool(False)

    if "labels" in objects or vtype in {
        "donutChart",
        "clusteredBarChart",
        "clusteredColumnChart",
    }:
        labels = obj_props(objects, "labels")
        set_font(labels, 8 if compact else 9)
        if compact or vtype in {"lineChart", "stackedAreaChart"}:
            labels["show"] = lit_bool(False)
        if vtype == "donutChart" and not compact:
            labels["labelStyle"] = lit_str("Percent")

    if vtype == "clusteredBarChart" and compact:
        cat = obj_props(objects, "categoryAxis")
        cat["concatLabels"] = lit_bool(True)

    if vtype == "gauge":
        set_font(obj_props(objects, "labels"), 16 if compact else 18)

    return [f"gráfico título {title_size}pt, ejes sin nombre técnico"]


def polish_visual(data: dict) -> list[str]:
    vtype = data.get("visual", {}).get("visualType", "")
    if vtype == "shape":
        return polish_shape(data)
    if vtype == "card":
        return polish_card(data)
    if vtype == "slicer":
        return polish_slicer(data)
    if vtype in TABLE_TYPES:
        return polish_table(data)
    if vtype in CHART_TYPES:
        return polish_chart(data)
    return []


def polish_theme() -> list[str]:
    if not THEME_PATH.exists():
        return []
    theme = json.loads(THEME_PATH.read_text(encoding="utf-8"))
    changes: list[str] = []

    if theme.get("dataColors", [None])[0] == "#ffffff":
        theme["dataColors"] = [
            "#093824",
            "#4c956c",
            "#001f54",
            "#04a777",
            "#92C5DE",
            "#4393C3",
        ]
        changes.append("dataColors sin blanco")

    all_styles = theme.setdefault("visualStyles", {}).setdefault("*", {}).setdefault("*", {})
    all_styles.setdefault("title", [{}])[0].update({"fontSize": 11, "bold": True})
    all_styles.setdefault("legend", [{}])[0].update({"fontSize": 9, "showTitle": False})
    all_styles.setdefault("categoryAxis", [{}])[0]["showAxisTitle"] = False
    all_styles.setdefault("valueAxis", [{}])[0]["showAxisTitle"] = False

    card = theme.setdefault("visualStyles", {}).setdefault("card", {}).setdefault("*", {})
    card.setdefault("labels", [{}])[0]["fontSize"] = 20
    card.setdefault("categoryLabels", [{}])[0]["show"] = False

    slicer = theme.setdefault("visualStyles", {}).setdefault("slicer", {}).setdefault("*", {})
    slicer.setdefault("header", [{}])[0]["show"] = False

    text_classes = theme.setdefault("textClasses", {})
    text_classes["callout"] = {"color": "#0A2B43", "fontFace": "Segoe UI", "fontSize": 20}
    text_classes["title"] = {"color": "#0A2B43", "fontFace": "Segoe UI", "fontSize": 11}
    text_classes["label"] = {"color": "#0A2B43", "fontFace": "Segoe UI", "fontSize": 9}
    changes.append("defaults tema conservadores")

    THEME_PATH.write_text(json.dumps(theme, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return changes


def main() -> None:
    summary: list[dict] = []
    for vf in sorted(REPORT_PAGES.rglob("visual.json")):
        data = json.loads(vf.read_text(encoding="utf-8"))
        changes = polish_visual(data)
        if changes:
            vf.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            summary.append({"file": str(vf.relative_to(REPORT_PAGES.parent.parent)), "changes": changes})

    theme_changes = polish_theme()
    print(f"Visuales actualizados: {len(summary)}")
    for row in summary:
        print(f"  {row['file']}: {', '.join(row['changes'])}")
    if theme_changes:
        print("Tema:", ", ".join(theme_changes))


if __name__ == "__main__":
    main()
