"""
Agent 4 — Validation & QA Agent

Performs static analysis and logical validation of the generated game code.
Returns a structured report that the Manager uses to decide whether to
accept the code or send it back to Agent 3 for fixes.
"""
import re
from crewai import Agent, Task, Crew, Process
from utils.llm_config import get_llm
from models.state import GameBuildState


def build_validation_agent() -> Agent:
    return Agent(
        role="QA Engineer & Code Reviewer",
        goal=(
            "Thoroughly validate the generated game code for syntax errors, logical "
            "flaws, missing functionality, and deviations from the architecture plan. "
            "Produce a clear, actionable validation report."
        ),
        backstory=(
            "You are a rigorous QA engineer and code reviewer specializing in "
            "JavaScript browser games. You have a methodical approach: you read every "
            "line, trace every execution path, and test every edge case mentally. "
            "You never let broken code pass. Your reports are specific — you cite "
            "exact problems, not vague complaints. You also recognize when code is "
            "genuinely good and pass it without unnecessary nitpicking."
        ),
        llm=get_llm(),
        allow_delegation=False,
        verbose=True,
    )


def run_validation(state: GameBuildState) -> dict:
    """
    Validates the generated game files against the architecture plan.
    
    Returns:
        {
            "status": "pass" | "fail",
            "errors": [...],
            "logic_issues": [...],
            "improvement_suggestions": [...],
            "feedback_for_agent3": str  # Consolidated feedback for retry
        }
    """
    agent = build_validation_agent()

    html_content = state.implementation_files.get("index.html", "MISSING")
    css_content = state.implementation_files.get("style.css", "MISSING")
    js_content = state.implementation_files.get("game.js", "MISSING")

    task = Task(
        description=f"""
You are validating generated browser game code. Be thorough and precise.

=== ARCHITECTURE PLAN (what should be implemented) ===
{state.architecture_plan_raw[:3000]}

=== GENERATED FILES ===

--- index.html ---
{html_content}

--- style.css ---
{css_content}

--- game.js ---
{js_content}

=== VALIDATION CHECKLIST ===

Perform ALL of the following checks:

**FILE COMPLETENESS**
- [ ] All 3 files present and non-empty?
- [ ] index.html has DOCTYPE, html, head, body tags?
- [ ] index.html loads game.js and style.css?
- [ ] Canvas element present in HTML (if canvas-based game)?

**JAVASCRIPT SYNTAX**
- [ ] No obvious syntax errors (unclosed braces, missing semicolons in critical places)?
- [ ] All functions that are called are also defined?
- [ ] All variables that are used are declared?
- [ ] No references to undefined DOM elements?

**GAME LOOP**
- [ ] requestAnimationFrame loop implemented (vanilla) OR Phaser game loop used?
- [ ] Update and render are separated?
- [ ] Delta time or FPS control present?

**GAME MECHANICS**
- [ ] Player can be controlled (keyboard/mouse events set up)?
- [ ] Start screen exists?
- [ ] Game over condition triggers correctly?
- [ ] Score is tracked and displayed?
- [ ] Win condition implemented (if applicable)?

**ARCHITECTURE COMPLIANCE**
- [ ] Does the code follow the architecture plan's class/function structure?
- [ ] Are all mechanics from the plan implemented?
- [ ] Any missing features from the plan?

**PLAYABILITY**
- [ ] Would this game actually run in a browser without errors?
- [ ] Is the game playable and fun at a basic level?
- [ ] Are there any infinite loops or performance issues?

=== OUTPUT FORMAT ===

Respond in EXACTLY this format:

VALIDATION_STATUS: <PASS|FAIL>

ERRORS (critical issues that break the game):
- <error 1 with specific description and location>
- <error 2>
[list all errors, or write "None" if no errors]

LOGIC_ISSUES (game won't work correctly but doesn't crash):
- <issue 1>
- <issue 2>
[list all issues, or write "None" if no issues]

MISSING_FEATURES (things in the plan that weren't implemented):
- <feature 1>
[list all, or write "None"]

IMPROVEMENT_SUGGESTIONS (nice to have, not blocking):
- <suggestion 1>
[list up to 3, or write "None"]

FEEDBACK_FOR_DEVELOPER:
<Write a clear, consolidated paragraph of everything Agent 3 must fix in the next iteration.
Be specific: mention exact function names, line issues, and what correct behavior should be.
If status is PASS, write "No changes needed — code is approved.">
""",
        expected_output=(
            "A structured validation report with VALIDATION_STATUS, ERRORS, LOGIC_ISSUES, "
            "MISSING_FEATURES, IMPROVEMENT_SUGGESTIONS, and FEEDBACK_FOR_DEVELOPER."
        ),
        agent=agent,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff()
    raw = str(result)

    return _parse_validation_output(raw)


def _parse_validation_output(raw: str) -> dict:
    """Parse Agent 4's structured validation output."""
    status = "fail"
    errors = []
    logic_issues = []
    missing_features = []
    suggestions = []
    feedback = ""

    lines = raw.split("\n")
    current_section = None

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("VALIDATION_STATUS:"):
            status_str = stripped.replace("VALIDATION_STATUS:", "").strip().upper()
            status = "pass" if "PASS" in status_str else "fail"

        elif stripped.startswith("ERRORS"):
            current_section = "errors"
        elif stripped.startswith("LOGIC_ISSUES"):
            current_section = "logic"
        elif stripped.startswith("MISSING_FEATURES"):
            current_section = "missing"
        elif stripped.startswith("IMPROVEMENT_SUGGESTIONS"):
            current_section = "suggestions"
        elif stripped.startswith("FEEDBACK_FOR_DEVELOPER"):
            current_section = "feedback"

        elif current_section and stripped.startswith("-") and stripped != "-":
            item = stripped[1:].strip()
            if item.lower() != "none" and item:
                if current_section == "errors":
                    errors.append(item)
                elif current_section == "logic":
                    logic_issues.append(item)
                elif current_section == "missing":
                    missing_features.append(item)
                elif current_section == "suggestions":
                    suggestions.append(item)

        elif current_section == "feedback" and stripped and not stripped.startswith("VALIDATION"):
            feedback += stripped + " "

    # Build consolidated feedback for Agent 3
    feedback_parts = []
    if errors:
        feedback_parts.append("CRITICAL ERRORS TO FIX:\n" + "\n".join(f"  - {e}" for e in errors))
    if logic_issues:
        feedback_parts.append("LOGIC ISSUES TO FIX:\n" + "\n".join(f"  - {l}" for l in logic_issues))
    if missing_features:
        feedback_parts.append("MISSING FEATURES TO ADD:\n" + "\n".join(f"  - {m}" for m in missing_features))
    if feedback.strip():
        feedback_parts.append(f"DEVELOPER NOTES:\n  {feedback.strip()}")

    return {
        "status": status,
        "errors": errors,
        "logic_issues": logic_issues,
        "missing_features": missing_features,
        "improvement_suggestions": suggestions,
        "feedback_for_agent3": "\n\n".join(feedback_parts) if feedback_parts else "No changes needed.",
    }
