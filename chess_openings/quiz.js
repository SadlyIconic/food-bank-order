function shuffle(arr) {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function pickRandom(arr, count, exclude = new Set()) {
  const pool = arr.filter((item) => !exclude.has(item));
  return shuffle(pool).slice(0, count);
}

function buildFirstMovesQuestion(opening, allOpenings) {
  const correct = opening.firstMoves;
  const wrong = pickRandom(
    allOpenings.filter((o) => o.id !== opening.id).map((o) => o.firstMoves),
    3
  );
  const options = shuffle([correct, ...wrong]);
  return {
    type: "firstMoves",
    prompt: `What are the characteristic starting moves of the ${opening.name}?`,
    options,
    answer: correct,
    explanation: `${opening.name} begins with ${correct}.`,
  };
}

function buildGoalQuestion(opening, allOpenings) {
  const correct = opening.goals[Math.floor(Math.random() * opening.goals.length)];
  const otherGoals = allOpenings
    .filter((o) => o.id !== opening.id)
    .flatMap((o) => o.goals);
  const wrong = pickRandom(otherGoals, 3, new Set([correct]));
  const options = shuffle([correct, ...wrong.slice(0, 3)]);
  return {
    type: "goal",
    prompt: `Which is a strategic goal in the ${opening.name}?`,
    options,
    answer: correct,
    explanation: `"${correct}" is a core plan for ${opening.name}.`,
  };
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

function buildNextMoveQuestion(opening, allOpenings) {
  const moves = opening.mainline.moves;
  if (moves.length < 2) return null;

  const stepIndex = Math.floor(Math.random() * (moves.length - 1));
  const correct = moves[stepIndex];
  const prefix = moves.slice(0, stepIndex);
  const prefixText = prefix.length ? formatMoveList(prefix) + " " : "";

  const moveNum = Math.floor(stepIndex / 2) + 1;
  const isWhite = stepIndex % 2 === 0;
  const moveLabel = isWhite ? `${moveNum}.` : `${moveNum}...`;

  const otherMoves = allOpenings
    .flatMap((o) => o.mainline.moves)
    .filter((m, i, arr) => m !== correct && arr.indexOf(m) === i);
  const wrong = pickRandom(otherMoves, 3, new Set([correct]));
  const options = shuffle([correct, ...wrong.slice(0, 3)]);

  return {
    type: "nextMove",
    prompt: `In the ${opening.mainline.name}, what move comes next after ${prefixText}? (${moveLabel}?)`,
    options,
    answer: correct,
    explanation: `The mainline continues with ${moveLabel}${correct}.`,
  };
}

function buildOpeningNameQuestion(opening, allOpenings) {
  const correct = opening.name;
  const wrong = pickRandom(
    allOpenings.filter((o) => o.id !== opening.id).map((o) => o.name),
    3
  );
  const options = shuffle([correct, ...wrong]);
  return {
    type: "openingName",
    prompt: `Which opening starts with: ${opening.firstMoves}?`,
    options,
    answer: correct,
    explanation: `${opening.firstMoves} is the ${opening.name}.`,
  };
}

function buildQuestionSet(opening, allOpenings) {
  const questions = [
    buildFirstMovesQuestion(opening, allOpenings),
    buildGoalQuestion(opening, allOpenings),
    buildGoalQuestion(opening, allOpenings),
    buildOpeningNameQuestion(opening, allOpenings),
  ];

  const nextMove = buildNextMoveQuestion(opening, allOpenings);
  if (nextMove) questions.push(nextMove);

  const extraGoal = buildGoalQuestion(opening, allOpenings);
  questions.push(extraGoal);

  return shuffle(questions).slice(0, 6);
}

let containerEl = null;
let quizState = null;

function renderPicker(openings) {
  const cards = openings
    .map(
      (o) => `
      <button type="button" class="opening-card quiz-picker-card" data-opening-id="${o.id}">
        <h3 class="card-name">${o.name}</h3>
        <p class="card-moves">${o.firstMoves}</p>
        <p class="card-tagline">${o.tagline}</p>
      </button>
    `
    )
    .join("");

  containerEl.innerHTML = `
    <nav class="detail-nav">
      <a href="#" class="back-link" id="quizBackToMenu">&larr; Back to menu</a>
    </nav>
    <header class="detail-header">
      <h2>Quiz Mode</h2>
    </header>
    <p class="trial-intro">Choose an opening to be quizzed on starting moves and strategic goals.</p>
    <div class="opening-cards quiz-picker-grid">${cards}</div>
  `;

  document.getElementById("quizBackToMenu")?.addEventListener("click", (e) => {
    e.preventDefault();
    window.dispatchEvent(new CustomEvent("navigate-menu"));
  });

  containerEl.querySelectorAll(".quiz-picker-card").forEach((btn) => {
    btn.addEventListener("click", () => {
      const opening = openings.find((o) => o.id === btn.dataset.openingId);
      if (opening) startQuiz(opening, openings);
    });
  });
}

function renderQuestion() {
  const { opening, questions, index, score, answered } = quizState;
  const total = questions.length;

  if (index >= total) {
    renderResults();
    return;
  }

  const q = questions[index];

  containerEl.innerHTML = `
    <nav class="detail-nav">
      <a href="#" class="back-link" id="quizChangeOpening">&larr; Choose another opening</a>
    </nav>
    <header class="detail-header">
      <h2>${opening.name} Quiz</h2>
      <span class="color-badge badge-${opening.color}">${opening.color}</span>
    </header>
    <div class="quiz-progress">
      <span>Question ${index + 1} of ${total}</span>
      <span>Score: ${score}/${index + (answered ? 1 : 0)}</span>
    </div>
    <div class="quiz-question-card">
      <p class="quiz-prompt">${q.prompt}</p>
      <div class="quiz-options" id="quizOptions">
        ${q.options
          .map(
            (opt) =>
              `<button type="button" class="quiz-option-btn" data-answer="${encodeURIComponent(opt)}">${opt}</button>`
          )
          .join("")}
      </div>
      <div id="quizFeedback" class="quiz-feedback hidden"></div>
      <button type="button" id="quizNextBtn" class="board-btn quiz-next-btn hidden">Next</button>
    </div>
  `;

  document.getElementById("quizChangeOpening")?.addEventListener("click", (e) => {
    e.preventDefault();
    renderPicker(quizState.allOpenings);
  });

  if (!answered) {
    containerEl.querySelectorAll(".quiz-option-btn").forEach((btn) => {
      btn.addEventListener("click", () => handleAnswer(decodeURIComponent(btn.dataset.answer)));
    });
  }
}

function handleAnswer(selected) {
  if (quizState.answered) return;

  const q = quizState.questions[quizState.index];
  const correct = selected === q.answer;
  if (correct) quizState.score++;

  quizState.answered = true;

  const feedback = document.getElementById("quizFeedback");
  const optionsEl = document.getElementById("quizOptions");
  const nextBtn = document.getElementById("quizNextBtn");

  optionsEl.querySelectorAll(".quiz-option-btn").forEach((btn) => {
    const val = decodeURIComponent(btn.dataset.answer);
    btn.disabled = true;
    if (val === q.answer) btn.classList.add("quiz-correct");
    else if (val === selected) btn.classList.add("quiz-wrong");
  });

  feedback.classList.remove("hidden");
  feedback.className = `quiz-feedback ${correct ? "quiz-feedback-correct" : "quiz-feedback-wrong"}`;
  feedback.innerHTML = correct
    ? `<strong>Correct!</strong> ${q.explanation}`
    : `<strong>Not quite.</strong> The answer is "${q.answer}". ${q.explanation}`;

  nextBtn.classList.remove("hidden");
  nextBtn.addEventListener("click", () => {
    quizState.index++;
    quizState.answered = false;
    renderQuestion();
  });
}

function renderResults() {
  const { opening, questions, score } = quizState;
  const pct = Math.round((score / questions.length) * 100);

  containerEl.innerHTML = `
    <nav class="detail-nav">
      <a href="#" class="back-link" id="quizChangeOpening">&larr; Choose another opening</a>
    </nav>
    <header class="detail-header">
      <h2>Quiz Complete</h2>
    </header>
    <div class="quiz-results">
      <p class="quiz-score">${score} / ${questions.length} correct (${pct}%)</p>
      <p class="quiz-results-msg">${pct >= 80 ? "Excellent work!" : pct >= 50 ? "Good effort — review the opening and try again." : "Keep studying — open the opening page to review."}</p>
      <div class="quiz-results-actions">
        <button type="button" id="quizRetryBtn" class="board-btn">Retry ${opening.name}</button>
        <a href="#${opening.id}" class="board-btn quiz-link-btn">Review opening</a>
        <button type="button" id="quizPickBtn" class="board-btn">Pick another opening</button>
      </div>
    </div>
  `;

  document.getElementById("quizChangeOpening")?.addEventListener("click", (e) => {
    e.preventDefault();
    renderPicker(quizState.allOpenings);
  });
  document.getElementById("quizRetryBtn")?.addEventListener("click", () => {
    startQuiz(opening, quizState.allOpenings);
  });
  document.getElementById("quizPickBtn")?.addEventListener("click", () => {
    renderPicker(quizState.allOpenings);
  });
  containerEl.querySelector(".quiz-link-btn")?.addEventListener("click", (e) => {
    e.preventDefault();
    window.location.hash = opening.id;
  });
}

function startQuiz(opening, allOpenings) {
  quizState = {
    opening,
    allOpenings,
    questions: buildQuestionSet(opening, allOpenings),
    index: 0,
    score: 0,
    answered: false,
  };
  renderQuestion();
}

export function renderQuizMode(container, openings) {
  containerEl = container;
  renderPicker(openings);
}

export function destroyQuizMode() {
  quizState = null;
  if (containerEl) {
    containerEl.innerHTML = "";
    containerEl = null;
  }
}
