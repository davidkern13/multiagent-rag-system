from core.system_builder import build_system
from evaluation.ragas_judge import run_ragas_evaluation
from evaluation.test_cases import TEST_CASES


def run_evaluation():
    """
    Runs the full evaluation pipeline:
    1. Build system once
    2. Run all test queries
    3. Evaluate with LLM-as-a-judge
    4. Print results
    """
    print("Building system...")
    manager = build_system("data/data.pdf")
    print("System ready!\n")

    questions, answers, contexts, ground_truths = [], [], [], []

    print("Running test queries...\n")
    for i, case in enumerate(TEST_CASES, 1):
        q = case["question"]
        gt = case["ground_truth"]

        print(f"[{i}/{len(TEST_CASES)}] Query: {q[:50]}...")

        answer, ctx = manager.route(q)

        questions.append(q)
        answers.append(answer)
        contexts.append(ctx)
        ground_truths.append(gt)

    # Run LLM-as-a-judge evaluation
    results = run_ragas_evaluation(
        questions=questions,
        answers=answers,
        contexts=contexts,
        ground_truths=ground_truths,
    )

    return results


if __name__ == "__main__":
    run_evaluation()
