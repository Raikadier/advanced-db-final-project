"""Limpia slicers (sin selección guardada) y reemplaza Azure Map por mapa relleno."""
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


def fix_slicer(data: dict) -> list[str]:
    changes: list[str] = []
    visual = data.setdefault("visual", {})
    objects = visual.setdefault("objects", {})

    if "general" in objects:
        del objects["general"]
        changes.append("quitar selección guardada")

    if "selection" in objects:
        for block in objects["selection"]:
            props = block.get("properties", {})
            if "strictSingleSelect" in props:
                del props["strictSingleSelect"]
                changes.append("quitar strictSingleSelect")
        if objects["selection"] and all(not b.get("properties") for b in objects["selection"]):
            del objects["selection"]

    if visual.get("drillFilterOtherVisuals") is not False:
        visual["drillFilterOtherVisuals"] = False
        changes.append("drillFilterOtherVisuals=false")

    sync = visual.get("syncGroup")
    if sync and sync.get("filterChanges") is not False:
        sync["filterChanges"] = False
        changes.append("sync filterChanges=false")

    return changes


def fix_filled_map() -> list[str]:
    data = json.loads(MAP_VISUAL.read_text(encoding="utf-8"))
    visual = data["visual"]
    if visual.get("visualType") == "filledMap":
        return []

    visual["visualType"] = "filledMap"
    visual["objects"] = {
        "mapStyles": [
            {
                "properties": {
                    "mapTheme": {
                        "expr": {"Literal": {"Value": "'grayscale'"}}
                    }
                }
            }
        ],
        "dataPoint": [
            {
                "properties": {
                    "fill": {
                        "solid": {
                            "color": {
                                "expr": {"Literal": {"Value": "'#093824'"}}
                            }
                        }
                    }
                }
            }
        ],
        "labels": [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "fontSize": {"expr": {"Literal": {"Value": "9D"}}},
                }
            }
        ],
        "legend": [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "position": {"expr": {"Literal": {"Value": "'Top'"}}},
                    "showTitle": {"expr": {"Literal": {"Value": "false"}}},
                    "fontSize": {"expr": {"Literal": {"Value": "9D"}}},
                }
            }
        ],
    }
    visual["visualContainerObjects"]["title"][0]["properties"]["text"] = {
        "expr": {"Literal": {"Value": "'Ventas por País (mapa)'"}}
    }
    visual["drillFilterOtherVisuals"] = True

    MAP_VISUAL.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ["azureMap a filledMap"]


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

    map_changes = fix_filled_map()

    print(f"Slicers corregidos: {len(summary)}")
    for row in summary:
        print(f"  [{row['title']}] {row['file']}: {', '.join(row['changes'])}")
    if map_changes:
        print("Mapa:", ", ".join(map_changes))


if __name__ == "__main__":
    main()
