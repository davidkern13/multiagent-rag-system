from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes


def build_hierarchical_nodes(documents):
    """
    Creates a hierarchical chunk structure:
    Large (512) -> Medium (256) -> Small (128)
    """

    parser = HierarchicalNodeParser.from_defaults(
        chunk_sizes=[512, 256, 128],
        chunk_overlap=20,
    )

    nodes = parser.get_nodes_from_documents(documents)
    leaf_nodes = get_leaf_nodes(nodes)

    return nodes, leaf_nodes
