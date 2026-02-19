"""
Manager Agent — Central Orchestrator

Controls the entire pipeline:
  1. Receive user prompt
  2. Run Agent 1 (clarification analysis)
  3. Interactive Q&A loop with user
  4. Run Agent 2 (architecture planning)
  5. Run Agent 3 (implementation)
  6. Run Agent 4 (validation)
  7. Loop Agent 3 ↔ Agent 4 until passing (max 3 iterations)
  8. Write files and produce run instructions

The Manager is a Python orchestrator — it controls flow.
CrewAI agents handle the actual AI reasoning within each phase.
"""
import time
from crewai import Agent, Task, Crew, Process

from models.state import GameBuildState
from agents.clarification_agent import run_clarification_analysis
from agents.planning_agent import run_planning
from agents.implementation_agent import run_implementation
from agents.validation_agent import run_validation
from utils.file_writer import write_game_files
from utils.llm_config import get_llm


# ─── Console helpers ─────────────────────────────────────────────────────────

def _print_banner(text: str):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def _print_phase(phase: str, desc: str = ""):
    print(f"\n{'─'*60}")
    print(f"  🎮 {phase}")
    if desc:
        print(f"     {desc}")
    print(f"{'─'*60}")

def _print_success(text: str):
    print(f"  ✅ {text}")

def _print_warning(text: str):
    print(f"  ⚠️  {text}")

def _print_info(text: str):
    print(f"  ℹ️  {text}")


# ─── Manager Agent (for final run instructions) ──────────────────────────────

def _build_manager_agent() -> Agent:
    return Agent(
        role="Game Build Manager",
        goal=(
            "Review the completed game build and produce clear, friendly instructions "
            "for how to open, run, and play the generated game."
        ),
        backstory=(
            "You are the project manager who oversaw the entire game development process. "
            "You write crystal-clear instructions that even non-technical users can follow. "
            "You always include: how to open the game, what controls to use, what the "
            "objective is, and any tips for getting the best experience."
        ),
        llm=get_llm(),
        allow_delegation=False,
        verbose=False,
    )


def _generate_run_instructions(state: GameBuildState) -> str:
    """Use the Manager Agent to generate friendly run/play instructions."""
    agent = _build_manager_agent()

    task = Task(
        description=f"""
The game development pipeline has completed successfully.

Game Details:
- Type: {state.detected_game_type}
- Complexity: {state.complexity_level}
- Original Idea: {state.user_prompt}
- Controls from plan: see architecture plan
- Output files: index.html, style.css, game.js (in ./generated_game/ folder)

Architecture Plan Summary:
{state.architecture_plan_raw[:2000]}

Write clear, friendly instructions covering:
1. How to run the game (open index.html in browser)
2. Complete controls list (keyboard keys, mouse if applicable)
3. Game objective / how to win
4. How to restart after game over
5. Any tips or tricks
6. Technical requirements (modern browser, no server needed)

Format it nicely with sections and emoji. Keep it concise but complete.
""",
        expected_output="Clear, friendly game run and play instructions.",
        agent=agent,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff()
    return str(result)


# ─── Main Manager Orchestrator ────────────────────────────────────────────────

class GameBuilderManager:
    """
    The central orchestrator. Controls all agent phases and user interaction.
    """

    def __init__(self):
        self.state = GameBuildState()

    def run(self):
        """Entry point — runs the full pipeline."""
        _print_banner("🎮 AGENTIC GAME BUILDER — Powered by CrewAI + Gemini")
        print("\nWelcome! Describe the game you want to build.")
        print("Be as vague or detailed as you like — I'll ask clarifying questions.\n")

        # ── Phase 1: Get user prompt ──────────────────────────────────────────
        self.state.user_prompt = input("Your game idea: ").strip()
        if not self.state.user_prompt:
            print("No input provided. Exiting.")
            return

        self.state.status = "clarifying"

        # ── Phase 2: Agent 1 — Analyze & Generate Questions ──────────────────
        _print_phase("PHASE 1/4 — Analyzing your game idea...", "Agent 1: Requirements Analyst")

        analysis = run_clarification_analysis(self.state.user_prompt)

        self.state.complexity_level = analysis["complexity_level"]
        self.state.detected_game_type = analysis["detected_game_type"]
        self.state.clarification_questions = analysis["clarification_questions"]

        _print_success(f"Detected game type: {self.state.detected_game_type}")
        _print_success(f"Complexity: {self.state.complexity_level}")

        # ── Phase 3: User Q&A Loop ────────────────────────────────────────────
        _print_phase("PHASE 2/4 — Clarification Questions", "Please answer these questions to help me build exactly what you want")

        questions = self.state.clarification_questions
        answers = []

        for i, question in enumerate(questions):
            print(f"\n  Q{i+1}: {question}")
            answer = input(f"  Your answer: ").strip()
            if not answer:
                answer = "No preference, use your best judgment."
            answers.append(answer)

        self.state.user_answers = answers

        # Build clarified requirements summary
        self.state.clarified_requirements = {
            "game_type": self.state.detected_game_type,
            "complexity": self.state.complexity_level,
            "qa_pairs": [
                {"question": q, "answer": a}
                for q, a in zip(questions, answers)
            ]
        }

        _print_success("All questions answered. Moving to planning phase...")

        # ── Phase 4: Agent 2 — Architecture Planning ─────────────────────────
        self.state.status = "planning"
        _print_phase("PHASE 3/4 — Creating Architecture Plan...", "Agent 2: System Architect")
        _print_info("This may take a moment — the architect is designing your game...")

        self.state.architecture_plan_raw = run_planning(self.state)
        _print_success("Architecture plan complete!")

        # ── Phase 5: Agent 3 + 4 — Implement & Validate Loop ─────────────────
        self.state.status = "implementing"
        _print_phase("PHASE 4/4 — Implementing & Validating...", "Agent 3: Developer ↔ Agent 4: QA")

        validation_feedback = ""

        for iteration in range(1, self.state.max_iterations + 1):
            self.state.iteration_count = iteration
            _print_info(f"Implementation iteration {iteration}/{self.state.max_iterations}...")

            # Agent 3: Generate/Fix code
            files = run_implementation(self.state, validation_feedback)

            if not files or len(files) < 3:
                _print_warning(f"Agent 3 produced incomplete files ({len(files)}/3). Retrying...")
                # Provide explicit instruction for retry
                validation_feedback = (
                    "The previous output was incomplete — not all 3 files were generated. "
                    "You MUST output ALL THREE files: index.html, style.css, AND game.js, "
                    "each with the ### filename header and proper code block."
                )
                continue

            self.state.implementation_files = files
            _print_success(f"Generated {len(files)} files: {', '.join(files.keys())}")

            # Agent 4: Validate
            _print_info("Running QA validation...")
            self.state.status = "validating"
            validation_report = run_validation(self.state)
            self.state.validation_report = validation_report
            self.state.validation_status = validation_report["status"]

            if validation_report["status"] == "pass":
                _print_success(f"✅ Validation PASSED on iteration {iteration}!")
                break
            else:
                _print_warning(f"Validation FAILED on iteration {iteration}.")
                if validation_report["errors"]:
                    print("  Critical errors:")
                    for err in validation_report["errors"][:3]:
                        print(f"    • {err}")
                if validation_report["logic_issues"]:
                    print("  Logic issues:")
                    for issue in validation_report["logic_issues"][:3]:
                        print(f"    • {issue}")

                validation_feedback = validation_report["feedback_for_agent3"]

                if iteration == self.state.max_iterations:
                    _print_warning(
                        "Max iterations reached. Using best available code. "
                        "Manual review may be needed."
                    )

        # ── Phase 6: Write Files ──────────────────────────────────────────────
        _print_phase("Writing game files to disk...")
        output_dir = write_game_files(self.state.implementation_files)
        _print_success(f"Game files written to: {output_dir}/")

        # ── Phase 7: Generate Run Instructions ───────────────────────────────
        _print_phase("Generating run instructions...")
        self.state.run_instructions = _generate_run_instructions(self.state)
        self.state.status = "done"

        # ── Final Output ──────────────────────────────────────────────────────
        _print_banner("🎉 BUILD COMPLETE!")
        print()
        print(self.state.run_instructions)
        print()
        _print_banner("Output files")
        for fname in ["index.html", "style.css", "game.js"]:
            if fname in self.state.implementation_files:
                size = len(self.state.implementation_files[fname])
                print(f"  📄 generated_game/{fname} ({size:,} chars)")
        print()
        print("  Open generated_game/index.html in your browser to play! 🎮")
        print()

        return self.state
