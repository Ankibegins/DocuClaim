import PyPDF2
import io
from typing import List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class PDFLoader:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    async def load_pdf(self, file_path: str) -> List[Document]:
        """Load and split PDF into chunks"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                # Split text into chunks
                chunks = self.text_splitter.split_text(text)
                
                # Convert to Document objects
                documents = [
                    Document(
                        page_content=chunk,
                        metadata={"source": file_path, "chunk_id": i}
                    )
                    for i, chunk in enumerate(chunks)
                ]
                
                return documents
                
        except Exception as e:
            raise Exception(f"Error loading PDF {file_path}: {str(e)}")
    
    async def load_pdf_from_bytes(self, pdf_bytes: bytes, source_name: str = "uploaded_document") -> List[Document]:
        """Load and split PDF from bytes"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Convert to Document objects
            documents = [
                Document(
                    page_content=chunk,
                    metadata={"source": source_name, "chunk_id": i}
                )
                for i, chunk in enumerate(chunks)
            ]
            
            return documents
            
        except Exception as e:
            raise Exception(f"Error loading PDF from bytes: {str(e)}") 