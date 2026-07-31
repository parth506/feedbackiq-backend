"""
Core constants for FeedbackIQ backend.

Centralizes all magic strings, collection names, cache key prefixes,
and domain-level constants. Import from here — never hard-code.
"""

# ── MongoDB Collection Names ───────────────────────────────────────────────────
COLLECTION_FEEDBACK = "feedback"
COLLECTION_USERS = "users"
COLLECTION_ORGANIZATIONS = "organizations"

# ── Cache Key Namespaces ───────────────────────────────────────────────────────
# All Redis keys follow: feedbackiq:<domain>:<resource>
CACHE_NS = "feedbackiq"
CACHE_KEY_DASHBOARD = f"{CACHE_NS}:dashboard:stats"
CACHE_KEY_ANALYTICS_TIME_SERIES = f"{CACHE_NS}:analytics:time_series"
CACHE_KEY_ANALYTICS_CATEGORIES = f"{CACHE_NS}:analytics:categories"
CACHE_KEY_SENTIMENT_EMOTIONS = f"{CACHE_NS}:sentiment:emotions"
CACHE_KEY_SENTIMENT_EVOLUTION = f"{CACHE_NS}:sentiment:evolution"
CACHE_KEY_TOPICS_IMPORTANCE = f"{CACHE_NS}:topics:importance"
CACHE_KEY_TOPICS_KEYWORDS = f"{CACHE_NS}:topics:keywords"
CACHE_KEY_AI_SUMMARY = f"{CACHE_NS}:ai:summary"
CACHE_KEY_AI_RECOMMENDATIONS = f"{CACHE_NS}:ai:recommendations"

# ── Sentiment Values ───────────────────────────────────────────────────────────
SENTIMENT_POSITIVE = "positive"
SENTIMENT_NEUTRAL = "neutral"
SENTIMENT_NEGATIVE = "negative"
SENTIMENT_VALUES = (SENTIMENT_POSITIVE, SENTIMENT_NEUTRAL, SENTIMENT_NEGATIVE)

# ── Pagination ─────────────────────────────────────────────────────────────────
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ── Dashboard ─────────────────────────────────────────────────────────────────
DASHBOARD_LATEST_FEEDBACK_LIMIT = 10

# ── Search ────────────────────────────────────────────────────────────────────
MAX_SEARCH_RESULTS = 50
SEARCH_REGEX_OPTIONS = "i"   # case-insensitive

# ── Topic Modeling Keyword Config ──────────────────────────────────────────────
TOPIC_SCAN_LIMIT = 200       # max documents to scan for keyword extraction
TOPIC_TOP_KEYWORDS = 10      # top N keywords to return
TOPIC_MIN_WORD_LENGTH = 3

TOPIC_STOPWORDS = frozenset({
    "the", "a", "an", "is", "it", "to", "for", "in", "and", "or",
    "of", "with", "this", "my", "was", "are", "be", "have", "has",
    "not", "but", "so", "on", "at", "by", "from", "as", "do",
})

# ── Monitoring ────────────────────────────────────────────────────────────────
MONITORING_SSE_INTERVAL_SECONDS = 3
MONITORING_WS_INTERVAL_SECONDS = 4

# ── Security ──────────────────────────────────────────────────────────────────
COMMENT_MAX_LENGTH = 1000
SEARCH_QUERY_MAX_LENGTH = 200
SEARCH_QUERY_MIN_LENGTH = 1

# ── Log Context Keys ──────────────────────────────────────────────────────────
LOG_CORRELATION_ID_HEADER = "X-Correlation-ID"
LOG_CORRELATION_ID_CTX_KEY = "correlation_id"
