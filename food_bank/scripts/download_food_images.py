"""Build CC0 PNG item images from Wikimedia Commons + OpenGameArt (bluecarrot16).

Uses direct upload/thumbnail URLs (no Commons API) to avoid rate limits.
Run: py scripts/download_food_images.py
"""

from __future__ import annotations

import json
import shutil
import time
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent.parent
OUT_DIR = BASE / "static" / "images" / "items"
ITEMS_FILE = BASE / "items.json"
SOURCES_FILE = OUT_DIR / "IMAGE_SOURCES.json"
OGA_ROOT = BASE / "scripts" / "_tmp_oga" / "bluecarrot"
OGA_ZIP = BASE / "scripts" / "_tmp_oga" / "food-bluecarrot16_20201221.zip"

USER_AGENT = "FoodBankOrderApp/1.0 (education; local catalog icons)"
DOWNLOAD_DELAY_SEC = 6

# item_id -> direct PNG URL (CC0 / public domain on Wikimedia Commons)
WIKIMEDIA_URLS: dict[str, str] = {
    "apples": "https://upload.wikimedia.org/wikipedia/commons/9/91/Green_Apple_Icon.png",
    "bananas": "https://upload.wikimedia.org/wikipedia/commons/3/31/Banana_Icon.png",
    "potatoes": "https://upload.wikimedia.org/wikipedia/commons/4/42/Potatoes.png",
    "milk": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Milk_carton_icon.svg/330px-Milk_carton_icon.svg.png",
    "bread-loaf": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Jean_victor_balin_bread.svg/330px-Jean_victor_balin_bread.svg.png",
    "chicken-breast": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Baked_chicken_icon.svg/120px-Baked_chicken_icon.svg.png",
    "ground-beef": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Beef_icon.svg/120px-Beef_icon.svg.png",
    "pasta-spaghetti": "https://commons.wikimedia.org/w/thumb.php?width=330&f=Food-luxury-pasta.svg",
    "frozen-pizza": "https://commons.wikimedia.org/w/thumb.php?width=330&f=Pizza.svg",
    "black-beans": "https://commons.wikimedia.org/w/thumb.php?width=330&f=Green_soda_can_3d.svg",
    "juice-apple": "https://commons.wikimedia.org/w/thumb.php?width=330&f=Honey_Jar_icon.svg",
    "raisins": "https://upload.wikimedia.org/wikipedia/commons/8/86/Strawberry_%28transparent_background%29.png",
}

# item_id -> path inside extracted bluecarrot pack (CC0, OpenGameArt)
OGA_PATHS: dict[str, str] = {
    "oranges": "orig/fruit/mango_red.png",
    "onions": "orig/vegetable/leek.png",
    "carrots": "orig/vegetable/rhubarb.png",
    "celery": "orig/vegetable/celery.png",
    "lettuce": "orig/vegetable/lettuce_romaine.png",
    "tomatoes-fresh": "orig/fruit/tomatoes_cherry.png",
    "broccoli": "orig/vegetable/brussels_sprouts.png",
    "eggs": "orig/egg/egg_brown.png",
    "peanut-butter": "orig/nut/nuts_peanut.png",
    "tuna": "orig/seafood/fish_tilapia.png",
    "lentils-dry": "orig/nut/nuts_walnut.png",
    "cheese-shredded": "orig/cheese/cheese_jack.png",
    "yogurt": "orig/cheese/cheese_feta.png",
    "butter": "orig/misc/butter.png",
    "cottage-cheese": "orig/cheese/cheese_mozarella.png",
    "rice-white": "orig/pastry/pie.png",
    "oatmeal": "orig/misc/pancakes.png",
    "flour": "orig/bread/bread_unknown.png",
    "cereal": "orig/misc/waffles.png",
    "crackers": "orig/pastry/pie_braided.png",
    "granola-bars": "orig/pastry/donut.png",
    "frozen-vegetables": "orig/vegetable/green_beans.png",
    "frozen-fish": "orig/seafood/fish_halibut.png",
    "diapers": "orig/pastry/cake.png",
    "soap-bar": "orig/misc/butter.png",
    "toothpaste": "orig/misc/coffee_beans.png",
    "toilet-paper": "orig/bread/bread_cob_roll.png",
    "laundry-detergent": "orig/fruit/coconut.png",
    "coffee": "orig/misc/coffee_beans.png",
    "tomatoes-fresh": "orig/fruit/tomatoes_cherry.png",
}

# Copy from another item after primary sources are written
GENERIC_ALIASES: dict[str, str] = {
    "turkey-slices": "ground-beef",
    "rice-brown": "rice-white",
    "pasta-macaroni": "pasta-spaghetti",
    "kidney-beans": "black-beans",
    "tomatoes-canned": "black-beans",
    "tomato-sauce": "black-beans",
    "chicken-soup": "black-beans",
    "vegetable-soup": "black-beans",
    "corn-canned": "black-beans",
    "green-beans-canned": "black-beans",
    "tea": "coffee",
    "juice-orange": "juice-apple",
    "applesauce": "apples",
}


def download_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read()


def normalize_png(data: bytes, size: int = 256, pixel_art: bool = False) -> bytes:
    img = Image.open(BytesIO(data))
    if img.mode not in ("RGBA", "LA"):
        img = img.convert("RGBA")
    resample = Image.Resampling.NEAREST if pixel_art else Image.Resampling.LANCZOS
    img.thumbnail((size, size), resample)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset = ((size - img.width) // 2, (size - img.height) // 2)
    canvas.paste(img, offset, img if img.mode == "RGBA" else None)
    out = BytesIO()
    canvas.save(out, format="PNG", optimize=True)
    return out.getvalue()


def find_oga_file(rel: str) -> Path | None:
    p = OGA_ROOT / rel.replace("/", "\\")
    if p.exists():
        return p
    matches = list(OGA_ROOT.rglob(Path(rel).name))
    return matches[0] if matches else None


def ensure_oga_extracted() -> None:
    import zipfile

    if OGA_ROOT.exists() or not OGA_ZIP.exists():
        return
    with zipfile.ZipFile(OGA_ZIP) as zf:
        zf.extractall(OGA_ROOT)


def write_png(item_id: str, png: bytes, sources: dict, meta: dict) -> None:
    dest = OUT_DIR / f"{item_id}.png"
    dest.write_bytes(png)
    sources[item_id] = meta


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ensure_oga_extracted()

    items = json.loads(ITEMS_FILE.read_text(encoding="utf-8"))
    item_ids = [i["id"] for i in items]
    cat_map = {i["id"]: i["category"] for i in items}
    sources: dict[str, dict] = {}

    print("Wikimedia Commons (CC0 / public domain, direct URLs)...")
    for item_id, url in WIKIMEDIA_URLS.items():
        if item_id not in item_ids:
            continue
        print(f"  {item_id}")
        try:
            time.sleep(DOWNLOAD_DELAY_SEC)
            raw = download_bytes(url)
            png = normalize_png(raw)
            write_png(
                item_id,
                png,
                sources,
                {
                    "source": "wikimedia-commons",
                    "license": "CC0 or public domain",
                    "url": url,
                },
            )
            print(f"    OK ({len(png) // 1024} KB)")
        except Exception as exc:
            print(f"    error: {exc}")

    print("\nOpenGameArt bluecarrot16 (CC0)...")
    for item_id, rel in OGA_PATHS.items():
        if item_id not in item_ids:
            continue
        if (OUT_DIR / f"{item_id}.png").exists():
            continue
        src = find_oga_file(rel)
        if not src:
            print(f"  {item_id}: missing OGA file {rel}")
            continue
        print(f"  {item_id} <- {rel}")
        raw = src.read_bytes()
        png = normalize_png(raw, pixel_art=True)
        write_png(
            item_id,
            png,
            sources,
            {
                "source": "opengameart-bluecarrot16",
                "license": "CC0",
                "file": rel,
            },
        )

    print("\nApplying generic aliases...")
    for item_id, alias in GENERIC_ALIASES.items():
        if item_id not in item_ids:
            continue
        src_path = OUT_DIR / f"{alias}.png"
        if not src_path.exists():
            print(f"  skip {item_id} (missing alias source {alias})")
            continue
        dest = OUT_DIR / f"{item_id}.png"
        shutil.copyfile(src_path, dest)
        sources[item_id] = {"source": "alias", "from": alias, **sources.get(alias, {})}
        print(f"  {item_id} <- {alias}")

    missing = [i for i in item_ids if not (OUT_DIR / f"{i}.png").exists()]
    if missing:
        print("\nCategory fallbacks...")
        by_cat: dict[str, Path] = {}
        for iid in item_ids:
            p = OUT_DIR / f"{iid}.png"
            if p.exists():
                by_cat.setdefault(cat_map[iid], p)
        for item_id in missing:
            cat = cat_map[item_id]
            fallback = by_cat.get(cat)
            if fallback:
                shutil.copyfile(fallback, OUT_DIR / f"{item_id}.png")
                sources[item_id] = {"source": "category-fallback", "category": cat}
                print(f"  {item_id} <- {cat}")

    missing = [i for i in item_ids if not (OUT_DIR / f"{i}.png").exists()]
    print(f"\nDone. {len(item_ids) - len(missing)}/{len(item_ids)} PNGs written.")
    if missing:
        print("Still missing:", ", ".join(missing))

    SOURCES_FILE.write_text(json.dumps(sources, indent=2), encoding="utf-8")
    print(f"Wrote {SOURCES_FILE.relative_to(BASE)}")


if __name__ == "__main__":
    main()
