import os
import uuid

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="FinBot — AI Stock Research Assistant",
    page_icon="📈",
    layout="wide",
)

st.markdown("""
<style>
    .route-badge {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
    }
    .badge-stock    { background: #e8f5e9; color: #2e7d32; }
    .badge-news     { background: #e3f2fd; color: #1565c0; }
    .badge-finance  { background: #f3e5f5; color: #6a1b9a; }

    .disclaimer {
        font-size: 12px;
        color: #888;
        font-style: italic;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "last_route" not in st.session_state:
    st.session_state.last_route = None


# ── Cached resources ───────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading FinBot agent...")
def load_agent():
    from agent.agent import build_agent
    return build_agent()


@st.cache_resource(show_spinner="Loading semantic router...")
def load_router():
    from agent.agent import build_router
    return build_router()


agent = load_agent()
router = load_router()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📈 FinBot")
    st.caption("AI-powered Stock Research Assistant")
    st.divider()

    st.markdown("**About**")
    st.markdown(
        "FinBot is a multi-tool AI agent that delivers real-time equity research "
        "briefs by combining stock fundamentals, live news, and Wikipedia context."
    )
    st.divider()

    if st.session_state.last_route:
        st.markdown("**Last query routed to**")
        badge_map = {
            "stock_analysis": ("📊", "badge-stock", "Stock Analysis"),
            "market_news":    ("📰", "badge-news",  "Market News"),
            "general_finance":("📚", "badge-finance","General Finance"),
        }
        icon, cls, label = badge_map.get(
            st.session_state.last_route, ("🔍", "badge-stock", st.session_state.last_route)
        )
        st.markdown(
            f'<span class="route-badge {cls}">{icon} {label}</span>',
            unsafe_allow_html=True,
        )
        st.divider()

    st.markdown("**Try asking**")
    examples = [
        "Give me an analyst brief on NVDA",
        "Compare Apple and Microsoft valuations",
        "What's the latest news on Tesla?",
        "Explain what a P/E ratio means",
        "Is Amazon overvalued right now?",
    ]
    for ex in examples:
        st.caption(f"› {ex}")

    st.divider()

    if st.button("🗑️ New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.last_route = None
        st.rerun()

    st.markdown(
        '<p class="disclaimer">FinBot provides data-driven insights only — not financial advice.</p>',
        unsafe_allow_html=True,
    )


# ── Main area ──────────────────────────────────────────────────────────────────
st.title("📈 FinBot — Stock Research Assistant")
st.caption("Powered by LangGraph · Groq LLaMA · Semantic Router · yFinance")

if not st.session_state.messages:
    st.markdown("""
Welcome! I'm **FinBot**, your AI equity research assistant.

I can help you with:
- 📊 **Stock fundamentals** — price, P/E ratio, market cap, revenue growth, EPS
- 📰 **Market news** — latest headlines and sentiment analysis
- 📚 **Finance education** — plain-English explanations of financial concepts

> *Disclaimer: FinBot provides data-driven research signals only, not financial advice.*
    """)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not os.getenv("GROQ_API_KEY"):
    st.error("⚠️ `GROQ_API_KEY` not found. Copy `.env.example` to `.env` and add your key.")
    st.stop()

if prompt := st.chat_input("Ask about a stock or finance topic..."):

    # Route detection
    detected_route = None
    if router:
        try:
            result = router(prompt)
            detected_route = result.name if result and result.name else None
            st.session_state.last_route = detected_route
        except Exception:
            detected_route = "finance"

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Out-of-scope guard
    if router and detected_route is None:
        reply = (
            "I'm specialised in **stock research and financial analysis**. "
            "Try asking something like:\n"
            "- *Give me an analyst brief on AAPL*\n"
            "- *What's the latest news on Tesla?*\n"
            "- *What is a P/E ratio?*"
        )
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.rerun()

    # Call the agent
    with st.chat_message("assistant"):
        with st.spinner("Researching…"):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            try:
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": prompt}]},
                    config,
                )
                reply = result["messages"][-1].content
            except Exception as e:
                reply = f"⚠️ Something went wrong: `{e}`\n\nPlease check your API keys and try again."

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
