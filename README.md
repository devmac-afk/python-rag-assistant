# StackAI: Python Stack Overflow Assistant

A high-performance RAG (Retrieval-Augmented Generation) chatbot specialized in Python programming, built using **Astro**, **FastAPI**, **Groq**, and **Supabase**.

## 🚀 Live Demo
**Frontend:** [Your Vercel URL here]  
**Backend API:** [Your Render URL here]

## 🛠️ Tech Stack
- **Frontend:** Astro, React, Tailwind CSS, Framer Motion (Glassmorphism UI)
- **Backend:** FastAPI (Python 3.11)
- **LLM:** Groq (Llama 3 / Mixtral) for ultra-fast generation
- **Embeddings:** Hugging Face Inference API (`BAAI/bge-small-en-v1.5`)
- **Vector Database:** Supabase (pgvector)
- **Orchestration:** LangChain

## 🏗️ Architecture
1. **Data Ingestion:** Stack Overflow Python Q&A dataset is cleaned and chunked (1500 chars).
2. **Vectorization:** Chunks are converted into 384-dimension embeddings via Hugging Face.
3. **Storage:** Vectors and metadata are stored in Supabase using the `pgvector` extension.
4. **Retrieval:** User queries are vectorized and a similarity search (Cosine Similarity) is performed via a Supabase RPC function.
5. **Generation:** Retrieved context + User query is sent to Groq Llama 3 for a grounded, accurate response.

## ⚙️ Setup Instructions

### 1. Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Data Ingestion (Optional)
If you wish to re-ingest the dataset:
```bash
python ingest.py
```

## 📄 Scalability & Trade-offs
*   **Data Curated:** Due to free-tier cloud constraints (Render/Supabase), the current database is optimized with a curated subset of **25,000 high-impact Python records** (~40k chunks).
*   **Cold Start:** As the backend is hosted on Render's free tier, the first request may experience a 30s delay if the server is sleeping.

## 🔒 Environment Variables
See `.env.example` for the required keys.
