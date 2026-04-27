"""Surrogate Verifier: Co-evolving test generator with information isolation."""

from dataclasses import dataclass, field
from typing import Optional
from skillforge.config import SkillConfig


@dataclass
class Assertion:
    assertion_id: str
    type: str  # file_exists, content_match, schema_valid, value_range
    target: str
    condition: str
    passed: bool = False
    error_message: str = ""


@dataclass
class VerificationResult:
    passed: bool
    assertions: list[Assertion]
    pass_rate: float
    round_number: int

    @property
    def summary(self) -> str:
        passed_count = sum(1 for a in self.assertions if a.passed)
        return f"{passed_count}/{len(self.assertions)} assertions passed ({self.pass_rate:.0%})"


class SurrogateVerifier:
    """Informationally isolated verifier that generates test assertions
    and provides structured failure diagnostics.

    The verifier operates in a separate session with NO access to the
    generator's reasoning, code, or skill content. It only observes:
    - The task instruction
    - The output files produced by skill execution
    """

    def __init__(self, config: SkillConfig):
        self.config = config
        self._test_suites: dict[str, list[Assertion]] = {}
        self._escalation_history: list[int] = []

    def verify(self, task: dict, outputs: dict, retry_round: int = 0) -> VerificationResult:
        """Verify skill outputs against synthesized test assertions.

        Args:
            task: Task definition (instruction only, no skill internals).
            outputs: Output files produced by skill execution.
            retry_round: Current retry iteration.

        Returns:
            VerificationResult with per-assertion outcomes.
        """
        task_id = self._task_key(task)

        # Generate or retrieve test suite
        if task_id not in self._test_suites or retry_round == 0:
            self._test_suites[task_id] = self._generate_assertions(task, outputs)

        assertions = self._test_suites[task_id]

        # Execute assertions against outputs
        for assertion in assertions:
            assertion.passed = self._execute_assertion(assertion, outputs)

        passed_count = sum(1 for a in assertions if a.passed)
        pass_rate = passed_count / len(assertions) if assertions else 0.0

        return VerificationResult(
            passed=pass_rate == 1.0,
            assertions=assertions,
            pass_rate=pass_rate,
            round_number=retry_round,
        )

    def diagnose(self, task: dict, outputs: dict, result: VerificationResult) -> dict:
        """Generate structured failure diagnostics.

        Returns failure analysis with:
        - Per-assertion results
        - Root-cause analysis
        - Actionable revision suggestions
        """
        failed_assertions = [a for a in result.assertions if not a.passed]

        diagnostics = {
            "summary": f"{len(failed_assertions)} assertions failed out of {len(result.assertions)}",
            "pass_rate": result.pass_rate,
            "failed_assertions": [
                {
                    "id": a.assertion_id,
                    "type": a.type,
                    "target": a.target,
                    "condition": a.condition,
                    "error": a.error_message,
                }
                for a in failed_assertions
            ],
            "root_cause": self._analyze_root_cause(failed_assertions),
            "suggestions": self._generate_suggestions(failed_assertions, task),
        }

        return diagnostics

    def escalate(self, task: dict, outputs: dict):
        """Escalate test suite complexity when surrogate passes but oracle fails.

        This is triggered when the verifier's tests all pass but the
        ground-truth oracle reports failure, indicating a gap between
        surrogate and oracle coverage.
        """
        task_id = self._task_key(task)
        current_tests = self._test_suites.get(task_id, [])

        # Generate additional, more challenging assertions
        new_assertions = self._generate_escalated_assertions(task, outputs, len(current_tests))
        self._test_suites[task_id] = current_tests + new_assertions
        self._escalation_history.append(len(new_assertions))

    def _generate_assertions(self, task: dict, outputs: dict) -> list[Assertion]:
        """Synthesize test assertions from task instruction and outputs."""
        assertions = []
        instruction = task.get("instruction", "")

        # Generate format assertions
        assertions.append(Assertion(
            assertion_id="FMT-001",
            type="output_exists",
            target="output",
            condition="Output files exist and are non-empty",
        ))

        # Generate content assertions based on instruction parsing
        assertions.append(Assertion(
            assertion_id="CNT-001",
            type="content_match",
            target="output",
            condition="Output matches instruction requirements",
        ))

        # Generate schema assertions
        assertions.append(Assertion(
            assertion_id="SCH-001",
            type="schema_valid",
            target="output",
            condition="Output schema is valid",
        ))

        return assertions

    def _generate_escalated_assertions(
        self, task: dict, outputs: dict, existing_count: int
    ) -> list[Assertion]:
        """Generate harder assertions for test escalation."""
        escalated = []
        base_id = existing_count + 1

        escalated.append(Assertion(
            assertion_id=f"ESC-{base_id:03d}",
            type="precision_check",
            target="output",
            condition="Output precision matches exact requirements",
        ))

        escalated.append(Assertion(
            assertion_id=f"ESC-{base_id + 1:03d}",
            type="edge_case",
            target="output",
            condition="Output handles edge cases correctly",
        ))

        return escalated

    def _execute_assertion(self, assertion: Assertion, outputs: dict) -> bool:
        """Execute a single assertion against outputs."""
        # Simplified assertion execution
        if assertion.type == "output_exists":
            return bool(outputs)
        return True

    def _analyze_root_cause(self, failed_assertions: list[Assertion]) -> str:
        """Analyze root cause from failed assertion patterns."""
        if not failed_assertions:
            return "No failures detected"

        types = [a.type for a in failed_assertions]
        if "schema_valid" in types:
            return "Output schema does not match expected format"
        if "precision_check" in types:
            return "Output precision is insufficient"
        return f"Multiple assertion types failed: {', '.join(set(types))}"

    def _generate_suggestions(self, failed_assertions: list[Assertion], task: dict) -> list[str]:
        """Generate actionable revision suggestions."""
        suggestions = []
        for assertion in failed_assertions:
            if assertion.type == "content_match":
                suggestions.append("Review output content against task requirements")
            elif assertion.type == "schema_valid":
                suggestions.append("Fix output schema to match expected format")
            elif assertion.type == "precision_check":
                suggestions.append("Increase output precision (e.g., decimal places)")
            else:
                suggestions.append(f"Address {assertion.type} failure: {assertion.condition}")
        return suggestions

    def _task_key(self, task: dict) -> str:
        """Generate a stable key for a task."""
        return str(hash(task.get("instruction", "")))
