"""Agentic Platform Integration — Tools, Agents, Events, and MCP support.

This module provides the bridge between SkillForge and external agent
orchestration frameworks (LangChain, AutoGen, CrewAI, Semantic Kernel,
VS Code Copilot agents, etc.).

Integration patterns:
    1. Tool Registration — expose SkillForge functions as agent tools
    2. Sub-Agent Delegation — provide SkillForge agents to orchestrators
    3. Event-Driven — subscribe to lifecycle events
    4. MCP Server — Model Context Protocol for VS Code agents
"""

from skillforge.agentic.tools import SkillForgeTool, create_tools
from skillforge.agentic.provider import SkillForgeAgentProvider
from skillforge.agentic.events import SkillForgeEventBus

__all__ = [
    "SkillForgeTool",
    "create_tools",
    "SkillForgeAgentProvider",
    "SkillForgeEventBus",
]
