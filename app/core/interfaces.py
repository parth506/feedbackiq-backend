"""
Core Abstract Interfaces for FeedbackIQ.

These Protocol classes define the contracts for all pluggable providers.
Swap implementations without changing any service or router code.

Current implementations:
  - LLMProviderInterface → RuleBasedLLMProvider (in ai_service.py, implicit)

Planned implementations:
  - OpenAIProvider(LLMProviderInterface)
  - AnthropicProvider(LLMProviderInterface)
  - HuggingFaceEmbeddingProvider(EmbeddingProviderInterface)
  - ProphetForecastProvider(PredictionProviderInterface)
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


# ── LLM Provider ──────────────────────────────────────────────────────────────

class LLMProviderInterface(ABC):
    """
    Abstract interface for Large Language Model providers.
    Implement this to swap between rule-based, OpenAI, Anthropic, etc.
    """

    @abstractmethod
    async def summarize(self, context: str, max_tokens: int = 200) -> str:
        """Generate a natural language summary from context text."""
        ...

    @abstractmethod
    async def classify(self, text: str, labels: List[str]) -> str:
        """Classify text into one of the provided labels."""
        ...

    @abstractmethod
    async def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract the top N keywords from a block of text."""
        ...


# ── Embedding Provider ────────────────────────────────────────────────────────

class EmbeddingProviderInterface(ABC):
    """
    Abstract interface for text embedding providers.
    Used for semantic search and vector-based retrieval.
    """

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Convert text to a dense vector embedding."""
        ...

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Convert a batch of texts to dense vector embeddings."""
        ...


# ── Prediction Provider ────────────────────────────────────────────────────────

class PredictionProviderInterface(ABC):
    """
    Abstract interface for time-series prediction models.
    Used for feedback volume forecasting and churn prediction.
    """

    @abstractmethod
    async def forecast(
        self,
        history: List[Dict[str, Any]],
        horizon_days: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Generate a forecast from historical data.

        Args:
            history: List of {"date": str, "value": float} dicts.
            horizon_days: Number of future days to forecast.

        Returns:
            List of {"date": str, "predicted": float, "lower": float, "upper": float} dicts.
        """
        ...


# ── Task Queue Interface ──────────────────────────────────────────────────────

class TaskQueueInterface(ABC):
    """
    Abstract interface for background task queues.
    Swap with Celery, Redis Queue, or Kafka without changing callers.
    """

    @abstractmethod
    async def enqueue(self, task_name: str, payload: Dict[str, Any]) -> str:
        """
        Enqueue a background task.

        Returns:
            Task ID string for status tracking.
        """
        ...

    @abstractmethod
    async def get_status(self, task_id: str) -> Dict[str, Any]:
        """Return the current status of a queued task."""
        ...
