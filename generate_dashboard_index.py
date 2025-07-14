# File: generate_dashboard_index.py

from pathlib import Path
import html

# Configuration
PROJECT_ROOT = Path(__file__).parent
RESULTS_DIR = PROJECT_ROOT / "results"
OUTPUT_FILE = PROJECT_ROOT / "index.html"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Dashboard Gallery</title>
  <style>
    body {{ font-family: sans-serif; margin: 20px; }}
    h1 {{ text-align: center; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }}
    .item {{ text-align: center; }}
    .item img {{ max-width: 100%; height: auto; border: 1px solid #ccc; }}
    .caption {{ margin-top: 8px; font-size: 0.9em; color: #333; }}
  </style>
</head>
<body>
  <h1>Dashboard Gallery</h1>
  <div class="grid">
    {items}
  </div>
</body>
</html>
"""

ITEM_TEMPLATE = """
<div class="item">
  <a href="{rel_path}" target="_blank">
    <img src="{rel_path}" alt="{name}">
  </a>
  <div class="caption">{name}</div>
</div>
"""

def main():
    if not RESULTS_DIR.exists():
        print(f"❌ Results directory not found at {RESULTS_DIR}")
        return

    # Find all dashboard PNGs
    dashboards = sorted(RESULTS_DIR.glob("*_dashboard.png"))
    if not dashboards:
        print("⚠️  No *_dashboard.png files found in results/")
        return

    items_html = []
    for img_path in dashboards:
        rel = img_path.relative_to(PROJECT_ROOT).as_posix()
        name = html.escape(img_path.stem)
        items_html.append(ITEM_TEMPLATE.format(rel_path=rel, name=name))

    page = HTML_TEMPLATE.format(items="\n".join(items_html))

    # Write out the index.html
    OUTPUT_FILE.write_text(page, encoding="utf-8")
    print(f"✅ Gallery generated at {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
