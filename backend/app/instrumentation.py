from prometheus_client import Counter, Histogram

REQUEST_COUNTER = Counter(
    "rag_requests_total",
    "Total number of RAG chat requests",
    labelnames=("status",),
)

RETRIEVAL_LATENCY = Histogram(
    "rag_retrieval_latency_seconds",
    "Latency for vector retrieval requests",
)

LLM_LATENCY = Histogram(
    "rag_llm_latency_seconds",
    "Latency for Ollama generations",
)

PROMPT_GUARD_COUNTER = Counter(
    "rag_guard_hits_total",
    "Number of times prompt guard blocked or flagged input",
    labelnames=("action",),
)

MODEL_USAGE_COUNTER = Counter(
    "rag_model_usage_total",
    "How often each model is used for chat responses",
    labelnames=("model",),
)
