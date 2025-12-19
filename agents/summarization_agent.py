class SummarizationAgent:
    def __init__(self, summary_index):
        self.query_engine = summary_index.as_query_engine()

    def answer(self, query: str):
        enhanced_query = (
            f"{query}\n\nProvide a clear and concise summary in 2-3 sentences."
        )
        response = self.query_engine.query(enhanced_query)
        return str(response)

    def answer_stream(self, query: str):
        """
        Stream summary response
        Yields: (text_chunk, is_final)
        """
        enhanced_query = (
            f"{query}\n\nProvide a clear and concise summary in 2-3 sentences."
        )

        # LlamaIndex query_engine doesn't support streaming directly
        # So we get the full response and simulate streaming
        response = self.query_engine.query(enhanced_query)
        full_text = str(response)

        # Stream character by character for smooth effect
        for i in range(0, len(full_text), 3):
            chunk = full_text[i : i + 3]
            yield chunk, False

        # Final yield
        yield full_text, True
