from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

# Enums
class ToolType(str, Enum):
    TAVILY = "tavily"
    ARXIV = "arxiv"
    YFINANCE = "yfinance"
    RAG = "rag"

class EvaluationMetric(str, Enum):
    CONTEXT_RECALL = "context_recall"
    FAITHFULNESS = "faithfulness"
    FACTUAL_CORRECTNESS = "factual_correctness"
    RESPONSE_RELEVANCY = "response_relevancy"
    CONTEXT_ENTITY_RECALL = "context_entity_recall"
    NOISE_SENSITIVITY = "noise_sensitivity"

# Base Models
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Wealth Advisor Models
class AdvisorQueryRequest(BaseModel):
    question: str = Field(..., description="Question to ask the wealth advisor")
    include_context: bool = Field(default=True, description="Include context in response")
    stream_response: bool = Field(default=False, description="Stream the response")

class AdvisorResponse(BaseModel):
    question: str
    response: str
    context: List[Dict[str, Any]] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    processing_time: Optional[float] = None

class StreamResponse(BaseModel):
    question: str
    stream_generator: Any  # This will be handled by FastAPI streaming

# RAG Models
class RAGQueryRequest(BaseModel):
    question: str = Field(..., description="Question for RAG system")
    top_k: int = Field(default=5, description="Number of documents to retrieve")

class RAGResponse(BaseModel):
    question: str
    response: str
    context: List[Dict[str, Any]] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    retrieval_score: Optional[float] = None

class DocumentUploadRequest(BaseModel):
    documents: List[Dict[str, Any]] = Field(..., description="Documents to add to RAG system")
    collection_name: Optional[str] = Field(default="default", description="Collection name")

class DocumentUploadResponse(BaseModel):
    message: str
    documents_added: int
    total_documents: int
    collection_name: str

# Context Parsing Models
class ContextParseRequest(BaseModel):
    context: str = Field(..., description="Context string to parse")
    source_type: Optional[str] = Field(default=None, description="Expected source type")

class ContextParseResponse(BaseModel):
    source: str
    parsed_data: Dict[str, Any]
    formatted_output: str
    parsing_confidence: Optional[float] = None

# Evaluation Models
class EvaluationRequest(BaseModel):
    test_questions: List[str] = Field(..., description="Test questions for evaluation")
    metrics: List[EvaluationMetric] = Field(default_factory=list)
    include_detailed_results: bool = Field(default=True)

class EvaluationResponse(BaseModel):
    metrics: Dict[str, float]
    overall_score: float
    recommendations: List[str] = Field(default_factory=list)
    detailed_results: Optional[Dict[str, Any]] = None

class TestGenerationRequest(BaseModel):
    num_tests: int = Field(default=10, ge=1, le=100)
    categories: List[str] = Field(default_factory=list)
    difficulty_level: Optional[str] = Field(default="medium")

class TestGenerationResponse(BaseModel):
    test_questions: List[str]
    categories: List[str]
    total_tests: int
    difficulty_distribution: Optional[Dict[str, int]] = None

# Tool Models
class SearchResult(BaseModel):
    title: str
    url: str
    content: str
    score: Optional[float] = None
    source: str = "tavily"

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    search_time: Optional[float] = None

class ArxivPaper(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    date: Optional[str] = None

class ArxivResponse(BaseModel):
    query: str
    papers: List[ArxivPaper]
    total_papers: int
    search_time: Optional[float] = None

class StockData(BaseModel):
    symbol: str
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open_price: Optional[float] = None
    previous_close: Optional[float] = None

class YFinanceResponse(BaseModel):
    symbol: str
    data: StockData
    last_updated: datetime = Field(default_factory=datetime.now)

# Analytics Models
class UsageAnalytics(BaseModel):
    total_queries: int
    successful_queries: int
    failed_queries: int
    average_response_time: float
    most_used_tools: List[Dict[str, Any]]
    query_categories: Dict[str, int]
    daily_usage: List[Dict[str, Any]]
    monthly_usage: List[Dict[str, Any]]

class PerformanceMetrics(BaseModel):
    context_recall_score: float
    faithfulness_score: float
    factual_correctness_score: float
    response_relevancy_score: float
    overall_performance_score: float
    evaluation_timestamp: datetime = Field(default_factory=datetime.now)
    test_dataset_size: int
    confidence_interval: Optional[Dict[str, float]] = None

# Error Models
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Configuration Models
class ServiceConfig(BaseModel):
    openai_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    langchain_api_key: Optional[str] = None
    model_name: str = "gpt-4o"
    temperature: float = 0.0
    max_tokens: int = 4000
    chunk_size: int = 750
    chunk_overlap: int = 100
    vector_store_type: str = "qdrant"
    embedding_model: str = "text-embedding-3-small"

class SystemStatus(BaseModel):
    status: str
    services: Dict[str, bool]
    uptime: Optional[float] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    active_connections: Optional[int] = None

# Document Models
class Document(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: Optional[str] = None
    page_number: Optional[int] = None
    chunk_id: Optional[str] = None

class DocumentCollection(BaseModel):
    name: str
    documents: List[Document]
    total_documents: int
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

# Tool Configuration Models
class ToolConfig(BaseModel):
    name: str
    enabled: bool = True
    max_results: int = 5
    timeout: int = 30
    retry_attempts: int = 3
    custom_parameters: Dict[str, Any] = Field(default_factory=dict)

class ToolRegistry(BaseModel):
    tools: Dict[str, ToolConfig]
    default_tools: List[str] = Field(default_factory=list)
    tool_priorities: Dict[str, int] = Field(default_factory=dict)

# Streaming Models
class StreamChunk(BaseModel):
    chunk_id: str
    content: str
    is_final: bool = False
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class StreamMetadata(BaseModel):
    total_chunks: int
    current_chunk: int
    estimated_remaining: Optional[float] = None
    tools_used: List[str] = Field(default_factory=list)
    confidence: Optional[float] = None

# Batch Processing Models
class BatchQueryRequest(BaseModel):
    questions: List[str] = Field(..., description="List of questions to process")
    batch_size: int = Field(default=10, ge=1, le=100)
    parallel_processing: bool = Field(default=True)

class BatchQueryResponse(BaseModel):
    results: List[AdvisorResponse]
    total_processed: int
    successful_queries: int
    failed_queries: int
    processing_time: float
    batch_id: str

# Webhook Models
class WebhookEvent(BaseModel):
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    event_id: str

class WebhookConfig(BaseModel):
    url: str
    events: List[str] = Field(default_factory=list)
    secret: Optional[str] = None
    enabled: bool = True
    retry_attempts: int = 3
    timeout: int = 30 