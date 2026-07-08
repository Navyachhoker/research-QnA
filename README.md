# 📚 ResearchGPT

> An AI-powered research assistant that allows users to upload research papers, build a semantic knowledge base, ask context-aware questions, generate summaries, and perform paper analysis using Retrieval-Augmented Generation (RAG).


---

## 📖 Overview

ResearchGPT is a full-stack AI application designed to simplify academic research by enabling users to interact with research papers conversationally.

Instead of manually searching through lengthy PDFs, users can upload papers into a personal knowledge base and ask natural language questions. The application retrieves the most relevant sections using vector similarity search and generates accurate, context-aware answers using a Large Language Model.

The project demonstrates modern AI application architecture by combining:

- Retrieval-Augmented Generation (RAG)
- Vector Databases
- Semantic Search
- FastAPI REST APIs
- React Frontend
- JWT Authentication
- Persistent Chat Sessions


# ✨ Features

### 📄 Research Paper Management

- Upload research papers (PDF)
- Automatic PDF text extraction
- Intelligent text chunking
- Persistent vector storage
- View uploaded papers
- Prevent duplicate indexing

---

### 🤖 AI Question Answering

Ask questions such as:

> "What methodology is used?"

> "Summarize the experiments."

> "What datasets were used?"

The application:

1. Retrieves relevant chunks
2. Builds contextual prompts
3. Sends them to the LLM
4. Generates grounded responses

---

### 🧠 Semantic Search

Instead of keyword matching, ResearchGPT uses sentence embeddings to perform semantic similarity search.

Benefits include:

- understands meaning rather than keywords
- retrieves relevant context
- reduces hallucinations
- improves answer quality

---

### 📑 Paper Analysis

Generate:

- concise summaries
- key contributions
- methodologies
- limitations
- future work

using AI.

---

### 💬 Chat History

Every conversation is stored.

Users can:

- create sessions
- revisit previous chats
- continue conversations
- maintain research history

---

### 🔒 Authentication

- JWT Authentication
- Secure Login
- User Registration
- Protected Routes
- Token-based Authorization

---

# 🏗 Architecture

```
                 +-------------------+
                 |   React Frontend  |
                 +---------+---------+
                           |
                     REST API
                           |
                 +---------v---------+
                 |      FastAPI      |
                 +---------+---------+
                           |
          +----------------+----------------+
          |                                 |
          |                                 |
   Authentication                     AI Services
          |                                 |
      SQLite DB                    RAG Pipeline
                                            |
                    +-----------------------+
                    |
            Sentence Transformer
                    |
               Vector Embeddings
                    |
                ChromaDB Vector Store
                    |
             Similarity Retrieval
                    |
             Context Construction
                    |
               Large Language Model
                    |
                Final AI Response
```

---

# ⚙ Tech Stack

## Frontend

- React
- React Router
- Axios
- CSS

---

## Backend

- FastAPI
- Python
- JWT Authentication
- SQLite
- SQLAlchemy

---

## AI Stack

- Sentence Transformers
- ChromaDB
- Retrieval-Augmented Generation (RAG)
- Large Language Model (Groq/OpenAI compatible)

---

## Other Libraries

- PyMuPDF
- python-dotenv
- passlib
- python-jose
- Pydantic

---

# 📂 Project Structure

```
ResearchGPT/
│
├── app/
│   ├── api/
│   ├── services/
│   ├── utils/
│   ├── database/
│   ├── models/
│   ├── schemas/
│   ├── core/
│   └── main.py
│
├── uploads/
├── chroma_db/
├── requirements.txt
├── .env
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── screenshots/
│   ├── login.png
│   ├── dashboard.png
│   ├── chat.png
│   └── analysis.png
│
└── README.md
```

---

# 🧠 RAG Pipeline

```
Upload PDF
      │
      ▼
Extract Text
      │
      ▼
Chunk Document
      │
      ▼
Generate Embeddings
      │
      ▼
Store in ChromaDB
      │
      ▼
User asks Question
      │
      ▼
Vector Similarity Search
      │
      ▼
Retrieve Top-k Chunks
      │
      ▼
Build Prompt
      │
      ▼
Large Language Model
      │
      ▼
Answer
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/ResearchGPT.git

cd ResearchGPT
```

---

## Backend

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```

---

Create a `.env`

```env
GROQ_API_KEY=your_api_key

SECRET_KEY=your_secret_key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Run backend

```bash
uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# 📌 API Endpoints

## Authentication

| Method | Endpoint | Description |
|----------|-----------|------------|
| POST | /auth/register | Register user |
| POST | /auth/login | Login |

---

## Papers

| Method | Endpoint |
|----------|-----------|
| POST | /papers/upload |
| GET | /papers/list |

---

## Question Answering

| Method | Endpoint |
|----------|-----------|
| POST | /qa/ask |

---

## Analysis

| Method | Endpoint |
|----------|-----------|
| POST | /analyze |

---

## Sessions

| Method | Endpoint |
|----------|-----------|
| GET | /sessions |
| POST | /sessions |
| GET | /sessions/{id} |

---

# 🔒 Security Features

- Password hashing using bcrypt
- JWT Authentication
- Protected API Routes
- Secure Token Verification
- Environment Variables
- Input Validation
- Error Handling

---

# 💡 Challenges Solved

### Efficient Document Retrieval

Instead of sending entire PDFs to the LLM, the application retrieves only the most relevant sections using vector similarity search.

---

### Reducing Hallucinations

The LLM receives only grounded context extracted from the uploaded research papers, improving factual accuracy.

---

### Persistent Knowledge Base

All embeddings are stored in ChromaDB, eliminating the need to reprocess documents after every restart.

---

### Scalable Architecture

The project separates concerns into:

- API layer
- Service layer
- Utility layer
- Database layer
- AI layer

making it easier to maintain and extend.

---

# 📈 Future Improvements

- Multi-document question answering
- Citation-aware responses
- PDF annotations
- OCR support for scanned papers
- Hybrid Search (BM25 + Vector Search)
- Cross-paper comparison
- Research paper recommendations
- User-specific vector collections
- Streaming AI responses
- Docker deployment
- CI/CD pipeline
- Cloud deployment (AWS/GCP/Azure)

---

# 🎯 Learning Outcomes

This project demonstrates practical experience with:

- Retrieval-Augmented Generation (RAG)
- FastAPI Backend Development
- React Frontend Development
- Vector Databases
- Semantic Search
- JWT Authentication
- REST API Design
- AI Application Development
- Prompt Engineering
- Large Language Models
- Production-ready Project Structure

---

# 🤝 Contributing

Contributions, issues, and feature requests are welcome.

If you'd like to improve the project, feel free to fork the repository and submit a pull request.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👩‍💻 Author

**Navya Chhoker**

If you found this project interesting, consider giving it a ⭐ on GitHub!