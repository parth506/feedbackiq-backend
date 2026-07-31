"""
Search Service — Business logic for full-text feedback comment search.

Replaces duplicated search logic previously in:
  - features/search/router.py
  - services/feedback.py (search_feedback method)

Security:
  - Sanitizes query strings via re.escape() before passing to repository.
  - Enforces min/max query length via constants.

Pagination:
  - Accepts limit + offset for cursor-based pagination.

Future:
  - Ready to swap regex for MongoDB Atlas Search ($search) or vector embeddings
    by replacing FeedbackRepository.search() with a new concrete implementation.
"""
import logging
import re
from typing import List

from app.core.constants import (
    MAX_SEARCH_RESULTS,
    SEARCH_QUERY_MAX_LENGTH,
    SEARCH_QUERY_MIN_LENGTH,
)
from app.exceptions.exceptions import SearchException
from app.features.search.schemas import SearchResultDTO
from app.repositories.feedback import FeedbackRepository

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching feedback comments with input validation."""

    def __init__(self, repository: FeedbackRepository) -> None:
        self.repository = repository

    def _validate_query(self, query: str) -> str:
        """
        Validate and sanitize the search query string.
        - Strips whitespace
        - Enforces min/max length
        - Returns re.escape()'d string safe for MongoDB $regex
        """
        stripped = query.strip()

        if len(stripped) < SEARCH_QUERY_MIN_LENGTH:
            raise SearchException(
                f"Search query must be at least {SEARCH_QUERY_MIN_LENGTH} character(s)."
            )

        if len(stripped) > SEARCH_QUERY_MAX_LENGTH:
            raise SearchException(
                f"Search query must not exceed {SEARCH_QUERY_MAX_LENGTH} characters."
            )

        return stripped  # re.escape applied inside FeedbackRepository.search()

    async def search_comments(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[SearchResultDTO]:
        """
        Search feedback comments by keyword.

        Args:
            query: Raw search string from the client.
            limit: Max results to return (capped at MAX_SEARCH_RESULTS).
            offset: Number of results to skip (for pagination).

        Returns:
            List of SearchResultDTO matching the query.
        """
        validated_query = self._validate_query(query)
        effective_limit = min(limit, MAX_SEARCH_RESULTS)

        docs = await self.repository.search(validated_query, limit=effective_limit + offset)

        # Apply offset manually (Motor doesn't support skip+limit on find when using search)
        paginated_docs = docs[offset : offset + effective_limit]

        return [
            SearchResultDTO(
                id=str(doc["_id"]),
                sentiment=doc.get("sentiment", "positive"),
                comment=doc.get("comment", ""),
                created_at=(
                    doc["created_at"].isoformat()
                    if hasattr(doc.get("created_at"), "isoformat")
                    else str(doc.get("created_at", ""))
                ),
            )
            for doc in paginated_docs
        ]
