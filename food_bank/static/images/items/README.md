# Item images

Transparent PNG icons for each catalog item (`{id}.png`).

## Sources (all CC0 / public domain)

- **Wikimedia Commons** — realistic CC0 icons (IconArchive, OpenClipart/Pixabay, etc.)
- **OpenGameArt** — [bluecarrot16 CC0 food pack](https://opengameart.org/content/food-icons) (upscaled pixel art for items without a Commons match)

Generic reuse (same image for similar items):

- All canned goods share one generic can icon
- Deli turkey reuses ground beef
- Brown rice / macaroni / second juices reuse their white/orange counterparts
- Tea reuses coffee (cup icon)

## Regenerate

```powershell
cd food_bank
py scripts/download_food_images.py
```

Attribution manifest: `IMAGE_SOURCES.json` (license is CC0 — credit optional).

Legacy SVG placeholders from `scripts/generate_icons.py` are kept for reference but are no longer used by the shop UI.
