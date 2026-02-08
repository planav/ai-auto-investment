from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AgentContext:
    """Context passed to agents during execution."""
    user_id: int
    risk_tolerance: str
    investment_horizon: int
    preferred_assets: List[str]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentResult:
    """Result returned by agent execution."""
    success: bool
    data: Dict[str, Any]
    explanation: Optional[str] = None
    confidence: Optional[float] = None
    errors: Optional[List[str]] = None


class BaseAgent(ABC):
    """Base class for all AI agents in the system."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the agent. Override in subclasses."""
        self._initialized = True
    
    @abstractmethod
    async def execute(self, context: AgentContext, **kwargs) -> AgentResult:
        """Execute the agent's main functionality."""
        pass
    
    async def cleanup(self) -> None:
        """Cleanup resources. Override in subclasses."""
        pass
    
    def is_initialized(self) -> bool:
        """Check if agent is initialized."""
        return self._initialized
