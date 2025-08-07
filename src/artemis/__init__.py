"""
Artemis-PY: A real-time async event-driven trading framework

This framework provides a flexible architecture for building trading bots and strategies.
Inspired by paradigmxyz/artemis, it consists of three main components:

- Collectors: Gather data from various sources (REST APIs, WebSocket feeds, etc.)
- Strategies: Process events and generate trading actions
- Executors: Execute the generated actions on exchanges or other systems

The framework uses asyncio for concurrent processing and provides a simple,
extensible architecture for building complex trading systems.
"""

from .engine import Engine
from .types import (
    ActionType,
    Collector,
    EventType,
    Executor,
    Strategy,
)

__version__ = "0.1.0"
__all__ = [
    "Engine",
    "Collector",
    "Strategy", 
    "Executor",
    "EventType",
    "ActionType",
]
