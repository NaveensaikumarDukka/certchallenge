# Wealth Advisor AI Copilot

A full-stack AI-powered wealth management platform that helps financial advisors with investment advice, portfolio management, and financial planning.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI       │
│   Frontend      │◄──►│   Backend       │
│   (React/TS)    │    │   (Python)      │
└─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Tailwind CSS  │    │   LangChain     │
│   UI Components │    │   RAG System    │
└─────────────────┘    └─────────────────┘
```

## 🚀 Features

### Frontend (Next.js)
- **Modern Chat Interface**: Real-time chat with AI advisor
- **Responsive Design**: Works on desktop and mobile
- **Markdown Support**: Rich text formatting in responses
- **Tool Integration**: Visual indicators for used tools
- **Real-time Status**: Backend health monitoring
- **Dark/Light Mode**: Theme support (coming soon)

### Backend (FastAPI)
- **AI-Powered Responses**: GPT-4 integration
- **RAG System**: Document-based knowledge retrieval
- **Multi-Tool Integration**: Tavily, ArXiv, Yahoo Finance
- **Context Parsing**: Structured data extraction
- **System Evaluation**: RAGAS performance metrics
- **RESTful API**: Comprehensive endpoints

## 📁 Project Structure

```
wealth-advisor-ai/
├── backend/                    # FastAPI Backend
│   ├── main.py                # FastAPI application
│   ├── models.py              # Pydantic models
│   ├── requirements.txt       # Python dependencies
│   └── services/              # Business logic
│       ├── context_parser.py  # Context parsing
│       ├── rag_service.py     # RAG system
│       ├── wealth_advisor_service.py
│       └── evaluation_service.py
│
├── frontend/                   # Next.js Frontend
│   ├── package.json           # Node.js dependencies
│   ├── next.config.js         # Next.js config
│   ├── tailwind.config.js     # Tailwind CSS config
│   └── src/
│       ├── app/               # Next.js 13+ app router
│       ├── components/        # React components
│       ├── lib/               # Utilities and API
│       └── hooks/             # Custom React hooks
│
├── docker-compose.yml         # Full stack deployment
└── README.md                  # This file
```

## 🛠️ Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker (optional)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd wealth-advisor-ai
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your_openai_api_key"
export TAVILY_API_KEY="your_tavily_api_key"
export COHERE_API_KEY="your_cohere_api_key"

# Run backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local

# Run frontend
npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and run both services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Individual Docker Builds

```bash
# Backend
cd backend
docker build -t wealth-advisor-backend .
docker run -p 8000:8000 wealth-advisor-backend

# Frontend
cd frontend
docker build -t wealth-advisor-frontend .
docker run -p 3000:3000 wealth-advisor-frontend
```

## 🔧 Configuration

### Backend Environment Variables

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
COHERE_API_KEY=your_cohere_api_key
LANGCHAIN_API_KEY=your_langchain_api_key

# Model Configuration
MODEL_NAME=gpt-4o
TEMPERATURE=0.0
MAX_TOKENS=4000

# RAG Configuration
CHUNK_SIZE=750
CHUNK_OVERLAP=100
VECTOR_STORE_TYPE=qdrant
EMBEDDING_MODEL=text-embedding-3-small
```

### Frontend Environment Variables

```env
# Backend API URL
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Development settings
NEXT_PUBLIC_DEV_MODE=true
```

## 📊 API Endpoints

### Core Endpoints
- `POST /api/v1/advisor/query` - Query the wealth advisor
- `POST /api/v1/rag/query` - Direct RAG queries
- `GET /api/v1/tools/search` - Tavily search
- `GET /api/v1/tools/arxiv` - ArXiv search
- `GET /api/v1/tools/yfinance` - Stock data

### Analytics & Monitoring
- `GET /health` - System health check
- `GET /api/v1/analytics/usage` - Usage analytics
- `GET /api/v1/analytics/performance` - Performance metrics

### Evaluation
- `POST /api/v1/evaluation/evaluate` - System evaluation
- `POST /api/v1/evaluation/generate-tests` - Generate test datasets

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Tests
```bash
cd backend
python test_api.py
```

## 🚀 Deployment

### Production Setup

1. **Environment Variables**: Set all required API keys
2. **Database**: Configure persistent vector store
3. **Monitoring**: Add logging and metrics
4. **Security**: Implement authentication
5. **Scaling**: Use load balancers

### Cloud Deployment

#### Vercel (Frontend)
```bash
cd frontend
vercel --prod
```

#### Railway/Render (Backend)
```bash
cd backend
# Deploy using Railway CLI or Render dashboard
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

- **Issues**: Create an issue in the repository
- **Documentation**: Check `/docs` endpoints
- **API Reference**: Visit `/docs` for interactive API docs

## 🔮 Roadmap

- [ ] Authentication and user management
- [ ] Multi-tenant support
- [ ] Advanced analytics dashboard
- [ ] Mobile app
- [ ] WebSocket real-time updates
- [ ] Advanced document processing
- [ ] More financial data sources
- [ ] Dark mode support
- [ ] Voice input/output
- [ ] PDF report generation
