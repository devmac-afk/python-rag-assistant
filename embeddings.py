import os
import logging
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from ingest import StackOverflowIngestor
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
TABLE_NAME = "stackoverflow_qa"

class VectorManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL or SUPABASE_SERVICE_KEY not found in .env")
        
        logger.info("Connecting to Supabase via HTTP API...")
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Connected to Supabase.")

    def embed_and_store(self, documents: List):
        logger.info(f"Generating embeddings and uploading {len(documents)} chunks...")
        
        batch_size = 50
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            data_to_upsert = []
            
            for doc in batch:
                embedding = self.model.encode(doc.page_content).tolist()
                unique_id = f"q{doc.metadata['question_id']}_c{doc.metadata['chunk_index']}"
                
                data_to_upsert.append({
                    "id": unique_id,
                    "embedding": embedding,
                    "metadata": doc.metadata
                })
            
            # Upsert via HTTP API
            self.supabase.table(TABLE_NAME).upsert(data_to_upsert).execute()
            logger.info(f"Uploaded batch {i // batch_size + 1}/{(len(documents) + batch_size - 1) // batch_size}")

        logger.info("Storage sync complete.")

    def search(self, query: str, limit: int = 3):
        logger.info(f"Searching for: {query}")
        query_embedding = self.model.encode(query).tolist()
        
        # Call the RPC function we created in Supabase SQL editor
        response = self.supabase.rpc(
            "match_stackoverflow_qa",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.1,  # Lowered threshold
                "match_count": limit
            }
        ).execute()
        
        return response.data

def main():
    # 1. Load Data using Ingestor
    input_file = "data/processed/stack_overflow_python_qa_clean.jsonl"
    ingestor = StackOverflowIngestor(input_file)
    df = ingestor.load_data()
    
    # Process a small batch for verification
    docs = ingestor.create_documents(df, limit=100)
    
    # 2. Initialize Vector Manager
    vm = VectorManager()
    
    # 3. Generate and Store
    vm.embed_and_store(docs)
    
    # 4. Verify Retrieval
    logger.info("Verifying search...")
    results = vm.search("How to join two tuples in python?")
    
    if results:
        for i, res in enumerate(results):
            print(f"\n--- Result {i+1} (Similarity: {res['similarity']:.4f}) ---")
            print(f"Title: {res['metadata']['question_title']}")
            print(f"Text Sample: {res['metadata'].get('question_id', 'N/A')}")
    else:
        logger.warning("No results found. Check if data was uploaded correctly.")

if __name__ == "__main__":
    main()
