"""Memory Manager: Three-tier evolving memory with adaptive retrieval."""

from dataclasses import dataclass, field
from typing import Optional
import math
from skillforge.config import SkillConfig


@dataclass
class MemoryEntry:
    """A single memory entry."""
    content: str
    tier: str  # episodic, semantic, procedural
    quality: float = 0.5
    age: int = 0
    tags: list = field(default_factory=list)
    source_task: str = ""


class MemoryManager:
    """Three-tier memory system with automatic promotion and adaptive retrieval.

    Tiers:
        - Episodic: Raw outcome records per task
        - Semantic: Cross-task patterns distilled periodically
        - Procedural: Executable rules promoted from high-confidence patterns
    """

    def __init__(self, config: SkillConfig):
        self.config = config
        self._episodic: list[MemoryEntry] = []
        self._semantic: list[MemoryEntry] = []
        self._procedural: list[MemoryEntry] = []
        self._episode_count = 0
        self._retrieval_policies = self._init_policies()
        self._policy_scores = {name: {"alpha": 1.0, "beta": 1.0} for name in self._retrieval_policies}

    def record(self, task: dict, skill, outputs: dict):
        """Record a task experience into episodic memory."""
        entry = MemoryEntry(
            content=f"Task: {task.get('instruction', '')[:200]}\n"
                    f"Skill v{skill.version} (acc={skill.accuracy:.0%})\n"
                    f"Status: {outputs.get('status', 'unknown')}",
            tier="episodic",
            quality=skill.accuracy,
            tags=list(task.get("environment", {}).get("tools", [])),
            source_task=task.get("instruction", "")[:100],
        )
        self._episodic.append(entry)
        self._episode_count += 1

        # Periodic semantic distillation
        if self._episode_count % self.config.memory.distill_interval == 0:
            self._distill_semantic()

    def record_success(self, task: dict, skill, result):
        """Record a successful task completion."""
        entry = MemoryEntry(
            content=f"SUCCESS: {task.get('instruction', '')[:200]}",
            tier="episodic",
            quality=1.0,
            source_task=task.get("instruction", "")[:100],
        )
        self._episodic.append(entry)

    def record_failure(self, task: dict, error=None):
        """Record a task failure for future learning."""
        entry = MemoryEntry(
            content=f"FAILURE: {task.get('instruction', '')[:200]}\nError: {error}",
            tier="episodic",
            quality=0.0,
            source_task=task.get("instruction", "")[:100],
        )
        self._episodic.append(entry)

    def retrieve(self, query: str, top_k: int = 5) -> list[MemoryEntry]:
        """Retrieve relevant memories using the adaptive retrieval controller.

        Uses Thompson Sampling to select among retrieval policies,
        then scores and ranks entries within the selected policy.
        """
        # Select retrieval policy via Thompson Sampling
        policy_name = self._select_policy()
        policy = self._retrieval_policies[policy_name]

        # Get candidate entries based on policy tier visibility
        candidates = []
        if "episodic" in policy["tiers"]:
            candidates.extend(self._episodic)
        if "semantic" in policy["tiers"]:
            candidates.extend(self._semantic)
        if "procedural" in policy["tiers"]:
            candidates.extend(self._procedural)

        if not candidates:
            return []

        # Score and rank entries
        scored = [(self._score_entry(query, entry), entry) for entry in candidates]
        scored.sort(key=lambda x: x[0], reverse=True)

        # Apply quality threshold
        threshold = self.config.memory.quality_threshold
        filtered = [(s, e) for s, e in scored if e.quality >= threshold]

        return [e for _, e in filtered[:top_k]]

    def _select_policy(self) -> str:
        """Select a retrieval policy using Thompson Sampling."""
        import random

        best_name = ""
        best_sample = -1.0

        for name, scores in self._policy_scores.items():
            # Sample from Beta distribution
            sample = random.betavariate(scores["alpha"], scores["beta"])
            if sample > best_sample:
                best_sample = sample
                best_name = name

        return best_name

    def update_policy_reward(self, policy_name: str, reward: float):
        """Update the Thompson Sampling posterior for a retrieval policy."""
        if policy_name in self._policy_scores:
            self._policy_scores[policy_name]["alpha"] += reward
            self._policy_scores[policy_name]["beta"] += 1.0 - reward

    def _score_entry(self, query: str, entry: MemoryEntry) -> float:
        """Compute relevance score for a memory entry.

        score = feature_match × quality_factor × recency_factor × tier_boost
        """
        # Feature match (keyword overlap)
        query_words = set(query.lower().split())
        entry_words = set(entry.content.lower().split())
        overlap = len(query_words & entry_words)
        feature_match = overlap / max(len(query_words), 1)

        # Quality factor
        quality_factor = 0.5 + 0.5 * entry.quality

        # Recency factor
        decay = self.config.retrieval.recency_decay
        recency_factor = 0.3 + 0.7 * math.exp(-decay * entry.age)

        # Tier boost
        tier_boost = self.config.retrieval.tier_boosts.get(entry.tier, 1.0)

        return feature_match * quality_factor * recency_factor * tier_boost

    def _distill_semantic(self):
        """Distill episodic memories into semantic patterns."""
        if len(self._episodic) < 3:
            return

        # Group recent episodic entries and find patterns
        recent = self._episodic[-self.config.memory.distill_interval:]

        # Extract common patterns (simplified)
        success_entries = [e for e in recent if e.quality > 0.7]
        failure_entries = [e for e in recent if e.quality < 0.3]

        if success_entries:
            pattern = MemoryEntry(
                content=f"Pattern: {len(success_entries)} successful tasks with common approach",
                tier="semantic",
                quality=sum(e.quality for e in success_entries) / len(success_entries),
            )
            self._semantic.append(pattern)

        if failure_entries:
            pattern = MemoryEntry(
                content=f"Warning: {len(failure_entries)} failures detected - check approach",
                tier="semantic",
                quality=0.3,
            )
            self._semantic.append(pattern)

        # Promote high-confidence semantic patterns to procedural
        self._promote_procedural()

    def _promote_procedural(self):
        """Promote high-confidence semantic patterns to procedural rules."""
        threshold = self.config.memory.promotion_threshold
        for entry in self._semantic:
            if entry.quality >= threshold and entry.tier == "semantic":
                procedural = MemoryEntry(
                    content=f"RULE: {entry.content}",
                    tier="procedural",
                    quality=entry.quality,
                )
                self._procedural.append(procedural)

    def _init_policies(self) -> dict:
        """Initialize the set of retrieval policies."""
        return {
            "none": {"tiers": [], "format": "none"},
            "recent_window": {"tiers": ["episodic"], "format": "sliding_window"},
            "compressed": {"tiers": ["semantic", "procedural"], "format": "ranked_truncate"},
            "full_detailed": {"tiers": ["episodic", "semantic", "procedural"], "format": "full"},
            "aggressive_learner": {"tiers": ["episodic", "semantic", "procedural"], "format": "large_budget"},
        }

    @property
    def stats(self) -> dict:
        return {
            "episodic_count": len(self._episodic),
            "semantic_count": len(self._semantic),
            "procedural_count": len(self._procedural),
            "total_episodes": self._episode_count,
        }
