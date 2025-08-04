import asyncio
import logging
import os
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import uuid
from tavily import TavilyClient

# LangChain imports
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from typing import Any

# Local imports
from .rag_service import RAGService

logger = logging.getLogger(__name__)

class WealthAdvisorService:
    """
    Main service for wealth management and financial advisory
    """
    
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service
        self.tools = {}
        self.model = None
        self.usage_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "tool_usage": {},
            "query_categories": {},
            "response_times": []
        }
        self.initialized = False
        
    async def initialize(self):
        """Initialize the wealth advisor service"""
        try:
            logger.info("Initializing Wealth Advisor Service...")
            
            # Initialize tools
            await self._initialize_tools()
            
            # Initialize model (no binding needed since tools are simple functions)
            self.model = ChatOpenAI(model="gpt-4o", temperature=0)
            
            # Initialize RAG service
            await self.rag_service.initialize()
            
            self.initialized = True
            logger.info("Wealth Advisor Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Wealth Advisor Service: {e}")
            raise
    
    async def reinitialize_tools(self):
        """Reinitialize tools (for when API keys are updated)"""
        try:
            logger.info("Reinitializing tools...")
            
            # Reinitialize tools
            await self._initialize_tools()
            
            # No need to rebind since tools are simple functions
            logger.info("Tools reinitialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to reinitialize tools: {e}")
            raise
    
    async def _initialize_tools(self):
        """Initialize all available tools"""
        try:
            # Clear existing tools
            self.tools = {}
            
            # Tavily search tool
            tavily_key = os.environ.get("TAVILY_API_KEY")
            if tavily_key and tavily_key.strip():
                try:
                    self.tools['tavily_search'] = self._create_tavily_tool()
                    logger.info("Tavily search tool initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize Tavily search tool: {e}")
            else:
                logger.warning("TAVILY_API_KEY not found or empty, skipping Tavily search tool")
            
            # ArXiv tool (no API key required)
            try:
                self.tools['arxiv_search'] = self._create_arxiv_tool()
                logger.info("ArXiv search tool initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize ArXiv search tool: {e}")
            
            # YFinance tool (no API key required)
            try:
                self.tools['yfinance_data'] = self._create_yfinance_tool()
                logger.info("YFinance tool initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize YFinance tool: {e}")
            
            # RAG tool
            try:
                self.tools['rag_query'] = self._create_rag_tool()
                logger.info("RAG tool initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize RAG tool: {e}")
            
            logger.info(f"Successfully initialized {len(self.tools)} tools: {list(self.tools.keys())}")
            
        except Exception as e:
            logger.error(f"Error initializing tools: {e}")
            # Don't raise the exception, just log it and continue with available tools
    
    def _create_yfinance_tool(self):
        """Create a custom yfinance tool"""
        def yfinance_data(symbol: str) -> str:
            """Get real-time stock data from Yahoo Finance. Use this tool to get current stock prices, market data, and financial metrics for any stock symbol."""
            try:
                import yfinance as yf
                
                # Clean and validate symbol
                symbol = symbol.upper().strip()
                if not symbol or len(symbol) > 10:
                    return f"Invalid stock symbol: {symbol}"
                
                logger.info(f"Fetching yfinance data for symbol: {symbol}")
                ticker = yf.Ticker(symbol)
                
                # Get basic info first
                info = ticker.info
                
                # Check if we got valid data
                if not info or info.get('regularMarketPrice') is None:
                    return f"No data found for stock symbol: {symbol}. Please verify the symbol is correct."
                
                # Format the result
                result = f"Stock: {symbol}\n"
                result += f"Price: ${info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))}\n"
                result += f"Previous Close: ${info.get('previousClose', 'N/A')}\n"
                result += f"Change: {info.get('regularMarketChange', 'N/A')}\n"
                result += f"Change %: {info.get('regularMarketChangePercent', 'N/A')}%\n"
                result += f"Volume: {info.get('volume', 'N/A'):,}\n" if info.get('volume') else "Volume: N/A\n"
                result += f"Market Cap: ${info.get('marketCap', 'N/A'):,}\n" if info.get('marketCap') else "Market Cap: N/A\n"
                result += f"P/E Ratio: {info.get('trailingPE', 'N/A')}\n"
                result += f"Dividend Yield: {info.get('dividendYield', 'N/A')}\n"
                result += f"52 Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}\n"
                result += f"52 Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}\n"
                
                logger.info(f"Successfully retrieved data for {symbol}")
                return result
                
            except Exception as e:
                logger.error(f"Error getting yfinance data for {symbol}: {e}")
                if "404" in str(e):
                    return f"Stock symbol '{symbol}' not found. Please verify the symbol is correct."
                elif "HTTP Error" in str(e):
                    return f"Network error while fetching data for {symbol}. Please try again later."
                else:
                    return f"Error getting data for {symbol}: {str(e)}"
        
        return yfinance_data
    
    def _create_arxiv_tool(self):
        """Create a custom ArXiv search tool"""
        def arxiv_search(query: str) -> str:
            """Search for academic papers on ArXiv. Use this tool to find research papers on financial topics, investment strategies, or economic analysis."""
            try:
                import arxiv
                search = arxiv.Search(
                    query=query,
                    max_results=5,
                    sort_by=arxiv.SortCriterion.SubmittedDate
                )
                
                results = []
                for result in search.results():
                    results.append({
                        'title': result.title,
                        'authors': [author.name for author in result.authors],
                        'summary': result.summary[:200] + '...' if len(result.summary) > 200 else result.summary,
                        'published': result.published.strftime('%Y-%m-%d'),
                        'url': result.entry_id
                    })
                
                if not results:
                    return f"No papers found for query: {query}"
                
                output = f"Found {len(results)} papers for '{query}':\n\n"
                for i, paper in enumerate(results, 1):
                    output += f"{i}. {paper['title']}\n"
                    output += f"   Authors: {', '.join(paper['authors'])}\n"
                    output += f"   Published: {paper['published']}\n"
                    output += f"   Summary: {paper['summary']}\n"
                    output += f"   URL: {paper['url']}\n\n"
                
                return output
            except Exception as e:
                return f"Error searching ArXiv for '{query}': {str(e)}"
        
        return arxiv_search
    
    def _create_tavily_tool(self):
        """Create a custom Tavily search tool"""
        def tavily_search(query: str) -> str:
            """Search the web for current information using Tavily. Use this tool to get the latest news, market updates, and real-time information."""
            try:
                import requests
                
                api_key = os.environ.get("TAVILY_API_KEY")
                if not api_key:
                    logger.warning("TAVILY_API_KEY not found in environment variables")
                    return "Tavily API key not configured. Please set TAVILY_API_KEY in your environment variables."
                
                if not api_key.strip():
                    logger.warning("TAVILY_API_KEY is empty")
                    return "Tavily API key is empty. Please provide a valid API key."
                
                
                logger.info(f"Making Tavily API request for query: {query}")
                tavily_client = TavilyClient(api_key=api_key)
                response = tavily_client.search(query)
                               
                if response is None:
                    logger.info(f"No results found for query: {query}")
                    return f"No results found for query: {query}"
                
                logger.info(f"Found {len(response['results'])} results for query: {query}")
                output = f"Found {len(response['results'])} results for '{query}':\n\n"
                
                for result in response['results']:
                    output += f"{result['title']}\n"
                    output += f"{result['content']}\n"
                    output += f"{result['url']}\n"
                    
                
                return output
            except requests.exceptions.Timeout:
                logger.error("Tavily API request timed out")
                return "Tavily search timed out. Please try again."
            except requests.exceptions.RequestException as e:
                logger.error(f"Tavily API request failed: {e}")
                return f"Tavily API request failed: {str(e)}"
            except Exception as e:
                logger.error(f"Unexpected error in Tavily search: {e}")
                return f"Error searching Tavily for '{query}': {str(e)}"
        
        return tavily_search
    
    def _create_rag_tool(self):
        """Create a RAG query tool"""
        def rag_query(question: str) -> str:
            """Query the knowledge base for wealth management information. Use this tool to get information from uploaded documents and financial resources."""
            try:
                # This would be called asynchronously in a real implementation
                # For now, we'll return a placeholder
                return f"RAG response for: {question}"
            except Exception as e:
                return f"Error in RAG query: {str(e)}"
        
        return rag_query
    
    async def process_query(self, question: str) -> Dict[str, Any]:
        """Process a query using the wealth advisor"""
        start_time = datetime.now()
        
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Processing query: {question}")
            
            # Update usage stats
            self.usage_stats["total_queries"] += 1
            
            # Determine query category
            category = self._categorize_query(question)
            self.usage_stats["query_categories"][category] = self.usage_stats["query_categories"].get(category, 0) + 1
            
            # Process the query
            response = await self._process_with_tools(question)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            self.usage_stats["response_times"].append(processing_time)
            
            # Update success stats
            self.usage_stats["successful_queries"] += 1
            
            return {
                "response": response["response"],
                "context": response.get("context", []),
                "tools_used": response.get("tools_used", []),
                "confidence": response.get("confidence", 0.8),
                "processing_time": processing_time,
                "category": category
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            self.usage_stats["failed_queries"] += 1
            raise
    
    async def _process_with_tools(self, question: str) -> Dict[str, Any]:
        """Process query using all available tools intelligently"""
        try:
            tools_used = []
            context = []
            tool_responses = []
            
            logger.info(f"Processing query: '{question}' with {len(self.tools)} available tools: {list(self.tools.keys())}")
            
            # 1. Always use Tavily search for current information (most comprehensive)
            try:
                tavily_tool = self.tools.get('tavily_search')
                if tavily_tool:
                    logger.info("Using Tavily search tool")
                    tools_used.append('tavily_search')
                    search_result = await asyncio.to_thread(tavily_tool, question)
                    logger.info(f"Tavily search result: {search_result[:100]}..." if search_result else "No result")
                    if search_result and "Error" not in search_result:
                        tool_responses.append(f"Current Information: {search_result}")
                        context.append("Search results from Tavily")
                else:
                    logger.warning("Tavily tool not available")
            except Exception as e:
                logger.warning(f"Tavily search failed: {e}")
            
            # 2. Always use ArXiv for academic/research context
            try:
                arxiv_tool = self.tools.get('arxiv_search')
                if arxiv_tool:
                    logger.info("Using ArXiv search tool")
                    tools_used.append('arxiv_search')
                    arxiv_result = await asyncio.to_thread(arxiv_tool, question)
                    logger.info(f"ArXiv search result: {arxiv_result[:100]}..." if arxiv_result else "No result")
                    if arxiv_result and "No papers found" not in arxiv_result and "Error" not in arxiv_result:
                        tool_responses.append(f"Academic Research: {arxiv_result}")
                        context.append("Academic papers from ArXiv")
                else:
                    logger.warning("ArXiv tool not available")
            except Exception as e:
                logger.warning(f"ArXiv search failed: {e}")
            
            # 3. Check for stock symbols in the question and get market data
            try:
                import re
                # Look for potential stock symbols (2-5 uppercase letters)
                stock_matches = re.findall(r'\b[A-Z]{2,5}\b', question.upper())
                yfinance_tool = self.tools.get('yfinance_data')
                
                if stock_matches and yfinance_tool:
                    # Filter out common words that might be mistaken for stock symbols
                    common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE', 'YEAR', 'YOUR', 'WHAT', 'WHEN', 'WHERE', 'WHICH', 'WHY', 'WITH', 'FROM', 'THAT', 'THIS', 'THEY', 'HAVE', 'WILL', 'WOULD', 'COULD', 'SHOULD', 'ABOUT', 'THERE', 'THEIR', 'TIME', 'VERY', 'GOOD', 'MUCH', 'SOME', 'THEN', 'THEM', 'THESE', 'PEOPLE', 'OTHER', 'FIRST', 'LONG', 'LITTLE', 'VERY', 'AFTER', 'WORDS', 'JUST', 'EACH', 'WHICH', 'SHE', 'SAID', 'DOES', 'SET', 'THREE', 'WANT', 'AIR', 'WELL', 'ALSO', 'PLAY', 'SMALL', 'END', 'PUT', 'HOME', 'READ', 'HAND', 'PORT', 'LARGE', 'SPELL', 'ADD', 'EVEN', 'LAND', 'HERE', 'MUST', 'BIG', 'HIGH', 'SUCH', 'FOLLOW', 'ACT', 'WHY', 'ASK', 'MEN', 'CHANGE', 'WENT', 'LIGHT', 'KIND', 'OFF', 'NEED', 'HOUSE', 'PICTURE', 'TRY', 'US', 'AGAIN', 'ANIMAL', 'POINT', 'MOTHER', 'WORLD', 'NEAR', 'BUILD', 'SELF', 'EARTH', 'FATHER', 'HEAD', 'STAND', 'OWN', 'PAGE', 'SHOULD', 'COUNTRY', 'FOUND', 'ANSWER', 'SCHOOL', 'GROW', 'STUDY', 'STILL', 'LEARN', 'PLANT', 'COVER', 'FOOD', 'SUN', 'FOUR', 'BETWEEN', 'STATE', 'KEEP', 'EYE', 'NEVER', 'LAST', 'LET', 'THOUGHT', 'CITY', 'TREE', 'CROSS', 'FARM', 'HARD', 'START', 'MIGHT', 'STORY', 'SAW', 'FAR', 'SEA', 'DRAW', 'LEFT', 'LATE', 'RUN', 'DONT', 'WHILE', 'PRESS', 'CLOSE', 'NIGHT', 'REAL', 'LIFE', 'FEW', 'NORTH', 'OPEN', 'SEEM', 'TOGETHER', 'NEXT', 'WHITE', 'CHILDREN', 'BEGIN', 'GOT', 'WALK', 'EXAMPLE', 'EASE', 'PAPER', 'GROUP', 'ALWAYS', 'MUSIC', 'THOSE', 'BOTH', 'MARK', 'OFTEN', 'LETTER', 'UNTIL', 'MILE', 'RIVER', 'CAR', 'FEET', 'CARE', 'SECOND', 'BOOK', 'CARRY', 'TOOK', 'SCIENCE', 'EAT', 'ROOM', 'FRIEND', 'BEGAN', 'IDEA', 'FISH', 'MOUNTAIN', 'STOP', 'ONCE', 'BASE', 'HEAR', 'HORSE', 'CUT', 'SURE', 'WATCH', 'COLOR', 'FACE', 'WOOD', 'MAIN', 'ENOUGH', 'PLAIN', 'GIRL', 'USUAL', 'YOUNG', 'READY', 'ABOVE', 'EVER', 'RED', 'LIST', 'THOUGH', 'FEEL', 'TALK', 'BIRD', 'SOON', 'BODY', 'DOG', 'FAMILY', 'DIRECT', 'POSE', 'LEAVE', 'SONG', 'MEASURE', 'DOOR', 'PRODUCT', 'BLACK', 'SHORT', 'NUMERAL', 'CLASS', 'WIND', 'QUESTION', 'HAPPEN', 'COMPLETE', 'SHIP', 'AREA', 'HALF', 'ROCK', 'ORDER', 'FIRE', 'SOUTH', 'PROBLEM', 'PIECE', 'TOLD', 'KNEW', 'PASS', 'SINCE', 'TOP', 'WHOLE', 'KING', 'SPACE', 'HEARD', 'BEST', 'HOUR', 'BETTER', 'TRUE', 'DURING', 'HUNDRED', 'FIVE', 'REMEMBER', 'STEP', 'EARLY', 'HOLD', 'WEST', 'GROUND', 'INTEREST', 'REACH', 'FAST', 'VERB', 'SING', 'LISTEN', 'SIX', 'TABLE', 'TRAVEL', 'LESS', 'MORNING', 'TEN', 'SIMPLE', 'SEVERAL', 'VOWEL', 'TOWARD', 'WAR', 'LAY', 'AGAINST', 'PATTERN', 'SLOW', 'CENTER', 'LOVE', 'PERSON', 'MONEY', 'SERVE', 'APPEAR', 'ROAD', 'MAP', 'RAIN', 'RULE', 'GOVERN', 'PULL', 'COLD', 'NOTICE', 'VOICE', 'UNIT', 'POWER', 'TOWN', 'FINE', 'CERTAIN', 'FLY', 'FALL', 'LEAD', 'CRY', 'DARK', 'MACHINE', 'NOTE', 'WAIT', 'PLAN', 'FIGURE', 'STAR', 'BOX', 'NOUN', 'FIELD', 'REST', 'CORRECT', 'ABLE', 'POUND', 'DONE', 'BEAUTY', 'DRIVE', 'STOOD', 'CONTAIN', 'FRONT', 'TEACH', 'WEEK', 'FINAL', 'GAVE', 'GREEN', 'OH', 'QUICK', 'DEVELOP', 'OCEAN', 'WARM', 'FREE', 'MINUTE', 'STRONG', 'SPECIAL', 'MIND', 'BEHIND', 'CLEAR', 'TAIL', 'PRODUCE', 'FACT', 'STREET', 'INCH', 'MULTIPLY', 'NOTHING', 'COURSE', 'STAY', 'WHEEL', 'FULL', 'FORCE', 'BLUE', 'OBJECT', 'DECIDE', 'SURFACE', 'DEEP', 'MOON', 'ISLAND', 'FOOT', 'SYSTEM', 'BUSY', 'TEST', 'RECORD', 'BOAT', 'COMMON', 'GOLD', 'POSSIBLE', 'PLANE', 'STEAD', 'DRY', 'WONDER', 'LAUGH', 'THOUSAND', 'AGO', 'RAN', 'CHECK', 'GAME', 'SHAPE', 'EQUATE', 'HOT', 'MISS', 'BROUGHT', 'HEAT', 'SNOW', 'TIRE', 'BRING', 'YES', 'DISTANT', 'FILL', 'EAST', 'PAINT', 'LANGUAGE', 'AMONG', 'GRAND', 'BALL', 'YET', 'WAVE', 'DROP', 'HEART', 'AM', 'PRESENT', 'HEAVY', 'DANCE', 'ENGINE', 'POSITION', 'ARM', 'WIDE', 'SAIL', 'MATERIAL', 'SIZE', 'VARY', 'SETTLE', 'SPEAK', 'WEIGHT', 'GENERAL', 'ICE', 'MATTER', 'CIRCLE', 'PAIR', 'INCLUDE', 'DIVIDE', 'SYLLABLE', 'FELT', 'PERHAPS', 'PICK', 'SUDDEN', 'COUNT', 'SQUARE', 'REASON', 'LENGTH', 'REPRESENT', 'ART', 'SUBJECT', 'REGION', 'ENERGY', 'HUNT', 'PROBABLE', 'BED', 'BROTHER', 'EGG', 'RIDE', 'CELL', 'BELIEVE', 'FRACTION', 'FOREST', 'SIT', 'RACE', 'WINDOW', 'STORE', 'SUMMER', 'TRAIN', 'SLEEP', 'PROVE', 'LONE', 'LEG', 'EXERCISE', 'WALL', 'CATCH', 'MOUNT', 'WISH', 'SKY', 'BOARD', 'JOY', 'WINTER', 'SAT', 'WRITTEN', 'WILD', 'INSTRUMENT', 'KEPT', 'GLASS', 'GRASS', 'COW', 'JOB', 'EDGE', 'SIGN', 'VISIT', 'PAST', 'SOFT', 'FUN', 'BRIGHT', 'GAS', 'WEATHER', 'MONTH', 'MILLION', 'BEAR', 'FINISH', 'HAPPY', 'HOPE', 'FLOWER', 'CLOTHE', 'STRANGE', 'GONE', 'TRADE', 'MELODY', 'TRIP', 'OFFICE', 'RECEIVE', 'ROW', 'MOUTH', 'EXACT', 'SYMBOL', 'DIE', 'LEAST', 'TROUBLE', 'SHOUT', 'EXCEPT', 'WROTE', 'SEED', 'TONE', 'JOIN', 'SUGGEST', 'CLEAN', 'BREAK', 'LADY', 'YARD', 'RISE', 'BAD', 'BLOW', 'OIL', 'BLOOD', 'TOUCH', 'GREW', 'CENT', 'MIX', 'TEAM', 'WIRE', 'COST', 'LOST', 'BROWN', 'WEAR', 'GARDEN', 'EQUAL', 'SENT', 'CHOOSE', 'FELL', 'FIT', 'FLOW', 'FAIR', 'BANK', 'COLLECT', 'SAVE', 'CONTROL', 'DECIMAL', 'EAR', 'ELSE', 'QUITE', 'BROKE', 'CASE', 'MIDDLE', 'KILL', 'SON', 'LAKE', 'MOMENT', 'SCALE', 'LOUD', 'SPRING', 'OBSERVE', 'CHILD', 'STRAIGHT', 'CONSONANT', 'NATION', 'DICTIONARY', 'MILK', 'SPEED', 'METHOD', 'ORGAN', 'PAY', 'AGE', 'SECTION', 'DRESS', 'CLOUD', 'SURPRISE', 'QUIET', 'STONE', 'TINY', 'CLIMB', 'COOL', 'DESIGN', 'POOR', 'LOT', 'EXPERIMENT', 'BOTTOM', 'KEY', 'IRON', 'SINGLE', 'STICK', 'FLAT', 'TWENTY', 'SKIN', 'SMILE', 'CREASE', 'HOLE', 'TRADE', 'LEAP', 'JUMP', 'BABY', 'EIGHT', 'VILLAGE', 'MEET', 'ROOT', 'BUY', 'RAISE', 'SOLVE', 'METAL', 'WHETHER', 'PUSH', 'SEVEN', 'PARAGRAPH', 'THIRD', 'SHALL', 'HELD', 'HAIR', 'DESCRIBE', 'COOK', 'FLOOR', 'EITHER', 'RESULT', 'BURN', 'HILL', 'SAFE', 'CAT', 'CENTURY', 'CONSIDER', 'TYPE', 'LAW', 'BIT', 'COAST', 'COPY', 'PHRASE', 'SILENT', 'TALL', 'SAND', 'SOIL', 'ROLL', 'TEMPERATURE', 'FINGER', 'INDUSTRY', 'VALUE', 'FIGHT', 'LIE', 'BEAT', 'EXCITE', 'NATURAL', 'VIEW', 'SENSE', 'CAPITAL', 'WONT', 'CHAIR', 'DANGER', 'FRUIT', 'RICH', 'THICK', 'SOLDIER', 'PROCESS', 'OPERATE', 'PRACTICE', 'SEPARATE', 'DIFFICULT', 'DOCTOR', 'PLEASE', 'PROTECT', 'NOON', 'CROP', 'MODERN', 'ELEMENT', 'HIT', 'STUDENT', 'CORNER', 'PARTY', 'SUPPLY', 'WHOSE', 'LOCATE', 'RING', 'CHARACTER', 'INSECT', 'CAUGHT', 'PERIOD', 'INDICATE', 'RADIO', 'SPOKE', 'ATOM', 'HUMAN', 'HISTORY', 'EFFECT', 'ELECTRIC', 'EXPECT', 'BONE', 'RAIL', 'IMAGINE', 'PROVIDE', 'AGREE', 'THUS', 'GENTLE', 'WOMAN', 'CAPTAIN', 'GUESS', 'NECESSARY', 'SHARP', 'WING', 'CREATE', 'NEIGHBOR', 'WASH', 'BAT', 'RATHER', 'CROWD', 'CORN', 'COMPARE', 'POEM', 'STRING', 'BELL', 'DEPEND', 'MEAT', 'RUB', 'TUBE', 'FAMOUS', 'DOLLAR', 'STREAM', 'FEAR', 'SIGHT', 'THIN', 'TRIANGLE', 'PLANET', 'HURRY', 'CHIEF', 'COLONY', 'CLOCK', 'MINE', 'TIE', 'ENTER', 'MAJOR', 'FRESH', 'SEARCH', 'SEND', 'YELLOW', 'GUN', 'ALLOW', 'PRINT', 'DEAD', 'SPOT', 'DESERT', 'SUIT', 'CURRENT', 'LIFT', 'ROSE', 'ARRIVE', 'MASTER', 'TRACK', 'PARENT', 'SHORE', 'DIVISION', 'SHEET', 'SUBSTANCE', 'FAVOR', 'CONNECT', 'POST', 'SPEND', 'CHORD', 'FAT', 'GLAD', 'ORIGINAL', 'SHARE', 'STATION', 'DAD', 'BREAD', 'CHARGE', 'PROPER', 'BAR', 'OFFER', 'SEGMENT', 'SLAVE', 'DUCK', 'INSTANT', 'MARKET', 'DEGREE', 'POPULATE', 'CHICK', 'DEAR', 'ENEMY', 'REPLY', 'DRINK', 'OCCUR', 'SUPPORT', 'SPEECH', 'NATURE', 'RANGE', 'STEAM', 'MOTION', 'PATH', 'LIQUID', 'LOG', 'MEANT', 'QUOTIENT', 'TEETH', 'SHELL', 'NECK'}
                    
                    # Filter out common words and get unique symbols
                    potential_symbols = [symbol for symbol in stock_matches if symbol not in common_words]
                    
                    if potential_symbols:
                        # Take the first potential symbol
                        symbol = potential_symbols[0]
                        logger.info(f"Detected stock symbol: {symbol}")
                        tools_used.append('yfinance_data')
                        stock_result = await asyncio.to_thread(yfinance_tool, symbol)
                        if stock_result and "Error" not in stock_result and "not found" not in stock_result.lower():
                            tool_responses.append(f"Stock Data for {symbol}: {stock_result}")
                            context.append(f"Stock market data for {symbol}")
                        else:
                            logger.warning(f"Failed to get stock data for {symbol}: {stock_result}")
                    else:
                        logger.info(f"No valid stock symbols found in query: {question}")
            except Exception as e:
                logger.warning(f"YFinance search failed: {e}")
            
            # 4. Always use RAG for knowledge base context (PDFs from data folder)
            tools_used.append('rag_query')
            rag_response = await self.rag_service.query(question)
            context.extend(rag_response.get("context", []))
            
            # 5. Intelligently combine all responses from all 4 tools
            rag_content = rag_response.get("response", "")
            
            logger.info(f"Tool responses count: {len(tool_responses)}")
            logger.info(f"RAG content: {rag_content[:100]}..." if rag_content else "No RAG content")
            
            # Combine responses from all tools
            all_responses = []
            
            # Add RAG response (PDF knowledge)
            if rag_content and "don't have specific information" not in rag_content.lower():
                all_responses.append(f"Knowledge Base (PDFs): {rag_content}")
            
            # Add external tool responses
            if tool_responses:
                all_responses.extend(tool_responses)
            
            if all_responses:
                # Combine all responses
                combined_response = "\n\n".join(all_responses)
                response = f"Based on my analysis using multiple sources:\n\n{combined_response}"
            else:
                # No information available from any source
                response = f"I understand you're asking about '{question}'. I've searched multiple sources including current information, academic research, market data, and our knowledge base, but don't have specific information about this topic. I can help you with general wealth management advice or try searching for different aspects of this topic."
            
            logger.info(f"Final response: {response[:200]}...")
            
            return {
                "response": response,
                "context": [{"content": ctx, "type": "context"} for ctx in context],
                "tools_used": tools_used,
                "confidence": rag_response.get("retrieval_score", 0.85)
            }
            
        except Exception as e:
            logger.error(f"Error in tool processing: {e}")
            raise
    
    async def stream_query(self, question: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream response from the wealth advisor"""
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Streaming query: {question}")
            
            # Simulate streaming response
            chunks = [
                {"chunk_id": "1", "content": "Processing your query...", "is_final": False},
                {"chunk_id": "2", "content": "Analyzing financial data...", "is_final": False},
                {"chunk_id": "3", "content": "Based on the available information, here's my analysis:", "is_final": False},
                {"chunk_id": "4", "content": "This is a comprehensive response to your wealth management question.", "is_final": True}
            ]
            
            for chunk in chunks:
                yield chunk
                await asyncio.sleep(0.5)  # Simulate processing time
                
        except Exception as e:
            logger.error(f"Error streaming query: {e}")
            yield {"chunk_id": "error", "content": f"Error: {str(e)}", "is_final": True}
    
    def _categorize_query(self, question: str) -> str:
        """Categorize the query type"""
        question_lower = question.lower()
        
        if any(keyword in question_lower for keyword in ['investment', 'portfolio', 'asset']):
            return "investment_advice"
        elif any(keyword in question_lower for keyword in ['retirement', 'planning', 'future']):
            return "retirement_planning"
        elif any(keyword in question_lower for keyword in ['tax', 'taxation', 'deduction']):
            return "tax_planning"
        elif any(keyword in question_lower for keyword in ['risk', 'volatility', 'diversification']):
            return "risk_management"
        elif any(keyword in question_lower for keyword in ['market', 'stock', 'trading']):
            return "market_analysis"
        else:
            return "general_advice"
    
    async def search_tavily(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search using Tavily"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Use Tavily search tool
            tool = self.tools.get('tavily_search')
            if tool:
                results = await asyncio.to_thread(tool.invoke, query)
                return results
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error in Tavily search: {e}")
            raise
    
    async def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search ArXiv papers"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Use ArXiv search tool
            tool = self.tools.get('arxiv_search')
            if tool:
                results = await asyncio.to_thread(tool.invoke, query)
                return results
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error in ArXiv search: {e}")
            raise
    
    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get stock data from yfinance"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Use YFinance tool
            tool = self.tools.get('yfinance_data')
            if tool:
                result = await asyncio.to_thread(tool.invoke, symbol)
                return {"symbol": symbol, "data": result}
            else:
                return {"symbol": symbol, "data": "Tool not available"}
                
        except Exception as e:
            logger.error(f"Error getting stock data: {e}")
            raise
    
    async def get_usage_analytics(self) -> Dict[str, Any]:
        """Get usage analytics"""
        try:
            avg_response_time = sum(self.usage_stats["response_times"]) / len(self.usage_stats["response_times"]) if self.usage_stats["response_times"] else 0
            
            return {
                "total_queries": self.usage_stats["total_queries"],
                "successful_queries": self.usage_stats["successful_queries"],
                "failed_queries": self.usage_stats["failed_queries"],
                "average_response_time": avg_response_time,
                "most_used_tools": self.usage_stats["tool_usage"],
                "query_categories": self.usage_stats["query_categories"],
                "daily_usage": [],  # Would be populated in a real system
                "monthly_usage": []  # Would be populated in a real system
            }
        except Exception as e:
            logger.error(f"Error getting usage analytics: {e}")
            raise
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health information"""
        try:
            return {
                "initialized": self.initialized,
                "tools_available": len(self.tools),
                "model_available": self.model is not None,
                "rag_service_healthy": await self.rag_service.get_system_health(),
                "status": "healthy" if self.initialized else "not_initialized"
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "status": "error",
                "error": str(e)
            } 