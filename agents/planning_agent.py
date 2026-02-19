"""
Agent 2 — System Architect & Planner

Takes the original prompt + clarification Q&A and produces a complete,
detailed technical plan that Agent 3 (Implementation) must follow exactly.
This is the most critical agent — its output quality determines game quality.
"""
from crewai import Agent, Task, Crew, Process
from utils.llm_config import get_llm
from models.state import GameBuildState


def build_planning_agent() -> Agent:
    return Agent(
        role="Senior Game Architect",
        goal=(
            "Produce a complete, unambiguous technical blueprint for a browser-based "
            "HTML/CSS/JavaScript game that a developer can implement without any "
            "further clarification. The plan must be detailed enough to generate "
            "fully working, playable game code."
        ),
        backstory=(
            "You are a principal engineer who has architected dozens of browser-based "
            "games using vanilla JavaScript and Phaser. You think in systems: game loops, "
            "state machines, event flows, rendering pipelines. Your plans are legendary "
            "for being so precise that junior developers can implement them perfectly "
            "on the first try. You never leave things vague."
        ),
        llm=get_llm(),
        allow_delegation=False,
        verbose=True,
    )


def run_planning(state: GameBuildState) -> str:
    """
    Runs Agent 2 to produce a complete technical architecture plan.
    Returns the raw plan text (stored in state.architecture_plan_raw).
    """
    agent = build_planning_agent()

    task = Task(
        description=f"""
You are the architect. Based on the game requirements below, create a COMPLETE technical plan.
The implementation agent will code EXACTLY what you specify — so leave nothing vague.

=== GAME REQUIREMENTS ===
{state.summary()}

=== YOUR DELIVERABLE ===

Produce a detailed technical architecture plan covering ALL of the following sections:

## 1. FRAMEWORK DECISION
- Choose: vanilla JavaScript OR Phaser.js
- Justify your choice based on the game type and complexity
- If Phaser: specify CDN URL to use
- If vanilla: describe canvas vs DOM approach

## 2. FILE STRUCTURE
- List all 3 files: index.html, style.css, game.js
- Describe the purpose of each file
- Describe what goes in index.html (canvas setup, script tags, etc.)
- Describe style.css rules needed

## 3. GAME MECHANICS (be very specific)
- Core gameplay loop (what happens every frame/tick)
- Player actions and responses
- Enemy/obstacle behavior (if any)
- Collision detection approach
- Win condition (exact trigger)
- Lose/game-over condition (exact trigger)
- Score system (how score is calculated and displayed)
- Difficulty progression (if any)

## 4. CONTROLS
- List every key/mouse event needed
- Map each control to its action
- Mobile touch support: yes/no and how

## 5. STATE MANAGEMENT
- List all game states: e.g. START_SCREEN, PLAYING, PAUSED, GAME_OVER
- Describe what happens in each state
- Describe state transitions (what triggers each transition)

## 6. RENDERING STRATEGY
- Canvas 2D context approach OR DOM-based
- What gets drawn each frame and in what order
- How background, player, enemies, UI are layered
- Animation approach (requestAnimationFrame loop)

## 7. CORE CLASSES & FUNCTIONS (with signatures)
- List every class that needs to be created with its properties and methods
- List every key function with its parameters and return value
- Be specific enough that an implementer can write the code directly

## 8. GAME LOOP DESIGN
- Describe the main game loop step by step
- Update logic order (input → physics → collision → render → UI)
- Target FPS and how it's achieved

## 9. ASSETS & VISUALS
- No external image files — use canvas shapes, colors, or CSS
- Define exact colors, sizes, shapes for every visual element
- Font choices for any text

## 10. EDGE CASES TO HANDLE
- List at least 5 edge cases the implementation must handle
- e.g. player going off-screen, multiple keys pressed at once, game reset

## 11. HTML STRUCTURE
- Exact DOM elements needed in index.html
- Canvas dimensions
- Any overlay divs for UI (score display, start screen, game over screen)

Be EXTREMELY specific. The implementation agent will follow your plan to the letter.
""",
        expected_output=(
            "A comprehensive technical architecture plan covering all 11 sections, "
            "detailed enough for direct implementation without further clarification."
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
    return str(result)
