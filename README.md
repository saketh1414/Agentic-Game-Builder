# 🎮 Agentic Game Builder

> A multi-agent AI system that turns a vague game idea into a fully playable browser game — powered by **CrewAI** and **Google Gemini**.

---

## 📐 Architecture Overview

```
User Prompt
     │
     ▼
┌─────────────────────────────────────────────┐
│           MANAGER AGENT (Orchestrator)       │
│   Python-controlled pipeline — decides      │
│   phase transitions, runs retry loops       │
└──────────────┬──────────────────────────────┘
               │
     ┌─────────▼──────────┐
     │  AGENT 1            │  ← Clarification & Complexity Analyzer
     │  Requirements       │     Analyzes prompt, detects game type,
     │  Analyst            │     generates targeted Q&A questions
     └─────────┬──────────┘
               │ (User answers questions interactively)
     ┌─────────▼──────────┐
     │  AGENT 2            │  ← System Architect & Planner
     │  Game Architect     │     Produces full technical blueprint:
     │                     │     mechanics, classes, game loop, rendering
     └─────────┬──────────┘
               │
     ┌─────────▼──────────┐
     │  AGENT 3            │  ← Implementation Agent
     │  Game Developer     │     Generates index.html, style.css, game.js
     └─────────┬──────────┘
               │ ◄────────────── (feedback loop, max 3 retries)
     ┌─────────▼──────────┐
     │  AGENT 4            │  ← Validation & QA Agent
     │  QA Engineer        │     Checks syntax, logic, completeness
     └─────────┬──────────┘
               │ (if FAIL → sends feedback to Agent 3)
               │ (if PASS → proceed)
     ┌─────────▼──────────┐
     │  MANAGER AGENT      │  ← Generates run instructions
     │  (Final Output)     │     Writes files, prints game guide
     └────────────────────┘
               │
     📁 generated_game/
        ├── index.html
        ├── style.css
        └── game.js
```

---

## 🤖 Agent Roles

### Manager Agent (Orchestrator)
The Python-level controller. It does **not** generate content — it controls the pipeline. It decides when clarification is sufficient, runs the Dev↔QA retry loop (max 3 iterations), and produces the final play instructions.

### Agent 1 — Requirements Analyst
- **Input:** Raw user game idea
- **Output:** Complexity level, game type, 3–7 targeted clarification questions
- **Skill:** Identifies ambiguity — asks only what truly matters for implementation

### Agent 2 — System Architect
- **Input:** Original prompt + Q&A answers
- **Output:** Full 11-section technical blueprint (framework, mechanics, class structure, game loop, rendering, edge cases)
- **Skill:** Defines everything before a line of code is written — the most critical agent

### Agent 3 — Game Developer
- **Input:** Architecture plan (+ validation feedback on retries)
- **Output:** Complete `index.html`, `style.css`, `game.js`
- **Skill:** Follows the blueprint precisely. No TODOs, no placeholders

### Agent 4 — QA Engineer
- **Input:** All 3 generated files + architecture plan
- **Output:** Structured validation report (`PASS` or `FAIL` with actionable feedback)
- **Checks:** Syntax errors, missing DOM elements, game loop correctness, win/lose conditions, control bindings, plan compliance

---

## 🗂 Project Structure

```
agentic-game-builder/
├── agents/
│   ├── manager.py              # Orchestrator — controls all phases
│   ├── clarification_agent.py  # Agent 1: analyzes prompt, generates questions
│   ├── planning_agent.py       # Agent 2: full architecture plan
│   ├── implementation_agent.py # Agent 3: generates game code
│   └── validation_agent.py     # Agent 4: validates output
├── models/
│   └── state.py                # GameBuildState — shared context object
├── utils/
│   ├── llm_config.py           # Gemini LLM setup via CrewAI
│   └── file_writer.py          # Parses agent output, writes files
├── generated_game/             # Output directory
│   ├── index.html              # (generated)
│   ├── style.css               # (generated)
│   └── game.js                 # (generated)
├── main.py                     # Entry point
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🐳 Docker — Build & Run

### Prerequisites
- Docker installed
- A Google Gemini API key ([get one free here](https://aistudio.google.com/app/apikey))

### Build the image
```bash
docker build -t game-builder .
```

### Run the agent (interactive)
> **⚠️ Disclaimer:** This container is designed to ask you questions during execution. Run it with `-it` so you can respond in real time. Also mount the `generated_game` directory to persist the output on the host.

```bash
# Mount the generated_game folder so you get the files on your host machine
docker run -it \
  -e GEMINI_API_KEY=your_gemini_api_key_here \
  -v $(pwd)/generated_game:/app/generated_game \
  game-builder
```

> **Windows (PowerShell):**
> ```powershell
> docker run -it `
>   -e GEMINI_API_KEY=your_gemini_api_key_here `
>   -v ${PWD}/generated_game:/app/generated_game `
>   game-builder
> ```

### What happens
1. You describe your game idea in the terminal
2. Agent 1 asks you clarifying questions
3. You answer them one by one
4. Agents 2, 3, 4 run automatically (may take 2–5 minutes)
5. Game files appear in `./generated_game/`
6. Open `generated_game/index.html` in your browser — game is ready!

---

## 🖥 Running Locally (without Docker)

### Setup
```bash
# Python 3.10–3.13 required
pip install -r requirements.txt

# Set your API key
export GEMINI_API_KEY="your-key-here"   # Linux/Mac
set GEMINI_API_KEY=your-key-here        # Windows CMD
$env:GEMINI_API_KEY="your-key-here"     # Windows PowerShell
```

### Run
```bash
python main.py
```

---

## 🎮 Example Session

```
============================================================
  🎮 AGENTIC GAME BUILDER — Powered by CrewAI + Gemini
============================================================

Your game idea: A snake game where the snake gets faster as it eats more food

────────────────────────────────────────────────────────────
  🎮 PHASE 1/4 — Analyzing your game idea...
     Agent 1: Requirements Analyst
────────────────────────────────────────────────────────────
  ✅ Detected game type: Snake / Arcade
  ✅ Complexity: medium

  Q1: Should the game have walls (game over on collision) or wrap-around edges?
  Your answer: Walls — hitting the edge ends the game

  Q2: Should food appear randomly, or in a specific pattern?
  Your answer: Random positions

  Q3: What color scheme do you prefer?
  Your answer: Dark background, bright green snake, red food

  [... planning, implementation, validation run automatically ...]

  ✅ Validation PASSED on iteration 1!

  🎉 BUILD COMPLETE!
  Open generated_game/index.html in your browser to play! 🎮
```

---

## ⚙️ Design Decisions & Trade-offs

### Why Python orchestrates instead of pure CrewAI hierarchical mode?
CrewAI's `Process.hierarchical` has a [known issue](https://towardsdatascience.com/why-crewais-manager-worker-architecture-fails-and-how-to-fix-it/) where it doesn't truly delegate conditionally — it runs all tasks sequentially regardless. For a pipeline that needs:
- An interactive user Q&A loop
- A conditional Dev↔QA retry loop
- Phase-transition logic

…Python control flow is far more reliable. Each **agent's reasoning** still runs inside CrewAI — Python just controls **when** agents are invoked.

### Why Gemini 2.0 Flash?
- Fast (low latency for code generation)
- Large context window (handles full plan + code in one prompt)
- Cost-effective for multi-agent iteration loops
- Swap to `gemini-1.5-pro` in `utils/llm_config.py` for higher quality

### Why vanilla JS as default? (with Phaser as an option)
Agent 2 decides the framework based on game complexity. Vanilla JS is chosen for simpler games because:
- Zero CDN dependency
- Guaranteed to work offline
- Easier for Agent 4 to validate

Phaser is chosen when the game needs physics, tilemaps, or complex sprite management.

### Structured state object (`GameBuildState`)
Rather than passing strings between agents, a shared `GameBuildState` dataclass carries all context. This ensures agents always have the full picture and prevents information loss across phases.

### Max 3 iterations for Dev↔QA loop
Balances quality vs cost. Most games pass in 1–2 iterations. On the 3rd, the best available code is used with a warning.

---

## 🚀 Improvements With More Time

| Area | Improvement |
|------|-------------|
| **Validation** | Integrate ESLint via subprocess for real syntax checking instead of LLM-based static analysis |
| **Validation** | Use Playwright/Puppeteer to headlessly run the game and detect runtime JS errors |
| **LLM** | Add response caching to avoid re-generating unchanged sections on retry |
| **UX** | Add a `--non-interactive` mode that accepts a JSON config file for CI/CD pipelines |
| **Quality** | Add a separate "Polish Agent" that improves visuals and UX after the code passes validation |
| **Observability** | Integrate CrewAI's built-in tracing or LangFuse for per-agent token usage and latency tracking |
| **Multi-game** | Add memory across sessions so the agent improves its game generation patterns over time |
| **Output** | Auto-zip the `generated_game/` folder and print a download link |

---

## 🔑 API Key Setup

| Method | Command |
|--------|---------|
| Environment variable | `export GEMINI_API_KEY=your_key` |
| Docker flag | `-e GEMINI_API_KEY=your_key` |
| Direct in code | Edit `utils/llm_config.py` line 16 |

Get a free Gemini API key at: https://aistudio.google.com/app/apikey

---

## 📋 Requirements

- Python 3.10–3.13
- Docker (optional, for containerized run)
- Google Gemini API key (free tier works)
- Modern web browser (Chrome, Firefox, Safari, Edge) to play the game
