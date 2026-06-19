import os

import yfinance as yf
from langchain.tools import tool

try:
    from langchain_community.tools import WikipediaQueryRun
    from langchain_community.utilities import WikipediaAPIWrapper
except Exception:
    WikipediaQueryRun = None
    WikipediaAPIWrapper = None

try:
    from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
except Exception:
    YahooFinanceNewsTool = None


@tool
def get_stock_fundamentals(ticker: str) -> dict:
    """
    Get stock fundamentals for a given ticker symbol (e.g. AAPL, NVDA, TSLA).
    Returns current price, P/E ratio, market cap, revenue growth, 52-week range,
    EPS, dividend yield, sector, and industry.
    """
    stock = yf.Ticker(ticker.upper())
    info = stock.info
    return {
        "ticker": ticker.upper(),
        "price": info.get("currentPrice"),
        "pe_ratio": info.get("trailingPE"),
        "market_cap": info.get("marketCap"),
        "revenue_growth": info.get("revenueGrowth"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "eps": info.get("trailingEps"),
        "dividend_yield": info.get("dividendYield"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "company_name": info.get("longName"),
    }


def build_tools() -> list:
    tools = [get_stock_fundamentals]

    try:
        tools.append(YahooFinanceNewsTool())
    except Exception:
        pass

    try:
        tools.append(WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=2)))
    except Exception:
        pass

    serpapi_key = os.getenv("SERPAPI_API_KEY")
    if serpapi_key:
        try:
            from langchain_community.utilities import SerpAPIWrapper

            serp = SerpAPIWrapper(
                serpapi_api_key=serpapi_key,
                params={"tbm": "nws", "tbs": "qdr:d"},
            )

            @tool
            def search_recent_news(query: str) -> str:
                """
                Search Google News from the past 24 hours for financial news,
                earnings announcements, analyst upgrades, and market events.
                """
                return serp.run(query)

            tools.append(search_recent_news)
        except Exception:
            pass

    return tools
