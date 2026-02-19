"""
Shared state object passed between all agents in the pipeline.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GameBuildState:
    # Phase 1: Raw input
    user_prompt: str = ""

    # Phase 2: Clarification
    clarification_questions: list = field(default_factory=list)
    user_answers: list = field(default_factory=list)
    clarified_requirements: dict = field(default_factory=dict)
    complexity_level: str = ""
    detected_game_type: str = ""

    # Phase 3: Planning
    architecture_plan: dict = field(default_factory=dict)
    architecture_plan_raw: str = ""

    # Phase 4: Implementation
    implementation_files: dict = field(default_factory=dict)  # {filename: content}

    # Phase 5: Validation
    validation_report: dict = field(default_factory=dict)
    validation_status: str = "pending"  # pending | pass | fail

    # Meta
    iteration_count: int = 0
    max_iterations: int = 3
    status: str = "init"  # init | clarifying | planning | implementing | validating | done
    run_instructions: str = ""

    def summary(self) -> str:
        """Compact summary for passing context to agents."""
        return f"""
USER PROMPT: {self.user_prompt}

GAME TYPE: {self.detected_game_type}
COMPLEXITY: {self.complexity_level}

CLARIFICATIONS:
{self._format_qa()}

REQUIREMENTS SUMMARY:
{self.clarified_requirements}
""".strip()

    def _format_qa(self) -> str:
        pairs = []
        for i, (q, a) in enumerate(zip(self.clarification_questions, self.user_answers)):
            pairs.append(f"  Q{i+1}: {q}\n  A{i+1}: {a}")
        return "\n".join(pairs) if pairs else "None"
