# Wealth Advisor AI - System Flow Diagram

## Simple Data Flow

```mermaid
graph TD
    A[User Input] --> B[Frontend Chat Interface]
    B --> C[Next.js API Routes]
    C --> D[FastAPI Backend]
    D --> E[Query Router]
    E --> F{Query Type}
    
    F -->|Web Search| G[Tavily Search]
    F -->|Research| H[ArXiv Papers]
    F -->|Stock Data| I[YFinance API]
    F -->|Document Q&A| J[RAG System]
    
    G --> K[Response Combiner]
    H --> K
    I --> K
    J --> K
    
    K --> L[AI Processing]
    L --> M[Formatted Response]
    M --> N[Frontend Display]
    N --> O[User Sees Result]
    
    style A fill:#e1f5fe
    style O fill:#e8f5e8
    style D fill:#fff3e0
    style K fill:#f3e5f5
```

## Component Overview

### Frontend Layer
- **Chat Interface**: User input and message display
- **Settings Modal**: API key management and preferences
- **Tool Status**: Real-time backend health monitoring

### API Gateway
- **Next.js Routes**: Frontend API endpoints
- **FastAPI Backend**: Main backend service
- **CORS Middleware**: Cross-origin request handling

### Backend Services
- **Query Router**: Categorizes and routes user queries
- **Tool Manager**: Manages external tool connections
- **Response Combiner**: Merges results from multiple tools
- **Analytics Tracker**: Usage metrics and health monitoring

### External Tools
- **Tavily Search**: Web search and news
- **ArXiv Research**: Academic papers and research
- **YFinance**: Real-time stock and financial data
- **RAG System**: Document-based knowledge retrieval

### Data Layer
- **PDF Processor**: Document text extraction
- **Vector Store**: Embeddings and similarity search
- **API Services**: External API integrations

## Key Data Flow Steps

1. **User Input** → User types question in chat interface
2. **Query Processing** → Backend categorizes and routes the query
3. **Tool Selection** → Appropriate tools are selected based on query type
4. **Data Retrieval** → Tools fetch relevant information
5. **Response Generation** → AI processes and combines results
6. **Format & Display** → Formatted response sent to frontend
7. **User Feedback** → User receives comprehensive answer

## Tool Integration Flow

```mermaid
graph LR
    A[User Query] --> B{Query Analysis}
    B -->|Market Info| C[Tavily + YFinance]
    B -->|Research| D[ArXiv + RAG]
    B -->|General| E[Tavily + RAG]
    B -->|Financial| F[YFinance + RAG]
    
    C --> G[AI Processing]
    D --> G
    E --> G
    F --> G
    
    G --> H[Structured Response]
    H --> I[User Interface]
    
    style A fill:#e1f5fe
    style I fill:#e8f5e8
    style G fill:#f3e5f5
```

This flow diagram shows how the Wealth Advisor AI system processes user queries through multiple specialized tools and returns comprehensive, AI-enhanced responses. 