import pandas as pd
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StackOverflowIngestor:
    def __init__(self, file_path: str, chunk_size=3000, chunk_overlap=300):
        self.file_path = Path(file_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def load_data(self) -> pd.DataFrame:
        logger.info(f"Loading data from {self.file_path}...")
        if self.file_path.suffix == '.jsonl':
            return pd.read_json(self.file_path, orient='records', lines=True)
        else:
            raise ValueError("Unsupported file format. Please use .jsonl")

    def create_documents(self, df: pd.DataFrame, limit: int = None) -> list[Document]:
        if limit:
            df = df.head(limit)
        
        logger.info(f"Converting {len(df)} rows into LangChain documents...")
        all_documents = []
        
        for _, row in df.iterrows():
            # Create base metadata
            metadata = {
                "question_id": int(row['question_id']),
                "answer_id": int(row['answer_id']),
                "question_title": row['question_title'],
                "tags": row['tags_text'],
                "source_url": row['source_url'],
                "answer_url": row['answer_url'],
                "question_score": int(row['question_score']),
                "answer_score": int(row['answer_score'])
            }
            
            # Split the document text
            text_chunks = self.splitter.split_text(row['document_text'])
            
            for i, chunk in enumerate(text_chunks):
                # Enrich metadata with chunk info
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_index"] = i
                chunk_metadata["content"] = chunk # Added this line
                
                doc = Document(page_content=chunk, metadata=chunk_metadata)
                all_documents.append(doc)
                
        logger.info(f"Created {len(all_documents)} document chunks.")
        return all_documents

def main():
    # Test the ingestor with a small sample
    input_file = "data/processed/stack_overflow_python_qa_clean.jsonl"
    if not Path(input_file).exists():
        logger.error(f"Input file {input_file} not found. Ensure Phase 2 generated the JSONL file.")
        return

    ingestor = StackOverflowIngestor(input_file)
    df = ingestor.load_data()
    
    # Process first 100 rows for validation
    docs = ingestor.create_documents(df, limit=100)
    
    if docs:
        logger.info("Validation Sample:")
        logger.info(f"Content length: {len(docs[0].page_content)}")
        logger.info(f"Metadata: {docs[0].metadata}")
        logger.info("Ingestion pipeline verified.")

if __name__ == "__main__":
    main()
