"""Configuration management for SkillForge."""

from dataclasses import dataclass, field
from typing import Optional
import yaml
import os


@dataclass
class LLMBackendConfig:
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.3
    max_tokens: int = 4096
    api_key_env: str = "OPENAI_API_KEY"


@dataclass
class SkillBankConfig:
    storage: str = "local"
    path: str = "./skill_bank"
    max_skills: int = 1000
    dedup_strategy: str = "trigger_match"


@dataclass
class MemoryTierConfig:
    capacity: int = 500
    quality_threshold: float = 0.3
    distill_interval: int = 10
    max_patterns: int = 200
    promotion_threshold: float = 0.8
    max_rules: int = 50


@dataclass
class RetrievalConfig:
    top_k: int = 5
    recency_decay: float = 0.01
    tier_boosts: dict = field(default_factory=lambda: {
        "episodic": 1.0,
        "semantic": 1.2,
        "procedural": 1.5,
    })


@dataclass
class EvolutionConfig:
    max_rounds: int = 5
    surrogate_retries: int = 15
    convergence_threshold: float = 0.95
    context_cap: float = 0.7
    failure_trigger: int = 3


@dataclass
class EvaluationConfig:
    timeout_per_task: int = 300
    parallel_workers: int = 4
    num_seeds: int = 5
    metrics: list = field(default_factory=lambda: [
        "pass_rate", "correctness_score", "evolution_efficiency", "token_cost"
    ])


@dataclass
class SkillConfig:
    llm_backend: LLMBackendConfig = field(default_factory=LLMBackendConfig)
    skill_bank: SkillBankConfig = field(default_factory=SkillBankConfig)
    memory: MemoryTierConfig = field(default_factory=MemoryTierConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    evolution: EvolutionConfig = field(default_factory=EvolutionConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)

    @classmethod
    def from_yaml(cls, path: str) -> "SkillConfig":
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        config = cls()
        if "llm_backend" in data:
            config.llm_backend = LLMBackendConfig(**data["llm_backend"])
        if "skill_bank" in data:
            config.skill_bank = SkillBankConfig(**data["skill_bank"])
        if "evolution" in data:
            config.evolution = EvolutionConfig(**data["evolution"])
        return config

    @classmethod
    def from_dict(cls, data: dict) -> "SkillConfig":
        config = cls()
        if "llm_backend" in data:
            config.llm_backend = LLMBackendConfig(**data["llm_backend"])
        if "skill_bank" in data:
            config.skill_bank = SkillBankConfig(**data["skill_bank"])
        if "evolution" in data:
            config.evolution = EvolutionConfig(**data["evolution"])
        return config
