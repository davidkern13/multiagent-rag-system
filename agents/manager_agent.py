class ManagerAgent:
    def __init__(self, needle_agent, summary_agent, llm, mcp=None):
        self.needle_agent = needle_agent
        self.summary_agent = summary_agent
        self.llm = llm  # ← LLM לבדיקות
        self.mcp = mcp

    def is_relevant_query(self, query: str) -> tuple:
        """
        Use LLM to check if query is relevant to trading data.
        Returns: (is_relevant, response_message)
        """
        prompt = f"""You are a filter for a PLTR stock trading data Q&A system (November 2025).

RELEVANT queries include:
- Price questions (open, close, high, low, ranges)
- Percentage changes and trends
- Volume questions
- Date-specific queries (what happened on X date)
- Comparisons (first week vs last week, highest vs lowest)
- Statistics (average, maximum, minimum)
- Technical analysis (moving averages, trends)
- ANY question about November 2025 PLTR trading data

IRRELEVANT queries:
- Questions about other stocks
- Questions about other time periods (not November 2025)
- General questions unrelated to stock data
- Requests for investment advice or predictions

Query: "{query}"

Rules:
1. If it's a greeting (hi, hello, hey) → respond with "GREETING: [friendly response inviting them to ask about PLTR data]"
2. If it asks ANYTHING about PLTR November 2025 trading (prices, dates, comparisons, stats) → respond "RELEVANT"
3. If it's completely unrelated → respond "IRRELEVANT: [explain you only handle PLTR November 2025 data]"

BE GENEROUS - if there's ANY connection to trading data analysis, mark it RELEVANT.

Response:"""

        try:
            response = self.llm.complete(prompt).text.strip()

            if response.startswith("RELEVANT"):
                return True, None

            elif response.startswith("GREETING:"):
                message = response.replace("GREETING:", "").strip()
                return False, message

            elif response.startswith("IRRELEVANT:"):
                message = response.replace("IRRELEVANT:", "").strip()
                return False, message

            else:
                # If unclear, assume relevant (better safe than sorry)
                return True, None

        except Exception as e:
            # If LLM fails, allow the query
            print(f"[WARN] Relevance check failed: {e}")
            return True, None

    def classify_intent(self, query: str) -> str:
        """
        Classify query intent:
        - 'summary': High-level overview questions
        - 'needle': Specific factual questions
        """
        q = query.lower()

        summary_keywords = ["overview", "high-level", "main topics", "general summary"]
        if any(k in q for k in summary_keywords):
            return "summary"

        return "needle"

    def route(self, query: str):
        # Check relevance with LLM
        is_relevant, message = self.is_relevant_query(query)

        if not is_relevant:
            # Return LLM's response directly
            return message, [], None

        intent = self.classify_intent(query)

        if intent == "summary":
            answer = self.summary_agent.answer(query)
            return answer, [], None

        answer, contexts, response_obj = self.needle_agent.answer(query)

        if self.mcp:
            extra = self.mcp.run(query, contexts)
            if extra:
                answer += f"\n\n{extra}"

        return answer, contexts, response_obj

    def route_stream(self, query: str):
        """
        Stream response with LLM relevance check
        Yields: (text_chunk, contexts, is_final)
        """
        # Check relevance with LLM
        is_relevant, message = self.is_relevant_query(query)

        if not is_relevant:
            # Return LLM's friendly response
            yield message, [], True
            return

        intent = self.classify_intent(query)

        if intent == "summary":
            # Stream from summary agent
            full_answer = ""

            for chunk, is_final in self.summary_agent.answer_stream(query):
                if is_final:
                    full_answer = chunk
                    yield chunk, [], True
                else:
                    yield chunk, [], False
            return

        # Stream from needle agent
        full_answer = ""
        contexts = []

        for delta, ctxs, is_final in self.needle_agent.answer_stream(query):
            if is_final:
                full_answer = delta
                contexts = ctxs
            else:
                yield delta, [], False

        # Add MCP if needed
        if self.mcp and full_answer:
            extra = self.mcp.run(query, contexts)
            if extra:
                full_answer += f"\n\n{extra}"
                yield f"\n\n{extra}", contexts, False

        # Final yield
        yield full_answer, contexts, True
