import os
import logging
from typing import List, Dict, Any
from pathlib import Path
import fitz  # PyMuPDF - the module is called fitz
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Service for processing PDF files from the data folder"""
    
    def __init__(self, data_folder: str = "../data"):
        self.data_folder = Path(data_folder)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from a PDF file"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def process_all_pdfs(self) -> List[Document]:
        """Process all PDF files in the data folder"""
        documents = []
        
        logger.info(f"Looking for PDFs in: {self.data_folder.absolute()}")
        
        if not self.data_folder.exists():
            logger.warning(f"Data folder {self.data_folder.absolute()} does not exist")
            return documents
        
        # Find all PDF files
        pdf_files = list(self.data_folder.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {self.data_folder.absolute()}")
        for pdf_file in pdf_files:
            logger.info(f"  - {pdf_file.name}")
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Processing PDF: {pdf_file.name}")
                text = self.extract_text_from_pdf(pdf_file)
                
                if text.strip():
                    # Create document with metadata
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": str(pdf_file),
                            "filename": pdf_file.name,
                            "file_type": "pdf",
                            "file_size": pdf_file.stat().st_size
                        }
                    )
                    documents.append(doc)
                    logger.info(f"Successfully processed {pdf_file.name} ({len(text)} characters)")
                else:
                    logger.warning(f"No text extracted from {pdf_file.name}")
                    
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {e}")
        
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        try:
            logger.info(f"Chunking {len(documents)} documents")
            chunked_docs = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunked_docs)} chunks")
            return chunked_docs
        except Exception as e:
            logger.error(f"Error chunking documents: {e}")
            return documents
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about PDF processing"""
        try:
            pdf_files = list(self.data_folder.glob("*.pdf")) if self.data_folder.exists() else []
            
            stats = {
                "total_pdfs": len(pdf_files),
                "pdf_files": [f.name for f in pdf_files],
                "data_folder": str(self.data_folder),
                "folder_exists": self.data_folder.exists()
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {"error": str(e)} 