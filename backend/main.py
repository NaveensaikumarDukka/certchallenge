from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import asyncio
from contextlib import asynccontextmanager
import logging

# Import our custom modules
from models import *
from services.wealth_advisor_service import WealthAdvisorService
from services.rag_service import RAGService
from services.evaluation_service import EvaluationService
from services.context_parser import ContextParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances
wealth_advisor_service = None
rag_service = None
evaluation_service = None
context_parser = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    global wealth_advisor_service, rag_service, evaluation_service, context_parser
    
    logger.info("Initializing Wealth Advisor API services...")
    
    try:
        # Initialize services
        context_parser = ContextParser()
        rag_service = RAGService()
        wealth_advisor_service = WealthAdvisorService(rag_service)
        evaluation_service = EvaluationService()
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    logger.info("Shutting down Wealth Advisor API...")

# Create FastAPI app
app = FastAPI(
    title="Wealth Advisor AI Copilot API",
    description="AI-powered platform that helps financial advisors with wealth management and investment advice",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "wealth_advisor": wealth_advisor_service is not None,
            "rag_service": rag_service is not None,
            "evaluation_service": evaluation_service is not None,
            "context_parser": context_parser is not None
        }
    }

# Wealth Advisor endpoints
@app.post("/api/v1/advisor/query", response_model=AdvisorResponse)
async def query_advisor(request: AdvisorQueryRequest):
    """Query the wealth advisor with a question using all 4 tools"""
    try:
        logger.info(f"Processing query: {request.question}")
        response = await wealth_advisor_service.process_query(request.question)
        
        # Log which tools were used
        tools_used = response.get("tools_used", [])
        logger.info(f"Tools used: {tools_used}")
        
        return AdvisorResponse(
            question=request.question,
            response=response["response"],
            context=response.get("context", []),
            tools_used=tools_used,
            confidence=response.get("confidence", 0.0)
        )
    except Exception as e:
        logger.error(f"Error processing advisor query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/advisor/tools/status")
async def get_tools_status():
    """Get status of all available tools"""
    try:
        tools_status = {
            "tavily_search": "tavily_search" in wealth_advisor_service.tools if wealth_advisor_service else False,
            "arxiv_search": "arxiv_search" in wealth_advisor_service.tools if wealth_advisor_service else False,
            "yfinance_data": "yfinance_data" in wealth_advisor_service.tools if wealth_advisor_service else False,
            "rag_query": "rag_query" in wealth_advisor_service.tools if wealth_advisor_service else False,
            "total_tools": len(wealth_advisor_service.tools) if wealth_advisor_service else 0
        }
        
        # Check API key details
        tavily_key = os.environ.get("TAVILY_API_KEY")
        tavily_status = {
            "configured": bool(tavily_key),
            "has_value": bool(tavily_key and tavily_key.strip()),
            "key_length": len(tavily_key) if tavily_key else 0
        }
        
        return {
            "tools_status": tools_status,
            "api_keys_configured": {
                "openai": bool(os.environ.get("OPENAI_API_KEY")),
                "tavily": bool(os.environ.get("TAVILY_API_KEY")),
                "cohere": bool(os.environ.get("COHERE_API_KEY")),
                "langsmith": bool(os.environ.get("LANGCHAIN_API_KEY"))
            },
            "tavily_details": tavily_status
        }
    except Exception as e:
        logger.error(f"Error getting tools status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/advisor/stream", response_model=StreamResponse)
async def stream_advisor_query(request: AdvisorQueryRequest):
    """Stream response from the wealth advisor"""
    try:
        async def generate_stream():
            async for chunk in wealth_advisor_service.stream_query(request.question):
                yield chunk
        
        return StreamResponse(
            question=request.question,
            stream_generator=generate_stream()
        )
    except Exception as e:
        logger.error(f"Error streaming advisor query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# RAG endpoints
@app.post("/api/v1/rag/query", response_model=RAGResponse)
async def rag_query(request: RAGQueryRequest):
    """Query the RAG system directly"""
    try:
        response = await rag_service.query(request.question)
        return RAGResponse(
            question=request.question,
            response=response["response"],
            context=response.get("context", []),
            sources=response.get("sources", [])
        )
    except Exception as e:
        logger.error(f"Error processing RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rag/add-documents", response_model=DocumentUploadResponse)
async def add_documents(request: DocumentUploadRequest):
    """Add documents to the RAG system"""
    try:
        result = await rag_service.add_documents(request.documents)
        return DocumentUploadResponse(
            message="Documents added successfully",
            documents_added=result["documents_added"],
            total_documents=result["total_documents"]
        )
    except Exception as e:
        logger.error(f"Error adding documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Context parsing endpoints
@app.post("/api/v1/context/parse", response_model=ContextParseResponse)
async def parse_context(request: ContextParseRequest):
    """Parse context from various sources"""
    try:
        parsed_data = context_parser.parse_generic_context(request.context)
        return ContextParseResponse(
            source=parsed_data["source"],
            parsed_data=parsed_data,
            formatted_output=context_parser.to_string(parsed_data)
        )
    except Exception as e:
        logger.error(f"Error parsing context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/context/parse-tavily", response_model=ContextParseResponse)
async def parse_tavily_context(request: ContextParseRequest):
    """Parse Tavily-specific context"""
    try:
        parsed_data = context_parser.parse_tavily_context(request.context)
        return ContextParseResponse(
            source="tavily",
            parsed_data=parsed_data,
            formatted_output=context_parser.to_string(parsed_data)
        )
    except Exception as e:
        logger.error(f"Error parsing Tavily context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/context/parse-arxiv", response_model=ContextParseResponse)
async def parse_arxiv_context(request: ContextParseRequest):
    """Parse ArXiv-specific context"""
    try:
        parsed_data = context_parser.parse_arxiv_context(request.context)
        return ContextParseResponse(
            source="arxiv",
            parsed_data=parsed_data,
            formatted_output=context_parser.to_string(parsed_data)
        )
    except Exception as e:
        logger.error(f"Error parsing ArXiv context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/context/parse-yfinance", response_model=ContextParseResponse)
async def parse_yfinance_context(request: ContextParseRequest):
    """Parse yfinance-specific context"""
    try:
        parsed_data = context_parser.parse_yfinance_context(request.context)
        return ContextParseResponse(
            source="yfinance",
            parsed_data=parsed_data,
            formatted_output=context_parser.to_string(parsed_data)
        )
    except Exception as e:
        logger.error(f"Error parsing yfinance context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Evaluation endpoints
@app.post("/api/v1/evaluation/evaluate", response_model=EvaluationResponse)
async def evaluate_system(request: EvaluationRequest):
    """Evaluate the system performance"""
    try:
        result = await evaluation_service.evaluate(request.test_questions)
        return EvaluationResponse(
            metrics=result["metrics"],
            overall_score=result["overall_score"],
            recommendations=result["recommendations"]
        )
    except Exception as e:
        logger.error(f"Error evaluating system: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/evaluation/generate-tests", response_model=TestGenerationResponse)
async def generate_test_dataset(request: TestGenerationRequest):
    """Generate test dataset for evaluation"""
    try:
        result = await evaluation_service.generate_test_dataset(
            request.num_tests,
            request.categories
        )
        return TestGenerationResponse(
            test_questions=result["test_questions"],
            categories=result["categories"],
            total_tests=result["total_tests"]
        )
    except Exception as e:
        logger.error(f"Error generating test dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Tool endpoints
@app.get("/api/v1/tools/search", response_model=SearchResponse)
async def search_tavily(query: str, max_results: int = 5):
    """Search using Tavily"""
    try:
        results = await wealth_advisor_service.search_tavily(query, max_results)
        return SearchResponse(
            query=query,
            results=results,
            total_results=len(results)
        )
    except Exception as e:
        logger.error(f"Error searching Tavily: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tools/arxiv", response_model=ArxivResponse)
async def search_arxiv(query: str, max_results: int = 5):
    """Search ArXiv papers"""
    try:
        results = await wealth_advisor_service.search_arxiv(query, max_results)
        return ArxivResponse(
            query=query,
            papers=results,
            total_papers=len(results)
        )
    except Exception as e:
        logger.error(f"Error searching ArXiv: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tools/yfinance", response_model=YFinanceResponse)
async def get_stock_data(symbol: str):
    """Get stock data from yfinance"""
    try:
        data = await wealth_advisor_service.get_stock_data(symbol)
        return YFinanceResponse(
            symbol=symbol,
            data=data
        )
    except Exception as e:
        logger.error(f"Error getting stock data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.get("/api/v1/analytics/usage", response_model=UsageAnalytics)
async def get_usage_analytics():
    """Get usage analytics"""
    try:
        analytics = await wealth_advisor_service.get_usage_analytics()
        return UsageAnalytics(**analytics)
    except Exception as e:
        logger.error(f"Error getting usage analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/performance", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """Get system performance metrics"""
    try:
        metrics = await evaluation_service.get_performance_metrics()
        return PerformanceMetrics(**metrics)
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Settings endpoints
@app.post("/api/v1/settings/update-keys")
async def update_api_keys(request: dict):
    """Update API keys in the backend"""
    try:
        logger.info(f"Backend received API keys request: {request}")
        
        # Update environment variables for any keys provided
        updated_keys = []
        
        if 'openai' in request and request['openai']:
            os.environ["OPENAI_API_KEY"] = request['openai']
            updated_keys.append('openai')
            logger.info("Updated OpenAI API key")
        
        if 'tavily' in request and request['tavily']:
            os.environ["TAVILY_API_KEY"] = request['tavily']
            updated_keys.append('tavily')
            logger.info("Updated Tavily API key")
        
        if 'langsmith' in request and request['langsmith']:
            os.environ["LANGCHAIN_API_KEY"] = request['langsmith']
            updated_keys.append('langsmith')
            logger.info("Updated LangSmith API key")
        
        if 'cohere' in request and request['cohere']:
            os.environ["COHERE_API_KEY"] = request['cohere']
            updated_keys.append('cohere')
            logger.info("Updated Cohere API key")
        
        logger.info(f"Updated {len(updated_keys)} API keys: {updated_keys}")
        
        # Reinitialize services with new keys
        if wealth_advisor_service and updated_keys:
            try:
                logger.info("Reinitializing wealth advisor service tools...")
                await wealth_advisor_service.reinitialize_tools()
                logger.info("Wealth advisor service tools reinitialized with new API keys")
            except Exception as e:
                logger.warning(f"Failed to reinitialize wealth advisor service tools: {e}")
        
        if rag_service and ('openai' in updated_keys or 'cohere' in updated_keys):
            try:
                logger.info("Reinitializing RAG service...")
                await rag_service.initialize()
                logger.info("RAG service reinitialized with new API keys")
            except Exception as e:
                logger.warning(f"Failed to reinitialize RAG service: {e}")
        
        logger.info("API keys updated successfully")
        
        return {
            "success": True,
            "message": f"Updated {len(updated_keys)} API keys successfully",
            "updated_keys": updated_keys,
            "total_keys_configured": len([k for k in ['openai', 'tavily', 'langsmith', 'cohere'] if os.environ.get(f"{k.upper()}_API_KEY")])
        }
        
    except Exception as e:
        logger.error(f"Error updating API keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/settings/status")
async def get_settings_status():
    """Get current settings status"""
    try:
        # Get PDF processing stats
        pdf_stats = {}
        if rag_service and hasattr(rag_service, 'pdf_processor'):
            pdf_stats = rag_service.pdf_processor.get_processing_stats()
        
        return {
            "openai_configured": bool(os.environ.get("OPENAI_API_KEY")),
            "tavily_configured": bool(os.environ.get("TAVILY_API_KEY")),
            "langsmith_configured": bool(os.environ.get("LANGCHAIN_API_KEY")),
            "cohere_configured": bool(os.environ.get("COHERE_API_KEY")),
            "services_healthy": {
                "wealth_advisor": wealth_advisor_service is not None,
                "rag_service": rag_service is not None,
                "evaluation_service": evaluation_service is not None,
                "context_parser": context_parser is not None
            },
            "pdf_processing": pdf_stats
        }
    except Exception as e:
        logger.error(f"Error getting settings status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 