import { Chessboard, FEN, COLOR } from "https://cdn.jsdelivr.net/npm/cm-chessboard@8/src/Chessboard.js";
import { Chess } from "https://cdn.jsdelivr.net/npm/chess.mjs@1/src/chess.mjs/Chess.js";
import { renderTrialBoard, destroyTrialBoard } from "./trial-board.js";
import { renderQuizMode, destroyQuizMode } from "./quiz.js";

const menuView = document.getElementById("menuView");
const detailView = document.getElementById("detailView");
const trialView = document.getElementById("trialView");
const quizView = document.getElementById("quizView");
const whiteOpeningsEl = document.getElementById("whiteOpenings");
const blackOpeningsEl = document.getElementById("blackOpenings");
const tabOpenings = document.getElementById("tabOpenings");
const tabTrialBoard = document.getElementById("tabTrialBoard");
const tabQuiz = document.getElementById("tabQuiz");
let openingsData = [];
let board = null;

const boardControllerState = {
  moves: [],
  stepIndex: -1,
  playTimer: null,
  activeLineId: null,
};

function formatMoveList(moves) {
  if (!moves || moves.length === 0) return "";

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

function formatMoveLabel(moves, stepIndex) {
  if (stepIndex < 0) return "Starting position";
  const move = moves[stepIndex];
  const moveNum = Math.floor(stepIndex / 2) + 1;
  if (stepIndex % 2 === 0) {
    return `${moveNum}.${move}`;
  }
  return `${moveNum}...${move}`;
}

function goToMove(moves, stepIndex) {
  const game = new Chess();
  for (let i = 0; i <= stepIndex; i++) {
    const result = game.move(moves[i]);
    if (!result) break;
  }
  if (board) {
    board.setPosition(game.fen(), false);
  }
  return game;
}

function stopPlay() {
  if (boardControllerState.playTimer) {
    clearInterval(boardControllerState.playTimer);
    boardControllerState.playTimer = null;
  }
  const playBtn = document.getElementById("boardPlayBtn");
  if (playBtn) playBtn.textContent = "Play";
}

function updateBoardControls() {
  const { moves, stepIndex } = boardControllerState;
  const label = document.getElementById("boardMoveLabel");
  const counter = document.getElementById("boardMoveCounter");

  if (label) label.textContent = formatMoveLabel(moves, stepIndex);
  if (counter) {
    counter.textContent = `${Math.max(0, stepIndex + 1)} / ${moves.length}`;
  }

  const prevBtn = document.getElementById("boardPrevBtn");
  const nextBtn = document.getElementById("boardNextBtn");
  if (prevBtn) prevBtn.disabled = stepIndex < 0;
  if (nextBtn) nextBtn.disabled = stepIndex >= moves.length - 1;
}

function loadLine(lineId, moves) {
  stopPlay();
  boardControllerState.moves = moves;
  boardControllerState.stepIndex = -1;
  boardControllerState.activeLineId = lineId;

  document.querySelectorAll(".line-card.active").forEach((el) => {
    el.classList.remove("active");
  });
  const activeCard = document.querySelector(`[data-line-id="${lineId}"]`);
  if (activeCard) activeCard.classList.add("active");

  goToMove(moves, -1);
  updateBoardControls();
}

function boardStart() {
  stopPlay();
  boardControllerState.stepIndex = -1;
  goToMove(boardControllerState.moves, -1);
  updateBoardControls();
}

function boardPrev() {
  stopPlay();
  if (boardControllerState.stepIndex >= 0) {
    boardControllerState.stepIndex--;
    goToMove(boardControllerState.moves, boardControllerState.stepIndex);
    updateBoardControls();
  }
}

function boardNext() {
  stopPlay();
  if (boardControllerState.stepIndex < boardControllerState.moves.length - 1) {
    boardControllerState.stepIndex++;
    goToMove(boardControllerState.moves, boardControllerState.stepIndex);
    updateBoardControls();
  }
}

function boardPlay() {
  const playBtn = document.getElementById("boardPlayBtn");
  if (boardControllerState.playTimer) {
    stopPlay();
    return;
  }

  if (playBtn) playBtn.textContent = "Pause";

  boardControllerState.playTimer = setInterval(() => {
    if (boardControllerState.stepIndex >= boardControllerState.moves.length - 1) {
      stopPlay();
      return;
    }
    boardControllerState.stepIndex++;
    goToMove(boardControllerState.moves, boardControllerState.stepIndex);
    updateBoardControls();
  }, 800);
}

function initBoard(opening) {
  const boardEl = document.getElementById("chessboard");
  if (!boardEl) return;

  if (board) {
    board.destroy();
    board = null;
  }

  const orientation = opening.color === "black" ? COLOR.black : COLOR.white;

  board = new Chessboard(boardEl, {
    position: FEN.start,
    orientation,
    assetsUrl: "https://cdn.jsdelivr.net/npm/cm-chessboard@8/assets/",
    style: {
      cssClass: "chessboard-demo",
    },
  });

  document.getElementById("boardStartBtn")?.addEventListener("click", boardStart);
  document.getElementById("boardPrevBtn")?.addEventListener("click", boardPrev);
  document.getElementById("boardNextBtn")?.addEventListener("click", boardNext);
  document.getElementById("boardPlayBtn")?.addEventListener("click", boardPlay);
}

function renderStrategyList(items) {
  return items.map((item) => `<li>${item}</li>`).join("");
}

function renderLineCard(line, lineId, type) {
  const notation = formatMoveList(line.moves);
  return `
    <article class="line-card" data-line-id="${lineId}" data-type="${type}">
      <div class="line-header">
        <h4 class="line-name">${line.name}</h4>
        <button type="button" class="show-board-btn" data-line-id="${lineId}">Show on board</button>
      </div>
      <p class="move-notation">${notation}</p>
      <p class="line-notes">${line.notes}</p>
    </article>
  `;
}

function renderLichessSection(opening) {
  if (!opening.lichessResources?.length) return "";

  const links = opening.lichessResources
    .map(
      (resource) => `
      <a href="${resource.url}" target="_blank" rel="noopener noreferrer" class="lichess-card">
        <strong>${resource.name}</strong>
        <span>${resource.description}</span>
      </a>
    `
    )
    .join("");

  return `
    <section class="detail-section">
      <h3>Deeper Lines on Lichess</h3>
      <p class="lichess-intro">Optional — explore more extensive variations, stats, and master games on Lichess.</p>
      <div class="lichess-links">${links}</div>
    </section>
  `;
}

function renderOpeningDetail(opening) {
  const colorLabel = opening.color === "white" ? "White" : "Black";
  const colorClass = opening.color === "white" ? "badge-white" : "badge-black";

  const mainlineId = `${opening.id}-mainline`;
  const sidelinesHtml = opening.sidelines
    .map((line, i) => renderLineCard(line, `${opening.id}-sideline-${i}`, "sideline"))
    .join("");

  detailView.innerHTML = `
    <div class="detail-layout">
      <aside class="board-panel">
        <div id="chessboard" class="board-container"></div>
        <div class="board-controls">
          <p id="boardMoveLabel" class="board-move-label">Starting position</p>
          <div class="board-buttons">
            <button type="button" id="boardStartBtn" class="board-btn">Start</button>
            <button type="button" id="boardPrevBtn" class="board-btn" disabled>Prev</button>
            <button type="button" id="boardNextBtn" class="board-btn">Next</button>
            <button type="button" id="boardPlayBtn" class="board-btn board-btn-play">Play</button>
          </div>
          <p id="boardMoveCounter" class="board-counter">0 / ${opening.mainline.moves.length}</p>
        </div>
      </aside>

      <div class="detail-content">
        <nav class="detail-nav">
          <a href="#" class="back-link" id="backToMenu">&larr; Back to menu</a>
        </nav>

        <header class="detail-header">
          <h2>${opening.name}</h2>
          <span class="color-badge ${colorClass}">${colorLabel}</span>
        </header>

        <section class="detail-section">
          <h3>Overview</h3>
          <p>${opening.overview}</p>
        </section>

        <section class="detail-section">
          <h3>Mainline</h3>
          ${renderLineCard(opening.mainline, mainlineId, "mainline")}
        </section>

        <section class="detail-section">
          <h3>Sidelines</h3>
          <div class="lines-list">${sidelinesHtml}</div>
        </section>

        <section class="detail-section strategy-section">
          <h3>Strategy</h3>
          <div class="strategy-grid">
            <div class="strategy-block">
              <h4>Goals</h4>
              <ul>${renderStrategyList(opening.goals)}</ul>
            </div>
            <div class="strategy-block">
              <h4>Advantages</h4>
              <ul>${renderStrategyList(opening.advantages)}</ul>
            </div>
            <div class="strategy-block">
              <h4>Disadvantages / Risks</h4>
              <ul>${renderStrategyList(opening.disadvantages)}</ul>
            </div>
            <div class="strategy-block">
              <h4>Long-term Plans</h4>
              <ul>${renderStrategyList(opening.longTermPlans)}</ul>
            </div>
          </div>
        </section>

        ${renderLichessSection(opening)}
      </div>
    </div>
  `;

  document.getElementById("backToMenu")?.addEventListener("click", (e) => {
    e.preventDefault();
    navigateTo("");
  });

  const lineMap = {
    [mainlineId]: opening.mainline.moves,
  };
  opening.sidelines.forEach((line, i) => {
    lineMap[`${opening.id}-sideline-${i}`] = line.moves;
  });

  document.querySelectorAll(".show-board-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const lineId = btn.dataset.lineId;
      loadLine(lineId, lineMap[lineId]);
    });
  });

  initBoard(opening);
  loadLine(mainlineId, opening.mainline.moves);
}

function renderOpeningCard(opening) {
  const card = document.createElement("a");
  card.href = `#${opening.id}`;
  card.className = "opening-card";
  card.innerHTML = `
    <h3 class="card-name">${opening.name}</h3>
    <p class="card-moves">${opening.firstMoves}</p>
    <p class="card-tagline">${opening.tagline}</p>
  `;
  card.addEventListener("click", (e) => {
    e.preventDefault();
    navigateTo(opening.id);
  });
  return card;
}

function renderMenu() {
  whiteOpeningsEl.innerHTML = "";
  blackOpeningsEl.innerHTML = "";

  openingsData.forEach((opening) => {
    const card = renderOpeningCard(opening);
    if (opening.color === "white") {
      whiteOpeningsEl.appendChild(card);
    } else {
      blackOpeningsEl.appendChild(card);
    }
  });
}

function hideAllViews() {
  menuView.classList.add("hidden");
  detailView.classList.add("hidden");
  trialView.classList.add("hidden");
  quizView.classList.add("hidden");
}

function updateTabs(hashId) {
  const isTrial = hashId === "trial-board";
  const isQuiz = hashId === "quiz";
  tabOpenings?.classList.toggle("active", !isTrial && !isQuiz && !hashId);
  tabTrialBoard?.classList.toggle("active", isTrial);
  tabQuiz?.classList.toggle("active", isQuiz);
  if (hashId && hashId !== "trial-board" && hashId !== "quiz") {
    tabOpenings?.classList.add("active");
  }
}

function cleanupBoards() {
  stopPlay();
  destroyTrialBoard();
  destroyQuizMode();
  if (board) {
    board.destroy();
    board = null;
  }
}

function showMenu() {
  cleanupBoards();
  hideAllViews();
  menuView.classList.remove("hidden");
  detailView.innerHTML = "";
  updateTabs(null);
}
function showDetail(openingId) {
  const opening = openingsData.find((o) => o.id === openingId);
  if (!opening) {
    showMenu();
    return;
  }

  cleanupBoards();
  hideAllViews();
  detailView.classList.remove("hidden");
  updateTabs(openingId);
  renderOpeningDetail(opening);
}

function showTrialBoard() {
  cleanupBoards();
  hideAllViews();
  trialView.classList.remove("hidden");
  updateTabs("trial-board");
  renderTrialBoard(trialView, openingsData);
}

function showQuizMode() {
  cleanupBoards();
  hideAllViews();
  quizView.classList.remove("hidden");
  updateTabs("quiz");
  renderQuizMode(quizView, openingsData);
}

function getHashId() {
  const hash = window.location.hash.slice(1);
  return hash || null;
}

function navigateTo(routeId) {
  if (routeId) {
    if (window.location.hash.slice(1) === routeId) {
      handleRoute();
    } else {
      window.location.hash = routeId;
    }
  } else {
    history.pushState(null, "", window.location.pathname + window.location.search);
    showMenu();
  }
}

function handleRoute() {
  const id = getHashId();
  if (id === "trial-board") {
    showTrialBoard();
  } else if (id === "quiz") {
    showQuizMode();
  } else if (id) {
    showDetail(id);
  } else {
    showMenu();
  }
}
async function init() {
  try {
    const response = await fetch("openings.json");
    if (!response.ok) throw new Error("Failed to load openings.json");
    const data = await response.json();
    openingsData = data.openings;
    renderMenu();
    handleRoute();
  } catch (err) {
    menuView.innerHTML = `
      <p class="error-msg">
        Could not load openings. If you opened this file directly, run a local server:
        <code>python -m http.server 8080</code> from the chess_openings folder.
      </p>
    `;
    console.error(err);
  }
}

window.addEventListener("hashchange", handleRoute);
window.addEventListener("navigate-menu", () => navigateTo(""));

tabOpenings?.addEventListener("click", (e) => {
  e.preventDefault();
  navigateTo("");
});

tabTrialBoard?.addEventListener("click", (e) => {
  e.preventDefault();
  navigateTo("trial-board");
});

tabQuiz?.addEventListener("click", (e) => {
  e.preventDefault();
  navigateTo("quiz");
});

init();