"""Audita el mapa Azure Maps: modelo, medida y bindings PBIR."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_VISUAL = (
    ROOT
    / "proyecto-bi"
    / "northwind_bi.Report"
    / "definition"
    / "pages"
    / "d72257249741148631d0"
    / "visuals"
    / "ebfc2b4fd2f76f7f2d0a"
    / "visual.json"
)
TERRITORIO_CSV = ROOT / "plan-b" / "csvs" / "dim_territorio.csv"
OUT = ROOT / "proyecto-bi" / "AUDIT-map-visual.json"


def pais_mapa(country: str) -> str:
    if country == "USA":
        return "United States"
    if country == "UK":
        return "United Kingdom"
    return country


def audit() -> dict:
    visual = json.loads(MAP_VISUAL.read_text(encoding="utf-8"))
    v = visual["visual"]
    qs = v.get("query", {}).get("queryState", {})
    buckets = set(qs.keys())
    location = qs.get("Location", {}).get("projections", [])
    loc_field = ""
    if location:
        loc_field = location[0].get("field", {}).get("Column", {}).get("Property", "")

    filled = v.get("objects", {}).get("filledMap", [{}])[0].get("properties", {})
    bubble = v.get("objects", {}).get("bubbleLayer", [{}])[0].get("properties", {})
    has_cf = "FillRule" in json.dumps(filled.get("defaultColor", {}))

    issues: list[dict] = []
    vtype = v.get("visualType")
    if vtype not in ("azureMap", "clusteredBarChart", "treemap"):
        issues.append({"severity": "error", "code": "wrong_visual_type", "detail": vtype})

    if vtype == "azureMap" and "Latitude" in buckets:
        has_cf = False
        if not bubble.get("show", {}).get("expr", {}).get("Literal", {}).get("Value") == "true":
            issues.append({"severity": "error", "code": "bubble_layer_off", "detail": "Capa burbujas desactivada."})
        if filled.get("show", {}).get("expr", {}).get("Literal", {}).get("Value") == "true":
            issues.append({"severity": "warning", "code": "filled_map_on", "detail": "Desactivar filledMap si se usan burbujas."})
    elif vtype == "clusteredBarChart":
        cat = qs.get("Category", {}).get("projections", [])
        cat_field = cat[0].get("field", {}).get("Column", {}).get("Property", "") if cat else ""
        has_cf = "FillRule" in json.dumps(v.get("objects", {}).get("dataPoint", {}))
        if cat_field != "pais_mapa":
            issues.append({"severity": "warning", "code": "category_field", "detail": cat_field})
        if not has_cf:
            issues.append({"severity": "warning", "code": "no_bar_gradient", "detail": "Sin FillRule en barras"})
    elif vtype == "azureMap" and "Latitude" not in buckets:
        if "Values" not in buckets:
            issues.append({
                "severity": "warning",
                "code": "missing_values_bucket",
                "detail": "Azure Maps choropleth suele necesitar medida en Values además de Tooltips/CF.",
            })
        loc_entity = location[0].get("field", {}).get("Column", {}).get("Expression", {}).get("SourceRef", {}).get("Entity", "") if location else ""
        if loc_field == "pais_mapa" and loc_entity == "dim_territorio":
            issues.append({
                "severity": "warning",
                "code": "territory_grain_location",
                "detail": "Location en dim_territorio (69 ciudades) duplica países; usar dim_pais (21 filas).",
            })
        if loc_entity != "dim_pais":
            issues.append({
                "severity": "warning",
                "code": "location_not_dim_pais",
                "detail": f"Location debería ser dim_pais[pais_mapa], actual: {loc_entity}.{loc_field}",
            })
        if not filled.get("show", {}).get("expr", {}).get("Literal", {}).get("Value") == "true":
            issues.append({"severity": "error", "code": "filled_map_off", "detail": "Capa filledMap desactivada."})
        if bubble.get("show", {}).get("expr", {}).get("Literal", {}).get("Value") == "true":
            issues.append({"severity": "warning", "code": "bubble_layer_on", "detail": "Capa burbujas compite con choropleth."})
        if not has_cf:
            issues.append({
                "severity": "error",
                "code": "no_conditional_format",
                "detail": "defaultColor sin FillRule (sin gradiente por medida).",
            })

    rows = []
    if TERRITORIO_CSV.exists():
        import csv

        rows = list(csv.DictReader(TERRITORIO_CSV.open(encoding="utf-8")))
    by_pais = Counter(pais_mapa(r["country"]) for r in rows)

    report = {
        "visualType": v.get("visualType"),
        "buckets": sorted(buckets),
        "locationField": loc_field,
        "filledMapShow": filled.get("show", {}).get("expr", {}).get("Literal", {}).get("Value"),
        "hasColorGradient": has_cf,
        "territoryRows": len(rows),
        "uniqueCountries": len(by_pais),
        "rowsPerCountrySample": dict(sorted(by_pais.items(), key=lambda x: -x[1])[:5]),
        "issues": issues,
        "fixesApplied": [
            "Azure Maps burbujas: dim_pais[latitud/longitud], Size=[Ventas por País], Legend=zona",
            "Fondo grayscale_light, filledMap OFF, bubbleLayer ON",
            "Treemap auxiliar: dim_pais[zona] > [country]",
        ],
    }
    return report


def main() -> None:
    report = audit()
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nAudit: {OUT}")


if __name__ == "__main__":
    main()
