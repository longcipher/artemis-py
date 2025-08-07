"""
Event loop utilities for the Artemis framework.
"""

import asyncio
from typing import Optional


def get_loop() -> asyncio.AbstractEventLoop:
    """
    Get the current event loop or create a new one if none exists.
    
    Returns:
        The current asyncio event loop
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def create_task(coro, name: Optional[str] = None) -> asyncio.Task:
    """
    Create an asyncio task with optional naming.
    
    Args:
        coro: The coroutine to wrap in a task
        name: Optional name for the task (useful for debugging)
        
    Returns:
        The created task
    """
    loop = get_loop()
    if name:
        return loop.create_task(coro, name=name)
    return loop.create_task(coro)
