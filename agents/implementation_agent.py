"""
Agent 3 — Implementation Agent

Takes the architecture plan from Agent 2 and generates complete, runnable
game files: index.html, style.css, and game.js.

On retry (called by Manager after validation failure), receives validation
feedback and regenerates improved code.
"""
from crewai import Agent, Task, Crew, Process
from utils.llm_config import get_llm
from models.state import GameBuildState


def build_implementation_agent() -> Agent:
    return Agent(
        role="Senior Game Developer",
        goal=(
            "Generate complete, working, playable browser game code in three files "
            "(index.html, style.css, game.js) that strictly follows the architecture "
            "plan. The game must run locally in a browser with zero modifications."
        ),
        backstory=(
            "You are a meticulous senior front-end game developer. You write clean, "
            "modular JavaScript that works perfectly on the first run. You follow "
            "architecture blueprints exactly — no improvisation, no shortcuts, no "
            "placeholder TODOs. Every function you write is complete and tested in "
            "your head before you write it. You never use external assets or CDNs "
            "unless the architecture plan specifies them."
        ),
        llm=get_llm(),
        allow_delegation=False,
        verbose=True,
    )


_IMPLEMENTATION_PROMPT_BASE = """
You are implementing a browser-based game. Follow the architecture plan EXACTLY.

=== GAME SUMMARY ===
{summary}

=== ARCHITECTURE PLAN ===
{plan}

{feedback_section}

=== YOUR TASK ===
Generate THREE complete files. Each file must be complete — no TODOs, no placeholders.

CRITICAL RULES:
1. The game MUST be immediately playable when index.html is opened in a browser
2. Follow the architecture plan — do not invent new mechanics not in the plan
3. ALL game logic goes in game.js
4. style.css handles only visual styling (layout, colors, fonts)  
5. index.html loads style.css and game.js, and contains the canvas/DOM structure
6. No external image files — use canvas drawing (rectangles, circles, arcs, paths)
7. If using Phaser, include the CDN script tag in index.html
8. If using vanilla JS, use requestAnimationFrame for the game loop
9. Include clear START SCREEN with game title and "Press SPACE / Click to Start" instructions
10. Include GAME OVER screen showing final score and "Press R / Click to Restart"
11. Show live score on screen during gameplay
12. Handle keyboard controls as specified in the plan
13. The game must have clear win/lose conditions that work correctly

OUTPUT FORMAT — use EXACTLY these headers followed by code blocks:

### index.html
```html
<!DOCTYPE html>
<html>
...complete HTML...
</html>
```

### style.css
```css
/* Complete CSS */
...
```

### game.js
```javascript
// Complete JavaScript
...
```

Do not include any explanation text outside the code blocks.
Generate the complete code for all three files now.
"""


def run_implementation(state: GameBuildState, validation_feedback: str = "") -> dict:
    """
    Runs Agent 3 to generate game files.
    
    Args:
        state: Current GameBuildState with plan
        validation_feedback: If this is a retry, include validation errors
    
    Returns:
        dict with keys: index.html, style.css, game.js (raw content)
    """
    agent = build_implementation_agent()

    feedback_section = ""
    if validation_feedback:
        feedback_section = f"""
=== VALIDATION FEEDBACK (iteration {state.iteration_count}) ===
The previous implementation had the following issues that MUST be fixed:

{validation_feedback}

Address ALL issues above. Do not introduce new bugs while fixing existing ones.
"""

    prompt = _IMPLEMENTATION_PROMPT_BASE.format(
        summary=state.summary(),
        plan=state.architecture_plan_raw,
        feedback_section=feedback_section,
    )

    task = Task(
        description=prompt,
        expected_output=(
            "Three complete, working game files: index.html, style.css, and game.js, "
            "each labeled with ### filename and enclosed in appropriate code blocks."
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

    # Parse files from response
    from utils.file_writer import extract_files_from_response
    files = extract_files_from_response(raw)

    return files
