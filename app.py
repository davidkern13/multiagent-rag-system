"""
Trading Analysis with Charts + Token Analysis
Fixed version with show_tokens working
"""

import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts
import re
from datetime import datetime
from typing import List, Dict


def extract_trading_data(contexts: List[str]) -> List[Dict]:
    """Extract OHLCV data from contexts"""
    data = []

    for ctx in contexts:
        # Pattern: Date Open High Low Close %Change Volume
        pattern = r"(\d{4}-\d{2}-\d{2})\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+[\+\-]?([\d.]+)%"
        matches = re.findall(pattern, ctx)

        for match in matches:
            date, open_p, high, low, close, pct = match

            # Convert to Unix timestamp
            dt = datetime.strptime(date, "%Y-%m-%d")
            timestamp = int(dt.timestamp())

            data.append(
                {
                    "time": timestamp,
                    "date": date,
                    "open": float(open_p),
                    "high": float(high),
                    "low": float(low),
                    "close": float(close),
                    "change_pct": float(pct),
                }
            )

    # Sort by time
    data.sort(key=lambda x: x["time"])
    return data


def find_highlight_dates(query: str, data: List[Dict]) -> List[str]:
    """Find dates to highlight based on query"""
    query_lower = query.lower()

    if "highest" in query_lower or "maximum" in query_lower:
        max_day = max(data, key=lambda x: x["change_pct"])
        return [max_day["date"]]

    elif "lowest" in query_lower or "minimum" in query_lower:
        min_day = min(data, key=lambda x: x["change_pct"])
        return [min_day["date"]]

    return []


def analyze_token_usage_simple(query: str, answer: str, contexts: List[str]) -> Dict:
    """Simple token analysis - approximation"""
    # Rough approximation: 1 token ≈ 4 characters
    query_tokens = len(query) // 4
    answer_tokens = len(answer) // 4
    context_tokens = sum(len(ctx) for ctx in contexts) // 4

    return {
        "query_tokens": query_tokens,
        "answer_tokens": answer_tokens,
        "context_tokens": context_tokens,
        "total_tokens": query_tokens + answer_tokens + context_tokens,
    }


# Page config
st.set_page_config(layout="wide", page_title="Trading Analysis")

# Custom CSS
st.markdown(
    """
<style>
    .token-info {
        background-color: #e8f4f8;
        border-left: 4px solid #1f77b4;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.85em;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("📊 Trading Analysis")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chart_data" not in st.session_state:
    st.session_state.chart_data = None
if "show_tokens" not in st.session_state:
    st.session_state.show_tokens = False

# Two columns
col_chat, col_chart = st.columns([1, 1])

with col_chat:
    st.subheader("💬 Chat")

    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # Show token info if available
            if "token_info" in msg and st.session_state.show_tokens:
                st.markdown(
                    f'<div class="token-info">{msg["token_info"]}</div>',
                    unsafe_allow_html=True,
                )

    # Chat input
    if prompt := st.chat_input("Ask about trading data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                # Import system
                from core.system_builder import build_system

                @st.cache_resource
                def get_manager():
                    return build_system("data/data.pdf")

                manager = get_manager()
                answer, contexts, _ = manager.route(prompt)

                st.markdown(answer)

                # Token analysis
                token_data = analyze_token_usage_simple(prompt, answer, contexts)
                token_report = f"""
📊 Token Usage:
  Query: {token_data['query_tokens']} tokens
  Answer: {token_data['answer_tokens']} tokens
  Context: {token_data['context_tokens']} tokens
  Total: {token_data['total_tokens']} tokens
"""

                # Show if enabled
                if st.session_state.show_tokens:
                    st.markdown(
                        f'<div class="token-info">{token_report}</div>',
                        unsafe_allow_html=True,
                    )

                # Save to messages
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "token_info": token_report}
                )

                # Extract data for chart
                if contexts:
                    data = extract_trading_data(contexts)
                    if data:
                        highlight_dates = find_highlight_dates(prompt, data)
                        st.session_state.chart_data = {
                            "data": data,
                            "highlight_dates": highlight_dates,
                        }

with col_chart:
    st.subheader("📈 Candlestick Chart")

    if st.session_state.chart_data:
        data = st.session_state.chart_data["data"]
        highlight_dates = st.session_state.chart_data["highlight_dates"]

        # Prepare candlestick data
        candlestick_data = []
        markers = []

        for d in data:
            candlestick_data.append(
                {
                    "time": d["time"],
                    "open": d["open"],
                    "high": d["high"],
                    "low": d["low"],
                    "close": d["close"],
                }
            )

            # Add marker if highlighted
            if d["date"] in highlight_dates:
                markers.append(
                    {
                        "time": d["time"],
                        "position": "aboveBar",
                        "color": "#f68410",
                        "shape": "circle",
                        "text": f"{d['change_pct']:+.2f}%",
                    }
                )

        # Chart options
        chartOptions = {
            "layout": {
                "textColor": "black",
                "background": {"type": "solid", "color": "white"},
            },
            "grid": {
                "vertLines": {"color": "#e1e1e1"},
                "horzLines": {"color": "#e1e1e1"},
            },
            "crosshair": {"mode": 0},
        }

        # Series
        seriesCandlestick = [
            {
                "type": "Candlestick",
                "data": candlestick_data,
                "options": {
                    "upColor": "#26a69a",
                    "downColor": "#ef5350",
                    "borderVisible": False,
                    "wickUpColor": "#26a69a",
                    "wickDownColor": "#ef5350",
                },
            }
        ]

        # Add markers if any
        if markers:
            seriesCandlestick[0]["markers"] = markers

        # Render
        renderLightweightCharts(
            [{"chart": chartOptions, "series": seriesCandlestick}], "candlestick"
        )

        # Show stats
        st.caption(f"📊 Showing {len(data)} days")

        with st.expander("Statistics"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("High", f"${max(d['high'] for d in data):.2f}")
            with col2:
                st.metric("Low", f"${min(d['low'] for d in data):.2f}")
            with col3:
                max_pct = max(d["change_pct"] for d in data)
                st.metric("Max Change", f"+{max_pct:.2f}%")

    else:
        st.info("👈 Ask a question to see live chart!")
        st.caption("Try asking:")
        st.code("What was the highest daily percentage increase?")
        st.code("Show me trading data for April")
        st.code("What happened on 2025-04-09?")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    st.session_state.show_tokens = st.checkbox(
        "Show Token Usage",
        value=st.session_state.show_tokens,
        help="Display token usage for each response",
    )

    st.divider()

    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chart_data = None
        st.rerun()

    st.divider()

    st.caption("⚠️ Not financial advice • Educational only")
