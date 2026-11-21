<div align="center">

# 🤖 LangGraph AI Chatbot

### Multi-user conversational AI built with LangGraph, Streamlit & SQLite

**Python · LangGraph · Streamlit · SQLite · Argon2 · LLM API**

A hands-on AI chatbot project featuring user registration, login, persistent conversations, and a clean chat interface.

</div>

---

## 📸 Application Screenshots

### 🔐 Login & Registration

The application provides account creation and login before entering the chat interface. Passwords are hashed with Argon2 rather than stored in plaintext.

> 📷 **Screenshot pending:** Save a screenshot of your real login/registration screen as `screenshots/login-register.png` and the image below will appear automatically.

![Login and Registration Screen](screenshots/login-register.png)

### 💬 AI Chat Interface

Chat with the assistant, start new conversations, and access conversation titles from the sidebar.

![AI Chat Interface](screenshots/chat-interface.png)

---

## ✨ Features

- **Login & registration:** Username/password account creation and sign-in.
- **Password hashing:** Argon2-based password storage and verification.
- **AI-powered chat:** LLM responses using a LangGraph workflow.
- **Streaming responses:** Chat messages are streamed into the Streamlit interface.
- **Conversation history:** SQLite-backed LangGraph checkpoints.
- **Multiple conversations:** Separate chat threads with saved titles.
- **User-scoped sidebar:** Conversation lists are queried for the signed-in user.
- **Environment configuration:** API credentials read from environment variables, not hardcoded.

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Frontend | Streamlit |
| AI orchestration | LangGraph |
| LLM integration | LangChain `ChatOpenAI` with a configurable OpenAI-compatible API endpoint |
| Database | SQLite |
| Persistence | LangGraph `SqliteSaver` |
| Authentication | Username/password, Argon2 password hashing |

## 🧩 How It Works

```text
User
  │
  ▼
Streamlit UI ──► Registration / Login ──► SQLite users table
  │
  ▼
Chat input + thread ID
  │
  ▼
LangGraph chatbot workflow
  │
  ▼
LLM API ──► Streamed response
  │
  ▼
Streamlit chat display
  │
  └── SQLite checkpoints + conversation metadata
```

## 📁 Project Structure

```text
LangGraph-AI-Chatbot/
├── langGraph_backend.py             # LangGraph, SQLite and authentication logic
├── streamlit_frontend_threading.py  # Streamlit UI and chat sessions
├── screenshots/
│   ├── chat-interface.png
│   └── login-register.png           # Add your actual screenshot
├── .gitignore
└── README.md
```

## 🚀 Run Locally

**1. Clone the repository**

```bash
git clone https://github.com/rajchakrawarti999/LangGraph-AI-Chatbot.git
cd LangGraph-AI-Chatbot
```

**2. Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # Linux / WSL / macOS
```

**3. Install dependencies**

Install the dependencies used by the project (for example, `streamlit`, `langgraph`, `langchain-openai`, `langgraph-checkpoint-sqlite`, `python-dotenv`, and `argon2-cffi`). A pinned `requirements.txt` should be added after verifying the working environment.

**4. Configure your model API**

Create a local `.env` file and provide your own API credentials:

```dotenv
FREEMODEL_API_KEY=your_api_key_here
```

The current backend is configured for a specific OpenAI-compatible model provider. Review `langGraph_backend.py` if you want to use another provider or model.

**5. Launch the app**

```bash
streamlit run streamlit_frontend_threading.py
```

Open the local URL displayed in the terminal (usually `http://localhost:8501`).

## 🔒 Security & Current Limitations

> **Local learning/portfolio project — not production-ready yet.** The UI filters conversation listings by user, but ownership must also be enforced at the backend when loading checkpoints and streaming messages. Do not deploy this as a public multi-user service until those authorization checks and broader security controls are completed.

- Never commit `.env`, API tokens, `chatbot.db`, or its `-wal`/`-shm` files.
- Add server-side conversation ownership checks, rate limiting, robust session management, and deployment security review before public hosting.
- The local SQLite setup is intended for development, not high-concurrency production use.

## 🗺️ Future Improvements

- Backend-enforced conversation authorization
- Chat deletion and renaming
- Improved authentication and session lifecycle
- Automated tests and error handling
- Docker and production-ready deployment
- Model configuration and observability

## 👨‍💻 Author

**Raj Chakrawarti**  
GitHub: [@rajchakrawarti999](https://github.com/rajchakrawarti999)

---

<div align="center"><sub>Built as a practical LangGraph and backend engineering learning project.</sub></div>
