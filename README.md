# 📈 FinBot — AI Stock Research Assistant

An AI-powered equity research assistant built with **LangGraph agents**, **Groq LLaMA**, and a **Semantic Router**. Ask FinBot about any stock and get a structured analyst brief in seconds.

> **Disclaimer:** FinBot provides data-driven research signals only — not financial advice.

---

## Features

- 📊 **Stock Fundamentals** — real-time price, P/E ratio, market cap, revenue growth, EPS via yFinance
- 📰 **Market News** — latest headlines and sentiment via Yahoo Finance News
- 📚 **Finance Education** — plain-English explanations of financial concepts via Wikipedia
- 🧠 **Semantic Router** — intelligently routes queries to the right tool pipeline without keyword matching
- 💾 **Persistent Memory** — remembers your conversation across sessions using SQLite
- 🔄 **ReAct Loop** — agent reasons, calls tools, observes results, and iterates until satisfied

---

## Architecture

```
User Query
    │
    ▼
Semantic Router  ──── out of scope? ──► "I can't help with that"
    │
    ▼ finance-related
Finance Agent (LangGraph ReAct)
    ├── get_stock_fundamentals  (yFinance)
    ├── YahooFinanceNewsTool    (Yahoo Finance)
    ├── WikipediaQueryRun       (Wikipedia)
    └── search_recent_news      (SerpAPI, optional)
    │
    ▼
SQLite Checkpointer  ──► persistent memory across sessions
    │
    ▼
Streamlit UI  ──► structured analyst brief
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq — LLaMA 3.3 70B |
| Agent framework | LangGraph `create_react_agent` |
| Routing | Semantic Router + HuggingFace Embeddings |
| Tools | yFinance, Yahoo Finance News, Wikipedia, SerpAPI |
| Memory | SQLite via `langgraph-checkpoint-sqlite` |
| UI | Streamlit |

---

## Setup

**1. Clone the repo**
```bash
git clone <your-repo-url>
cd stock-research-assistant
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure API keys**
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

**4. Run the app**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Example Queries

```
Give me an analyst brief on NVDA
Compare Apple and Microsoft on valuation
What's the latest news on Tesla?
Is Amazon overvalued right now?
Explain what a P/E ratio means
What happened with the Fed rate decision?
```

---

## Project Structure

```
stock-research-assistant/
├── app.py                  # Streamlit UI
├── agent/
│   ├── agent.py            # LangGraph agent + Semantic Router setup
│   ├── tools.py            # LangChain tools (yFinance, news, Wikipedia)
│   └── prompts.py          # System prompt for FinBot
├── data/
│   └── finbot.db           # SQLite persistent memory (auto-created)
├── .env.example            # Environment variables template
├── requirements.txt
└── README.md
```

---

## How It Works

1. **Semantic Router** classifies the user's query into `stock_analysis`, `market_news`, `general_finance`, or out-of-scope — using embedding similarity, not keywords.

2. **Finance Agent** runs a ReAct loop: it reasons about which tools to call, executes them, observes the results, and repeats until it has enough information to write the final brief.

3. **SQLite Checkpointer** stores the full message history per session thread, so the agent remembers context across multiple turns ("Now compare it with AMD").

4. **Streamlit UI** displays the conversation, shows which route was detected, and lets users start fresh sessions.
