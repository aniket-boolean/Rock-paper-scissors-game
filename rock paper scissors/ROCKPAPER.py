#HOST AND PORT ARE SET TO LOCAL HOST ADDRESS while 
#BASE_DIR, HTML_FILE, and SCORE_FILE locate index.html and score.json next to app.py.
import json
import os
import random
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 5050
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCORE_FILE = os.path.join(BASE_DIR, "score.json")
#GAME RULES AND DEFAULT SCORE 
WEAPONS = {
    "rock": {"label": "Rock", "icon": "#icon-rock", "beats": "scissors"},
    "paper": {"label": "Paper", "icon": "#icon-paper", "beats": "rock"},
    "scissors": {"label": "Scissors", "icon": "#icon-scissors", "beats": "paper"},
}
#SCORE READ, WRITE AND WINNER ROUND LOGIC 
#read_score() loads score.json safely, write_score() saves updated scores, and evaluate_round() 
# decides "win", "lose", or "draw" plus the status text.
DEFAULT_SCORE = {"player": 0, "draws": 0, "cpu": 0}


def read_score():
    if not os.path.exists(SCORE_FILE):
        write_score(DEFAULT_SCORE.copy())
        return DEFAULT_SCORE.copy()
    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Invalid score format")
        return {
            "player": max(0, int(data.get("player", 0))),
            "draws": max(0, int(data.get("draws", 0))),
            "cpu": max(0, int(data.get("cpu", 0))),
        }
    except (OSError, ValueError, TypeError):
        fresh = DEFAULT_SCORE.copy()
        write_score(fresh)
        return fresh


def write_score(score_data):
    with open(SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(score_data, f, indent=2)


def evaluate_round(player_choice, cpu_choice):
    p_label = WEAPONS[player_choice]["label"].upper()
    c_label = WEAPONS[cpu_choice]["label"].upper()
    if player_choice == cpu_choice:
        return "draw", f"STALEMATE // BOTH DEPLOYED {p_label}"
    if WEAPONS[player_choice]["beats"] == cpu_choice:
        return "win", f"VICTORY // {p_label} OVERRIDES {c_label}"
    return "lose", f"BREACH // A.I. {c_label} DEFEATS {p_label}"

#FRONTEND CODE
#Head and Bone/Sage CSS Styles
#Page metadata, title (Rock paper scissors), and CSS 
# rules for bone/sage colors, card frame, scoreboard, orbs, status banner, buttons
# , and pop animation (with .subtitle hidden).
#Hidden SVG Vector Symbols
#Main Card UI Markup
#Frontend JavaScript Logic(635 TO 754)
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Rock paper scissors</title>
  <link rel="icon" type="image/png" href="/ITSROCK.png" />
  <style>
    :root {
      --bg-bone: #f6f4ec;
      --bg-panel: #fbfaf5;
      --bg-soft: #eef2e8;
      --sage-deep: #3d6b4c;
      --sage-mid: #6b9b78;
      --sage-light: #a8ccb2;
      --sage-glow: rgba(107, 155, 120, 0.25);
      --moss-win: #2f7d4b;
      --moss-win-bg: rgba(74, 156, 102, 0.14);
      --clay-lose: #b56558;
      --clay-lose-bg: rgba(181, 101, 88, 0.14);
      --sand-draw: #b88b3b;
      --sand-draw-bg: rgba(184, 139, 59, 0.14);
      --ink-main: #253329;
      --ink-muted: #5d7063;
      --border-soft: #d7e2d5;
    }

- {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: var(--bg-bone);
      background-image:
        radial-gradient(circle at 20% 10%, rgba(168, 204, 178, 0.28) 0%, transparent 50%),
        radial-gradient(circle at 85% 90%, rgba(188, 214, 194, 0.24) 0%, transparent 50%);
      color: var(--ink-main);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 1.5rem;
      overflow-x: hidden;
    }

    .hud-frame {
      position: relative;
      width: 100%;
      max-width: 540px;
      background: var(--bg-panel);
      border: 1px solid var(--border-soft);
      border-radius: 22px;
      padding: 2.2rem 1.8rem;
      text-align: center;
      box-shadow:
        0 14px 34px -12px rgba(45, 74, 54, 0.14),
        0 0 0 4px rgba(168, 204, 178, 0.16);
    }

    .system-tag {
      display: inline-block;
      font-size: 0.68rem;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--sage-deep);
      background: var(--bg-soft);
      border: 1px solid var(--sage-light);
      padding: 0.28rem 0.9rem;
      border-radius: 999px;
      margin-bottom: 0.75rem;
      font-weight: 600;
    }

    h1 {
      font-size: 1.85rem;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--ink-main);
      margin-bottom: 1.25rem;
    }

    .subtitle {
      display: none;
    }

    .preface-box {
      text-align: left;
      background: var(--bg-bone);
      border: 1px solid var(--border-soft);
      border-radius: 16px;
      padding: 1.05rem 1.2rem;
      margin-bottom: 1.65rem;
      box-shadow: inset 0 1px 4px rgba(37, 51, 41, 0.03);
    }

    .rules-heading {
      font-size: 0.78rem;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--sage-deep);
      margin-bottom: 0.55rem;
    }

    .rules-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      font-size: 0.88rem;
      line-height: 1.5;
      color: var(--ink-main);
      margin-bottom: 0.9rem;
      padding-bottom: 0.8rem;
      border-bottom: 1px solid var(--border-soft);
    }

    .about-note {
      font-size: 0.88rem;
      line-height: 1.55;
      color: var(--ink-muted);
    }

    .about-label {
      font-weight: 700;
      color: var(--sage-deep);
      letter-spacing: 0.03em;
    }

    .scoreboard {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.85rem;
      margin-bottom: 1.85rem;
    }

    .score-card {
      background: var(--bg-bone);
      border: 1px solid var(--border-soft);
      border-radius: 14px;
      padding: 0.85rem 0.5rem;
      box-shadow: inset 0 1px 4px rgba(37, 51, 41, 0.03);
    }

    .score-card.you {
      border-color: var(--sage-light);
      background: #f2f7f0;
    }

    .score-card.draws {
      border-color: #dfd3b5;
      background: #f8f6ee;
    }

    .score-card.cpu {
      border-color: #e3c8c2;
      background: #f9f2f0;
    }

    .score-label {
      font-size: 0.7rem;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--ink-muted);
      font-weight: 700;
    }

    .score-value {
      font-size: 1.85rem;
      font-weight: 800;
      margin-top: 0.2rem;
      font-variant-numeric: tabular-nums;
    }

    .score-card.you .score-value {
      color: var(--moss-win);
    }

    .score-card.draws .score-value {
      color: var(--sand-draw);
    }

    .score-card.cpu .score-value {
      color: var(--clay-lose);
    }

    .arena {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      padding: 1.5rem 1.25rem;
      margin-bottom: 1.6rem;
      background: linear-gradient(180deg, #f3f7ef 0%, var(--bg-bone) 100%);
      border: 1px solid var(--border-soft);
      border-radius: 18px;
    }

    .combatant {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.65rem;
    }

    .holo-orb {
      width: 108px;
      height: 108px;
      border-radius: 50%;
      background: radial-gradient(circle at 35% 30%, #ffffff, #e6efe4 75%);
      border: 2px solid var(--sage-light);
      display: flex;
      justify-content: center;
      align-items: center;
      box-shadow:
        0 8px 20px -6px var(--sage-glow),
        inset 0 0 14px rgba(168, 204, 178, 0.25);
      transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1), border-color 0.25s ease, box-shadow 0.25s ease;
    }

    .holo-orb svg {
      width: 64px;
      height: 64px;
      filter: drop-shadow(0 4px 8px rgba(61, 107, 76, 0.16));
      transition: transform 0.25s ease;
    }

    .holo-orb.win {
      border-color: var(--moss-win);
      transform: scale(1.06);
      box-shadow:
        0 10px 24px -6px rgba(47, 125, 75, 0.32),
        inset 0 0 16px var(--moss-win-bg);
    }

    .holo-orb.lose {
      border-color: var(--clay-lose);
      opacity: 0.82;
      transform: scale(0.96);
      box-shadow:
        0 8px 18px -6px rgba(181, 101, 88, 0.25),
        inset 0 0 14px var(--clay-lose-bg);
    }

    .holo-orb.draw {
      border-color: var(--sand-draw);
      box-shadow:
        0 8px 20px -6px rgba(184, 139, 59, 0.28),
        inset 0 0 14px var(--sand-draw-bg);
    }

    .combatant-name {
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--ink-muted);
    }

    .vs-core {
      font-size: 0.92rem;
      font-weight: 800;
      letter-spacing: 0.14em;
      color: var(--sage-deep);
      padding: 0.42rem 0.65rem;
      border: 1px solid var(--sage-light);
      border-radius: 10px;
      background: var(--bg-soft);
    }

    .status-hud {
      padding: 0.85rem 1rem;
      margin-bottom: 1.75rem;
      border-radius: 12px;
      font-size: 0.88rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: var(--sage-deep);
      background: var(--bg-soft);
      border: 1px solid var(--sage-light);
      transition: all 0.25s ease;
    }

    .status-hud.win {
      color: var(--moss-win);
      background: var(--moss-win-bg);
      border-color: var(--sage-mid);
    }

    .status-hud.lose {
      color: var(--clay-lose);
      background: var(--clay-lose-bg);
      border-color: #dfb4ad;
    }

    .status-hud.draw {
      color: var(--sand-draw);
      background: var(--sand-draw-bg);
      border-color: #dcc596;
    }

    .weapon-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.9rem;
      margin-bottom: 1.65rem;
    }

    .weapon-btn {
      background: linear-gradient(180deg, #ffffff 0%, #eff5ec 100%);
      border: 1px solid var(--border-soft);
      border-radius: 16px;
      padding: 1.15rem 0.5rem;
      color: var(--ink-main);
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.65rem;
      box-shadow: 0 6px 16px -8px rgba(37, 51, 41, 0.14);
      transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
    }

    .weapon-btn svg {
      width: 52px;
      height: 52px;
      filter: drop-shadow(0 3px 6px rgba(61, 107, 76, 0.15));
      transition: transform 0.2s ease;
    }

    .weapon-btn:hover:not(:disabled) {
      transform: translateY(-3px);
      border-color: var(--sage-mid);
      background: linear-gradient(180deg, #ffffff 0%, #e4efe0 100%);
      box-shadow: 0 10px 22px -8px var(--sage-glow);
    }

    .weapon-btn:hover:not(:disabled) svg {
      transform: scale(1.07);
    }

    .weapon-btn:active:not(:disabled) {
      transform: translateY(0);
    }

    .weapon-btn:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }

    .weapon-label {
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--sage-deep);
    }

    .reset-btn {
      background: var(--bg-bone);
      border: 1px solid var(--border-soft);
      color: var(--ink-muted);
      padding: 0.6rem 1.4rem;
      border-radius: 10px;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .reset-btn:hover:not(:disabled) {
      background: var(--bg-soft);
      border-color: var(--sage-mid);
      color: var(--sage-deep);
    }

    .footer-end {
      margin-top: 1.55rem;
      padding-top: 1rem;
      border-top: 1px solid var(--border-soft);
      text-align: center;
      display: flex;
      flex-direction: column;
      gap: 0.55rem;
    }

    .end-about {
      font-size: 0.84rem;
      line-height: 1.5;
      color: var(--ink-muted);
    }

    .github-footer {
      font-size: 0.78rem;
      color: var(--ink-muted);
      letter-spacing: 0.03em;
    }

    .github-link {
      color: var(--sage-deep);
      font-weight: 700;
      text-decoration: none;
      border-bottom: 1px dashed var(--sage-mid);
    }

    .github-link:hover {
      color: var(--ink-main);
      border-bottom-style: solid;
    }

    @keyframes pulsePop {
      0% { transform: scale(0.86); opacity: 0.5; }
      65% { transform: scale(1.06); opacity: 1; }
      100% { transform: scale(1); opacity: 1; }
    }

    .pop-in {
      animation: pulsePop 0.3s ease-out forwards;
    }
  </style>
</head>

<body>
  <svg width="0" height="0" style="position:absolute;visibility:hidden;" aria-hidden="true">
    <defs>
      <linearGradient id="cyberMetal" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#f7faf5" />
        <stop offset="50%" stop-color="#9bc4a7" />
        <stop offset="100%" stop-color="#4d7c5c" />
      </linearGradient>

      <linearGradient id="cyberCore" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#88b897" />
        <stop offset="100%" stop-color="#3f6b4e" />
      </linearGradient>

      <symbol id="icon-idle" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="36" fill="none" stroke="url(#cyberMetal)" stroke-width="3" stroke-dasharray="14 8" />
        <circle cx="50" cy="50" r="22" fill="none" stroke="#8ab597" stroke-width="2.2" stroke-dasharray="6 6" />
        <circle cx="50" cy="50" r="7" fill="#4e7d5d" />
      </symbol>

      <symbol id="icon-rock" viewBox="0 0 100 100">
        <rect x="30" y="68" width="40" height="16" rx="5" fill="url(#cyberCore)" stroke="#3d6b4c" stroke-width="1.8" />
        <line x1="38" y1="76" x2="62" y2="76" stroke="#f6f4ec" stroke-width="2.2" stroke-linecap="round" />
        <rect x="22" y="34" width="56" height="36" rx="14" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.5" />
        <rect x="23" y="24" width="13" height="22" rx="6" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.8" />
        <rect x="36.5" y="21" width="13" height="24" rx="6" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.8" />
        <rect x="50" y="22" width="13" height="23" rx="6" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.8" />
        <rect x="63.5" y="26" width="12.5" height="20" rx="6" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.8" />
        <rect x="24" y="45" width="38" height="13" rx="6.5" fill="url(#cyberCore)" stroke="#f6f4ec" stroke-width="1.4" />
      </symbol>

      <symbol id="icon-paper" viewBox="0 0 100 100">
        <rect x="32" y="72" width="36" height="14" rx="5" fill="url(#cyberCore)" stroke="#3d6b4c" stroke-width="1.8" />
        <rect x="26" y="42" width="48" height="32" rx="12" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.5" />
        <rect x="26" y="16" width="10.5" height="34" rx="5.2" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.6" />
        <rect x="38.5" y="11" width="10.5" height="38" rx="5.2" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.6" />
        <rect x="51" y="13" width="10.5" height="36" rx="5.2" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.6" />
        <rect x="63.5" y="20" width="10.5" height="30" rx="5.2" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.6" />
        <rect x="13" y="44" width="22" height="10.5" rx="5.2" transform="rotate(-28 24 49)" fill="url(#cyberCore)" stroke="#f6f4ec" stroke-width="1.4" />
        <circle cx="50" cy="58" r="7" fill="url(#cyberCore)" stroke="#f6f4ec" stroke-width="1.4" />
      </symbol>

      <symbol id="icon-scissors" viewBox="0 0 100 100">
        <rect x="31" y="71" width="38" height="14" rx="5" fill="url(#cyberCore)" stroke="#3d6b4c" stroke-width="1.8" />
        <rect x="27" y="12" width="12" height="44" rx="6" transform="rotate(-14 33 34)" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.5" />
        <rect x="52" y="12" width="12" height="44" rx="6" transform="rotate(14 58 34)" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.5" />
        <rect x="24" y="42" width="52" height="31" rx="13" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.6" />
        <rect x="52" y="42" width="12" height="19" rx="6" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.6" />
        <rect x="64" y="45" width="11" height="17" rx="5.5" fill="url(#cyberMetal)" stroke="#3d6b4c" stroke-width="1.6" />
        <rect x="25" y="48" width="30" height="12" rx="6" fill="url(#cyberCore)" stroke="#f6f4ec" stroke-width="1.4" />
      </symbol>
    </defs>
  </svg>

  <main class="hud-frame">
    <span class="system-tag">WELCOME TO THE GAME</span>
    <h1>Rock paper scissors</h1>
    <p class="subtitle">Python Backend // score.json Sync</p>

    <section class="preface-box" aria-label="Game rules and about game">
      <div class="rules-heading">Game rules:</div>
      <ul class="rules-list">
        <li>1.Click on any 3 weapons(Rock,paper,scissors)</li>
        <li>2. rock can beat scissors</li>
        <li>3. paper can beat rock</li>
        <li>4. Scissors can beat paper</li>
        <li>5.If computer and the player obtain same weapon , then  its a tie</li>
      </ul>
      
    </section>

    <section class="scoreboard" aria-label="Scoreboard">
      <div class="score-card you">
        <div class="score-label">Player</div>
        <div class="score-value" id="player-score">00</div>
      </div>
      <div class="score-card draws">
        <div class="score-label">Stalemate</div>
        <div class="score-value" id="draw-score">00</div>
      </div>
      <div class="score-card cpu">
        <div class="score-label">A.I. Core</div>
        <div class="score-value" id="cpu-score">00</div>
      </div>
    </section>

    <section class="arena" aria-label="Match Arena">
      <div class="combatant">
        <div class="holo-orb" id="player-orb">
          <svg id="player-svg"><use href="#icon-idle"></use></svg>
        </div>
        <span class="combatant-name">You</span>
      </div>

      <div class="vs-core">VS</div>

      <div class="combatant">
        <div class="holo-orb" id="cpu-orb">
          <svg id="cpu-svg"><use href="#icon-idle"></use></svg>
        </div>
        <span class="combatant-name">A.I. Core</span>
      </div>
    </section>

    <div class="status-hud" id="status-hud">Connecting to Python Core...</div>

    <section class="weapon-grid" aria-label="Weapon Selectors">
      <button class="weapon-btn" type="button" data-choice="rock">
        <svg><use href="#icon-rock"></use></svg>
        <span class="weapon-label">Rock</span>
      </button>
      <button class="weapon-btn" type="button" data-choice="paper">
        <svg><use href="#icon-paper"></use></svg>
        <span class="weapon-label">Paper</span>
      </button>
      <button class="weapon-btn" type="button" data-choice="scissors">
        <svg><use href="#icon-scissors"></use></svg>
        <span class="weapon-label">Scissors</span>
      </button>
    </section>

    <button class="reset-btn" type="button" id="reset-btn">Reset</button>

    <!-- ABOUT AT LAST, RIGHT BEFORE GITHUB LINK -->
    <footer class="footer-end" id="about-and-github">
      <p class="end-about" id="about-section">
        <span class="about-label">About:</span> This game is a project ,Which i made to entertain the world , Enjoy the game
      </p>
      <div class="github-footer" id="github-section">
        GitHub Project:
        <a class="github-link" href="#YOUR_GITHUB_REPO_URL" target="_blank" rel="noopener noreferrer">
          Add GitHub Repository Link After Deployment
        </a>
      </div>
    </footer>
  </main>

  <script>
    document.addEventListener("DOMContentLoaded", () => {
      const WEAPON_ICONS = {
        rock: "#icon-rock",
        paper: "#icon-paper",
        scissors: "#icon-scissors"
      };

      const playerScoreEl = document.getElementById("player-score");
      const drawScoreEl = document.getElementById("draw-score");
      const cpuScoreEl = document.getElementById("cpu-score");
      const playerOrbEl = document.getElementById("player-orb");
      const cpuOrbEl = document.getElementById("cpu-orb");
      const playerSvgEl = document.getElementById("player-svg");
      const cpuSvgEl = document.getElementById("cpu-svg");
      const statusHudEl = document.getElementById("status-hud");
      const weaponButtons = document.querySelectorAll(".weapon-btn");
      const resetBtn = document.getElementById("reset-btn");

      function formatScore(num) {
        return String(num).padStart(2, "0");
      }

      function setOrbIcon(svgElement, iconId) {
        const useTag = svgElement.querySelector("use");
        useTag.setAttribute("href", iconId);
        svgElement.classList.remove("pop-in");
        void svgElement.offsetWidth;
        svgElement.classList.add("pop-in");
      }

      function setControlsDisabled(disabled) {
        weaponButtons.forEach((btn) => { btn.disabled = disabled; });
        resetBtn.disabled = disabled;
      }

      function renderScore(score) {
        playerScoreEl.textContent = formatScore(score.player);
        drawScoreEl.textContent = formatScore(score.draws);
        cpuScoreEl.textContent = formatScore(score.cpu);
      }

      async function loadScore() {
        try {
          const res = await fetch("/api/score", { cache: "no-store" });
          if (!res.ok) throw new Error("Failed to sync score");
          const data = await res.json();
          renderScore(data.score);
          statusHudEl.textContent = "System Ready — Awaiting Input";
          statusHudEl.className = "status-hud";
        } catch (err) {
          statusHudEl.textContent = "Run `python app.py` and open 127.0.0.1:5050";
          statusHudEl.className = "status-hud lose";
        }
      }

      async function playRound(choice) {
        setControlsDisabled(true);
        try {
          const res = await fetch("/api/play", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ choice }),
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.error || "Round error");

          renderScore(data.score);
          setOrbIcon(playerSvgEl, WEAPON_ICONS[data.playerChoice] || "#icon-idle");
          setOrbIcon(cpuSvgEl, WEAPON_ICONS[data.cpuChoice] || "#icon-idle");

          playerOrbEl.className = `holo-orb ${data.outcome}`;
          cpuOrbEl.className = `holo-orb ${
            data.outcome === "win" ? "lose" : data.outcome === "lose" ? "win" : "draw"
          }`;

          statusHudEl.textContent = data.message;
          statusHudEl.className = `status-hud ${data.outcome}`;
        } catch (err) {
          statusHudEl.textContent = err.message;
          statusHudEl.className = "status-hud lose";
        } finally {
          setControlsDisabled(false);
        }
      }

      async function resetArena() {
        setControlsDisabled(true);
        try {
          const res = await fetch("/api/reset", { method: "POST" });
          const data = await res.json();
          if (!res.ok) throw new Error(data.error || "Reset failed");

          renderScore(data.score);
          setOrbIcon(playerSvgEl, "#icon-idle");
          setOrbIcon(cpuSvgEl, "#icon-idle");

          playerOrbEl.className = "holo-orb";
          cpuOrbEl.className = "holo-orb";
          statusHudEl.textContent = data.message;
          statusHudEl.className = "status-hud";
        } catch (err) {
          statusHudEl.textContent = err.message;
          statusHudEl.className = "status-hud lose";
        } finally {
          setControlsDisabled(false);
        }
      }

      weaponButtons.forEach((btn) => {
        btn.addEventListener("click", () => playRound(btn.dataset.choice));
      });

      resetBtn.addEventListener("click", resetArena);
      loadScore();
    });
  </script>
</body>
</html>
"""

#HTTP Request Handler & Server Startup
class GameRequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _write_bytes(self, body):
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def send_json(self, payload, status_code=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self._write_bytes(body)

    def send_html(self, html_text, status_code=200):
        body = html_text.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self._write_bytes(body)

    def read_json_body(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            length = 0
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def do_GET(self):
        clean_path = self.path.split("?", 1)[0]
        if clean_path in ("/", "/index.html"):
            self.send_html(HTML_PAGE, 200)
        elif clean_path == "/ITSROCK.png":
            icon_path = os.path.join(BASE_DIR, "ITSROCK.png")
            if os.path.exists(icon_path):
                with open(icon_path, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self._write_bytes(body)
            else:
                self.send_json({"error": "ITSROCK.png not found"}, 404)
        elif clean_path == "/api/score":
            self.send_json({"score": read_score()}, 200)
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        clean_path = self.path.split("?", 1)[0]
        if clean_path == "/api/play":
            try:
                payload = self.read_json_body()
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.send_json({"error": "Invalid JSON body"}, 400)
                return

            player_choice = str(payload.get("choice", "")).lower().strip()
            if player_choice not in WEAPONS:
                self.send_json({"error": "Invalid choice. Choose rock, paper, or scissors."}, 400)
                return

            cpu_choice = random.choice(list(WEAPONS.keys()))
            outcome, message = evaluate_round(player_choice, cpu_choice)
            score = read_score()

            if outcome == "win":
                score["player"] += 1
            elif outcome == "lose":
                score["cpu"] += 1
            else:
                score["draws"] += 1

            write_score(score)
            self.send_json({
                "playerChoice": player_choice,
                "cpuChoice": cpu_choice,
                "outcome": outcome,
                "message": message,
                "score": score,
            }, 200)

        elif clean_path == "/api/reset":
            fresh_score = DEFAULT_SCORE.copy()
            write_score(fresh_score)
            self.send_json({
                "message": "SCORE DATA RESET // AWAITING INPUT",
                "score": fresh_score,
            }, 200)
        else:
            self.send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        print(f"[RockPaperScissors] {self.address_string()} - {format % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), GameRequestHandler)
    print(f"Rock paper scissors running at http://{HOST}:{PORT} (Press Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()