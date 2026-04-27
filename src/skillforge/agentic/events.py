"""SkillForge Event Bus — Event-driven integration for agent orchestrators.

Allows external systems to subscribe to SkillForge lifecycle events
for reactive workflows (e.g., trigger re-evolution on failure,
notify dashboard on skill improvement).
"""

from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SkillForgeEvent:
    """A lifecycle event emitted by SkillForge."""
    event_type: str
    timestamp: str = ""
    data: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"


# Standard event types
EVENT_SKILL_EVOLVED = "skill.evolved"
EVENT_SKILL_STORED = "skill.stored"
EVENT_SKILL_RETRIEVED = "skill.retrieved"
EVENT_TASK_COMPLETED = "task.completed"
EVENT_TASK_FAILED = "task.failed"
EVENT_MEMORY_RECORDED = "memory.recorded"
EVENT_MEMORY_PROMOTED = "memory.promoted"
EVENT_VERIFIER_PASSED = "verifier.passed"
EVENT_VERIFIER_FAILED = "verifier.failed"
EVENT_ORACLE_PASSED = "oracle.passed"
EVENT_ORACLE_FAILED = "oracle.failed"
EVENT_EVOLUTION_TRIGGERED = "evolution.triggered"


class SkillForgeEventBus:
    """Event bus for SkillForge lifecycle events.

    Usage:
        bus = SkillForgeEventBus(forge=forge)

        @bus.on("skill.evolved")
        def handle_evolution(event):
            print(f"Skill evolved to v{event.data['version']}")

        @bus.on("task.failed")
        def handle_failure(event):
            # Trigger re-evolution or alert
            pass

        # Emit events from SkillForge operations
        bus.emit("skill.evolved", {"skill_id": "...", "version": 3, "accuracy": 0.85})
    """

    def __init__(self, forge: Any = None):
        self.forge = forge
        self._handlers: dict[str, list[Callable]] = {}

    def on(self, event_type: str) -> Callable:
        """Decorator to register an event handler.

        Args:
            event_type: Event type to subscribe to (e.g., "skill.evolved").

        Returns:
            Decorator function.
        """
        def decorator(func: Callable) -> Callable:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(func)
            return func
        return decorator

    def subscribe(self, event_type: str, handler: Callable):
        """Programmatically subscribe a handler to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable):
        """Remove a handler from an event type."""
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h is not handler
            ]

    def emit(self, event_type: str, data: Optional[dict] = None):
        """Emit an event, calling all registered handlers.

        Args:
            event_type: The event type (e.g., "skill.evolved").
            data: Event payload.
        """
        event = SkillForgeEvent(event_type=event_type, data=data or {})
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            handler(event)

        # Also notify wildcard handlers
        wildcard_handlers = self._handlers.get("*", [])
        for handler in wildcard_handlers:
            handler(event)

    def list_event_types(self) -> list[str]:
        """List all standard event types."""
        return [
            EVENT_SKILL_EVOLVED,
            EVENT_SKILL_STORED,
            EVENT_SKILL_RETRIEVED,
            EVENT_TASK_COMPLETED,
            EVENT_TASK_FAILED,
            EVENT_MEMORY_RECORDED,
            EVENT_MEMORY_PROMOTED,
            EVENT_VERIFIER_PASSED,
            EVENT_VERIFIER_FAILED,
            EVENT_ORACLE_PASSED,
            EVENT_ORACLE_FAILED,
            EVENT_EVOLUTION_TRIGGERED,
        ]

    def list_subscriptions(self) -> dict[str, int]:
        """List active subscriptions with handler counts."""
        return {event: len(handlers) for event, handlers in self._handlers.items()}
