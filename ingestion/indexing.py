# build_all_indexes.py

from ingestion.loader import load_pdf
from core.embeddings import get_embedding_model
from core.llm_provider import get_llm

from retrieval.hierarchical_retrieval import build_hierarchical_retriever
from retrieval.summary_retrieval import build_summary_index


def build_all_indexes(pdf_path: str):
    """
    Main indexing entry point.
    Builds and returns all indexes used by the system.
    """

    # 1. Load documents
    documents = load_pdf(pdf_path)

    # 2. Load providers
    embed_model = get_embedding_model()
    llm = get_llm()

    # 3. Build indexes
    hierarchical_retriever = build_hierarchical_retriever(
        documents,
        embed_model,
    )

    summary_index = build_summary_index(documents)

    return {
        "hierarchical_retriever": hierarchical_retriever,
        "summary_index": summary_index,
    }
