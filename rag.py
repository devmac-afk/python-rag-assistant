import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from embeddings import VectorManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class RAGEngine:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.vector_manager = VectorManager()
        
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in .env")
        
        self.llm = ChatGroq(
            temperature=0,
            model_name=model_name,
            groq_api_key=groq_api_key
        )
        
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

    def _format_docs(self, results: List[Dict[str, Any]]) -> str:
        formatted = []
        for res in results:
            meta = res.get('metadata', {})
            # We now have the 'content' field in metadata
            content = meta.get('content', '')
            title = meta.get('question_title', 'No Title')
            tags = meta.get('tags', '')
            
            doc_str = f"--- Document Start ---\nTitle: {title}\nTags: {tags}\n\n{content}\n--- Document End ---"
            formatted.append(doc_str)
            
        return "\n\n".join(formatted)

    def ask(self, question: str) -> str:
        logger.info(f"Processing question: {question}")
        
        # 1. Retrieve relevant chunks
        raw_results = self.vector_manager.search(question, limit=3)
        
        # 2. Format context
        context = self._format_docs(raw_results)
        
        # 3. Create chain manually for more control
        chain = self.prompt | self.llm | StrOutputParser()
        
        # 4. Generate answer
        response = chain.invoke({"context": context, "question": question})
        return response

def main():
    engine = RAGEngine()
    
    # Test query
    question = "How can I join two tuples in Python?"
    print(f"\nUser Question: {question}")
    
    answer = engine.ask(question)
    print(f"\nAI Assistant Answer:\n{answer}")

if __name__ == "__main__":
    main()
