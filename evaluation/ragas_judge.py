"""
Ragas-based evaluation for RAG system
"""

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from datasets import Dataset
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings


def run_ragas_evaluation(questions, answers, contexts, ground_truths):
    """
    Run Ragas evaluation on the test set.

    Args:
        questions: List of queries
        answers: List of generated answers
        contexts: List of retrieved context lists
        ground_truths: List of ground truth answers

    Returns:
        Dictionary with evaluation results
    """

    # Configure Ragas to use Ollama
    llm = Ollama(model="gemma3:4b", temperature=0.3)
    embeddings = OllamaEmbeddings(model="mxbai-embed-large", embed_batch_size=4)

    # Prepare data in Ragas format
    data = {
        "question": questions,
        "answer": answers,
        "contexts": [[str(c) for c in ctx] for ctx in contexts],
        "ground_truth": ground_truths,
    }

    # Create dataset
    dataset = Dataset.from_dict(data)

    print("\n" + "=" * 70)
    print("🔍 RAGAS EVALUATION STARTED")
    print("=" * 70)

    # Run evaluation
    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision,
        ],
        llm=llm,
        embeddings=embeddings,
    )

    # Convert to dict for cleaner output
    result_dict = result.to_pandas().mean().to_dict()

    print("\n" + "=" * 70)
    print("📊 RAGAS EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Faithfulness:       {result_dict.get('faithfulness', 0):.3f}")
    print(f"Answer Relevancy:   {result_dict.get('answer_relevancy', 0):.3f}")
    print(f"Context Recall:     {result_dict.get('context_recall', 0):.3f}")
    print(f"Context Precision:  {result_dict.get('context_precision', 0):.3f}")
    print("=" * 70 + "\n")

    return result_dict
