# Chess Openings Learning App

A static, no-build-step app for studying chess opening mainlines, sidelines, and strategy. Open the menu, pick an opening, read the notes, and step through lines on an interactive board.

## Quick start

### Option 1: Local server (recommended)

ES modules and `fetch()` for `openings.json` require serving files over HTTP on most browsers (especially when opening from Windows).

```bash
cd chess_openings
python -m http.server 8080
```

On Windows, you can also use the helper script (kills any old server on port 8080 first):

```powershell
.\serve.ps1
```

Then open [http://localhost:8080](http://localhost:8080) in your browser.

### Option 2: Direct file open

Some browsers allow opening `index.html` directly via `file://`. If the menu shows a load error, use Option 1 instead.

## What's included

| Opening | Color | First moves |
|---------|-------|-------------|
| Queen's Gambit | White | 1.d4 d5 2.c4 |
| Vienna Gambit | White | 1.e4 e5 2.Nc3 Nf6 3.f4 |
| Caro-Kann | Black | 1.e4 c6 2.d4 d5 |
| King's Indian | Black | 1.d4 Nf6 2.c4 g6 3.Nc3 Bg7 |

Each opening page includes:

- Overview and color badge
- Mainline with move notation and notes
- 2–3 common sidelines
- Strategy blocks: goals, advantages, disadvantages, long-term plans
- Interactive board with **Start**, **Prev**, **Next**, and **Play** controls

URL hash routing (`#queens-gambit`, etc.) makes links shareable and works with the browser back button.

## How to add an opening

All content lives in `openings.json`. No code changes are required for a new opening.

1. Open `openings.json` and add an object to the `"openings"` array.
2. Use a unique `"id"` (lowercase, hyphenated) — this becomes the URL hash.
3. Set `"color"` to `"white"` or `"black"` (controls which menu section it appears in).
4. Fill in the text fields and move arrays using **SAN** notation (e.g. `"Nf3"`, `"O-O"`, `"dxe4"`).

Example skeleton:

```json
{
  "id": "london-system",
  "name": "London System",
  "color": "white",
  "tagline": "Solid setup with Bf4",
  "firstMoves": "1.d4 d5 2.Bf4",
  "overview": "Two or three sentences describing the opening.",
  "goals": ["Goal one", "Goal two"],
  "advantages": ["Advantage one"],
  "disadvantages": ["Risk one"],
  "longTermPlans": ["Plan one"],
  "mainline": {
    "name": "Main Line Name",
    "moves": ["d4", "d5", "Bf4", "Nf6", "e3", "e6"],
    "notes": "Brief explanation of the line."
  },
  "sidelines": [
    {
      "name": "Sideline Name",
      "moves": ["d4", "d5", "Bf4", "c5"],
      "notes": "When and why this appears."
    }
  ]
}
```

Refresh the page — the new opening appears on the menu automatically.

### Move array tips

- Moves are in SAN without move numbers: `["e4", "e5", "Nf3"]`
- Use `"O-O"` and `"O-O-O"` for castling
- Captures and checks are written normally: `"Nxe4"`, `"Qh5+"`
- Each sideline should be a complete sequence from the starting position (or a recognizable branch point if you trim earlier moves)

## File structure

```
chess_openings/
  index.html           # App shell
  style.css            # Dark chess-themed layout
  app.js               # Menu, routing, detail view, board controller
  trial-board.js       # Interactive trial board page
  quiz.js              # Quiz mode
  engine.js            # Stockfish engine wrapper
  opening-match.js     # Opening line detection
  stockfish-worker.js  # Stockfish web worker loader
  openings.json        # All opening content
  README.md            # This file
```

## Trial Board

Use the **Trial Board** tab to play legal moves on a free board. After each move:

- **Eval bar** — position evaluation from White's perspective
- **Best move** — engine suggestion (Stockfish, depth 14)
- **Opening detection** — matches your moves against mainlines and sidelines in `openings.json`

## Quiz Mode

Use the **Quiz Mode** tab to test yourself on any opening:

- Starting move orders
- Strategic goals
- Opening identification from move sequences
- Next move in the mainline

Six questions per round with instant feedback and a score summary.

## Lichess Deep Lines

Each opening page includes optional **Deeper Lines on Lichess** links — external links to Lichess opening trees and the analysis explorer for more extensive variations.

## Dependencies (CDN)

- [chess.mjs](https://www.npmjs.com/package/chess.mjs) — move validation and FEN generation
- [cm-chessboard](https://github.com/shaack/cm-chessboard) — SVG chessboard UI
- [stockfish.js](https://www.npmjs.com/package/stockfish.js) — browser chess engine (via web worker)

No npm install or build step is required.
