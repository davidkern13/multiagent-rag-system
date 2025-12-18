from llama_index.core import SummaryIndex, StorageContext, load_index_from_storage
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
    Build a summary index with persistent storage.
    """
    chroma_path = "./chroma_storage"
    docstore_path = "./docstore_summary"
    collection_name = "insurance_summaries"

    # Check if both exist
    chroma_exists = os.path.exists(chroma_path)
    docstore_exists = os.path.exists(docstore_path)

    if chroma_exists and docstore_exists:
        print("[INFO] Found existing summary storage, loading from disk...")

        try:
            chroma_client = chromadb.PersistentClient(path=chroma_path)
            chroma_collection = chroma_client.get_collection(name=collection_name)
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

            # Load storage context with persisted docstore
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store, persist_dir=docstore_path
            )

            # Load index from storage
            index = load_index_from_storage(storage_context)

            print("[INFO] ✅ Loaded existing summary index successfully!")
            return index

        except Exception as e:
            print(f"[WARN] Failed to load summary index: {e}")
            print("[INFO] Creating new summary index...")

    else:
        print("[INFO] Creating new summary index...")

    # Add metadata to docs first
    print("[INFO] Adding metadata to documents...")
    for d in docs:
        text = d.text
        d.metadata = {
            "doc_type": extract_doc_type(text),
            "timestamp": extract_timestamp(text),
            "entities": extract_entities_from_text(text, top_n=10),
        }

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
    print("[INFO] Building summary index...")
    index = SummaryIndex.from_documents(
        docs,
        storage_context=storage_context,
        show_progress=True,
    )

    # ✅ PERSIST TO DISK
    print(f"[INFO] Persisting summary index to {docstore_path}...")
    storage_context.persist(persist_dir=docstore_path)

    print(f"[INFO] ✅ Created and persisted summary index!")
    print(f"[INFO]    - ChromaDB: {chroma_path}")
    print(f"[INFO]    - Docstore: {docstore_path}")

    return index
