import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ContextParser:
    """
    A parser class to extract and structure context from various sources:
    - Tavily search results
    - ArXiv papers
    - yfinance data
    - AI RAG tool outputs
    """
    
    def __init__(self):
        self.tavily_patterns = {
            'title': r'<title>(.*?)</title>',
            'content': r'<content>(.*?)</content>',
            'url': r'<url>(.*?)</url>',
            'score': r'<score>(.*?)</score>'
        }
        
        self.arxiv_patterns = {
            'title': r'Title:\s*(.*?)(?:\n|$)',
            'authors': r'Authors:\s*(.*?)(?:\n|$)',
            'abstract': r'Abstract:\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            'categories': r'Categories:\s*(.*?)(?:\n|$)',
            'doi': r'DOI:\s*(.*?)(?:\n|$)',
            'arxiv_id': r'arXiv:(\d+\.\d+)',
            'date': r'Date:\s*(.*?)(?:\n|$)'
        }
        
        self.yfinance_patterns = {
            'ticker': r'Ticker:\s*([A-Z]+)',
            'price': r'Price:\s*\$?([\d,]+\.?\d*)',
            'change': r'Change:\s*([+-]?\$?[\d,]+\.?\d*)',
            'volume': r'Volume:\s*([\d,]+)',
            'market_cap': r'Market Cap:\s*\$?([\d,]+\.?\d*[KMB]?)',
            'pe_ratio': r'P/E Ratio:\s*([\d,]+\.?\d*)',
            'dividend_yield': r'Dividend Yield:\s*([\d,]+\.?\d*%)'
        }
        
        self.rag_patterns = {
            'query': r'Query:\s*(.*?)(?:\n|$)',
            'response': r'Response:\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            'sources': r'Sources:\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            'confidence': r'Confidence:\s*([\d,]+\.?\d*%)',
            'timestamp': r'Timestamp:\s*(.*?)(?:\n|$)'
        }
    
    async def parse_tavily_context(self, context: str) -> Dict[str, Any]:
        """
        Parse Tavily search context and extract structured data
        """
        try:
            parsed_data = {
                'source': 'tavily',
                'results': [],
                'total_results': 0,
                'query_time': None
            }
            
            # Extract individual results
            results_blocks = re.split(r'<result>', context)
            
            for block in results_blocks[1:]:  # Skip first empty block
                result = {}
                for field, pattern in self.tavily_patterns.items():
                    match = re.search(pattern, block, re.DOTALL)
                    if match:
                        result[field] = match.group(1).strip()
                
                if result:
                    parsed_data['results'].append(result)
            
            parsed_data['total_results'] = len(parsed_data['results'])
            return parsed_data
        except Exception as e:
            logger.error(f"Error parsing Tavily context: {e}")
            raise
    
    async def parse_arxiv_context(self, context: str) -> Dict[str, Any]:
        """
        Parse ArXiv paper context and extract structured data
        """
        try:
            parsed_data = {
                'source': 'arxiv',
                'papers': [],
                'total_papers': 0
            }
            
            # Split by paper blocks (assuming papers are separated by double newlines)
            paper_blocks = re.split(r'\n\n+', context.strip())
            
            for block in paper_blocks:
                if not block.strip():
                    continue
                    
                paper = {}
                for field, pattern in self.arxiv_patterns.items():
                    match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
                    if match:
                        paper[field] = match.group(1).strip()
                
                if paper:
                    parsed_data['papers'].append(paper)
            
            parsed_data['total_papers'] = len(parsed_data['papers'])
            return parsed_data
        except Exception as e:
            logger.error(f"Error parsing ArXiv context: {e}")
            raise
    
    async def parse_yfinance_context(self, context: str) -> Dict[str, Any]:
        """
        Parse yfinance data context and extract structured data
        """
        try:
            parsed_data = {
                'source': 'yfinance',
                'stocks': [],
                'total_stocks': 0
            }
            
            # Split by stock blocks
            stock_blocks = re.split(r'Stock:\s*', context)
            
            for block in stock_blocks[1:]:  # Skip first empty block
                stock = {}
                for field, pattern in self.yfinance_patterns.items():
                    match = re.search(pattern, block, re.IGNORECASE)
                    if match:
                        stock[field] = match.group(1).strip()
                
                if stock:
                    parsed_data['stocks'].append(stock)
            
            parsed_data['total_stocks'] = len(parsed_data['stocks'])
            return parsed_data
        except Exception as e:
            logger.error(f"Error parsing yfinance context: {e}")
            raise
    
    async def parse_rag_context(self, context: str) -> Dict[str, Any]:
        """
        Parse AI RAG tool context and extract structured data
        """
        try:
            parsed_data = {
                'source': 'ai_rag',
                'interactions': [],
                'total_interactions': 0
            }
            
            # Split by interaction blocks
            interaction_blocks = re.split(r'Interaction:\s*', context)
            
            for block in interaction_blocks[1:]:  # Skip first empty block
                interaction = {}
                for field, pattern in self.rag_patterns.items():
                    match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
                    if match:
                        interaction[field] = match.group(1).strip()
                
                if interaction:
                    parsed_data['interactions'].append(interaction)
            
            parsed_data['total_interactions'] = len(parsed_data['interactions'])
            return parsed_data
        except Exception as e:
            logger.error(f"Error parsing RAG context: {e}")
            raise
    
    async def parse_generic_context(self, context: str) -> Dict[str, Any]:
        """
        Generic parser that attempts to detect and parse any context type
        """
        try:
            context_lower = context.lower()
            
            if 'tavily' in context_lower or '<result>' in context:
                return await self.parse_tavily_context(context)
            elif 'arxiv' in context_lower or 'categories:' in context_lower:
                return await self.parse_arxiv_context(context)
            elif 'yfinance' in context_lower or 'ticker:' in context_lower:
                return await self.parse_yfinance_context(context)
            elif 'rag' in context_lower or 'query:' in context_lower:
                return await self.parse_rag_context(context)
            else:
                # Fallback: try to extract any structured data
                return {
                    'source': 'unknown',
                    'raw_content': context,
                    'extracted_data': await self._extract_any_data(context)
                }
        except Exception as e:
            logger.error(f"Error in generic context parsing: {e}")
            raise
    
    async def _extract_any_data(self, context: str) -> Dict[str, Any]:
        """
        Extract any recognizable data patterns from unknown context
        """
        try:
            extracted = {}
            
            # Look for common patterns
            patterns = {
                'urls': r'https?://[^\s<>"]+',
                'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'dates': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
                'numbers': r'\$?[\d,]+\.?\d*',
                'percentages': r'[\d,]+\.?\d*%'
            }
            
            for key, pattern in patterns.items():
                matches = re.findall(pattern, context)
                if matches:
                    extracted[key] = matches
            
            return extracted
        except Exception as e:
            logger.error(f"Error extracting data patterns: {e}")
            return {}
    
    async def to_string(self, parsed_data: Dict[str, Any]) -> str:
        """
        Convert parsed data back to a formatted string
        """
        try:
            if parsed_data['source'] == 'tavily':
                return await self._tavily_to_string(parsed_data)
            elif parsed_data['source'] == 'arxiv':
                return await self._arxiv_to_string(parsed_data)
            elif parsed_data['source'] == 'yfinance':
                return await self._yfinance_to_string(parsed_data)
            elif parsed_data['source'] == 'ai_rag':
                return await self._rag_to_string(parsed_data)
            else:
                return await self._generic_to_string(parsed_data)
        except Exception as e:
            logger.error(f"Error converting to string: {e}")
            raise
    
    async def _tavily_to_string(self, data: Dict[str, Any]) -> str:
        result = f"Tavily Search Results ({data['total_results']} results)\n"
        result += "=" * 50 + "\n\n"
        
        for i, result_item in enumerate(data['results'], 1):
            result += f"Result {i}:\n"
            result += f"Title: {result_item.get('title', 'N/A')}\n"
            result += f"URL: {result_item.get('url', 'N/A')}\n"
            result += f"Score: {result_item.get('score', 'N/A')}\n"
            result += f"Content: {result_item.get('content', 'N/A')[:200]}...\n\n"
        
        return result
    
    async def _arxiv_to_string(self, data: Dict[str, Any]) -> str:
        result = f"ArXiv Papers ({data['total_papers']} papers)\n"
        result += "=" * 50 + "\n\n"
        
        for i, paper in enumerate(data['papers'], 1):
            result += f"Paper {i}:\n"
            result += f"Title: {paper.get('title', 'N/A')}\n"
            result += f"Authors: {paper.get('authors', 'N/A')}\n"
            result += f"Categories: {paper.get('categories', 'N/A')}\n"
            result += f"DOI: {paper.get('doi', 'N/A')}\n"
            result += f"Date: {paper.get('date', 'N/A')}\n"
            result += f"Abstract: {paper.get('abstract', 'N/A')[:300]}...\n\n"
        
        return result
    
    async def _yfinance_to_string(self, data: Dict[str, Any]) -> str:
        result = f"YFinance Data ({data['total_stocks']} stocks)\n"
        result += "=" * 50 + "\n\n"
        
        for i, stock in enumerate(data['stocks'], 1):
            result += f"Stock {i}:\n"
            result += f"Ticker: {stock.get('ticker', 'N/A')}\n"
            result += f"Price: ${stock.get('price', 'N/A')}\n"
            result += f"Change: {stock.get('change', 'N/A')}\n"
            result += f"Volume: {stock.get('volume', 'N/A')}\n"
            result += f"Market Cap: ${stock.get('market_cap', 'N/A')}\n"
            result += f"P/E Ratio: {stock.get('pe_ratio', 'N/A')}\n"
            result += f"Dividend Yield: {stock.get('dividend_yield', 'N/A')}\n\n"
        
        return result
    
    async def _rag_to_string(self, data: Dict[str, Any]) -> str:
        result = f"AI RAG Interactions ({data['total_interactions']} interactions)\n"
        result += "=" * 50 + "\n\n"
        
        for i, interaction in enumerate(data['interactions'], 1):
            result += f"Interaction {i}:\n"
            result += f"Query: {interaction.get('query', 'N/A')}\n"
            result += f"Response: {interaction.get('response', 'N/A')[:300]}...\n"
            result += f"Sources: {interaction.get('sources', 'N/A')}\n"
            result += f"Confidence: {interaction.get('confidence', 'N/A')}\n"
            result += f"Timestamp: {interaction.get('timestamp', 'N/A')}\n\n"
        
        return result
    
    async def _generic_to_string(self, data: Dict[str, Any]) -> str:
        result = f"Generic Context Data\n"
        result += "=" * 50 + "\n\n"
        result += f"Source: {data['source']}\n"
        result += f"Raw Content: {data['raw_content'][:500]}...\n\n"
        
        if 'extracted_data' in data:
            result += "Extracted Data:\n"
            for key, values in data['extracted_data'].items():
                result += f"{key.title()}: {values[:5]}\n"
        
        return result 