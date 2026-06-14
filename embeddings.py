import os
import logging
import requests
import time
from dotenv import load_dotenv
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
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
TABLE_NAME = "stackoverflow_qa"

class VectorManager:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        logger.info(f"Using Hugging Face API for embedding model: {model_name}...")
        # Note: BAAI/bge-small-en-v1.5 is a feature-extraction model
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_name}"
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL or SUPABASE_SERVICE_KEY not found in .env")
            
        if not HUGGINGFACE_API_KEY:
            logger.warning("HUGGINGFACE_API_KEY not found in .env. Falling back to unauthenticated requests (rate limited).")
        
        self.headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"} if HUGGINGFACE_API_KEY else {}
        
        logger.info("Connecting to Supabase via HTTP API...")
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Connected to Supabase.")

    def _get_embeddings_from_api(self, texts: List[str]) -> List[List[float]]:
        """Fetch embeddings from HF Inference API with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            response = requests.post(self.api_url, headers=self.headers, json={"inputs": texts, "options": {"wait_for_model": True}})
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 503: # Model loading
                logger.info("HF Model is loading, waiting 10s...")
                time.sleep(10)
            else:
                raise Exception(f"HF API Error ({response.status_code}): {response.text}")
        
        raise Exception("Failed to get embeddings after multiple retries.")

    def embed_and_store(self, documents: List):
        logger.info(f"Generating embeddings via HF API and uploading {len(documents)} chunks...")
        
        batch_size = 50 
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            data_to_upsert = []
            
            try:
                contents = [doc.page_content for doc in batch]
                embeddings = self._get_embeddings_from_api(contents)
                
                for j, doc in enumerate(batch):
                    unique_id = f"q{doc.metadata['question_id']}_c{doc.metadata['chunk_index']}"
                    data_to_upsert.append({
                        "id": unique_id,
                        "embedding": embeddings[j],
                        "metadata": doc.metadata
                    })
                
                self.supabase.table(TABLE_NAME).upsert(data_to_upsert).execute()
                logger.info(f"Uploaded batch {i // batch_size + 1}/{(len(documents) + batch_size - 1) // batch_size}")
                time.sleep(0.5) # Prevent rate limiting
            except Exception as e:
                logger.error(f"Failed to upload batch {i}: {e}")
                time.sleep(2)

        logger.info("Storage sync complete.")

    def search(self, query: str, limit: int = 3):
        logger.info(f"Searching for: {query}")
        try:
            # Get single embedding
            embeddings = self._get_embeddings_from_api([query])
            query_embedding = embeddings[0]
            
            # Call the RPC function we created in Supabase SQL editor
            response = self.supabase.rpc(
                "match_stackoverflow_qa",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.1,
                    "match_count": limit
                }
            ).execute()
            
            return response.data
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

def main():
    # Placeholder for local testing if needed
    pass

if __name__ == "__main__":
    main()
