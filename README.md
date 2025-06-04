# Lead-to-Lease Chat Microservice

A tenant-facing chat microservice for property bookings. This project provides an AI-powered assistant that guides prospects through the leasing process, collects their information, checks property availability, and schedules tours, all via a conversational interface.

---

## Architecture Overview

The project is organized as a full-stack application with a FastAPI backend and a simple HTML/JS/CSS frontend.

- **Frontend:** A responsive chat UI built with HTML, CSS, and vanilla JavaScript.
- **Backend:** A FastAPI server that manages chat sessions, integrates with OpenAI's GPT models, and interacts with a SQLite database for user, property, and booking management.
- **Database:** SQLite database (`lead_to_lease.db`) stores users, properties, availability slots, and bookings.
- **Agent:** Uses LangChain and OpenAI to power the conversational logic and tool integrations.

---

## Dependencies

- Python 3.10+
- [FastAPI](https://fastapi.tiangolo.com/) (see `requirements.txt`)
- [LangChain](https://python.langchain.com/)
- [OpenAI API](https://platform.openai.com/)
- [dateutil](https://dateutil.readthedocs.io/)
- [pydantic](https://docs.pydantic.dev/)
- [sqlite3](https://docs.python.org/3/library/sqlite3.html)

---

## Installation & Setup

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd homewiz-takehome-challenge
   ```
2. **Install Python dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure `config.ini`**
   Before running the app, update the settings in `backend/config.ini`:
   - `OPENAI_API_KEY`: Your OpenAI API key.
   - `DATABASE_FILE`: Path to your SQLite database file (default: lead_to_lease.db).
   - `MODEL`: OpenAI model to use (e.g., gpt-4o).
   - `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `FROM_EMAIL`: SMTP settings for sending confirmation emails.
   **Important:** Do not commit your API keys or sensitive credentials to version control.
4. **Initialize and seed the database:**
   The backend will automatically initialize and seed the database on first run using `backend/seed.sql`.
5. **Run the backend server:**
   ```sh
   cd backend
   uvicorn main:app --reload --port 8000
   ```
6. **Open the frontend:**
  Open `frontend/index.html` in your browser. The frontend expects the backend to be running at `http://localhost:8000`.

---

## Project Structure & File Descriptions

homewiz-takehome-challenge/
│
├── README.md
├── requirements.txt
│
├── backend/
│   ├── agent.py
│   ├── config.ini
│   ├── db.py
│   ├── lead_to_lease.db
│   ├── main.py
│   ├── schema.py
│   ├── seed.sql
│   ├── tools.py
│   └── utils.py
│   
└── frontend/
    ├── index.html
    ├── script.js
    └── styles.css

Backend Files
- `agent.py`: Sets up the conversational agent, integrates LangChain tools, manages per-session memory and agent executors.
- `config.ini`: Stores configuration for API keys, database, and email. Update this file before running the app.
- `db.py`: Handles all database operations (users, properties, availability, bookings).
- `main.py`: FastAPI app definition, chat endpoint, CORS setup, and app lifecycle management.
- `schema.py`: Pydantic models for validating and structuring API and agent tool data.
- `seed.sql`: SQL statements to populate the database with sample users, properties, and availability.
- `tools.py`: Implements business logic for validation, booking, and prospect info storage.
- `utils.py`: Utility functions for sending emails and loading configuration.

Frontend Files
- `index.html`: Main chat interface.
- `script.js`: Handles chat form submission, displays messages, and communicates with the backend.
- `styles.css`: Styles for the chat UI.

---

## Usage

1. Open the chat UI in your browser.
2. Interact with the AI assistant to provide your details and book a property tour.
3. The assistant will validate your information, check availability, and send a confirmation email upon successful booking.

---

## Notes

- The backend must be running for the frontend to function.
- The database is seeded with sample data for testing.
- Email sending requires valid SMTP credentials in config.ini.
- For production use, secure your API keys and sensitive data.

---

## Tradeoffs & Next Steps

#### Tradeoffs
- **Per-Session Agent vs. Shared Agent:**
Each chat session uses its own `AgentExecutor` with a dedicated memory instance. This ensures session isolation and avoids concurrency issues. However, it introduces slight memory overhead. For demo or light usage, this is acceptable. In a production environment, a caching mechanism  would help manage memory more efficiently.

- **In-Memory Session Store:**
The app currently uses Python dictionaries to store agent and memory objects. This works well for local development but is not suitable for multi-instance deployments or persistent conversations. A Redis-backed memory or database-based session manager would be more robust.

- **Gmail SMTP Limitations:**
Gmail overrides the From: address unless it matches the authenticated Gmail account. This means using a custom address like donotreply@lead2lease.com won’t work with Gmail SMTP directly. To support branded sender addresses, a transactional email service like SendGrid, Mailgun, or Postmark should be used.

- **No Session Expiration:**
There is no built-in session cleanup logic. All session memory and agent instances persist in RAM for the lifetime of the server process. This is fine for a take-home project but would not scale in a production environment.

#### Next Steps
- **Add Persistent or Distributed Memory Store:**
Replace the in-memory session and memory stores with Redis, SQLite, or another persistent backend.
- **Implement Session TTL or LRU Eviction:**
Add logic to expire inactive sessions after a time window (e.g., 30 minutes), or limit the total number of cached sessions using an LRU (Least Recently Used) strategy.
- **Extend Conversational Flow:**
Enhance the agent with support for rescheduling, canceling, or modifying tour bookings. This could include multiple-turn interactions or action plans with follow-up prompts.