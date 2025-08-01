from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import aiofiles

from ..utils.pdf_loader import PDFLoader
from ..utils.embeddings import EmbeddingManager
from ..utils.vectorstore import FAISSVectorStore
from ..utils.pdf_utils import PDFUtils
from config import settings

router = APIRouter()

# Global instances (in production, use dependency injection)
embedding_manager = None
vector_store = None
pdf_loader = None
pdf_utils = None

class UploadResponse(BaseModel):
    status: str
    message: str
    filename: str
    chunks_indexed: int
    total_documents: int
    file_info: Dict[str, Any]

class UploadStatusResponse(BaseModel):
    status: str
    progress: float
    message: str
    chunks_processed: int
    total_chunks: int

async def get_services():
    """Initialize services if not already done"""
    global embedding_manager, vector_store, pdf_loader, pdf_utils
    
    if embedding_manager is None:
        embedding_manager = EmbeddingManager(settings.EMBEDDING_MODEL)
    
    if vector_store is None:
        vector_store = FAISSVectorStore(embedding_manager)
        # Try to load existing index
        try:
            vector_store.load_index()
        except:
            pass  # No existing index, will be created when documents are added
    
    if pdf_loader is None:
        pdf_loader = PDFLoader(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    
    if pdf_utils is None:
        pdf_utils = PDFUtils()

@router.post("/upload_pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF document with enhanced functionality"""
    try:
        print(f"Starting upload for file: {file.filename}")
        await get_services()
        print("Services initialized successfully")
        
        # Validate file
        if not await pdf_utils.validate_pdf_file(file):
            print("File validation failed")
            raise HTTPException(
                status_code=400, 
                detail="Invalid PDF file. Please check file type and size."
            )
        print("File validation passed")
        
        # Save file
        file_path = await pdf_utils.save_pdf_file(file)
        print(f"File saved to: {file_path}")
        file_info = pdf_utils.get_file_info(file_path)
        
        # Process PDF
        print("Starting PDF processing")
        documents = await pdf_loader.load_pdf(file_path)
        print(f"PDF processed, {len(documents)} chunks created")
        
        # Add to vector store
        print("Adding documents to vector store")
        await vector_store.add_documents(documents)
        
        # Save index
        print("Saving vector index")
        vector_store.save_index()
        
        result = UploadResponse(
            status="uploaded",
            message="Document uploaded and indexed successfully",
            filename=file.filename,
            chunks_indexed=len(documents),
            total_documents=vector_store.get_document_count(),
            file_info=file_info
        )
        print(f"Upload completed successfully: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = f"Error uploading document: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(error_details)  # Log the error for debugging
        raise HTTPException(
            status_code=500, 
            detail=f"Error uploading document: {str(e)}"
        )

@router.post("/upload_pdf_async", response_model=Dict[str, Any])
async def upload_pdf_async(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Upload PDF and process in background"""
    try:
        await get_services()
        
        # Validate file
        if not await pdf_utils.validate_pdf_file(file):
            raise HTTPException(
                status_code=400, 
                detail="Invalid PDF file. Please check file type and size."
            )
        
        # Save file
        file_path = await pdf_utils.save_pdf_file(file)
        
        # Start background processing
        if background_tasks:
            background_tasks.add_task(process_pdf_background, file_path, file.filename)
        
        return {
            "status": "processing",
            "message": "Document uploaded. Processing in background...",
            "filename": file.filename,
            "task_id": str(hash(file_path))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error uploading document: {str(e)}"
        )

async def process_pdf_background(file_path: str, filename: str):
    """Background task to process PDF"""
    try:
        await get_services()
        
        # Process PDF
        documents = await pdf_loader.load_pdf(file_path)
        
        # Add to vector store
        await vector_store.add_documents(documents)
        
        # Save index
        vector_store.save_index()
        
        print(f"Background processing completed for {filename}: {len(documents)} chunks indexed")
        
    except Exception as e:
        print(f"Background processing failed for {filename}: {str(e)}")

@router.get("/upload_status/{task_id}", response_model=UploadStatusResponse)
async def get_upload_status(task_id: str):
    """Get status of background upload processing"""
    # This is a simplified implementation
    # In production, you'd use a proper task queue like Celery
    return UploadStatusResponse(
        status="completed",
        progress=100.0,
        message="Processing completed",
        chunks_processed=0,
        total_chunks=0
    )

@router.get("/uploaded_files", response_model=List[Dict[str, Any]])
async def get_uploaded_files():
    """Get list of uploaded files"""
    await get_services()
    
    files = []
    try:
        for file_path in pdf_utils.upload_dir.glob("*.pdf"):
            file_info = pdf_utils.get_file_info(str(file_path))
            if file_info:
                files.append(file_info)
    except Exception as e:
        print(f"Error listing files: {str(e)}")
    
    return files

@router.delete("/uploaded_files/{filename}")
async def delete_uploaded_file(filename: str):
    """Delete an uploaded file"""
    await get_services()
    
    try:
        file_path = pdf_utils.upload_dir / filename
        if file_path.exists():
            file_path.unlink()
            return {"message": f"File {filename} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error deleting file: {str(e)}"
        )

@router.post("/cleanup_files")
async def cleanup_old_files():
    """Clean up old uploaded files"""
    await get_services()
    
    try:
        pdf_utils.cleanup_old_files()
        return {"message": "Cleanup completed"}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error during cleanup: {str(e)}"
        )

@router.get("/test_upload")
async def test_upload_endpoint():
    """Test endpoint to check if upload route is accessible"""
    return {
        "status": "ok",
        "message": "Upload endpoint is accessible",
        "timestamp": "2024-08-01T16:00:00Z"
    } 