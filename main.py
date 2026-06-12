import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from rag import RAGEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Stack Overflow Python RAG Assistant",
    description="API for a RAG-based assistant specialized in Python questions using Stack Overflow data.",
    version="1.0.0"
)

# Add CORS middleware to allow requests from the Astro frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG Engine
# Note: In a production app, you might want to use a dependency or singleton pattern
try:
    rag_engine = RAGEngine()
    logger.info("RAG Engine initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize RAG Engine: {e}")
    rag_engine = None

# Request/Response Models
class QuestionRequest(BaseModel):
    question: str

class SourceMetadata(BaseModel):
    question_title: str
    source_url: str
    answer_url: str
    tags: str

class AskResponse(BaseModel):
    answer: str
    sources: List[SourceMetadata]

# Endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "rag_engine": "ready" if rag_engine else "not_initialized"
    }

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: QuestionRequest):
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG Engine not initialized")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        logger.info(f"Received question: {request.question}")
        
        # 1. Get Answer
        answer = rag_engine.ask(request.question)
        
        # 2. Get Sources (re-run search to get clean source objects for API)
        raw_results = rag_engine.vector_manager.search(request.question, limit=3)
        
        sources = []
        for res in raw_results:
            meta = res.get('metadata', {})
            sources.append(SourceMetadata(
                question_title=meta.get('question_title', 'Unknown'),
                source_url=meta.get('source_url', '#'),
                answer_url=meta.get('answer_url', '#'),
                tags=meta.get('tags', '')
            ))
            
        return AskResponse(answer=answer, sources=sources)
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
