class SummarizationAgent:
    def __init__(self, summary_index):
        self.query_engine = summary_index.as_query_engine()

    def answer(self, query: str):
        enhanced_query = (
            f"{query}\n\nProvide a clear and concise summary in 2-3 sentences."
        )
        response = self.query_engine.query(enhanced_query)
        return str(response)
