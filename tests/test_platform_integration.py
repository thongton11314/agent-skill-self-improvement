"""Tests for cross-platform integration — VS Code Copilot, Claude, Codex.

Validates that all platform integration files exist, have correct formats,
contain required fields, and are consistent across platforms.
"""

import os
import re
import unittest
from pathlib import Path


# Repo root — resolve from this test file's location
REPO_ROOT = Path(__file__).resolve().parent.parent


def _parse_yaml_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter from a markdown file.

    Returns a dict of key-value pairs parsed from the --- delimited block.
    Only handles simple scalar and list values (no nested objects).
    """
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    frontmatter = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            # Strip surrounding quotes
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            # Parse inline lists: [a, b, c]
            if value.startswith("[") and value.endswith("]"):
                value = [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
            frontmatter[key] = value
    return frontmatter


def _read_file_text(filepath: Path) -> str:
    """Read a file as UTF-8 text."""
    return filepath.read_text(encoding="utf-8")


# ============================================================
# VS Code Copilot Chat — Agents
# ============================================================
class TestVSCodeCopilotAgents(unittest.TestCase):
    """Validate .github/agents/*.agent.md files."""

    AGENTS_DIR = REPO_ROOT / ".github" / "agents"
    EXPECTED_AGENTS = [
        "skillforge-evolver.agent.md",
        "skillforge-retriever.agent.md",
        "skillforge-evaluator.agent.md",
    ]

    def test_agents_directory_exists(self):
        self.assertTrue(self.AGENTS_DIR.is_dir(), ".github/agents/ directory must exist")

    def test_all_agent_files_exist(self):
        for filename in self.EXPECTED_AGENTS:
            filepath = self.AGENTS_DIR / filename
            self.assertTrue(filepath.is_file(), f"Missing agent file: {filename}")

    def test_agent_files_have_yaml_frontmatter(self):
        for filename in self.EXPECTED_AGENTS:
            filepath = self.AGENTS_DIR / filename
            fm = _parse_yaml_frontmatter(filepath)
            self.assertTrue(len(fm) > 0, f"{filename} must have YAML frontmatter")

    def test_agent_files_have_required_fields(self):
        """Each .agent.md must have: description, name, tools."""
        for filename in self.EXPECTED_AGENTS:
            filepath = self.AGENTS_DIR / filename
            fm = _parse_yaml_frontmatter(filepath)
            for field in ("description", "name", "tools"):
                self.assertIn(field, fm, f"{filename} missing required field: {field}")

    def test_agent_descriptions_contain_trigger_phrases(self):
        """Descriptions must contain 'Use when:' for agent discovery."""
        for filename in self.EXPECTED_AGENTS:
            filepath = self.AGENTS_DIR / filename
            fm = _parse_yaml_frontmatter(filepath)
            desc = fm.get("description", "")
            self.assertIn("Use when:", desc,
                          f"{filename} description must contain 'Use when:' for discovery")

    def test_agent_tools_are_valid_aliases(self):
        """Tools must be valid Copilot tool aliases."""
        valid_aliases = {"execute", "read", "edit", "search", "agent", "web", "todo"}
        for filename in self.EXPECTED_AGENTS:
            filepath = self.AGENTS_DIR / filename
            fm = _parse_yaml_frontmatter(filepath)
            tools = fm.get("tools", [])
            if isinstance(tools, str):
                tools = [tools]
            for tool in tools:
                self.assertIn(tool, valid_aliases,
                              f"{filename} has invalid tool alias: {tool}")

    def test_agent_body_not_empty(self):
        """Agent files must have meaningful body content after frontmatter."""
        for filename in self.EXPECTED_AGENTS:
            filepath = self.AGENTS_DIR / filename
            text = _read_file_text(filepath)
            # Remove frontmatter
            body = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL).strip()
            self.assertGreater(len(body), 100,
                               f"{filename} body too short — must contain agent instructions")

    def test_agent_names_are_unique(self):
        names = set()
        for filename in self.EXPECTED_AGENTS:
            filepath = self.AGENTS_DIR / filename
            fm = _parse_yaml_frontmatter(filepath)
            name = fm.get("name", "")
            self.assertNotIn(name, names, f"Duplicate agent name: {name}")
            names.add(name)


# ============================================================
# VS Code Copilot Chat — Skills
# ============================================================
class TestVSCodeCopilotSkills(unittest.TestCase):
    """Validate .github/skills/*/SKILL.md files."""

    SKILLS_DIR = REPO_ROOT / ".github" / "skills"
    EXPECTED_SKILLS = [
        "skillforge-evolve",
        "skillforge-retrieve",
        "skillforge-evaluate",
    ]

    def test_skills_directory_exists(self):
        self.assertTrue(self.SKILLS_DIR.is_dir(), ".github/skills/ directory must exist")

    def test_all_skill_folders_exist(self):
        for skill_name in self.EXPECTED_SKILLS:
            skill_dir = self.SKILLS_DIR / skill_name
            self.assertTrue(skill_dir.is_dir(), f"Missing skill folder: {skill_name}/")

    def test_all_skill_files_exist(self):
        for skill_name in self.EXPECTED_SKILLS:
            skill_file = self.SKILLS_DIR / skill_name / "SKILL.md"
            self.assertTrue(skill_file.is_file(), f"Missing SKILL.md in {skill_name}/")

    def test_skill_frontmatter_has_required_fields(self):
        """Each SKILL.md must have: name, description."""
        for skill_name in self.EXPECTED_SKILLS:
            filepath = self.SKILLS_DIR / skill_name / "SKILL.md"
            fm = _parse_yaml_frontmatter(filepath)
            for field in ("name", "description"):
                self.assertIn(field, fm, f"{skill_name}/SKILL.md missing field: {field}")

    def test_skill_name_matches_folder(self):
        """The name field in frontmatter must match the folder name."""
        for skill_name in self.EXPECTED_SKILLS:
            filepath = self.SKILLS_DIR / skill_name / "SKILL.md"
            fm = _parse_yaml_frontmatter(filepath)
            self.assertEqual(fm.get("name"), skill_name,
                             f"Folder '{skill_name}' but name field is '{fm.get('name')}'")

    def test_skill_descriptions_nonempty(self):
        for skill_name in self.EXPECTED_SKILLS:
            filepath = self.SKILLS_DIR / skill_name / "SKILL.md"
            fm = _parse_yaml_frontmatter(filepath)
            desc = fm.get("description", "")
            self.assertGreater(len(desc), 20,
                               f"{skill_name}/SKILL.md description too short for discovery")

    def test_skill_body_has_procedure(self):
        """Skill body must contain step-by-step procedures."""
        for skill_name in self.EXPECTED_SKILLS:
            filepath = self.SKILLS_DIR / skill_name / "SKILL.md"
            text = _read_file_text(filepath)
            body = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)
            self.assertIn("## ", body,
                          f"{skill_name}/SKILL.md must have section headings")
            self.assertIn("```python", body,
                          f"{skill_name}/SKILL.md must include Python code examples")


# ============================================================
# Claude — CLAUDE.md + .claude/skills/
# ============================================================
class TestClaudePlatform(unittest.TestCase):
    """Validate CLAUDE.md and .claude/skills/*/SKILL.md files."""

    CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
    CLAUDE_SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
    EXPECTED_SKILLS = [
        "skillforge-evolve",
        "skillforge-retrieve",
        "skillforge-evaluate",
    ]

    def test_claude_md_exists(self):
        self.assertTrue(self.CLAUDE_MD.is_file(), "CLAUDE.md must exist at repo root")

    def test_claude_md_has_project_overview(self):
        text = _read_file_text(self.CLAUDE_MD)
        self.assertIn("SkillForge", text)
        self.assertIn("## Project Overview", text)

    def test_claude_md_has_architecture_section(self):
        text = _read_file_text(self.CLAUDE_MD)
        self.assertIn("## Architecture", text)

    def test_claude_md_has_key_files_section(self):
        text = _read_file_text(self.CLAUDE_MD)
        self.assertIn("## Key Files", text)
        self.assertIn("AGENTS.md", text)
        self.assertIn("wiki/index.md", text)

    def test_claude_md_has_conventions(self):
        text = _read_file_text(self.CLAUDE_MD)
        self.assertIn("## Development Conventions", text)
        self.assertIn("pytest", text)

    def test_claude_md_has_common_tasks(self):
        text = _read_file_text(self.CLAUDE_MD)
        self.assertIn("## Common Tasks", text)
        self.assertIn("evolve_skill", text)

    def test_claude_md_references_skills(self):
        text = _read_file_text(self.CLAUDE_MD)
        self.assertIn(".claude/skills/", text)

    def test_claude_skills_directory_exists(self):
        self.assertTrue(self.CLAUDE_SKILLS_DIR.is_dir(),
                        ".claude/skills/ directory must exist")

    def test_all_claude_skill_folders_exist(self):
        for skill_name in self.EXPECTED_SKILLS:
            skill_dir = self.CLAUDE_SKILLS_DIR / skill_name
            self.assertTrue(skill_dir.is_dir(),
                            f"Missing .claude/skills/{skill_name}/")

    def test_all_claude_skill_files_exist(self):
        for skill_name in self.EXPECTED_SKILLS:
            filepath = self.CLAUDE_SKILLS_DIR / skill_name / "SKILL.md"
            self.assertTrue(filepath.is_file(),
                            f"Missing .claude/skills/{skill_name}/SKILL.md")

    def test_claude_skill_frontmatter(self):
        for skill_name in self.EXPECTED_SKILLS:
            filepath = self.CLAUDE_SKILLS_DIR / skill_name / "SKILL.md"
            fm = _parse_yaml_frontmatter(filepath)
            self.assertIn("name", fm, f".claude/{skill_name} missing 'name'")
            self.assertIn("description", fm, f".claude/{skill_name} missing 'description'")

    def test_claude_skill_name_matches_folder(self):
        for skill_name in self.EXPECTED_SKILLS:
            filepath = self.CLAUDE_SKILLS_DIR / skill_name / "SKILL.md"
            fm = _parse_yaml_frontmatter(filepath)
            self.assertEqual(fm.get("name"), skill_name,
                             f".claude folder '{skill_name}' but name is '{fm.get('name')}'")


# ============================================================
# Codex — AGENTS.md
# ============================================================
class TestCodexPlatform(unittest.TestCase):
    """Validate AGENTS.md is readable and complete for Codex."""

    AGENTS_MD = REPO_ROOT / "AGENTS.md"

    def test_agents_md_exists(self):
        self.assertTrue(self.AGENTS_MD.is_file(), "AGENTS.md must exist at repo root")

    def test_agents_md_has_purpose(self):
        text = _read_file_text(self.AGENTS_MD)
        self.assertIn("## Purpose", text)

    def test_agents_md_has_directory_structure(self):
        text = _read_file_text(self.AGENTS_MD)
        self.assertIn("## Directory Structure", text)
        self.assertIn("skillforge/", text)

    def test_agents_md_has_agent_interfaces(self):
        text = _read_file_text(self.AGENTS_MD)
        self.assertIn("## SkillForge Agent Interfaces", text)
        self.assertIn("skillforge.evolver", text)
        self.assertIn("skillforge.retriever", text)
        self.assertIn("skillforge.evaluator", text)

    def test_agents_md_has_platform_integration(self):
        text = _read_file_text(self.AGENTS_MD)
        self.assertIn("## Platform Integration", text)

    def test_agents_md_references_all_platforms(self):
        text = _read_file_text(self.AGENTS_MD)
        self.assertIn("VS Code Copilot Chat", text)
        self.assertIn("Claude Code", text)
        self.assertIn("OpenAI Codex", text)

    def test_agents_md_has_workflows(self):
        text = _read_file_text(self.AGENTS_MD)
        self.assertIn("## Workflows", text)

    def test_agents_md_has_guiding_principles(self):
        text = _read_file_text(self.AGENTS_MD)
        self.assertIn("## Guiding Principles", text)


# ============================================================
# Cross-platform skill definitions (skills/)
# ============================================================
class TestCrossPlatformSkills(unittest.TestCase):
    """Validate skills/ directory — framework-agnostic skill definitions."""

    SKILLS_DIR = REPO_ROOT / "skills"
    EXPECTED_FILES = [
        "evolve-skill.md",
        "retrieve-and-apply.md",
        "evaluate-skills.md",
    ]

    def test_skills_directory_exists(self):
        self.assertTrue(self.SKILLS_DIR.is_dir(), "skills/ directory must exist")

    def test_all_cross_platform_skill_files_exist(self):
        for filename in self.EXPECTED_FILES:
            filepath = self.SKILLS_DIR / filename
            self.assertTrue(filepath.is_file(), f"Missing cross-platform skill: {filename}")

    def test_cross_platform_skills_have_frontmatter(self):
        for filename in self.EXPECTED_FILES:
            filepath = self.SKILLS_DIR / filename
            fm = _parse_yaml_frontmatter(filepath)
            self.assertIn("name", fm, f"{filename} missing 'name' in frontmatter")
            self.assertIn("description", fm, f"{filename} missing 'description' in frontmatter")

    def test_cross_platform_skills_have_agent_id(self):
        """Cross-platform skills reference their backing agent."""
        for filename in self.EXPECTED_FILES:
            filepath = self.SKILLS_DIR / filename
            fm = _parse_yaml_frontmatter(filepath)
            self.assertIn("agent_id", fm, f"{filename} missing 'agent_id'")
            self.assertTrue(fm["agent_id"].startswith("skillforge."),
                            f"{filename} agent_id should start with 'skillforge.'")


# ============================================================
# Cross-platform consistency
# ============================================================
class TestCrossPlatformConsistency(unittest.TestCase):
    """Verify skills are consistent across all three platforms."""

    COPILOT_SKILLS = REPO_ROOT / ".github" / "skills"
    CLAUDE_SKILLS = REPO_ROOT / ".claude" / "skills"
    SKILL_PAIRS = [
        ("skillforge-evolve", "skillforge-evolve"),
        ("skillforge-retrieve", "skillforge-retrieve"),
        ("skillforge-evaluate", "skillforge-evaluate"),
    ]

    def test_same_skills_exist_on_both_platforms(self):
        """Copilot and Claude must have the same set of skills."""
        copilot_skills = {d.name for d in self.COPILOT_SKILLS.iterdir() if d.is_dir()}
        claude_skills = {d.name for d in self.CLAUDE_SKILLS.iterdir() if d.is_dir()}
        self.assertEqual(copilot_skills, claude_skills,
                         "Copilot and Claude skill sets must match")

    def test_skill_names_match_across_platforms(self):
        """The 'name' field must match across Copilot and Claude for each skill."""
        for copilot_name, claude_name in self.SKILL_PAIRS:
            copilot_fm = _parse_yaml_frontmatter(
                self.COPILOT_SKILLS / copilot_name / "SKILL.md"
            )
            claude_fm = _parse_yaml_frontmatter(
                self.CLAUDE_SKILLS / claude_name / "SKILL.md"
            )
            self.assertEqual(copilot_fm.get("name"), claude_fm.get("name"),
                             f"Name mismatch: Copilot={copilot_fm.get('name')} "
                             f"vs Claude={claude_fm.get('name')}")

    def test_skill_descriptions_match_across_platforms(self):
        """Descriptions should be identical across platforms."""
        for copilot_name, claude_name in self.SKILL_PAIRS:
            copilot_fm = _parse_yaml_frontmatter(
                self.COPILOT_SKILLS / copilot_name / "SKILL.md"
            )
            claude_fm = _parse_yaml_frontmatter(
                self.CLAUDE_SKILLS / claude_name / "SKILL.md"
            )
            self.assertEqual(copilot_fm.get("description"), claude_fm.get("description"),
                             f"Description mismatch for skill '{copilot_name}' "
                             f"between Copilot and Claude")

    def test_all_platforms_cover_evolve_retrieve_evaluate(self):
        """Every platform must cover the three core workflows: evolve, retrieve, evaluate."""
        # Copilot agents
        copilot_agents = REPO_ROOT / ".github" / "agents"
        agent_names = {f.stem.replace(".agent", "") for f in copilot_agents.glob("*.agent.md")}
        for keyword in ("evolver", "retriever", "evaluator"):
            self.assertTrue(
                any(keyword in name for name in agent_names),
                f"Copilot agents missing '{keyword}' agent"
            )

        # Copilot skills
        copilot_skill_names = {d.name for d in self.COPILOT_SKILLS.iterdir() if d.is_dir()}
        for keyword in ("evolve", "retrieve", "evaluate"):
            self.assertTrue(
                any(keyword in name for name in copilot_skill_names),
                f"Copilot skills missing '{keyword}' skill"
            )

        # Claude skills
        claude_skill_names = {d.name for d in self.CLAUDE_SKILLS.iterdir() if d.is_dir()}
        for keyword in ("evolve", "retrieve", "evaluate"):
            self.assertTrue(
                any(keyword in name for name in claude_skill_names),
                f"Claude skills missing '{keyword}' skill"
            )

        # Codex — AGENTS.md must reference all three
        agents_md = _read_file_text(REPO_ROOT / "AGENTS.md")
        for agent_id in ("skillforge.evolver", "skillforge.retriever", "skillforge.evaluator"):
            self.assertIn(agent_id, agents_md,
                          f"AGENTS.md missing reference to {agent_id}")

    def test_copilot_instructions_reference_key_files(self):
        """copilot-instructions.md must reference AGENTS.md and wiki."""
        filepath = REPO_ROOT / ".github" / "copilot-instructions.md"
        self.assertTrue(filepath.is_file())
        text = _read_file_text(filepath)
        self.assertIn("AGENTS.md", text)
        self.assertIn("wiki/index.md", text)

    def test_claude_md_references_agent_architecture(self):
        """CLAUDE.md must list the 5 discoverable agents."""
        text = _read_file_text(REPO_ROOT / "CLAUDE.md")
        for agent_id in ("skillforge.evolver", "skillforge.retriever",
                          "skillforge.executor", "skillforge.evaluator",
                          "skillforge.memory"):
            self.assertIn(agent_id, text,
                          f"CLAUDE.md missing agent reference: {agent_id}")


# ============================================================
# Copilot instructions coherence
# ============================================================
class TestCopilotInstructions(unittest.TestCase):
    """Validate .github/copilot-instructions.md is complete."""

    FILEPATH = REPO_ROOT / ".github" / "copilot-instructions.md"

    def test_file_exists(self):
        self.assertTrue(self.FILEPATH.is_file())

    def test_has_post_change_pipeline(self):
        text = _read_file_text(self.FILEPATH)
        self.assertIn("Post-Change Pipeline", text)

    def test_has_core_rules(self):
        text = _read_file_text(self.FILEPATH)
        self.assertIn("Core Rules", text)

    def test_references_wiki(self):
        text = _read_file_text(self.FILEPATH)
        self.assertIn("wiki/", text)


# ============================================================
# Integration with SkillForge runtime
# ============================================================
class TestRuntimeIntegrationAlignment(unittest.TestCase):
    """Ensure platform files reference actual SkillForge runtime components."""

    def setUp(self):
        from skillforge.config import SkillConfig
        from skillforge.core.forge import SkillForge
        from skillforge.agentic.provider import SkillForgeAgentProvider
        from skillforge.agentic.tools import create_tools

        self.forge = SkillForge()
        self.provider = SkillForgeAgentProvider(self.forge)
        self.tools = create_tools(self.forge)

    def test_agent_ids_match_runtime(self):
        """Agent IDs in platform files match the runtime provider."""
        runtime_ids = set(self.provider.list_agent_ids())
        expected = {
            "skillforge.evolver",
            "skillforge.retriever",
            "skillforge.executor",
            "skillforge.evaluator",
            "skillforge.memory",
        }
        self.assertEqual(runtime_ids, expected)

    def test_tool_count_matches_runtime(self):
        """Platform files claim 5 tools — runtime must produce 5."""
        self.assertEqual(len(self.tools), 5)

    def test_tool_names_match_runtime(self):
        """Tools referenced in platform docs must exist at runtime."""
        runtime_names = {t.name for t in self.tools}
        expected_names = {
            "skillforge_evolve_skill",
            "skillforge_find_skill",
            "skillforge_run_with_skill",
            "skillforge_evaluate",
            "skillforge_query_memory",
        }
        self.assertEqual(runtime_names, expected_names)

    def test_agents_md_agent_ids_match_runtime(self):
        """AGENTS.md agent table must list exactly the runtime agents."""
        text = _read_file_text(REPO_ROOT / "AGENTS.md")
        runtime_ids = self.provider.list_agent_ids()
        for agent_id in runtime_ids:
            self.assertIn(agent_id, text,
                          f"AGENTS.md missing runtime agent: {agent_id}")

    def test_claude_md_agent_ids_match_runtime(self):
        """CLAUDE.md agent table must list exactly the runtime agents."""
        text = _read_file_text(REPO_ROOT / "CLAUDE.md")
        runtime_ids = self.provider.list_agent_ids()
        for agent_id in runtime_ids:
            self.assertIn(agent_id, text,
                          f"CLAUDE.md missing runtime agent: {agent_id}")


if __name__ == "__main__":
    unittest.main()
