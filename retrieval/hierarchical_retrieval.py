from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import os

from retrieval.metadata_extractor import (
    extract_doc_type,
    extract_section_title,
    extract_entities_from_text,
)


def build_hierarchical_retriever(docs, embed_model, top_k: int = 15):
    chroma_path = "./chroma_storage"
    collection_name = "insurance_hierarchical"

    # Extract entities dynamically from the documents
    print("[INFO] Extracting entities from documents...")
    all_entities = set()
    for doc in docs:
        entities = extract_entities_from_text(doc.text, top_n=20)
        all_entities.update(entities)
    print(
        f"[INFO] Found {len(all_entities)} unique entities: {list(all_entities)[:10]}..."
    )

    # Check if ChromaDB already exists
    if os.path.exists(chroma_path):
        print("[INFO] Found existing ChromaDB storage, loading...")

        try:
            # Load existing ChromaDB
            chroma_client = chromadb.PersistentClient(path=chroma_path)
            chroma_collection = chroma_client.get_collection(name=collection_name)
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

            # Create storage context (docstore in memory, vectors from ChromaDB)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            # Rebuild nodes for docstore (needed for AutoMergingRetriever)
            parser = HierarchicalNodeParser.from_defaults(
                chunk_sizes=[1024, 512, 256],
                chunk_overlap=4,
            )
            nodes = parser.get_nodes_from_documents(docs)
            leaf_nodes = get_leaf_nodes(nodes)

            # Add metadata
            for node in leaf_nodes:
                text = node.get_content()
                node.metadata.update(
                    {
                        "doc_type": extract_doc_type(text),
                        "section_title": extract_section_title(text),
                        "parent_id": (
                            node.parent_node.node_id if node.parent_node else None
                        ),
                    }
                )

            # Add nodes to in-memory docstore
            storage_context.docstore.add_documents(nodes)

            # Create index (uses existing vectors from ChromaDB)
            index = VectorStoreIndex(
                leaf_nodes,
                storage_context=storage_context,
                embed_model=embed_model,
                show_progress=False,
            )

            print("[INFO] Loaded existing index successfully!")

            return AutoMergingRetriever(
                index.as_retriever(similarity_top_k=top_k),
                storage_context=storage_context,
                verbose=False,
            )

        except Exception as e:
            print(f"[WARN] Failed to load existing index: {e}")
            print("[INFO] Creating new index...")

    else:
        print("[INFO] No existing ChromaDB found, creating new index...")

    # Create new index from scratch
    parser = HierarchicalNodeParser.from_defaults(
        chunk_sizes=[1024, 512, 256],
        chunk_overlap=4,
    )

    nodes = parser.get_nodes_from_documents(docs)
    leaf_nodes = get_leaf_nodes(nodes)

    for node in leaf_nodes:
        text = node.get_content()
        node.metadata.update(
            {
                "doc_type": extract_doc_type(text),
                "section_title": extract_section_title(text),
                "parent_id": node.parent_node.node_id if node.parent_node else None,
            }
        )

    # Create ChromaDB (only storage location)
    chroma_client = chromadb.PersistentClient(path=chroma_path)

    # Delete old collection if exists
    try:
        chroma_client.delete_collection(name=collection_name)
    except:
        pass

    # Create fresh collection
    chroma_collection = chroma_client.create_collection(name=collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # Create storage context (ChromaDB for vectors, in-memory docstore)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    storage_context.docstore.add_documents(nodes)

    # Create index
    index = VectorStoreIndex(
        leaf_nodes,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=False,
    )

    print(f"[INFO] Created new index with ChromaDB at {chroma_path}")

    return AutoMergingRetriever(
        index.as_retriever(similarity_top_k=top_k),
        storage_context=storage_context,
        verbose=False,
    )
