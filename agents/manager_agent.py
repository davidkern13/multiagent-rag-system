class ManagerAgent:
    def __init__(self, needle_agent, summary_agent, mcp=None):
        self.needle_agent = needle_agent
        self.summary_agent = summary_agent
        self.mcp = mcp

    def classify_intent(self, query: str) -> str:
        """
        Classify query intent:
        - 'summary': High-level overview questions (entire document)
        - 'needle': Specific factual questions (detailed retrieval)
        """
        q = query.lower()

        # Summary keywords - must be truly high-level
        summary_keywords = ["overview", "high-level", "main topics", "general summary"]
        if any(k in q for k in summary_keywords):
            return "summary"

        # Everything else is needle (including specific summaries like "PLTR in November")
        return "needle"

    def route(self, query: str):
        intent = self.classify_intent(query)

        if intent == "summary":
            answer = self.summary_agent.answer(query)
            return answer, [], None  # ← No response object for summary

        answer, contexts, response_obj = self.needle_agent.answer(query)

        if self.mcp:
            extra = self.mcp.run(query, contexts)
            if extra:
                answer += f"\n\n{extra}"

        return answer, contexts, response_obj
