import {
  Chessboard,
  FEN,
  INPUT_EVENT_TYPE,
  COLOR,
  BORDER_TYPE,
} from "https://cdn.jsdelivr.net/npm/cm-chessboard@8/src/Chessboard.js";
import { MARKER_TYPE, Markers } from "https://cdn.jsdelivr.net/npm/cm-chessboard@8/src/extensions/markers/Markers.js";
import {
  PROMOTION_DIALOG_RESULT_TYPE,
  PromotionDialog,
} from "https://cdn.jsdelivr.net/npm/cm-chessboard@8/src/extensions/promotion-dialog/PromotionDialog.js";
import { Chess } from "https://cdn.jsdelivr.net/npm/chess.mjs@1/src/chess.mjs/Chess.js";
import {
  StockfishEngine,
  formatEval,
  evalToBarPercent,
  uciToSan,
} from "./engine.js";
import {
  buildLineIndex,
  findInBookMatches,
  findBestPartialMatch,
  findCompletedLines,
  formatMatchedMoves,
} from "./opening-match.js";

let trialBoard = null;
let trialGame = null;
let trialEngine = null;
let lineIndex = [];
let analysisToken = 0;
let containerEl = null;

function formatMoveList(moves) {
  const parts = [];
  for (let i = 0; i < moves.length; i += 2) {
    const moveNum = Math.floor(i / 2) + 1;
    const white = moves[i];
    const black = moves[i + 1];
    if (black !== undefined) {
      parts.push(`${moveNum}.${white} ${black}`);
    } else {
      parts.push(`${moveNum}.${white}`);
    }
  }
  return parts.join(" ");
}

function sideToMoveColor() {
  return trialGame.turn() === "w" ? COLOR.white : COLOR.black;
}

function enableInputForCurrentTurn() {
  if (!trialBoard) return;
  if (trialGame.game_over()) {
    trialBoard.disableMoveInput();
    return;
  }
  trialBoard.enableMoveInput(trialInputHandler, sideToMoveColor());
}

function updateMoveHistory() {
  const historyEl = document.getElementById("trialMoveHistory");
  if (!historyEl) return;
  const history = trialGame.history();
  historyEl.textContent = history.length ? formatMoveList(history) : "No moves yet";
}

function renderOpeningPanel() {
  const panel = document.getElementById("trialOpeningPanel");
  if (!panel) return;

  const played = trialGame.history();
  if (played.length === 0) {
    panel.innerHTML = `<p class="trial-opening-empty">Make moves to detect openings from your repertoire.</p>`;
    return;
  }

  const inBook = findInBookMatches(played, lineIndex);
  const completed = findCompletedLines(played, lineIndex);
  const partial = findBestPartialMatch(played, lineIndex);

  if (completed.length > 0) {
    const cards = completed
      .slice(0, 6)
      .map(
        (line) => `
        <article class="trial-opening-card">
          <div class="trial-opening-card-header">
            <strong>${line.openingName}</strong>
            <span class="color-badge badge-${line.openingColor}">${line.openingColor}</span>
          </div>
          <p class="trial-opening-line">${line.lineName}${line.type === "sideline" ? " (sideline)" : ""}</p>
          <p class="move-notation">${formatMatchedMoves(line.moves, line.moves.length)}</p>
          <a href="#${line.openingId}" class="trial-opening-link">View opening &rarr;</a>
        </article>
      `
      )
      .join("");

    const continued = played.length > completed[0].moves.length;
    const statusNote = continued
      ? ` — continued ${played.length - completed[0].moves.length} move${played.length - completed[0].moves.length > 1 ? "s" : ""} past this line`
      : "";

    panel.innerHTML = `
      <p class="trial-opening-status complete">Line complete${statusNote}</p>
      <div class="trial-opening-cards">${cards}</div>
    `;

    panel.querySelectorAll(".trial-opening-link").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        window.location.hash = link.getAttribute("href").slice(1);
      });
    });
    return;
  }

  if (inBook.length > 0) {
    const cards = inBook
      .slice(0, 6)
      .map(
        (line) => `
        <article class="trial-opening-card">
          <div class="trial-opening-card-header">
            <strong>${line.openingName}</strong>
            <span class="color-badge badge-${line.openingColor}">${line.openingColor}</span>
          </div>
          <p class="trial-opening-line">${line.lineName}${line.type === "sideline" ? " (sideline)" : ""}</p>
          <p class="move-notation">${formatMatchedMoves(line.moves, played.length)}</p>
          <a href="#${line.openingId}" class="trial-opening-link">View opening &rarr;</a>
        </article>
      `
      )
      .join("");

    panel.innerHTML = `
      <p class="trial-opening-status in-book">In repertoire — ${inBook.length} matching line${inBook.length > 1 ? "s" : ""}</p>
      <div class="trial-opening-cards">${cards}</div>
    `;

    panel.querySelectorAll(".trial-opening-link").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        window.location.hash = link.getAttribute("href").slice(1);
      });
    });
    return;
  }

  if (partial && partial.deviated) {
    panel.innerHTML = `
      <p class="trial-opening-status deviated">Left repertoire after ${partial.matchedMoves} move${partial.matchedMoves > 1 ? "s" : ""}</p>
      <article class="trial-opening-card">
        <div class="trial-opening-card-header">
          <strong>${partial.openingName}</strong>
          <span class="color-badge badge-${partial.openingColor}">${partial.openingColor}</span>
        </div>
        <p class="trial-opening-line">${partial.lineName}</p>
        <p class="move-notation">${formatMatchedMoves(partial.moves, partial.matchedMoves)}</p>
        <p class="line-notes">Your move <strong>${played[partial.matchedMoves]}</strong> is not in this line.</p>
        <a href="#${partial.openingId}" class="trial-opening-link">View opening &rarr;</a>
      </article>
    `;
    panel.querySelector(".trial-opening-link")?.addEventListener("click", (e) => {
      e.preventDefault();
      window.location.hash = partial.openingId;
    });
    return;
  }

  panel.innerHTML = `<p class="trial-opening-empty">No match with taught openings yet.</p>`;
}

function updateEvalUI(result) {
  const evalText = document.getElementById("trialEvalText");
  const bestMoveEl = document.getElementById("trialBestMove");
  const barWhite = document.getElementById("trialEvalBarWhite");

  if (!evalText || !bestMoveEl) return;

  if (!result) {
    evalText.textContent = "Analyzing…";
    bestMoveEl.textContent = "—";
    if (barWhite) barWhite.style.width = "50%";
    return;
  }

  const side = trialGame.turn();
  evalText.textContent = formatEval(result.score, side);
  const san = uciToSan(trialGame.fen(), result.bestmove, Chess);
  bestMoveEl.textContent = san ?? result.bestmove ?? "—";

  const whitePct = evalToBarPercent(result.score, side);
  if (barWhite) barWhite.style.width = `${whitePct}%`;
}

async function requestAnalysis() {
  if (!trialEngine || !trialGame) return;

  const token = ++analysisToken;
  updateEvalUI(null);

  try {
    await trialEngine.waitUntilReady();
    const result = await trialEngine.analyze(trialGame.fen(), 14);
    if (token !== analysisToken) return;
    updateEvalUI(result);
  } catch (err) {
    console.error(err);
    if (token !== analysisToken) return;
    document.getElementById("trialEvalText").textContent = "Engine unavailable";
  }
}

function afterPositionChange() {
  updateMoveHistory();
  renderOpeningPanel();
  requestAnalysis();
  enableInputForCurrentTurn();
}

function applyMove(from, to, promotion) {
  const move = trialGame.move({ from, to, promotion });
  if (!move) return false;

  trialBoard.disableMoveInput();
  trialBoard.setPosition(trialGame.fen(), true).then(() => {
    afterPositionChange();
  });
  return true;
}

function trialInputHandler(event) {
  if (event.type === INPUT_EVENT_TYPE.movingOverSquare) return;

  if (event.type !== INPUT_EVENT_TYPE.moveInputFinished) {
    event.chessboard.removeLegalMovesMarkers();
  }

  if (event.type === INPUT_EVENT_TYPE.moveInputStarted) {
    const moves = trialGame.moves({ square: event.squareFrom, verbose: true });
    event.chessboard.addLegalMovesMarkers(moves);
    return moves.length > 0;
  }

  if (event.type === INPUT_EVENT_TYPE.validateMoveInput) {
    const move = {
      from: event.squareFrom,
      to: event.squareTo,
      promotion: event.promotion,
    };
    const result = trialGame.move(move);

    if (result) {
      event.chessboard.state.moveInputProcess.then(() => {
        event.chessboard.setPosition(trialGame.fen(), true).then(() => {
          afterPositionChange();
        });
      });
      return true;
    }

    const possibleMoves = trialGame.moves({ square: event.squareFrom, verbose: true });
    for (const possibleMove of possibleMoves) {
      if (possibleMove.promotion && possibleMove.to === event.squareTo) {
        event.chessboard.showPromotionDialog(
          event.squareTo,
          sideToMoveColor(),
          (promoResult) => {
            if (promoResult.type === PROMOTION_DIALOG_RESULT_TYPE.pieceSelected) {
              applyMove(
                event.squareFrom,
                event.squareTo,
                promoResult.piece.charAt(1)
              );
            } else {
              enableInputForCurrentTurn();
              event.chessboard.setPosition(trialGame.fen(), true);
            }
          }
        );
        return true;
      }
    }

    return false;
  }

  if (event.type === INPUT_EVENT_TYPE.moveInputFinished && event.legalMove) {
    event.chessboard.disableMoveInput();
  }
}

function resetTrialGame() {
  analysisToken++;
  trialGame.reset();
  trialBoard.setPosition(trialGame.fen(), false).then(() => {
    afterPositionChange();
  });
}

function undoTrialMove() {
  if (trialGame.history().length === 0) return;
  analysisToken++;
  trialGame.undo();
  trialBoard.setPosition(trialGame.fen(), true).then(() => {
    afterPositionChange();
  });
}

function initTrialBoardElement() {
  const boardEl = document.getElementById("trialChessboard");
  if (!boardEl) return;

  trialBoard = new Chessboard(boardEl, {
    position: FEN.start,
    assetsUrl: "https://cdn.jsdelivr.net/npm/cm-chessboard@8/assets/",
    style: {
      cssClass: "chessboard-demo",
      borderType: BORDER_TYPE.none,
    },
    extensions: [
      { class: Markers, props: { autoMarkers: MARKER_TYPE.square } },
      { class: PromotionDialog },
    ],
  });

  enableInputForCurrentTurn();
}

export function renderTrialBoard(container, openings) {
  containerEl = container;
  lineIndex = buildLineIndex(openings);
  trialGame = new Chess();

  container.innerHTML = `
    <div class="trial-layout">
      <aside class="board-panel trial-board-panel">
        <div id="trialChessboard" class="board-container trial-board-container"></div>
        <div class="eval-bar-wrap">
          <span class="eval-bar-label eval-bar-label-black">Black</span>
          <div class="eval-bar" id="trialEvalBar">
            <div class="eval-bar-white" id="trialEvalBarWhite"></div>
          </div>
          <span class="eval-bar-label eval-bar-label-white">White</span>
        </div>
        <div class="trial-engine-info">
          <p><span class="trial-engine-label">Eval</span> <strong id="trialEvalText">Loading engine…</strong></p>
          <p><span class="trial-engine-label">Best</span> <strong id="trialBestMove" class="trial-best-move">—</strong></p>
        </div>
        <div class="board-buttons">
          <button type="button" id="trialResetBtn" class="board-btn">Reset</button>
          <button type="button" id="trialUndoBtn" class="board-btn">Undo</button>
        </div>
      </aside>

      <div class="trial-content">
        <nav class="detail-nav">
          <a href="#" class="back-link" id="trialBackToMenu">&larr; Back to menu</a>
        </nav>
        <header class="detail-header">
          <h2>Trial Board</h2>
        </header>
        <p class="trial-intro">Drag pieces to play legal moves. Engine analysis and opening detection update after each move.</p>

        <section class="detail-section">
          <h3>Move History</h3>
          <p id="trialMoveHistory" class="move-notation trial-move-history">No moves yet</p>
        </section>

        <section class="detail-section">
          <h3>Opening Detection</h3>
          <div id="trialOpeningPanel"></div>
        </section>
      </div>
    </div>
  `;

  document.getElementById("trialBackToMenu")?.addEventListener("click", (e) => {
    e.preventDefault();
    window.dispatchEvent(new CustomEvent("navigate-menu"));
  });
  document.getElementById("trialResetBtn")?.addEventListener("click", resetTrialGame);
  document.getElementById("trialUndoBtn")?.addEventListener("click", undoTrialMove);

  initTrialBoardElement();
  trialEngine = new StockfishEngine();
  renderOpeningPanel();
  requestAnalysis();
}

export function destroyTrialBoard() {
  analysisToken++;
  if (trialEngine) {
    trialEngine.destroy();
    trialEngine = null;
  }
  if (trialBoard) {
    trialBoard.destroy();
    trialBoard = null;
  }
  trialGame = null;
  if (containerEl) {
    containerEl.innerHTML = "";
    containerEl = null;
  }
}
