from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

from .routes.query_router import router as query_router
from .routes.upload_router import router as upload_router

# Create FastAPI app
app = FastAPI(
    title="ClauseMind - Intelligent Clause Retriever & Decision System",
    description="""
    🧠 **ClauseMind** - An intelligent system that uses LLM-powered semantic search to retrieve relevant clauses from insurance documents and provide automated decision-making.

    ## Features:
    - **Document Upload**: Upload PDF insurance documents with drag & drop
    - **Auto Indexing**: Automatic embedding generation and FAISS indexing
    - **Semantic Search**: Find relevant clauses using FAISS vector search
    - **LLM Reasoning**: Use Gemini to analyze clauses and make decisions
    - **Entity Extraction**: Automatically extract key information from queries
    - **Real-time Processing**: Background processing for large documents

    ## Pipeline:
    1. PDF Upload → Text Extraction & Chunking
    2. User Query → Entity Extraction (Gemini)
    3. Query Embedding → FAISS Vector Search
    4. Retrieved Clauses → LLM Reasoning (Gemini)
    5. Structured Output → Decision + Justification

    ## Tech Stack:
    - **Backend**: FastAPI (Async)
    - **Embeddings**: SentenceTransformers (MiniLM)
    - **Vector DB**: FAISS (Local)
    - **LLM**: Google Gemini (via LangChain)
    - **Document Processing**: PyPDF2
    - **File Handling**: Async file operations
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(query_router, prefix="/api/v1", tags=["ClauseMind API"])
app.include_router(upload_router, prefix="/api/v1", tags=["Document Upload"])

# Template rendering setup
templates = Jinja2Templates(directory="templates")

# Mount static assets (if any)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve HTML page on root URL
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("enhanced.html", {"request": request})

# JSON API info endpoint
@app.get("/api/v1", response_class=JSONResponse)
async def api_info():
    return {
        "api_name": "ClauseMind API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /api/v1/health",
            "upload": "POST /api/v1/upload_pdf",
            "upload_async": "POST /api/v1/upload_pdf_async",
            "query": "POST /api/v1/query",
            "documents": "GET /api/v1/documents",
            "uploaded_files": "GET /api/v1/uploaded_files"
        },
        "features": [
            "PDF document upload and processing",
            "Semantic clause retrieval using FAISS",
            "LLM-powered decision making with Gemini",
            "Entity extraction from natural language queries"
        ]
    }

# For local dev
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
