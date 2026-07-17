function normalizeSan(san) {
  return san.replace(/[+#?!]/g, "").trim();
}

export function buildLineIndex(openings) {
  const lines = [];
  for (const opening of openings) {
    lines.push({
      openingId: opening.id,
      openingName: opening.name,
      openingColor: opening.color,
      lineName: opening.mainline.name,
      type: "mainline",
      moves: opening.mainline.moves,
      notes: opening.mainline.notes,
    });
    opening.sidelines.forEach((sideline) => {
      lines.push({
        openingId: opening.id,
        openingName: opening.name,
        openingColor: opening.color,
        lineName: sideline.name,
        type: "sideline",
        moves: sideline.moves,
        notes: sideline.notes,
      });
    });
  }
  return lines;
}

export function findCompletedLines(playedMoves, lineIndex) {
  if (playedMoves.length === 0) return [];

  return lineIndex
    .filter((line) => {
      if (playedMoves.length < line.moves.length) return false;
      return line.moves.every(
        (move, i) => normalizeSan(playedMoves[i]) === normalizeSan(move)
      );
    })
    .sort((a, b) => {
      if (b.moves.length !== a.moves.length) return b.moves.length - a.moves.length;
      if (a.type !== b.type) return a.type === "mainline" ? -1 : 1;
      return a.openingName.localeCompare(b.openingName);
    });
}

export function findInBookMatches(playedMoves, lineIndex) {
  if (playedMoves.length === 0) return [];

  return lineIndex
    .filter((line) => {
      if (playedMoves.length > line.moves.length) return false;
      return playedMoves.every(
        (move, i) => normalizeSan(move) === normalizeSan(line.moves[i])
      );
    })
    .sort((a, b) => {
      if (b.moves.length !== a.moves.length) return b.moves.length - a.moves.length;
      if (a.type !== b.type) return a.type === "mainline" ? -1 : 1;
      return a.openingName.localeCompare(b.openingName);
    });
}

export function findBestPartialMatch(playedMoves, lineIndex) {
  if (playedMoves.length === 0) return null;

  let best = null;
  for (const line of lineIndex) {
    let matched = 0;
    for (let i = 0; i < playedMoves.length && i < line.moves.length; i++) {
      if (normalizeSan(playedMoves[i]) !== normalizeSan(line.moves[i])) break;
      matched++;
    }
    if (matched === 0) continue;

    const candidate = {
      ...line,
      matchedMoves: matched,
      inBook: matched === playedMoves.length,
      deviated: matched < playedMoves.length,
    };

    if (
      !best ||
      matched > best.matchedMoves ||
      (matched === best.matchedMoves &&
        line.type === "mainline" &&
        best.type !== "mainline")
    ) {
      best = candidate;
    }
  }
  return best;
}

export function formatMatchedMoves(moves, count) {
  return formatMoveList(moves.slice(0, count));
}

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
