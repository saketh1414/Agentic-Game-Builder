"""
Agent 1 — Clarification & Complexity Analyzer

Analyzes the user's raw prompt, determines complexity, and generates
targeted clarification questions to ensure nothing important is missed
before planning begins.
"""
from crewai import Agent, Task, Crew, Process
from utils.llm_config import get_llm


def build_clarification_agent() -> Agent:
    return Agent(
        role="Game Requirements Analyst",
        goal=(
            "Analyze the user's game idea, assess its complexity, and generate "
            "targeted, non-redundant clarification questions that will enable "
            "precise planning and implementation."
        ),
        backstory=(
            "You are a senior game designer and requirements analyst with 10+ years "
            "of experience shipping browser-based games. You have a sharp eye for "
            "ambiguity in game descriptions and know exactly what technical details "
            "are needed before a developer can begin. You ask minimal but highly "
            "targeted questions — never vague, never redundant."
        ),
        llm=get_llm(),
        allow_delegation=False,
        verbose=True,
    )


def run_clarification_analysis(user_prompt: str) -> dict:
    """
    Runs Agent 1 to analyze the user prompt and return:
    - complexity_level: low | medium | high
    - detected_game_type: e.g. "platformer", "shooter", "puzzle"
    - clarification_questions: list of strings
    """
    agent = build_clarification_agent()

    task = Task(
        description=f"""
Analyze the following game idea provided by a user and produce a structured analysis.

USER GAME IDEA:
"{user_prompt}"

Your job:
1. Identify the game genre/type (platformer, shooter, puzzle, arcade, RPG, etc.)
2. Assess complexity: "low" (simple single mechanic), "medium" (multiple mechanics), "high" (complex systems)
3. Generate between 3 and 7 TARGETED clarification questions. Focus only on aspects that:
   - Are genuinely ambiguous
   - Will materially affect the implementation
   - Cannot be reasonably assumed

Topics to consider for questions (only ask what's relevant and unclear):
- Single player or multiplayer?
- Win/lose conditions?
- Player controls (keyboard, mouse, touch)?
- Scoring system?
- Number of levels or infinite?
- Visual style (pixel, geometric shapes, color scheme)?
- Game speed / difficulty?
- Should it be mobile-friendly (responsive)?
- Any specific mechanics mentioned that need clarification?

DO NOT ask questions that can be reasonably assumed from context.
DO NOT ask more than 7 questions.

Respond in this EXACT format (no extra text before or after):

COMPLEXITY: <low|medium|high>
GAME_TYPE: <detected game type>
QUESTIONS:
1. <question 1>
2. <question 2>
3. <question 3>
[continue up to 7]
""",
        expected_output=(
            "A structured analysis with COMPLEXITY, GAME_TYPE, and numbered QUESTIONS "
            "in the exact format specified."
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

    # Parse the structured response
    return _parse_clarification_output(raw)


def _parse_clarification_output(raw: str) -> dict:
    """Parse Agent 1's structured output into a dict."""
    lines = raw.strip().split("\n")
    complexity = "medium"
    game_type = "arcade"
    questions = []
    in_questions = False

    for line in lines:
        line = line.strip()
        if line.startswith("COMPLEXITY:"):
            complexity = line.replace("COMPLEXITY:", "").strip().lower()
        elif line.startswith("GAME_TYPE:"):
            game_type = line.replace("GAME_TYPE:", "").strip()
        elif line.startswith("QUESTIONS:"):
            in_questions = True
        elif in_questions and line and line[0].isdigit() and "." in line:
            q = line.split(".", 1)[1].strip()
            if q:
                questions.append(q)

    # Fallback if parsing fails
    if not questions:
        questions = [
            "What are the win and lose conditions for the game?",
            "What controls should the player use (keyboard, mouse, or both)?",
            "Should the game have a scoring system? If so, how is score earned?",
        ]

    return {
        "complexity_level": complexity,
        "detected_game_type": game_type,
        "clarification_questions": questions,
    }
