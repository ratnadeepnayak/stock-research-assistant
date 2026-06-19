import os
import sqlite3

from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent

from agent.prompts import SYSTEM_PROMPT
from agent.tools import build_tools

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "finbot.db")


def build_agent():
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        temperature=0,
        max_retries=2,
    )

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    return create_react_agent(
        model=llm,
        tools=build_tools(),
        prompt=SystemMessage(content=SYSTEM_PROMPT),
        checkpointer=checkpointer,
    )


def build_router():
    try:
        from semantic_router import Route
        from semantic_router.encoders import HuggingFaceEncoder
        from semantic_router.routers import SemanticRouter

        encoder = HuggingFaceEncoder(
            name=os.getenv("EMBED_MODEL", "Qwen/Qwen3-Embedding-0.6B")
        )

        routes = [
            Route(
                name="stock_analysis",
                utterances=[
                    "What is Apple's P/E ratio?",
                    "Show me Tesla's market cap",
                    "What are NVIDIA's earnings per share?",
                    "How much revenue did Microsoft make last year?",
                    "What is Amazon's 52-week high?",
                    "Give me the fundamentals for Google stock",
                    "What is the current valuation of Meta?",
                    "How profitable is JPMorgan?",
                    "Is Berkshire Hathaway overvalued?",
                    "What's the dividend yield for Coca-Cola?",
                ],
            ),
            Route(
                name="market_news",
                utterances=[
                    "What is the latest news about Apple?",
                    "What happened with Tesla recently?",
                    "Any recent announcements from the Fed?",
                    "Tell me about recent layoffs in tech",
                    "What's happening with the banking sector?",
                    "Any earnings surprises this quarter?",
                    "What are analysts saying about NVIDIA?",
                    "Recent news on interest rate decisions",
                    "What did Jerome Powell say this week?",
                    "Breaking news about the crypto market",
                ],
            ),
            Route(
                name="general_finance",
                utterances=[
                    "What is compound interest?",
                    "Explain how the stock market works",
                    "What is a P/E ratio?",
                    "What is dollar cost averaging?",
                    "How do ETFs work?",
                    "What is the difference between a stock and a bond?",
                    "Explain what inflation means",
                    "What is a hedge fund?",
                    "How does the Federal Reserve control interest rates?",
                    "What is diversification in investing?",
                ],
            ),
        ]

        return SemanticRouter(encoder=encoder, routes=routes, auto_sync="local")

    except Exception:
        return None
