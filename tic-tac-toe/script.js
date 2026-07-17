const WINNING_LINES = [
  [0, 1, 2],
  [3, 4, 5],
  [6, 7, 8],
  [0, 3, 6],
  [1, 4, 7],
  [2, 5, 8],
  [0, 4, 8],
  [2, 4, 6],
];

let board = Array(9).fill(null);
let currentPlayer = "X";
let gameOver = false;
const scores = { x: 0, o: 0, ties: 0 };

let bestOf = 1;
let winsNeeded = 1;
let seriesActive = false;
let nextRoundTimer = null;
let returnMenuTimer = null;

const menuScreen = document.getElementById("menuScreen");
const gameScreen = document.getElementById("gameScreen");
const seriesInfoEl = document.getElementById("seriesInfo");
const statusEl = document.getElementById("status");
const boardEl = document.getElementById("board");
const resetBtn = document.getElementById("resetBtn");
const scoreXEl = document.getElementById("scoreX");
const scoreOEl = document.getElementById("scoreO");
const scoreTiesEl = document.getElementById("scoreTies");
const cells = document.querySelectorAll(".cell");
const menuBtns = document.querySelectorAll(".menu-btn");

function updateScoreboard() {
  scoreXEl.textContent = scores.x;
  scoreOEl.textContent = scores.o;
  scoreTiesEl.textContent = scores.ties;
}

function checkWinner() {
  for (const [a, b, c] of WINNING_LINES) {
    if (board[a] && board[a] === board[b] && board[a] === board[c]) {
      return { winner: board[a], line: [a, b, c] };
    }
  }
  if (board.every((cell) => cell !== null)) {
    return { winner: null, line: [] };
  }
  return null;
}

function updateStatus(message) {
  statusEl.textContent = message;
}

function clearTimers() {
  clearTimeout(nextRoundTimer);
  clearTimeout(returnMenuTimer);
}

function showMenu() {
  clearTimers();
  seriesActive = false;
  menuScreen.classList.remove("hidden");
  gameScreen.classList.add("hidden");
}

function startSeries(selectedBestOf) {
  clearTimers();
  bestOf = selectedBestOf;
  winsNeeded = Math.ceil(bestOf / 2);
  scores.x = 0;
  scores.o = 0;
  scores.ties = 0;
  updateScoreboard();

  seriesInfoEl.textContent = `Best of ${bestOf} — first to ${winsNeeded}`;
  menuScreen.classList.add("hidden");
  gameScreen.classList.remove("hidden");
  seriesActive = true;
  resetBoard();
}

function endSeries(winner) {
  seriesActive = false;
  resetBtn.disabled = true;
  updateStatus(`Player ${winner} wins the series! Returning to menu...`);
  returnMenuTimer = setTimeout(showMenu, 3000);
}

function scheduleNextRound() {
  clearTimeout(nextRoundTimer);
  resetBtn.disabled = false;
  nextRoundTimer = setTimeout(() => {
    if (seriesActive) startNextRound();
  }, 2000);
}

function startNextRound() {
  if (!seriesActive) return;
  clearTimeout(nextRoundTimer);
  resetBoard();
}

function handleGameEnd(result) {
  if (result.winner) {
    scores[result.winner.toLowerCase()]++;
    updateScoreboard();
    result.line.forEach((i) => cells[i].classList.add("winner"));

    if (scores[result.winner.toLowerCase()] >= winsNeeded) {
      updateStatus(`Player ${result.winner} wins!`);
      endSeries(result.winner);
      return;
    }

    updateStatus(
      `Player ${result.winner} wins! Series: X ${scores.x} – O ${scores.o}`
    );
    scheduleNextRound();
    return;
  }

  scores.ties++;
  updateScoreboard();
  updateStatus(`It's a draw! Series: X ${scores.x} – O ${scores.o}`);
  scheduleNextRound();
}

function handleCellClick(e) {
  const cell = e.target;
  if (!cell.classList.contains("cell")) return;

  const index = Number(cell.dataset.index);
  if (gameOver || board[index] !== null) return;

  board[index] = currentPlayer;
  cell.textContent = currentPlayer;
  cell.classList.add(currentPlayer.toLowerCase());
  cell.disabled = true;

  const result = checkWinner();

  if (result) {
    gameOver = true;
    cells.forEach((c) => (c.disabled = true));
    handleGameEnd(result);
    return;
  }

  currentPlayer = currentPlayer === "X" ? "O" : "X";
  updateStatus(`Player ${currentPlayer}'s turn`);
}

function resetBoard() {
  board = Array(9).fill(null);
  currentPlayer = "X";
  gameOver = false;
  resetBtn.disabled = true;

  cells.forEach((cell) => {
    cell.textContent = "";
    cell.disabled = false;
    cell.classList.remove("x", "o", "winner");
  });

  updateStatus("Player X's turn");
}

menuBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    startSeries(Number(btn.dataset.bestOf));
  });
});

boardEl.addEventListener("click", handleCellClick);
resetBtn.addEventListener("click", startNextRound);
