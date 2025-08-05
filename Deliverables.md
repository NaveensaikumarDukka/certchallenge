Task 1: Defining your Problem and Audience

**✅ Deliverables**

1. Write a succinct 1-sentence description of the problem
    Financial advisors in the wealth and asset management industry face growing challenges while assesing the clients profiles in suggesting the appropiate investment portfolios.
2. Write 1-2 paragraphs on why this is a problem for your specific user
    Financial Advisors challenges are like,
    1) Analyzing vast amounts of client data manually.
    2) Keeping up with market trends and regulatory changes.
    3) Personalizing advice for a diverse client base.
    4) Time-consuming portfolio rebalancing and risk assessments.
    5) Low scalability of advisory services.

    These limitations hinder the ability of advisors to deliver timely, tailored, and data-driven investment advice.

    Financial Advisors faces the above problems because of tidous existing manual process in checking everything related to client and market research which is time consuming in proposing the tailored results.


Task 2:Propose a Solution

**✅ Deliverables**

1. Write 1-2 paragraphs on your proposed solution.  How will it look and feel to the user?
    Build an AI-powered Wealth Advisor Copilot — a platform that helps financial advisors:
    1) Analyze client profiles, goals, and risk tolerance.
    2) Generate personalized investment strategies.
    3) Monitor portfolios in real time with smart alerts.
    4) Automate reporting, compliance, and document summarization.
    5) Enhance client engagement with AI-driven communication.

This copilot acts as a digital analyst, assistant, and compliance checker — improving accuracy, efficiency, and personalization.

Key Features to Develop
1. Client Profile Analyzer
Ingests structured/unstructured data from CRM, KYC, and financial statements.

Extracts client risk appetite, financial goals, and asset allocations using NLP and ML.

2. Smart Portfolio Builder
Recommends diversified portfolios using optimization algorithms.

Aligns with client goals (retirement, tax savings, etc.) and current market conditions.

Uses modern portfolio theory (MPT), ESG factors, or factor-based investing models.

3. AI-Powered Rebalancing & Alerts
Monitors market movements and triggers rebalancing suggestions.

Alerts advisors of risks (e.g., overexposure, volatility) or missed opportunities.

4. Natural Language Chat Assistant
Enables advisors to ask queries like:
"What are top-performing funds for a 45-year-old moderate risk investor?"

Provides responses using LLMs (e.g., GPT-4) based on internal data and market feeds.

5. Automated Report Generation
Generates investment summaries, performance reports, and compliance documents.

Customizable by advisor or firm branding.

6. Client Sentiment & Communication Coach
Analyzes client emails or call transcripts to detect sentiment.

Suggests personalized messages and next-best actions.


2. Describe the tools you plan to use in each part of your stack.  Write one sentence on why you made each tooling choice.
    1. LLM - gpt-4o - larger context windows
    2. Embedding Model - text-embedding-3-small - high accuracy and low latency
    3. Orchestration - RAG(Custom data), Tavily(Web search), Arxiv(research papers) and Yahoo Finance(Financial Stock Data)
    4. Vector Database - Qdrant - large-scale, high-performance vector search
    5. Monitoring - Langsmith - granular visibility into application tracking.
    6. Evaluation - RAGAS Metrics - RAG metrics focus on evaluating the effectiveness of both the retrieval and generation components of the RAG pipeline
    7. User Interface - React.JS - better modularity and fit for vercel prod deployment.
    8. (Optional) Serving & Inference
3. Where will you use an agent or agents?  What will you use “agentic reasoning” for in your app?
    Using the Agent here in building the LangGraph and bidding the toolbelt to it.


Task 3: Dealing with the Data
**✅ Deliverables**

1. Describe all of your data sources and external APIs, and describe what you’ll use them for.
    RAG(Custom data), Tavily(Web search), Arxiv(research papers) and Yahoo Finance(Financial Stock Data)
2. Describe the default chunking strategy that you will use.  Why did you make this decision?
    text-embedding-3-small because of high accuracy and low latency using RecursiveCharacterTextSplitter

Task 4: Building a Quick End-to-End Agentic RAG Prototype

**✅ Deliverables**

1. Build an end-to-end prototype and deploy it to a *local* endpoint
Have built an end-to-end application and deployed to local endpoint using FastAPI Backend, REACT JS Front end and the complied notebook.

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    FRONTEND LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                │
│  │   Chat Interface │    │   Settings Modal │    │   Tool Status   │                │
│  │                 │    │                 │    │                 │                │
│  │ • User Input    │    │ • API Key Mgmt  │    │ • Tool Health   │                │
│  │ • Message Display│    │ • Local Storage │    │ • Connection    │                │
│  │ • Tool Badges   │    │ • Auto-save     │    │ • Status Check  │                │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                │
│           │                       │                       │                        │
│           └───────────────────────┼───────────────────────┘                        │
│                                   │                                                │
└───────────────────────────────────┼────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                   API GATEWAY                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                │
│  │   Next.js API   │    │   FastAPI Backend│    │   CORS Middleware│                │
│  │   Routes        │    │   Endpoints     │    │                 │                │
│  │                 │    │                 │    │                 │                │
│  │ • /api/settings │    │ • /api/v1/query │    │ • Cross-origin  │                │
│  │ • /api/chat     │    │ • /api/v1/tools │    │ • Authentication│                │
│  │ • /api/status   │    │ • /api/v1/health│    │ • Rate Limiting │                │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                │
│           │                       │                                                │
│           └───────────────────────┼────────────────────────────────────────────────┘
│                                   │
└───────────────────────────────────┼────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                  BACKEND LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │                        WEALTH ADVISOR SERVICE                                  │ │
│  │                                                                                 │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │ │
│  │  │ Query Router│  │ Tool Manager│  │ Response    │  │ Analytics   │          │ │
│  │  │             │  │             │  │ Combiner    │  │ Tracker     │          │ │
│  │  │ • Categorize│  │ • Initialize│  │ • Merge     │  │ • Usage     │          │ │
│  │  │ • Route     │  │ • Reinit    │  │ • Format    │  │ • Metrics   │          │ │
│  │  │ • Validate  │  │ • Monitor   │  │ • Context   │  │ • Health    │          │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘          │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                   │                                                │
│                                   ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │                              TOOL ORCHESTRATION                                │ │
│  │                                                                                 │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │ │
│  │  │   TAVILY    │  │    ARXIV    │  │  YFINANCE   │  │     RAG     │          │ │
│  │  │   SEARCH    │  │   RESEARCH  │  │   STOCK     │  │  KNOWLEDGE  │          │ │
│  │  │             │  │             │  │    DATA     │  │    BASE     │          │ │
│  │  │ • Web Search│  │ • Papers    │  │ • Real-time │  │ • PDF Docs  │          │ │
│  │  │ • News      │  │ • Academic  │  │ • Prices    │  │ • Vector DB │          │ │
│  │  │ • Market    │  │ • Research  │  │ • Financials│  │ • Embeddings│          │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘          │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────┼────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 DATA LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                │
│  │   PDF Processor │    │   Vector Store  │    │   API Services  │                │
│  │                 │    │                 │    │                 │                │
│  │ • PyMuPDF       │    │ • Qdrant DB     │    │ • OpenAI API    │                │
│  │ • Text Extract  │    │ • Embeddings    │    │ • Tavily API    │                │
│  │ • Chunking      │    │ • Similarity    │    │ • ArXiv API     │                │
│  │ • Metadata      │    │ • Retrieval     │    │ • YFinance API  │                │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                │
│           │                       │                       │                        │
│           └───────────────────────┼───────────────────────┘                        │
│                                   │                                                │
└───────────────────────────────────┼────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 STORAGE LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                │
│  │   Local Storage │    │   Session Cache │    │   File System   │                │
│  │                 │    │                 │    │                 │                │
│  │ • API Keys      │    │ • Environment   │    │ • PDF Documents │                │
│  │ • User Prefs    │    │ • Variables     │    │ • Log Files     │                │
│  │ • Chat History  │    │ • Temp Data     │    │ • Config Files  │                │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────────────┘


Task 5: Creating a Golden Test Data Set

**✅ Deliverables**

1. Assess your pipeline using the RAGAS framework including key metrics faithfulness, response relevance, context precision, and context recall.  Provide a table of your output results.

| context_recall | faithfulness |factual_correctness | answer_relevancy | context_entity_recall |noise_sensitivity_relevant
|-----------------|-----------------|-----------------|-----------------|-----------------|-----------------|-----------------|
|  0.9479   | 0.3912    | 0.2850    |0.8706    |0.5350    |0.0809   |


2. What conclusions can you draw about the performance and effectiveness of your pipeline with this information?
    From the above RAGAS Metrics information, it clearly states that the output context is excellent, answer relevancy is good. Hence the output is aligned with the input and generated the relevant answers.

Task 6: The Benefits of Advanced Retrieval

**✅ Deliverables**

1. Describe the retrieval techniques that you plan to try and to assess in your application.  Write one sentence on why you believe each technique will be useful for your use case.
    I want to test my application using contextual retriever for to see the output is aligned to the input in context.
    Also, on the BM25 retriever for specific or extact word match like in quering the AAPL, GOOGL, TSLA Stocks.
2. Test a host of advanced retrieval techniques on your application.
    I would like to assess my application on different retriever techniques like BM25, etc,.

Task 7: Assessing Performance

**✅ Deliverables**

1. How does the performance compare to your original RAG application?  Test the fine-tuned embedding model using the RAGAS frameworks to quantify any improvements.  Provide results in a table.

| Retriever | context_recall | faithfulness |factual_correctness | answer_relevancy | context_entity_recall |noise_sensitivity_relevant
|-----------------|-----------------|-----------------|-----------------|-----------------|-----------------|-----------------|
| Basic    | 0.9479   | 0.3912    | 0.2850    |0.8706     |0.5350    |0.0809   |
| Contextaul Cohere Rerank   | 0.9694    | 0.5992    | 0.4900    |0.9583    |0.2801    |0.1693    |

Here, when compared to the basic retriever, we achieved good results from the advanced Contextual compression cohere rerank retriever.
which shows the importance of advanced retrieval mechanisms.

2. Articulate the changes that you expect to make to your app in the second half of the course. How will you improve your application?
    I want to improve the output through fine tuning in order to aling with the input context more also want to assess my application on BM25 Retriver.