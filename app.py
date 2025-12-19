"""
Trading Analysis - Container-based Layout
"""

import streamlit as st

# Use REAL tokenizer from utils
from core.tokenizer import analyze_token_usage, format_token_report


# Page config
st.set_page_config(
    layout="wide",
    page_title="Trading Analysis",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "Trading Analysis System - Educational purposes only",
    },
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_tokens" not in st.session_state:
    st.session_state.show_tokens = False
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# Layout: Chat on left, Examples on right
col1, col2 = st.columns([2.5, 1])

with col1:
    st.markdown("💬 Chat")

    # Chat container with fixed height
    chat_container = st.container(height=600)

    with chat_container:
        # Display messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

                if "token_info" in msg and st.session_state.show_tokens:
                    st.caption(msg["token_info"])

    # Chat input OUTSIDE container (always visible at bottom)
    user_input = st.chat_input("Ask about trading data...")

    # Handle input
    prompt = None
    if st.session_state.pending_query:
        prompt = st.session_state.pending_query
        st.session_state.pending_query = None
    elif user_input:
        prompt = user_input

    # Process prompt
    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate response
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                from core.system_builder import build_system

                @st.cache_resource
                def get_manager():
                    return build_system("data/data.pdf")

                manager = get_manager()

                # Placeholders
                status_placeholder = st.empty()
                message_placeholder = st.empty()

                full_response = ""
                contexts = []
                stream_started = False

                # Show spinner
                with status_placeholder:
                    with st.spinner("🔄 Processing..."):
                        st.caption("🧠 Routing to agent...")
                        st.caption("📊 Retrieving contexts...")
                        st.caption("🔍 Running AutoMerging...")

                        # Stream response
                        for delta, ctxs, is_final in manager.route_stream(prompt):
                            if not is_final:
                                if not stream_started:
                                    status_placeholder.empty()
                                    stream_started = True

                                full_response += delta
                                message_placeholder.markdown(full_response + "▌")
                            else:
                                full_response = delta
                                contexts = ctxs

                # Final answer
                status_placeholder.empty()
                message_placeholder.markdown(full_response)

                # Tokens - use tokenizer.py functions!
                if st.session_state.show_tokens:
                    token_data = analyze_token_usage(
                        query=prompt,
                        answer=full_response,
                        contexts=contexts,
                        response_obj=None,  # In streaming mode, will use approximation
                    )
                    st.caption(format_token_report(token_data))

                # Save to messages
                token_data = analyze_token_usage(prompt, full_response, contexts, None)
                token_info = format_token_report(token_data)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": full_response,
                        "token_info": token_info,
                    }
                )

        st.rerun()

with col2:
    # Statistical
    st.markdown("**📊 Statistical Queries**")

    for q in [
        "What was the highest daily percentage increase?",
        "What was the lowest daily percentage change?",
        "Which day had the largest volume?",
    ]:
        if st.button(q, key=f"stat_{q}", use_container_width=True):
            st.session_state.pending_query = q
            st.rerun()

    # Date-specific
    st.markdown("**📅 Date-Specific**")

    for q in [
        "What happened on 2025-11-10?",
        "Show me trading data for November 20",
        "What was the close price on 2025-11-24?",
    ]:
        if st.button(q, key=f"date_{q}", use_container_width=True):
            st.session_state.pending_query = q
            st.rerun()

    # Analytical
    st.markdown("**📈 Analytical**")

    for q in [
        "Compare first vs last week",
        "How many [UP] days?",
        "Average closing price?",
        "7-day moving average",
        "Summarize November trend",
    ]:
        if st.button(q, key=f"anal_{q}", use_container_width=True):
            st.session_state.pending_query = q
            st.rerun()

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    st.session_state.show_tokens = st.checkbox(
        "Show Token Usage",
        value=st.session_state.show_tokens,
    )

    st.divider()

    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.markdown("**📚 System Info**")
    st.caption("• Hierarchical Indexing")
    st.caption("• AutoMerging Retrieval")
    st.caption("• MapReduce Summaries")

    st.divider()
    st.caption("⚠️ Educational only")
