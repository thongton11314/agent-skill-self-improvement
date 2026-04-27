"""Skill Bank: Persistent repository of evolving skill packages."""

from dataclasses import dataclass, field
from typing import Optional
import json
import os


@dataclass
class Skill:
    """A structured skill package."""
    trigger_condition: str
    strategy: str
    accuracy: float
    version: int
    artifacts: dict = field(default_factory=dict)
    failure_buffer: list = field(default_factory=list)
    skill_id: str = ""

    def to_prompt_context(self) -> str:
        """Convert skill to prompt-injectable context."""
        return f"""# Skill Guide
## When to Use
{self.trigger_condition}

## Strategy
{self.strategy}

## Version: v{self.version} (accuracy: {self.accuracy:.0%})
"""

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "trigger_condition": self.trigger_condition,
            "strategy": self.strategy,
            "accuracy": self.accuracy,
            "version": self.version,
            "artifacts": {k: v for k, v in self.artifacts.items()},
            "failure_count": len(self.failure_buffer),
        }


class SkillBank:
    """Persistent repository for storing and retrieving evolved skills."""

    def __init__(self, config):
        self.config = config
        self._skills: dict[str, Skill] = {}
        self._next_id = 1

    def store(self, skill: Skill) -> str:
        """Store a skill in the bank. Returns the skill ID."""
        if not skill.skill_id:
            skill.skill_id = f"skill-{self._next_id:04d}"
            self._next_id += 1

        self._skills[skill.skill_id] = skill
        return skill.skill_id

    def retrieve(self, query: str, top_k: int = 3, min_accuracy: float = 0.0) -> list[Skill]:
        """Retrieve relevant skills by semantic similarity to query.

        Args:
            query: Natural language query.
            top_k: Maximum number of skills to return.
            min_accuracy: Minimum accuracy threshold.

        Returns:
            List of matching skills, ranked by relevance.
        """
        candidates = [
            s for s in self._skills.values()
            if s.accuracy >= min_accuracy
        ]

        # Score by simple keyword overlap (production: use embeddings)
        scored = []
        query_words = set(query.lower().split())
        for skill in candidates:
            trigger_words = set(skill.trigger_condition.lower().split())
            overlap = len(query_words & trigger_words)
            scored.append((overlap, skill))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:top_k]]

    def get(self, skill_id: str) -> Optional[Skill]:
        """Get a specific skill by ID."""
        return self._skills.get(skill_id)

    def get_latest(self, version: Optional[int] = None) -> Optional[Skill]:
        """Get the latest skill, optionally filtered by version."""
        if not self._skills:
            return None

        candidates = list(self._skills.values())
        if version is not None:
            candidates = [s for s in candidates if s.version == version]

        if not candidates:
            return None

        return max(candidates, key=lambda s: s.version)

    def list_all(self) -> list[Skill]:
        """List all skills in the bank."""
        return list(self._skills.values())

    def remove(self, skill_id: str) -> bool:
        """Remove a skill from the bank."""
        if skill_id in self._skills:
            del self._skills[skill_id]
            return True
        return False

    @property
    def size(self) -> int:
        return len(self._skills)
