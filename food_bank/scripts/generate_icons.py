"""Generate simple original SVG icons for each catalog item (CC0 / project-owned)."""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ITEMS_FILE = BASE / "items.json"
OUT_DIR = BASE / "static" / "images" / "items"

# Visual recipe per item: (primary, secondary, shape keyword)
RECIPES: dict[str, tuple[str, str, str]] = {
    "apples": ("#e11d48", "#166534", "apple"),
    "bananas": ("#facc15", "#854d0e", "banana"),
    "oranges": ("#f97316", "#166534", "orange"),
    "potatoes": ("#d4a574", "#78716c", "potato"),
    "onions": ("#fde68a", "#a16207", "onion"),
    "carrots": ("#fb923c", "#166534", "carrot"),
    "celery": ("#86efac", "#166534", "celery"),
    "lettuce": ("#4ade80", "#166534", "lettuce"),
    "tomatoes-fresh": ("#ef4444", "#166534", "tomato"),
    "broccoli": ("#22c55e", "#14532d", "broccoli"),
    "chicken-breast": ("#fecaca", "#f97316", "chicken"),
    "ground-beef": ("#991b1b", "#450a0a", "beef"),
    "eggs": ("#fef3c7", "#f59e0b", "eggs"),
    "peanut-butter": ("#ca8a04", "#854d0e", "jar"),
    "tuna": ("#64748b", "#1e3a5f", "can"),
    "lentils-dry": ("#84cc16", "#365314", "bag"),
    "turkey-slices": ("#fdba74", "#c2410c", "deli"),
    "milk": ("#f8fafc", "#2563eb", "milk"),
    "cheese-shredded": ("#fbbf24", "#ca8a04", "cheese"),
    "yogurt": ("#ffffff", "#6366f1", "tub"),
    "butter": ("#fef08a", "#ca8a04", "box"),
    "cottage-cheese": ("#f1f5f9", "#94a3b8", "tub"),
    "rice-white": ("#ffffff", "#2563eb", "bag"),
    "rice-brown": ("#d6d3d1", "#78716c", "bag"),
    "pasta-spaghetti": ("#fde68a", "#ca8a04", "box"),
    "pasta-macaroni": ("#fcd34d", "#b45309", "box"),
    "bread-loaf": ("#d97706", "#92400e", "bread"),
    "oatmeal": ("#e7e5e4", "#78716c", "canister"),
    "flour": ("#fafaf9", "#57534e", "bag"),
    "cereal": ("#f472b6", "#2563eb", "box"),
    "black-beans": ("#1e293b", "#64748b", "can"),
    "kidney-beans": ("#991b1b", "#64748b", "can"),
    "tomatoes-canned": ("#dc2626", "#64748b", "can"),
    "tomato-sauce": ("#b91c1c", "#64748b", "can"),
    "chicken-soup": ("#fde68a", "#64748b", "can"),
    "vegetable-soup": ("#4ade80", "#64748b", "can"),
    "corn-canned": ("#facc15", "#64748b", "can"),
    "green-beans-canned": ("#22c55e", "#64748b", "can"),
    "crackers": ("#fde68a", "#d97706", "box"),
    "granola-bars": ("#92400e", "#fbbf24", "box"),
    "applesauce": ("#fda4af", "#e11d48", "pack"),
    "raisins": ("#7c2d12", "#451a03", "box"),
    "juice-apple": ("#ef4444", "#166534", "bottle"),
    "juice-orange": ("#fb923c", "#166534", "bottle"),
    "coffee": ("#78350f", "#451a03", "bag"),
    "tea": ("#166534", "#14532d", "box"),
    "frozen-vegetables": ("#38bdf8", "#22c55e", "frozen"),
    "frozen-fish": ("#93c5fd", "#1e40af", "frozen"),
    "frozen-pizza": ("#fbbf24", "#dc2626", "frozen"),
    "diapers": ("#bae6fd", "#2563eb", "household"),
    "soap-bar": ("#fbcfe8", "#db2777", "household"),
    "toothpaste": ("#e0f2fe", "#0284c7", "household"),
    "toilet-paper": ("#ffffff", "#94a3b8", "household"),
    "laundry-detergent": ("#60a5fa", "#1d4ed8", "household"),
}


def svg_wrap(body: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-hidden="true">\n'
        f"{body}\n"
        "</svg>\n"
    )


def shape_svg(shape: str, primary: str, secondary: str) -> str:
    bg = f'<rect width="64" height="64" rx="12" fill="#f8fafc"/>'
    shapes = {
        "apple": f'<circle cx="32" cy="34" r="18" fill="{primary}"/><path d="M32 16c0-4 6-6 8-2" stroke="{secondary}" stroke-width="2" fill="none"/>',
        "banana": f'<path d="M18 44c8-20 20-26 28-22-4 10-10 18-20 24z" fill="{primary}" stroke="{secondary}" stroke-width="1.5"/>',
        "orange": f'<circle cx="32" cy="34" r="17" fill="{primary}"/><circle cx="28" cy="30" r="2" fill="#fff" opacity=".35"/>',
        "potato": f'<ellipse cx="32" cy="34" rx="20" ry="14" fill="{primary}"/><ellipse cx="26" cy="30" rx="3" ry="2" fill="{secondary}" opacity=".3"/>',
        "onion": f'<circle cx="32" cy="34" r="16" fill="{primary}"/><path d="M32 18v6M24 22l4 4M40 22l-4 4" stroke="{secondary}" stroke-width="1.5"/>',
        "carrot": f'<path d="M32 48L22 26c12-2 18 0 20 8z" fill="{primary}"/><path d="M28 24l4-8 4 8" stroke="{secondary}" stroke-width="2"/>',
        "celery": f'<path d="M26 48V20c0-4 6-6 6-2v30M38 48V22c0-4 6-4 6 0v26" stroke="{primary}" stroke-width="5" stroke-linecap="round"/>',
        "lettuce": f'<circle cx="32" cy="36" r="16" fill="{primary}"/><path d="M20 36c6-8 18-8 24 0" stroke="{secondary}" stroke-width="2" fill="none"/>',
        "tomato": f'<circle cx="32" cy="34" r="16" fill="{primary}"/><path d="M28 20l4-4 4 4" stroke="{secondary}" stroke-width="2" fill="none"/>',
        "broccoli": f'<circle cx="32" cy="28" r="14" fill="{primary}"/><rect x="28" y="38" width="8" height="14" rx="2" fill="{secondary}"/>',
        "chicken": f'<ellipse cx="32" cy="34" rx="18" ry="14" fill="{primary}"/><ellipse cx="32" cy="34" rx="10" ry="8" fill="{secondary}" opacity=".25"/>',
        "beef": f'<rect x="14" y="24" width="36" height="24" rx="6" fill="{primary}"/><path d="M18 30h28M18 36h28M18 42h28" stroke="{secondary}" stroke-width="1" opacity=".4"/>',
        "eggs": f'<ellipse cx="26" cy="36" rx="10" ry="13" fill="{primary}" stroke="{secondary}"/><ellipse cx="40" cy="36" rx="10" ry="13" fill="{primary}" stroke="{secondary}"/>',
        "jar": f'<rect x="22" y="18" width="20" height="32" rx="4" fill="{primary}" stroke="{secondary}"/><rect x="24" y="14" width="16" height="6" rx="2" fill="{secondary}"/>',
        "can": f'<rect x="20" y="16" width="24" height="36" rx="4" fill="{secondary}"/><rect x="22" y="22" width="20" height="16" rx="2" fill="{primary}"/>',
        "bag": f'<path d="M18 22h28l-4 30H22z" fill="{primary}"/><path d="M24 22c0-6 16-6 16 0" stroke="{secondary}" stroke-width="2" fill="none"/>',
        "deli": f'<rect x="14" y="28" width="36" height="16" rx="4" fill="{primary}"/><rect x="18" y="32" width="28" height="3" fill="{secondary}" opacity=".5"/>',
        "milk": f'<rect x="22" y="16" width="20" height="36" rx="3" fill="{primary}" stroke="{secondary}"/><path d="M24 16h16l-2-6H26z" fill="{secondary}"/>',
        "cheese": f'<rect x="16" y="28" width="32" height="18" rx="3" fill="{primary}"/><rect x="20" y="32" width="6" height="6" fill="{secondary}" opacity=".5"/><rect x="30" y="32" width="6" height="6" fill="{secondary}" opacity=".5"/>',
        "tub": f'<rect x="18" y="22" width="28" height="24" rx="6" fill="{primary}" stroke="{secondary}"/><rect x="20" y="18" width="24" height="8" rx="4" fill="{secondary}"/>',
        "box": f'<rect x="16" y="20" width="32" height="28" rx="4" fill="{primary}" stroke="{secondary}"/><path d="M16 28h32" stroke="{secondary}" opacity=".5"/>',
        "bread": f'<rect x="14" y="26" width="36" height="18" rx="8" fill="{primary}"/><path d="M18 30h28" stroke="{secondary}" opacity=".4"/>',
        "canister": f'<rect x="22" y="14" width="20" height="38" rx="8" fill="{primary}" stroke="{secondary}"/><rect x="26" y="24" width="12" height="8" rx="2" fill="{secondary}" opacity=".35"/>',
        "bottle": f'<rect x="26" y="20" width="12" height="32" rx="4" fill="{primary}"/><rect x="24" y="14" width="16" height="8" rx="3" fill="{secondary}"/>',
        "frozen": f'<rect x="14" y="18" width="36" height="30" rx="6" fill="{primary}" stroke="{secondary}"/><path d="M20 24l8 8-8 8M36 24l8 8-8 8" stroke="#fff" stroke-width="2" opacity=".7"/>',
        "household": f'<rect x="18" y="20" width="28" height="28" rx="6" fill="{primary}" stroke="{secondary}"/><circle cx="32" cy="34" r="8" fill="{secondary}" opacity=".35"/>',
    }
    body = shapes.get(shape, shapes["box"])
    return svg_wrap(bg + body)


def main() -> None:
    items = json.loads(ITEMS_FILE.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for item in items:
        item_id = item["id"]
        recipe = RECIPES.get(item_id, ("#94a3b8", "#64748b", "box"))
        svg = shape_svg(recipe[2], recipe[0], recipe[1])
        (OUT_DIR / f"{item_id}.svg").write_text(svg, encoding="utf-8")
    print(f"Generated {len(items)} icons in {OUT_DIR}")


if __name__ == "__main__":
    main()
