# Wealth Advisor AI Frontend

A modern Next.js frontend for the Wealth Advisor AI Copilot with a beautiful chat interface and settings management.

## 🚀 Features

### Chat Interface
- **Real-time Chat**: Interactive chat with AI advisor
- **Markdown Support**: Rich text formatting in responses
- **Tool Integration**: Visual indicators for used tools
- **Auto-scroll**: Smooth message flow
- **Copy Messages**: One-click message copying
- **Error Handling**: Graceful error display
- **Loading States**: Beautiful loading animations

### Settings Management
- **API Key Management**: Secure storage of OpenAI, Tavily, LangSmith, and Cohere API keys
- **Password Visibility**: Toggle to show/hide API keys
- **Backend Connection**: Real-time backend status monitoring
- **Connection Testing**: Test backend connectivity
- **Local Storage**: Persistent API key storage
- **Validation**: Input validation for API keys

## 🛠️ Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Set environment variables
echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

### Environment Variables

Create a `.env.local` file:

```env
# Backend API URL
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Development settings
NEXT_PUBLIC_DEV_MODE=true
```

## 📱 Usage

### Chat Interface
1. Open the application in your browser
2. Type your financial questions in the chat input
3. View AI responses with tool indicators
4. Use quick action buttons for common questions

### Settings
1. Click the settings icon (⚙️) in the header
2. Enter your API keys:
   - **OpenAI API Key**: For GPT-4 responses
   - **Tavily API Key**: For web search functionality
   - **LangSmith API Key**: For monitoring and evaluation
   - **Cohere API Key**: For reranking and context compression
3. Click "Save" to store the keys
4. Test the backend connection

## 🔧 API Keys

### Required API Keys

#### OpenAI API Key
- **Purpose**: Generate AI responses
- **Format**: `sk-...`
- **Get it**: [OpenAI Platform](https://platform.openai.com/api-keys)

#### Tavily API Key
- **Purpose**: Web search functionality
- **Format**: `tvly-...`
- **Get it**: [Tavily](https://tavily.com/)

#### LangSmith API Key
- **Purpose**: Monitoring and evaluation
- **Format**: `ls_...`
- **Get it**: [LangSmith](https://smith.langchain.com/)

#### Cohere API Key
- **Purpose**: Reranking and context compression
- **Format**: `...`
- **Get it**: [Cohere](https://cohere.ai/)

## 🏗️ Architecture

### Components
- `ChatInterface.tsx`: Main chat interface
- `Message.tsx`: Individual message component
- `ChatInput.tsx`: Message input with auto-resize
- `Settings.tsx`: API key management modal
- `ToolSelector.tsx`: Tool status indicators
- `LoadingSpinner.tsx`: Loading animations

### Hooks
- `useChat.ts`: Chat state management
- `useAnalytics.ts`: Analytics data (future)

### API Integration
- `api.ts`: Backend API client
- `types.ts`: TypeScript type definitions

## 🎨 Styling

### Tailwind CSS
- Custom color palette
- Responsive design
- Dark/light mode support (coming soon)
- Smooth animations with Framer Motion

### Design System
- **Primary Colors**: Blue gradient (#3B82F6 to #8B5CF6)
- **Secondary Colors**: Gray scale for text and backgrounds
- **Success**: Green for positive states
- **Error**: Red for error states
- **Warning**: Yellow for warnings

## 🔒 Security

### API Key Storage
- **Frontend**: Stored in localStorage (for development)
- **Backend**: Environment variables
- **Production**: Use secure key management systems

### Best Practices
- Never commit API keys to version control
- Use environment variables in production
- Implement proper authentication (future)
- Regular key rotation

## 🚀 Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Docker
```bash
# Build image
docker build -t wealth-advisor-frontend .

# Run container
docker run -p 3000:3000 wealth-advisor-frontend
```

## 🧪 Testing

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run e2e tests
npm run test:e2e
```

## 📊 Performance

### Optimization
- **Code Splitting**: Automatic with Next.js
- **Image Optimization**: Built-in Next.js Image component
- **Bundle Analysis**: Use `@next/bundle-analyzer`
- **Caching**: Static generation where possible

### Monitoring
- **Error Tracking**: Sentry integration (future)
- **Analytics**: Google Analytics (future)
- **Performance**: Core Web Vitals monitoring

## 🔮 Roadmap

### Short Term
- [ ] Dark mode support
- [ ] Voice input/output
- [ ] File upload for documents
- [ ] Export chat history

### Medium Term
- [ ] User authentication
- [ ] Multi-tenant support
- [ ] Advanced analytics dashboard
- [ ] Mobile app

### Long Term
- [ ] Real-time collaboration
- [ ] Advanced document processing
- [ ] Integration with more financial data sources
- [ ] AI model fine-tuning interface

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
- **Documentation**: Check the main README
- **API Reference**: Visit `/docs` for backend API docs 