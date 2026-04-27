"""LLM Middleware: Transparent skill augmentation for LLM pipelines."""

from typing import Any, Callable, Optional
import functools


class LLMMiddleware:
    """Middleware that intercepts LLM calls to inject skill context.

    Usage:
        middleware = LLMMiddleware(forge=forge)

        @middleware.enhance
        def process_query(query: str) -> str:
            return llm.generate(query)
    """

    def __init__(self, forge: Any, config: Optional[dict] = None):
        self.forge = forge
        self.config = config or {}
        self._auto_detect = self.config.get("auto_detect_domain", True)
        self._context_budget = self.config.get("context_budget", 4096)
        self._top_k = self.config.get("retrieval_top_k", 3)
        self._inject_position = self.config.get("inject_position", "system")
        self._outcome_log: list[dict] = []

    def enhance(self, func: Callable) -> Callable:
        """Decorator that wraps an LLM call with skill augmentation."""
        @functools.wraps(func)
        def wrapper(query: str, *args, **kwargs) -> Any:
            augmented_query = self.augment(query)
            result = func(augmented_query, *args, **kwargs)
            return result
        return wrapper

    def augment(self, query: str) -> str:
        """Augment a query with relevant skill context from the Skill Bank.

        Args:
            query: The original user query or prompt.

        Returns:
            The augmented query with skill context injected.
        """
        skills = self.forge.skill_bank.retrieve(
            query=query,
            top_k=self._top_k,
            min_accuracy=0.5,
        )

        if not skills:
            return query

        # Build skill context within token budget
        skill_context_parts = []
        total_chars = 0
        char_budget = self._context_budget * 4  # rough token-to-char ratio

        for skill in skills:
            context = skill.to_prompt_context()
            if total_chars + len(context) > char_budget:
                break
            skill_context_parts.append(context)
            total_chars += len(context)

        if not skill_context_parts:
            return query

        skill_context = "\n\n".join(skill_context_parts)

        if self._inject_position == "system":
            return f"[Skill Context]\n{skill_context}\n[End Skill Context]\n\n{query}"
        elif self._inject_position == "user_prefix":
            return f"{skill_context}\n\n{query}"
        elif self._inject_position == "few_shot":
            return f"Here are relevant examples and strategies:\n{skill_context}\n\nNow answer:\n{query}"
        else:
            return f"{query}\n\n{skill_context}"

    def record_outcome(self, query: str, response: str, success: bool = True):
        """Record the outcome of an augmented LLM call for learning."""
        self._outcome_log.append({
            "query": query[:200],
            "response_length": len(response),
            "success": success,
        })

        if success:
            self.forge.memory.record_success(
                {"instruction": query},
                None,
                {"response": response[:500]},
            )
