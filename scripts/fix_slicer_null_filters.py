"""Remove slicer default selections that filter to null from PBIR visual.json files."""
import json
from pathlib import Path

REPORT_PAGES = Path(__file__).resolve().parents[1] / "proyecto-bi" / "northwind_bi.Report" / "definition" / "pages"

fixed: list[str] = []
for vf in REPORT_PAGES.rglob("visual.json"):
    text = vf.read_text(encoding="utf-8")
    if '"Value": "null"' not in text:
        continue
    data = json.loads(text)
    visual = data.get("visual", {})
    objects = visual.get("objects", {})
    if "general" in objects:
        del objects["general"]
        vf.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        fixed.append(str(vf.relative_to(REPORT_PAGES.parent.parent)))

print(f"Fixed {len(fixed)} files:")
for path in fixed:
    print(f"  {path}")
