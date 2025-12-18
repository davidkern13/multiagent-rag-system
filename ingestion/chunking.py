from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes


def build_hierarchical_nodes(documents):
    """
    Creates a hierarchical chunk structure:
    small -> medium -> large
    """

    parser = HierarchicalNodeParser.from_defaults(
        chunk_sizes=[256, 512, 1024],
        chunk_overlap=50,
    )

    nodes = parser.get_nodes_from_documents(documents)
    leaf_nodes = get_leaf_nodes(nodes)

    return nodes, leaf_nodes
