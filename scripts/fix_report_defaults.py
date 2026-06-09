"""Limpia slicers (sin selección guardada) y valida mapa Azure Maps con capa filledMap."""
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
MAP_VISUAL = (
    REPORT_PAGES
    / "d72257249741148631d0"
    / "visuals"
    / "ebfc2b4fd2f76f7f2d0a"
    / "visual.json"
)


def slicer_title(data: dict) -> str:
    visual = data.get("visual", {})
    for block in visual.get("visualContainerObjects", {}).get("title", []):
        lit = block.get("properties", {}).get("text", {}).get("expr", {}).get("Literal", {})
        if "Value" in lit:
            return lit["Value"].strip("'")
    return ""


def lit_bool(value: bool) -> dict:
    return {"expr": {"Literal": {"Value": "true" if value else "false"}}}


def fix_slicer(data: dict) -> list[str]:
    changes: list[str] = []
    visual = data.setdefault("visual", {})
    objects = visual.setdefault("objects", {})

    if "general" in objects:
        del objects["general"]
        changes.append("quitar selección guardada")

    selection_blocks = objects.setdefault("selection", [{"properties": {}}])
    props = selection_blocks[0].setdefault("properties", {})

    if props.pop("strictSingleSelect", None) is not None:
        changes.append("quitar strictSingleSelect")

    if props.get("singleSelect") != lit_bool(False):
        props["singleSelect"] = lit_bool(False)
        changes.append("singleSelect=false")

    if props.get("selectAllCheckboxEnabled") != lit_bool(True):
        props["selectAllCheckboxEnabled"] = lit_bool(True)
        changes.append("selectAllCheckboxEnabled=true")

    data_blocks = objects.get("data", [])
    if data_blocks:
        data_props = data_blocks[0].setdefault("properties", {})
        if data_props.pop("isInvertedSelectionMode", None) is not None:
            changes.append("quitar isInvertedSelectionMode")

    if visual.get("drillFilterOtherVisuals") is not False:
        visual["drillFilterOtherVisuals"] = False
        changes.append("drillFilterOtherVisuals=false")

    sync = visual.get("syncGroup")
    if sync and sync.get("filterChanges") is not False:
        sync["filterChanges"] = False
        changes.append("sync filterChanges=false")

    return changes


def fix_azure_map() -> list[str]:
    """No-op si el mapa ya es azureMap con capa filledMap activa."""
    data = json.loads(MAP_VISUAL.read_text(encoding="utf-8"))
    visual = data["visual"]
    if visual.get("visualType") == "azureMap":
        filled = visual.get("objects", {}).get("filledMap", [])
        if filled and filled[0].get("properties", {}).get("show", {}).get("expr", {}).get("Literal", {}).get("Value") == "true":
            return []
    return ["mapa: revisar visual.json manualmente (azureMap + filledMap)"]


def main() -> None:
    summary: list[dict] = []
    for vf in sorted(REPORT_PAGES.rglob("visual.json")):
        data = json.loads(vf.read_text(encoding="utf-8"))
        if data.get("visual", {}).get("visualType") != "slicer":
            continue
        changes = fix_slicer(data)
        if changes:
            vf.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            summary.append({"file": str(vf.relative_to(REPORT_PAGES.parent.parent)), "title": slicer_title(data), "changes": changes})

    map_changes = fix_azure_map()

    print(f"Slicers corregidos: {len(summary)}")
    for row in summary:
        print(f"  [{row['title']}] {row['file']}: {', '.join(row['changes'])}")
    if map_changes:
        print("Mapa:", ", ".join(map_changes))


if __name__ == "__main__":
    main()
