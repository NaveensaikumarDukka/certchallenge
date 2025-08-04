# Wealth Advisor AI Copilot API

A FastAPI-based backend for an AI-powered wealth management platform that helps financial advisors with investment advice, portfolio management, and financial planning.

## Features

- **AI-Powered Wealth Advisory**: Intelligent responses to financial queries
- **RAG (Retrieval-Augmented Generation)**: Context-aware responses based on financial documents
- **Multi-Tool Integration**: Tavily search, ArXiv papers, Yahoo Finance data
- **Context Parsing**: Parse and structure data from various sources
- **System Evaluation**: RAGAS-based performance evaluation
- **Real-time Analytics**: Usage tracking and performance metrics
- **Streaming Responses**: Real-time response streaming
- **Comprehensive API**: RESTful endpoints for all functionality

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Wealth Advisor │    │   RAG Service   │
│                 │    │    Service      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Context Parser │    │  Evaluation     │    │  Vector Store   │
│                 │    │  Service        │    │  (Qdrant)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd wealth-advisor-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
COHERE_API_KEY=your_cohere_api_key
LANGCHAIN_API_KEY=your_langchain_api_key

# Configuration
MODEL_NAME=gpt-4o
TEMPERATURE=0.0
MAX_TOKENS=4000
CHUNK_SIZE=750
CHUNK_OVERLAP=100

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### 3. Run the Application

```bash
# Development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Health & Status

- `GET /health` - System health check
- `GET /api/v1/analytics/usage` - Usage analytics
- `GET /api/v1/analytics/performance` - Performance metrics

### Wealth Advisor

- `POST /api/v1/advisor/query` - Query the wealth advisor
- `POST /api/v1/advisor/stream` - Stream responses from advisor

### RAG System

- `POST /api/v1/rag/query` - Direct RAG queries
- `POST /api/v1/rag/add-documents` - Add documents to RAG system

### Context Parsing

- `POST /api/v1/context/parse` - Parse generic context
- `POST /api/v1/context/parse-tavily` - Parse Tavily context
- `POST /api/v1/context/parse-arxiv` - Parse ArXiv context
- `POST /api/v1/context/parse-yfinance` - Parse yfinance context

### Evaluation

- `POST /api/v1/evaluation/evaluate` - Evaluate system performance
- `POST /api/v1/evaluation/generate-tests` - Generate test datasets

### Tools

- `GET /api/v1/tools/search` - Tavily search
- `GET /api/v1/tools/arxiv` - ArXiv search
- `GET /api/v1/tools/yfinance` - Stock data

## Usage Examples

### 1. Query the Wealth Advisor

```python
import requests

# Query the advisor
response = requests.post("http://localhost:8000/api/v1/advisor/query", 
    json={
        "question": "What are the best investment strategies for retirement planning?",
        "include_context": True,
        "stream_response": False
    }
)

print(response.json())
```

### 2. Add Documents to RAG System

```python
# Add financial documents
documents = [
    {
        "content": "Wealth management involves comprehensive financial planning...",
        "metadata": {"source": "wealth_guide.pdf", "page": 1}
    }
]

response = requests.post("http://localhost:8000/api/v1/rag/add-documents",
    json={"documents": documents}
)
```

### 3. Parse Context

```python
# Parse Tavily search results
tavily_context = """
<result>
<title>Investment Strategies 2024</title>
<content>Latest investment strategies for wealth management...</content>
<url>https://example.com</url>
</result>
"""

response = requests.post("http://localhost:8000/api/v1/context/parse-tavily",
    json={"context": tavily_context}
)
```

### 4. Evaluate System Performance

```python
# Run evaluation
test_questions = [
    "What are the key principles of wealth management?",
    "How should I diversify my portfolio?",
    "What tax considerations are important for retirement?"
]

response = requests.post("http://localhost:8000/api/v1/evaluation/evaluate",
    json={"test_questions": test_questions}
)
```

## Configuration

### Service Configuration

The system can be configured through environment variables or the `ServiceConfig` model:

```python
from models import ServiceConfig

config = ServiceConfig(
    model_name="gpt-4o",
    temperature=0.0,
    max_tokens=4000,
    chunk_size=750,
    chunk_overlap=100,
    vector_store_type="qdrant",
    embedding_model="text-embedding-3-small"
)
```

### Tool Configuration

Tools can be configured individually:

```python
from models import ToolConfig

tavily_config = ToolConfig(
    name="tavily_search",
    enabled=True,
    max_results=5,
    timeout=30,
    retry_attempts=3
)
```

## Development

### Project Structure

```
wealth-advisor-api/
├── main.py                 # FastAPI application
├── models.py              # Pydantic models
├── requirements.txt       # Dependencies
├── README.md             # This file
├── services/             # Service modules
│   ├── __init__.py
│   ├── context_parser.py
│   ├── rag_service.py
│   ├── wealth_advisor_service.py
│   └── evaluation_service.py
├── data/                 # Document storage
├── tests/                # Test files
└── docs/                 # Documentation
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with coverage
pytest --cov=services tests/
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
    volumes:
      - ./data:/app/data
```

### Production Considerations

1. **Environment Variables**: Use secure environment variable management
2. **API Keys**: Rotate API keys regularly
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **Monitoring**: Add application monitoring and logging
5. **Security**: Implement authentication and authorization
6. **Scaling**: Use load balancers for horizontal scaling

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all required API keys are set in `.env`
2. **Import Errors**: Verify all dependencies are installed
3. **Memory Issues**: Adjust chunk sizes for large documents
4. **Timeout Errors**: Increase timeout values for long-running operations

### Logging

The application uses structured logging. Check logs for detailed error information:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the troubleshooting section

## Roadmap

- [ ] Authentication and authorization
- [ ] Multi-tenant support
- [ ] Advanced analytics dashboard
- [ ] Mobile API support
- [ ] WebSocket support for real-time updates
- [ ] Advanced document processing
- [ ] Integration with more financial data sources
