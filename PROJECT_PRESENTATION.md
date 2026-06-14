# StackAI: Technical Case Study & Project Documentation

## 1. Project Overview
**StackAI** is a high-performance RAG (Retrieval-Augmented Generation) assistant specialized in Python programming. It leverages a curated knowledge base of 25,000+ Stack Overflow Q&A pairs to provide grounded, accurate, and cited technical support to developers.

- **Objective:** To reduce developer "search fatigue" by providing instant, validated answers to Python queries.
- **Key Metric:** Sub-2-second response time with verifiable sources.

---

## 2. System Architecture
The system is built on a modern, decoupled architecture designed for high speed and low memory footprint.

### **The Flow:**
1.  **User Input:** The query is captured via a responsive **Astro/React** frontend.
2.  **Vectorization:** The **FastAPI** backend sends the query to the **Hugging Face Inference API** to generate a 384-dimension embedding.
3.  **Retrieval:** A Cosine Similarity search is performed in **Supabase (pgvector)** to find the top 3 most relevant context chunks.
4.  **Generation:** The query and retrieved context are sent to **Groq (Llama 3)**, which generates a natural language response.
5.  **Output:** The response is rendered with Markdown support and clickable citations.

---

## 3. The Technical Stack
| Layer | Technology |
| :--- | :--- |
| **Frontend** | Astro, React, Tailwind CSS, Framer Motion |
| **Backend** | FastAPI, Python 3.11, LangChain |
| **LLM** | Groq (Llama 3 70B) |
| **Embeddings** | BAAI/bge-small-en-v1.5 (via Hugging Face API) |
| **Database** | Supabase (PostgreSQL + pgvector) |
| **Deployment** | Vercel (Frontend), Render (Backend) |

---

## 4. Key Design Decisions & Trade-offs
### **Memory-Efficient Inference**
Initially, the system used local `sentence-transformers`. However, the heavy PyTorch dependency exceeded Render's 512MB RAM limit.
- **Solution:** Migrated to the **Hugging Face Inference API**. This reduced backend memory usage by **~80%**, ensuring 100% stability on free-tier cloud infrastructure.

### **Strategic Data Curation**
While the full dataset contains 50,000+ records, the current production database is optimized with **25,000 high-impact Python records**.
- **Reasoning:** This trade-off ensures sub-second retrieval latency and stays within the free-tier storage limits of Supabase while still providing a vast knowledge base.

---

## 5. Scaling to 100+ Concurrent Users
To transition from a Proof of Concept (PoC) to a production-scale system, the following strategies would be implemented:

### **A. Latency & Throughput**
- **Semantic Caching (Redis):** Cache embeddings and responses for common questions. If a query is 95% similar to a cached one, serve the answer in <10ms.
- **Async Concurrency:** Fully migrate all DB and API calls to `async/await` to handle hundreds of non-blocking requests per second.

### **B. Infrastructure Scaling**
- **Horizontal Scaling:** Deploy the backend as a Dockerized cluster on **AWS ECS** or **Kubernetes** with an auto-scaling group based on CPU/RAM load.
- **Database Optimization:** Move to a managed Postgres cluster with **Read Replicas** to distribute the vector search load.

---

## 6. Future Roadmap
1.  **Monitoring & Observability:** Integrate **LangSmith** to track retrieval quality and detect "hallucination" patterns.
2.  **Multi-Turn Memory:** Implement session-based memory (PostgresChatMessageHistory) to allow for follow-up questions.
3.  **Continuous Data Sync:** Build an automated pipeline using **GitHub Actions** to pull the latest "Python" tagged questions from Stack Overflow weekly.

---

## 7. Project Links
- **Live Application:** [Paste Vercel Link]
- **Backend API:** [Paste Render Link]
- **Source Code:** [Paste GitHub Link]
