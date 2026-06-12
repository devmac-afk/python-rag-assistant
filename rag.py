import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from embeddings import VectorManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class RAGEngine:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.vector_manager = VectorManager()
        
        # Initialize Groq LLM
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in .env")
        
        self.llm = ChatGroq(
            temperature=0,
            model_name=model_name,
            groq_api_key=groq_api_key
        )
        
        # Define the prompt template
        self.prompt = ChatPromptTemplate.from_template("""
        You are a helpful and expert Python programming assistant.
        Use the following retrieved context from Stack Overflow to answer the user's question accurately.
        
        Guidelines:
        1. If the context doesn't contain the answer, say "I don't have enough specific information in my Stack Overflow database to answer this accurately."
        2. Keep your answer concise and focused on the technical solution.
        3. Always include a code example if relevant.
        4. If multiple solutions exist in the context, summarize the best one.
        
        Context:
        {context}
        
        Question: 
        {question}
        
        Answer:
        """)

    def _format_docs(self, docs: List[Dict[str, Any]]) -> str:
        formatted = []
        for doc in docs:
            # metadata is stored in the 'metadata' key in our Supabase response
            meta = doc.get('metadata', {})
            content = f"Title: {meta.get('question_title')}\nTags: {meta.get('tags')}\n\nQuestion/Answer:\n{doc.get('id')}" # We don't store full text in metadata to save space, but we have it in our cleaning phase. 
            # Wait, our current Supabase setup stores the FULL doc.metadata. 
            # Let's check what's in doc.metadata. In embeddings.py, we put doc.metadata which is row['document_text']? No, ingest.py metadata didn't include document_text.
            # I need to fix ingest.py/embeddings.py to include the chunk text in metadata if I want to retrieve it easily via HTTP API.
            
            # Re-checking ingest.py: metadata = {"question_id": ..., "question_title": ..., "tags": ..., "source_url": ...}
            # It DOES NOT include the text of the chunk itself.
            
            # FIX: I need to update embeddings.py to include 'content' in the metadata so the RAG can actually read it.
            pass
        return "\n\n".join(formatted)

    def get_chain(self):
        # This will be updated after fixing the metadata issue
        chain = (
            {"context": self.vector_manager.search, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        return chain

if __name__ == "__main__":
    # This is a placeholder for testing
    print("RAG Engine initialized.")
