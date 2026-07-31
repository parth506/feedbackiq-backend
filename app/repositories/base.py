"""
Abstract Base Repository.

Defines the contract that all MongoDB repositories must implement.
Concrete repositories (e.g., FeedbackRepository) extend this class and
override methods for their specific collection.

Design decisions:
  - Uses ABC to enforce method implementation at class definition time.
  - All methods are async — Motor is always async.
  - `aggregate()` accepts a generic pipeline list to keep repositories flexible.
  - `find()` accepts an optional filter dict and projection for flexibility.
  - Pagination params (limit, offset) are standardized.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseRepository(ABC):
    """Abstract repository defining the standard data access contract."""

    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert one document. Returns the inserted document with _id as str."""
        ...

    @abstractmethod
    async def find(
        self,
        filter_query: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0,
        sort_field: str = "created_at",
        sort_direction: int = -1,
    ) -> List[Dict[str, Any]]:
        """Find documents matching the filter, with pagination and sorting."""
        ...

    @abstractmethod
    async def find_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Find a single document by its MongoDB ObjectId string."""
        ...

    @abstractmethod
    async def update(self, document_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a document by ID. Returns True if a document was modified."""
        ...

    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """Delete a document by ID. Returns True if a document was deleted."""
        ...

    @abstractmethod
    async def count(self, filter_query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching the optional filter."""
        ...

    @abstractmethod
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute an aggregation pipeline and return the results as a list."""
        ...

    @abstractmethod
    async def search(self, query_str: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Text search within documents. Implementation defines search strategy."""
        ...

    @abstractmethod
    async def find_latest(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return the N most recently created documents."""
        ...
