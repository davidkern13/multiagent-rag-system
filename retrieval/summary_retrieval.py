"""
Summary Index with MapReduce Strategy
Using Document objects for better compatibility
"""

from llama_index.core import (
    SummaryIndex,
    StorageContext,
    load_index_from_storage,
    Document,
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.node_parser import SentenceSplitter
import chromadb
import os
from retrieval.metadata_extractor import (
    extract_doc_type,
    extract_timestamp,
    extract_entities_from_text,
)


def build_summary_index(docs):
    """
    Build a summary index with MapReduce strategy:
    1. MAP: Summarize each chunk
    2. REDUCE: Store hierarchical summaries
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

            storage_context = StorageContext.from_defaults(
                vector_store=vector_store, persist_dir=docstore_path
            )

            index = load_index_from_storage(storage_context)

            print("[INFO] ✅ Loaded existing summary index successfully!")
            return index

        except Exception as e:
            print(f"[WARN] Failed to load summary index: {e}")
            print("[INFO] Creating new summary index...")

    else:
        print("[INFO] Creating new summary index with MapReduce strategy...")

    # ==========================================
    # MAP-REDUCE IMPLEMENTATION
    # ==========================================

    # STEP 1: Split into chunks
    print("[INFO] Splitting documents into chunks...")
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    all_nodes = []

    for doc_idx, doc in enumerate(docs):
        chunks = splitter.split_text(doc.text)
        print(f"[INFO] Document split into {len(chunks)} chunks")

        # MAP Phase: Create summary for each chunk
        for chunk_idx, chunk in enumerate(chunks):
            # Extract metadata
            metadata = {
                "doc_idx": doc_idx,
                "chunk_idx": chunk_idx,
                "doc_type": extract_doc_type(chunk),
                "timestamp": extract_timestamp(chunk),
                "entities": extract_entities_from_text(chunk, top_n=10),
                "is_leaf": True,  # This is a leaf node
            }

            # Create node with original text
            node = Document(
                text=chunk,
                metadata=metadata,
            )
            all_nodes.append(node)

        # REDUCE Phase: Create section summaries (every 5 chunks)
        section_size = 5
        for i in range(0, len(chunks), section_size):
            section_chunks = chunks[i : min(i + section_size, len(chunks))]
            combined_text = "\n\n---\n\n".join(section_chunks)

            # Create section summary node
            section_metadata = {
                "doc_idx": doc_idx,
                "section_idx": i // section_size,
                "doc_type": "section_summary",
                "is_section": True,  # This is a section node
                "chunk_count": len(section_chunks),
            }

            section_node = Document(
                text=f"[SECTION SUMMARY]\n{combined_text}",
                metadata=section_metadata,
            )
            all_nodes.append(section_node)

        # REDUCE Phase 2: Create document summary
        doc_summary_text = "\n\n".join(
            chunks[:3]
        )  # First 3 chunks as document overview

        doc_metadata = {
            "doc_idx": doc_idx,
            "doc_type": "document_summary",
            "is_document": True,  # This is a document-level node
            "total_chunks": len(chunks),
        }

        doc_node = Document(
            text=f"[DOCUMENT SUMMARY]\n{doc_summary_text}",
            metadata=doc_metadata,
        )
        all_nodes.append(doc_node)

    print(f"[INFO] MapReduce complete:")
    print(f"[INFO]   - Total nodes: {len(all_nodes)}")
    print(
        f"[INFO]   - Leaf chunks: {sum(1 for n in all_nodes if n.metadata.get('is_leaf'))}"
    )
    print(
        f"[INFO]   - Section summaries: {sum(1 for n in all_nodes if n.metadata.get('is_section'))}"
    )
    print(
        f"[INFO]   - Document summaries: {sum(1 for n in all_nodes if n.metadata.get('is_document'))}"
    )

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

    # Create index from hierarchical documents
    print("[INFO] Building summary index from MapReduce documents...")
    index = SummaryIndex.from_documents(
        all_nodes,  # ✅ Using Document objects
        storage_context=storage_context,
        show_progress=True,
    )

    # ✅ PERSIST TO DISK
    print(f"[INFO] Persisting summary index to {docstore_path}...")
    storage_context.persist(persist_dir=docstore_path)

    print(f"[INFO] ✅ Created and persisted MapReduce summary index!")
    print(f"[INFO]    - ChromaDB: {chroma_path}")
    print(f"[INFO]    - Docstore: {docstore_path}")
    print(f"[INFO]    - Strategy: MAP (chunks) → REDUCE (sections) → REDUCE (document)")

    return index
