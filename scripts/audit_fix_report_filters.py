"""Audit PBIR slicer filter state and apply fixes for flash-then-blank reports."""
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
PAGES_JSON = REPORT_PAGES / "pages.json"


def extract_slicer_selection(data: dict) -> str | None:
    visual = data.get("visual", {})
    if visual.get("visualType") != "slicer":
        return None
    general = visual.get("objects", {}).get("general", [])
    if not general:
        return None
    try:
        values = (
            general[0]["properties"]["filter"]["filter"]["Where"][0]["Condition"]["In"]["Values"]
        )
        return json.dumps(values, ensure_ascii=False)
    except (KeyError, IndexError, TypeError):
        return "<unparsed>"


def main() -> None:
    audit: list[dict] = []
    fixed_general = 0
    fixed_sync = 0
    fixed_drill = 0

    for vf in sorted(REPORT_PAGES.rglob("visual.json")):
        data = json.loads(vf.read_text(encoding="utf-8"))
        visual = data.get("visual", {})
        if visual.get("visualType") != "slicer":
            continue

        rel = str(vf.relative_to(REPORT_PAGES.parent.parent))
        title = ""
        for block in visual.get("visualContainerObjects", {}).get("title", []):
            lit = block.get("properties", {}).get("text", {}).get("expr", {}).get("Literal", {})
            if "Value" in lit:
                title = lit["Value"].strip("'")
                break

        selection = extract_slicer_selection(data)
        sync = visual.get("syncGroup", {})
        audit.append(
            {
                "file": rel,
                "title": title,
                "savedSelection": selection,
                "syncGroup": sync.get("groupName"),
                "filterChanges": sync.get("filterChanges"),
                "drillFilterOtherVisuals": visual.get("drillFilterOtherVisuals"),
            }
        )

        objects = visual.setdefault("objects", {})
        if "general" in objects:
            del objects["general"]
            fixed_general += 1

        if "syncGroup" in visual:
            visual["syncGroup"]["filterChanges"] = False
            fixed_sync += 1

        if visual.get("drillFilterOtherVisuals") is not False:
            visual["drillFilterOtherVisuals"] = False
            fixed_drill += 1

        # strictSingleSelect en año/trimestre fuerza selección vacía que filtra todo
        if title in ("Año", "Trimestre", "anio", "trimestre"):
            objects = visual.setdefault("objects", {})
            selection_blocks = objects.get("selection", [])
            for block in selection_blocks:
                props = block.get("properties", {})
                props.pop("strictSingleSelect", None)
            if selection_blocks and all(not b.get("properties") for b in selection_blocks):
                del objects["selection"]

        vf.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    pages = json.loads(PAGES_JSON.read_text(encoding="utf-8"))
    old_active = pages.get("activePageName")
    pages["activePageName"] = "e3e43335c708953e4407"
    PAGES_JSON.write_text(json.dumps(pages, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    out = REPORT_PAGES.parent.parent / "AUDIT-report-filters.json"
    out.write_text(
        json.dumps(
            {
                "diagnosis": "flash_then_blank = modelo OK, filtros de segmentador se aplican tras el render",
                "slicers": audit,
                "fixes": {
                    "removedGeneralBlocks": fixed_general,
                    "syncFilterChangesDisabled": fixed_sync,
                    "slicerDrillFilterDisabled": fixed_drill,
                    "activePage": {"from": old_active, "to": "e3e43335c708953e4407"},
                },
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(audit, indent=2, ensure_ascii=False))
    print(f"\nFixes: general={fixed_general}, sync={fixed_sync}, drill={fixed_drill}")
    print(f"Audit written to {out}")


if __name__ == "__main__":
    main()
