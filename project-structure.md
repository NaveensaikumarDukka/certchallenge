# Wealth Advisor AI Copilot - Project Structure

```
wealth-advisor-ai/
├── backend/                    # FastAPI Backend
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   ├── README.md
│   ├── test_api.py
│   ├── .env
│   └── services/
│       ├── __init__.py
│       ├── context_parser.py
│       ├── rag_service.py
│       ├── wealth_advisor_service.py
│       └── evaluation_service.py
│
├── frontend/                   # Next.js Frontend
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── .env.local
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── globals.css
│   │   │   └── api/
│   │   │       └── chat/
│   │   │           └── route.ts
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── Message.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ToolSelector.tsx
│   │   │   ├── Analytics.tsx
│   │   │   └── ui/
│   │   │       ├── Button.tsx
│   │   │       ├── Card.tsx
│   │   │       └── Badge.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   ├── types.ts
│   │   │   └── utils.ts
│   │   └── hooks/
│   │       ├── useChat.ts
│   │       └── useAnalytics.ts
│   └── README.md
│
├── docker-compose.yml          # Full stack deployment
├── .gitignore
└── README.md                   # Main project README 