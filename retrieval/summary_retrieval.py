from llama_index.core import SummaryIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import os
from retrieval.metadata_extractor import (
    extract_doc_type,
    extract_timestamp,
    extract_entities_from_text,
)


def build_summary_index(docs):
    """
    Build a summary index with ChromaDB (only one storage location).
    LLM is used only at query time via Settings.llm
    """
    chroma_path = "./chroma_storage"
    collection_name = "insurance_summaries"

    # Add metadata to docs first
    for d in docs:
        text = d.text
        d.metadata = {
            "doc_type": extract_doc_type(text),
            "timestamp": extract_timestamp(text),
            "entities": extract_entities_from_text(text, top_n=10),
        }

    # Check if ChromaDB exists
    if os.path.exists(chroma_path):
        print("[INFO] Found existing ChromaDB for summary index, loading...")

        try:
            chroma_client = chromadb.PersistentClient(path=chroma_path)
            chroma_collection = chroma_client.get_collection(name=collection_name)
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            # Create index (vectors already in ChromaDB)
            index = SummaryIndex.from_documents(
                docs,
                storage_context=storage_context,
                show_progress=False,
            )

            print("[INFO] Loaded existing summary index successfully!")
            return index

        except Exception as e:
            print(f"[WARN] Failed to load summary index: {e}")
            print("[INFO] Creating new summary index...")

    else:
        print("[INFO] Creating new summary index...")

    # Create ChromaDB
    chroma_client = chromadb.PersistentClient(path=chroma_path)

    # Delete old collection if exists
    try:
        chroma_client.delete_collection(name=collection_name)
    except:
        pass

    # Create fresh collection
    chroma_collection = chroma_client.create_collection(name=collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # Create storage context
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Create index
    index = SummaryIndex.from_documents(
        docs,
        storage_context=storage_context,
        show_progress=False,
    )

    print(f"[INFO] Created summary index in ChromaDB at {chroma_path}")

    return index
