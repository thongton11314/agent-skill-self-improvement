"""Synthetic Test Case Generator."""

from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class TestCase:
    """A synthetic test case."""
    test_id: str
    task_id: str
    test_type: str
    description: str
    assertions: list = field(default_factory=list)
    expected_outcome: str = "pass"
    difficulty: str = "medium"

    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "task_id": self.task_id,
            "test_type": self.test_type,
            "description": self.description,
            "assertions": self.assertions,
            "expected_outcome": self.expected_outcome,
            "difficulty": self.difficulty,
        }


class SyntheticTestGenerator:
    """Generates synthetic test cases without human annotation.

    Strategies:
        - instruction_derived: Parse instructions to extract testable requirements
        - output_probe: Analyze outputs to generate edge-case probes
        - metamorphic: Apply input transformations with predictable output changes
        - adversarial: Generate challenging inputs that probe robustness
        - regression: Store outputs from passing versions for backward compatibility
    """

    def __init__(
        self,
        domain: str = "general",
        strategies: Optional[list[str]] = None,
    ):
        self.domain = domain
        self.strategies = strategies or [
            "instruction_derived", "output_probe", "metamorphic", "adversarial"
        ]

    def generate(
        self,
        task_specs: list[dict],
        num_cases_per_task: int = 10,
        difficulty_distribution: Optional[dict] = None,
    ) -> list[TestCase]:
        """Generate synthetic test cases for a set of task specifications.

        Args:
            task_specs: List of task definitions with 'task_id' and 'instruction'.
            num_cases_per_task: Number of test cases to generate per task.
            difficulty_distribution: Dict mapping difficulty levels to proportions.

        Returns:
            List of generated TestCase objects.
        """
        difficulty_dist = difficulty_distribution or {"easy": 0.3, "medium": 0.5, "hard": 0.2}
        all_tests = []

        for task_spec in task_specs:
            task_id = task_spec.get("task_id", f"task-{len(all_tests):04d}")
            instruction = task_spec.get("instruction", "")

            for i in range(num_cases_per_task):
                # Select strategy round-robin
                strategy = self.strategies[i % len(self.strategies)]

                # Select difficulty
                difficulty = self._sample_difficulty(difficulty_dist, i, num_cases_per_task)

                test = self._generate_single(task_id, instruction, strategy, difficulty, i)
                all_tests.append(test)

        return all_tests

    def _generate_single(
        self, task_id: str, instruction: str, strategy: str, difficulty: str, index: int
    ) -> TestCase:
        """Generate a single test case."""
        generators = {
            "instruction_derived": self._gen_instruction_derived,
            "output_probe": self._gen_output_probe,
            "metamorphic": self._gen_metamorphic,
            "adversarial": self._gen_adversarial,
            "regression": self._gen_regression,
        }

        generator = generators.get(strategy, self._gen_instruction_derived)
        return generator(task_id, instruction, difficulty, index)

    def _gen_instruction_derived(
        self, task_id: str, instruction: str, difficulty: str, index: int
    ) -> TestCase:
        """Parse instructions to extract testable requirements."""
        return TestCase(
            test_id=f"TST-ID-{task_id}-{index:03d}",
            task_id=task_id,
            test_type="instruction_derived",
            description=f"Verify task output meets instruction requirement #{index + 1}",
            assertions=[{
                "assertion_id": f"A{index + 1}",
                "type": "content_match",
                "condition": f"Output satisfies requirement from instruction",
                "severity": "critical" if difficulty == "hard" else "major",
            }],
            difficulty=difficulty,
        )

    def _gen_output_probe(
        self, task_id: str, instruction: str, difficulty: str, index: int
    ) -> TestCase:
        """Analyze outputs to generate edge-case probes."""
        return TestCase(
            test_id=f"TST-OP-{task_id}-{index:03d}",
            task_id=task_id,
            test_type="output_probe",
            description=f"Probe output format and structure",
            assertions=[{
                "assertion_id": f"A{index + 1}",
                "type": "schema_valid",
                "condition": "Output conforms to expected schema",
                "severity": "major",
            }],
            difficulty=difficulty,
        )

    def _gen_metamorphic(
        self, task_id: str, instruction: str, difficulty: str, index: int
    ) -> TestCase:
        """Apply input transformations with predictable output changes."""
        return TestCase(
            test_id=f"TST-MM-{task_id}-{index:03d}",
            task_id=task_id,
            test_type="metamorphic",
            description=f"Verify behavior consistency under input transformation",
            assertions=[{
                "assertion_id": f"A{index + 1}",
                "type": "invariant",
                "condition": "Output relationship holds under transformation",
                "severity": "major",
            }],
            difficulty=difficulty,
        )

    def _gen_adversarial(
        self, task_id: str, instruction: str, difficulty: str, index: int
    ) -> TestCase:
        """Generate challenging inputs that probe robustness."""
        return TestCase(
            test_id=f"TST-ADV-{task_id}-{index:03d}",
            task_id=task_id,
            test_type="adversarial",
            description=f"Test robustness against adversarial input",
            assertions=[{
                "assertion_id": f"A{index + 1}",
                "type": "error_handling",
                "condition": "Skill handles malformed input gracefully",
                "severity": "critical",
            }],
            difficulty="hard",
        )

    def _gen_regression(
        self, task_id: str, instruction: str, difficulty: str, index: int
    ) -> TestCase:
        """Store passing outputs for backward compatibility."""
        return TestCase(
            test_id=f"TST-REG-{task_id}-{index:03d}",
            task_id=task_id,
            test_type="regression",
            description=f"Verify backward compatibility with previous outputs",
            assertions=[{
                "assertion_id": f"A{index + 1}",
                "type": "output_match",
                "condition": "Output matches previously verified result",
                "severity": "major",
            }],
            difficulty=difficulty,
        )

    def _sample_difficulty(self, dist: dict, index: int, total: int) -> str:
        """Sample a difficulty level based on distribution."""
        pos = index / max(total - 1, 1)
        if pos < dist.get("easy", 0.3):
            return "easy"
        elif pos < dist.get("easy", 0.3) + dist.get("medium", 0.5):
            return "medium"
        return "hard"

    def save(self, test_cases: list[TestCase], path: str):
        """Save test cases to JSON file."""
        data = [tc.to_dict() for tc in test_cases]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
