
from services.rag.retriever import RetrieverService
from tests.evaluation.dataset import EVALUATION_DATASET
from tests.evaluation.metrics import (
    recall_at_k,
    reciprocal_rank_at_k,
)


def unique_in_order(values: list[str]) -> list[str]:
    """Keep the first occurrence of each value, preserving rank order."""
    return list(dict.fromkeys(values))


def evaluate_retrieval(k: int = 5) -> dict:
    if not 1 <= k <= 10:
        raise ValueError("k must be between 1 and 10")

    retriever = RetrieverService()

    recalls = []
    reciprocal_ranks = []
    details = []

    try:
        for case in EVALUATION_DATASET:
            # Fetch more chunks because multiple chunks can come
            # from the same Markdown document.
            results = retriever.search(
                query=case.question,
                limit=10,
            )

            raw_paths = [
                result["source_path"] for result in results
            ]

            # Evaluate the first K distinct documents, not K chunks.
            retrieved_paths = unique_in_order(raw_paths)[:k]

            recall = recall_at_k(
                retrieved_paths,
                case.expected_source_paths,
                k,
            )

            reciprocal_rank = reciprocal_rank_at_k(
                retrieved_paths,
                case.expected_source_paths,
                k,
            )

            recalls.append(recall)
            reciprocal_ranks.append(reciprocal_rank)

            details.append(
                {
                    "case_id": case.case_id,
                    "recall_at_k": recall,
                    "reciprocal_rank_at_k": reciprocal_rank,
                    "expected_sources": list(
                        case.expected_source_paths
                    ),
                    "retrieved_sources": retrieved_paths,
                    "raw_chunk_count": len(results),
                    "unique_document_count": len(
                        unique_in_order(raw_paths)
                    ),
                }
            )
    finally:
        retriever.close()

    if not details:
        raise ValueError("Evaluation dataset cannot be empty")

    return {
        "case_count": len(details),
        "k": k,
        "evaluation_level": "document",
        "mean_recall_at_k": sum(recalls) / len(recalls),
        "mean_reciprocal_rank_at_k": (
            sum(reciprocal_ranks) / len(reciprocal_ranks)
        ),
        "details": details,
    }


if __name__ == "__main__":
    import json

    report = evaluate_retrieval(k=5)
    print(json.dumps(report, indent=2, ensure_ascii=False))
