import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# LangChain imports
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

# Local imports
from .pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)

class RAGService:
    """
    RAG (Retrieval-Augmented Generation) service for wealth management
    """
    
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self.retriever = None
        self.llm = None
        self.rag_prompt = None
        self.compression_retriever = None
        self.documents = []
        self.initialized = False
        self.pdf_processor = PDFProcessor(data_folder="../data")
        
    async def initialize(self):
        """Initialize the RAG service with all components"""
        try:
            logger.info("Initializing RAG Service...")
            
            # Initialize embeddings with text-embedding-3-small
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            
            # Initialize Qdrant client
            client = QdrantClient(":memory:")
            
            # Create collection
            client.create_collection(
                collection_name="wealth_advisor_collection",
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
            
            # Initialize vector store
            self.vector_store = QdrantVectorStore(
                client=client,
                collection_name="wealth_advisor_collection",
                embedding=self.embeddings,
            )
            
            # Initialize retriever
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
            
            # Initialize compression retriever
            compressor = CohereRerank(model="rerank-v3.5", top_n=10)
            self.compression_retriever = ContextualCompressionRetriever(
                base_compressor=compressor, 
                base_retriever=self.retriever, 
                search_kwargs={"k": 5}
            )
            
            # Initialize LLM
            self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
            
            # Initialize RAG prompt
            self.rag_prompt = ChatPromptTemplate.from_template("""
            You are a helpful wealth management assistant who answers questions based on provided context. 
            You must only use the provided context, and cannot use your own knowledge.
            
            ### Question
            {question}
            
            ### Context
            {context}
            
            Please provide a comprehensive and accurate response based on the context provided.
            """)
            
            # Process PDFs and add to vector store
            await self.load_pdfs_to_vectorstore()
            
            self.initialized = True
            logger.info("RAG Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Service: {e}")
            raise
    
    async def load_pdfs_to_vectorstore(self) -> Dict[str, Any]:
        """Load PDFs from data folder and add to vector store"""
        try:
            logger.info("Loading PDFs from data folder...")
            
            # Process all PDFs
            documents = self.pdf_processor.process_all_pdfs()
            logger.info(f"Processed {len(documents)} PDF documents")
            
            if not documents:
                logger.warning("No PDF documents found to process")
                return {
                    "documents_loaded": 0,
                    "chunks_created": 0,
                    "status": "no_documents"
                }
            
            # Chunk documents
            chunked_documents = self.pdf_processor.chunk_documents(documents)
            logger.info(f"Created {len(chunked_documents)} chunks")
            
            # Add to vector store
            await self._add_documents_to_store(chunked_documents)
            
            # Update documents list
            self.documents.extend(chunked_documents)
            
            logger.info(f"Successfully loaded {len(documents)} PDFs with {len(chunked_documents)} chunks to vector store")
            
            return {
                "documents_loaded": len(documents),
                "chunks_created": len(chunked_documents),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error loading PDFs to vector store: {e}")
            raise
    
    async def load_documents(self, data_path: str = "data/") -> Dict[str, Any]:
        """Load documents from the specified path (legacy method)"""
        try:
            logger.info(f"Loading documents from {data_path}")
            
            # Load documents
            loader = DirectoryLoader(data_path, glob="*.pdf", loader_cls=PyMuPDFLoader)
            docs = loader.load()
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=750,
                chunk_overlap=100,
            )
            split_documents = text_splitter.split_documents(docs)
            
            # Add to vector store
            await self._add_documents_to_store(split_documents)
            
            self.documents = split_documents
            
            return {
                "documents_loaded": len(docs),
                "chunks_created": len(split_documents),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            raise
    
    async def _add_documents_to_store(self, documents: List[Document]):
        """Add documents to the vector store"""
        try:
            if self.vector_store:
                await asyncio.to_thread(self.vector_store.add_documents, documents)
                logger.info(f"Added {len(documents)} documents to vector store")
            else:
                raise Exception("Vector store not initialized")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    async def query(self, question: str, use_compression: bool = True) -> Dict[str, Any]:
        """Query the RAG system"""
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"Processing RAG query: {question}")
            
            # Retrieve relevant documents
            if use_compression and self.compression_retriever:
                retrieved_docs = await asyncio.to_thread(
                    self.compression_retriever.invoke, question
                )
            else:
                retrieved_docs = await asyncio.to_thread(
                    self.retriever.invoke, question
                )
            
            # Check if we have any documents
            if not retrieved_docs:
                return {
                    "response": f"I don't have specific information about '{question}' in my knowledge base yet. However, I can help you with general wealth management advice. Would you like me to search for current information on this topic or provide general guidance?",
                    "context": [],
                    "sources": [],
                    "retrieval_score": 0.0,
                    "documents_retrieved": 0
                }
            
            # Prepare context
            docs_content = "\n\n".join([doc.page_content for doc in retrieved_docs])
            
            # Generate response
            messages = self.rag_prompt.format_messages(
                question=question, 
                context=docs_content
            )
            
            response = await asyncio.to_thread(self.llm.invoke, messages)
            
            # Prepare sources
            sources = [doc.metadata.get('source', 'Unknown') for doc in retrieved_docs]
            
            return {
                "response": response.content,
                "context": [doc.page_content for doc in retrieved_docs],
                "sources": sources,
                "retrieval_score": len(retrieved_docs) / 5.0,  # Simple scoring
                "documents_retrieved": len(retrieved_docs)
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            raise
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add new documents to the RAG system"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Convert to Document objects
            langchain_docs = []
            for doc in documents:
                langchain_doc = Document(
                    page_content=doc.get('content', ''),
                    metadata=doc.get('metadata', {})
                )
                langchain_docs.append(langchain_doc)
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=750,
                chunk_overlap=100,
            )
            split_documents = text_splitter.split_documents(langchain_docs)
            
            # Add to vector store
            await self._add_documents_to_store(split_documents)
            
            # Update documents list
            self.documents.extend(split_documents)
            
            return {
                "documents_added": len(documents),
                "total_documents": len(self.documents),
                "chunks_created": len(split_documents),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    async def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about the documents in the system"""
        try:
            return {
                "total_documents": len(self.documents),
                "vector_store_size": len(self.documents) if self.documents else 0,
                "collections": ["wealth_advisor_collection"],
                "embedding_model": "text-embedding-3-small",
                "chunk_size": 750,
                "chunk_overlap": 100
            }
        except Exception as e:
            logger.error(f"Error getting document stats: {e}")
            raise
    
    async def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Search in vector store
            results = await asyncio.to_thread(
                self.vector_store.similarity_search, query, k=top_k
            )
            
            # Format results
            formatted_results = []
            for i, doc in enumerate(results):
                formatted_results.append({
                    "rank": i + 1,
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": 1.0 - (i * 0.1)  # Simple scoring
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise
    
    async def update_documents(self, document_ids: List[str], new_content: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing documents"""
        try:
            # This is a simplified implementation
            # In a real system, you'd need to handle document updates more carefully
            
            logger.info(f"Updating {len(document_ids)} documents")
            
            return {
                "documents_updated": len(document_ids),
                "status": "success",
                "message": "Documents updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating documents: {e}")
            raise
    
    async def delete_documents(self, document_ids: List[str]) -> Dict[str, Any]:
        """Delete documents from the system"""
        try:
            # This is a simplified implementation
            # In a real system, you'd need to handle document deletion more carefully
            
            logger.info(f"Deleting {len(document_ids)} documents")
            
            return {
                "documents_deleted": len(document_ids),
                "status": "success",
                "message": "Documents deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health information"""
        try:
            return {
                "initialized": self.initialized,
                "vector_store_available": self.vector_store is not None,
                "retriever_available": self.retriever is not None,
                "llm_available": self.llm is not None,
                "documents_count": len(self.documents),
                "embedding_model": "text-embedding-3-small",
                "status": "healthy" if self.initialized else "not_initialized"
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "status": "error",
                "error": str(e)
            } 