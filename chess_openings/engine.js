export class StockfishEngine {
  constructor() {
    this.worker = new Worker(new URL("./stockfish-worker.js", import.meta.url));
    this.ready = false;
    this.readyPromise = new Promise((resolve) => {
      this._resolveReady = resolve;
    });
    this.analysisResolve = null;
    this.latestInfo = null;

    this.worker.onmessage = (event) => this.handleMessage(event.data);
    this.worker.postMessage("uci");
  }

  handleMessage(line) {
    if (typeof line !== "string") return;

    if (line === "uciok") {
      this.ready = true;
      this._resolveReady();
      return;
    }

    if (line.startsWith("info ")) {
      const score = parseScore(line);
      const pvMove = parsePvMove(line);
      if (score !== null) {
        this.latestInfo = { score, pvMove, raw: line };
      }
      return;
    }

    if (line.startsWith("bestmove ")) {
      const parts = line.split(" ");
      const bestmove = parts[1];
      if (this.analysisResolve) {
        const resolve = this.analysisResolve;
        this.analysisResolve = null;
        resolve({
          bestmove,
          score: this.latestInfo?.score ?? null,
          pvMove: this.latestInfo?.pvMove ?? bestmove,
        });
      }
    }
  }

  async waitUntilReady() {
    await this.readyPromise;
  }

  analyze(fen, depth = 14) {
    return new Promise((resolve) => {
      this.latestInfo = null;
      this.analysisResolve = resolve;
      this.worker.postMessage("stop");
      this.worker.postMessage(`position fen ${fen}`);
      this.worker.postMessage(`go depth ${depth}`);
    });
  }

  destroy() {
    this.worker.postMessage("quit");
    this.worker.terminate();
  }
}

function parseScore(line) {
  const mateMatch = line.match(/\sscore mate (-?\d+)/);
  if (mateMatch) {
    const mateIn = Number(mateMatch[1]);
    return { type: "mate", value: mateIn };
  }

  const cpMatch = line.match(/\sscore cp (-?\d+)/);
  if (cpMatch) {
    return { type: "cp", value: Number(cpMatch[1]) };
  }

  return null;
}

function parsePvMove(line) {
  const pvMatch = line.match(/\spv ([a-h][1-8][a-h][1-8][qrbn]?)/);
  return pvMatch ? pvMatch[1] : null;
}

export function scoreToCentipawns(score, sideToMove) {
  if (!score) return 0;
  if (score.type === "mate") {
    const sign = score.value > 0 ? 1 : -1;
    return sign * (10000 - Math.abs(score.value) * 100);
  }
  const cp = score.value;
  return sideToMove === "w" ? cp : -cp;
}

export function formatEval(score, sideToMove) {
  if (!score) return "—";
  if (score.type === "mate") {
    const mateFor = score.value > 0 ? "White" : "Black";
    return `M${Math.abs(score.value)} (${mateFor})`;
  }
  const cp = scoreToCentipawns(score, sideToMove);
  const pawns = (cp / 100).toFixed(2);
  if (cp > 0) return `+${pawns}`;
  if (cp < 0) return pawns;
  return "0.00";
}

export function evalToBarPercent(score, sideToMove) {
  const cp = scoreToCentipawns(score, sideToMove);
  const clamped = Math.max(-800, Math.min(800, cp));
  return 50 + (clamped / 800) * 50;
}

export function uciToSan(fen, uciMove, Chess) {
  if (!uciMove || uciMove === "(none)") return null;
  const game = new Chess(fen);
  const from = uciMove.slice(0, 2);
  const to = uciMove.slice(2, 4);
  const promotion = uciMove.length > 4 ? uciMove[4] : undefined;
  const result = game.move({ from, to, promotion });
  return result ? result.san : uciMove;
}
