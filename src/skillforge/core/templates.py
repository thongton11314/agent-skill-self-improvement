"""Domain-specific skill templates for common task categories.

Provides pre-configured skill scaffolds that accelerate evolution
by giving the Skill Generator a domain-aware starting point.
"""

from typing import Optional
from skillforge.core.skill_bank import Skill


# Template registry
_TEMPLATES: dict[str, dict] = {
    "software_engineering": {
        "trigger_prefix": "Software engineering task:",
        "strategy_template": """# Software Engineering Skill

## Workflow
1. Parse requirements and identify sub-tasks
2. Design the module structure (files, classes, functions)
3. Implement core logic with error handling
4. Add input validation at system boundaries
5. Write output in the expected format
6. Run self-checks (imports resolve, no syntax errors, edge cases handled)

## Constraints
- Follow language idioms and conventions
- Handle file I/O errors (missing files, permissions, encoding)
- Validate all external inputs
- Use structured logging, not print statements
- Ensure outputs match the exact format specification

## Common Pitfalls
- Off-by-one errors in iteration and indexing
- Not closing file handles (use context managers)
- Hardcoding paths instead of using parameters
- Missing error handling for network/filesystem operations
""",
        "default_tools": ["python", "json", "os", "sys"],
    },
    "data_analysis": {
        "trigger_prefix": "Data analysis task:",
        "strategy_template": """# Data Analysis Skill

## Workflow
1. Load and inspect data (shape, dtypes, nulls, sample rows)
2. Clean data (handle missing values, fix types, remove duplicates)
3. Perform the requested analysis or computation
4. Validate results (sanity checks, expected ranges, no NaN in output)
5. Format output as specified (CSV, JSON, report)

## Constraints
- Always inspect data before processing — never assume schema
- Handle missing/null values explicitly (drop, fill, or flag)
- Use vectorized operations over row-by-row iteration
- Round numeric outputs to appropriate precision
- Include column headers in all tabular outputs

## Common Pitfalls
- Timezone issues when parsing dates
- Integer overflow with large aggregations
- Division by zero in ratio calculations
- Losing data types during merge/join operations
""",
        "default_tools": ["python", "pandas", "numpy"],
    },
    "scientific_computing": {
        "trigger_prefix": "Scientific computing task:",
        "strategy_template": """# Scientific Computing Skill

## Workflow
1. Define the mathematical model and parameters
2. Choose the appropriate numerical method
3. Implement with numerical stability in mind
4. Validate against known analytical solutions or reference values
5. Report results with precision matching requirements

## Constraints
- Use numerically stable algorithms (avoid catastrophic cancellation)
- Validate convergence for iterative methods
- Report precision: match the required decimal places exactly
- Handle edge cases (singular matrices, division by zero, overflow)
- Compare against reference implementations when available

## Common Pitfalls
- Floating point comparison with == instead of tolerance-based
- Not checking convergence criteria for iterative solvers
- Using insufficient grid resolution for numerical methods
- Ignoring numerical stability (e.g., naive matrix inversion)
""",
        "default_tools": ["python", "numpy", "scipy"],
    },
    "web_development": {
        "trigger_prefix": "Web development task:",
        "strategy_template": """# Web Development Skill

## Workflow
1. Plan the page/component structure
2. Implement HTML with semantic elements
3. Add CSS styling (responsive, accessible)
4. Add JavaScript for interactivity (if needed)
5. Validate: valid HTML5, no console errors, responsive layout

## Constraints
- Use semantic HTML elements (header, nav, main, article, footer)
- Ensure responsive design (mobile-first or desktop-first with breakpoints)
- Escape user inputs to prevent XSS
- Use relative units (rem, em, %) over absolute (px) where appropriate
- Ensure keyboard accessibility for interactive elements

## Common Pitfalls
- Not escaping special characters in dynamic content
- Missing viewport meta tag for mobile
- CSS specificity conflicts
- Event listeners on dynamically created elements
""",
        "default_tools": ["html", "css", "javascript"],
    },
    "system_administration": {
        "trigger_prefix": "System administration task:",
        "strategy_template": """# System Administration Skill

## Workflow
1. Identify the system resources or processes to monitor/manage
2. Implement data collection (filesystem, processes, network, logs)
3. Apply the analysis or transformation logic
4. Format output as structured data (JSON, CSV)
5. Add error handling for permission and access issues

## Constraints
- Handle permission errors gracefully (don't crash on access denied)
- Use cross-platform approaches where possible
- Log timestamps in ISO 8601 format
- Validate paths and inputs before operations
- Never modify system state unless explicitly requested

## Common Pitfalls
- Assuming Unix paths on Windows (or vice versa)
- Not handling processes that exit during monitoring
- Race conditions when reading rapidly changing files
- Insufficient permissions for system-level operations
""",
        "default_tools": ["python", "os", "shutil", "json", "subprocess"],
    },
}


def get_template(domain: str) -> Optional[dict]:
    """Get a domain-specific skill template.

    Args:
        domain: Domain name (e.g., 'software_engineering', 'data_analysis').

    Returns:
        Template dict with trigger_prefix, strategy_template, and default_tools.
        None if domain not found.
    """
    return _TEMPLATES.get(domain)


def list_domains() -> list[str]:
    """List all available domain templates."""
    return list(_TEMPLATES.keys())


def create_from_template(domain: str, instruction: str, tools: Optional[list[str]] = None) -> Skill:
    """Create an initial skill from a domain template.

    This gives the Skill Generator a head start by providing
    domain-specific workflow structure, constraints, and pitfalls.

    Args:
        domain: Domain name.
        instruction: Task instruction.
        tools: Override tools list (uses template defaults if None).

    Returns:
        A Skill (v0) pre-populated with domain knowledge.
    """
    template = get_template(domain)
    if not template:
        # Fall back to generic
        return Skill(
            trigger_condition=instruction[:200],
            strategy=f"# Task\n{instruction}\n\n## Workflow\n1. Analyze requirements\n2. Implement\n3. Validate",
            accuracy=0.0,
            version=0,
            artifacts={"SKILL.md": f"# Skill\n{instruction}"},
        )

    strategy = f"{template['strategy_template']}\n\n## Task-Specific Notes\n{instruction[:500]}"
    tool_list = tools or template["default_tools"]

    return Skill(
        trigger_condition=f"{template['trigger_prefix']} {instruction[:180]}",
        strategy=strategy,
        accuracy=0.0,
        version=0,
        artifacts={
            "SKILL.md": strategy,
        },
    )
