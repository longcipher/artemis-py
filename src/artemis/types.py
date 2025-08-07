"""
Base types and abstract classes for the Artemis framework.

This module defines the core interfaces that all components must implement:
- Collector: For gathering data from various sources
- Strategy: For processing events and generating actions  
- Executor: For executing actions on external systems

It also defines common enums for event and action types.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional


class Collector(ABC):
    """
    Abstract base class for all data collectors.
    
    Collectors are responsible for gathering data from various sources such as:
    - REST API endpoints
    - WebSocket feeds  
    - Database queries
    - File system monitoring
    - External message queues
    
    Each collector runs independently and pushes events to the engine's event queue.
    """

    @abstractmethod
    def start(self, timeout: Optional[int] = None) -> None:
        """
        Start the collector.
        
        Args:
            timeout: Optional timeout in seconds for the collector operations
        """
        pass

    @abstractmethod
    async def get_event_stream(self) -> Optional[Dict[str, Any]]:
        """
        Get the next event from the collector's stream.
        
        Returns:
            Dict containing event data, or None if no events are available
        """
        pass


class Strategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    Strategies receive events from collectors and generate actions for executors.
    They contain the core business logic for trading decisions.
    
    Examples:
    - Arbitrage strategies
    - Market making strategies
    - Liquidation strategies
    - Technical analysis strategies
    """

    @abstractmethod
    async def sync_state(self) -> None:
        """
        Synchronize the strategy's internal state.
        
        This method is called before the strategy starts processing events.
        Use it to initialize any required state, fetch market data, etc.
        """
        pass

    @abstractmethod
    async def process_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process an incoming event and optionally generate an action.
        
        Args:
            event: The event data to process
            
        Returns:
            Optional action dictionary, or None if no action should be taken
        """
        pass


class Executor(ABC):
    """
    Abstract base class for all executors.
    
    Executors receive actions from strategies and execute them on external systems.
    They handle the actual interaction with exchanges, databases, or other services.
    
    Examples:
    - Exchange order executors
    - Database writers
    - Notification senders
    - External API callers
    """

    @abstractmethod
    async def sync_state(self) -> None:
        """
        Synchronize the executor's internal state.
        
        This method is called before the executor starts processing actions.
        Use it to authenticate with external services, cache metadata, etc.
        """
        pass

    @abstractmethod
    async def execute(self, action: Dict[str, Any]) -> None:
        """
        Execute an action.
        
        Args:
            action: The action data to execute
        """
        pass


class EventType(str, Enum):
    """
    Enumeration of supported event types.
    
    Add new event types here as you extend the framework with new collectors.
    """
    
    # Generic events
    TICK = "tick"
    TRADE = "trade"
    ORDER_BOOK = "order_book"
    BALANCE_UPDATE = "balance_update"
    
    # Custom application events can be added by extending this enum
    # or by using string literals directly


class ActionType(str, Enum):
    """
    Enumeration of supported action types.
    
    Add new action types here as you extend the framework with new executors.
    """
    
    # Generic actions
    PLACE_ORDER = "place_order"
    CANCEL_ORDER = "cancel_order" 
    UPDATE_ORDER = "update_order"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"
    
    # Custom application actions can be added by extending this enum
    # or by using string literals directly
