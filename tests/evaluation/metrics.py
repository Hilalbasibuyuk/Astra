
import re
from collections.abc import Sequence


def recall_at_k(
    retrieved_paths: Sequence[str],
    expected_paths: Sequence[str],
    k: int,
) -> float:
    if k < 1:
        raise ValueError("k must be at least 1")

    expected = set(expected_paths)
    if not expected:
        raise ValueError("expected_paths cannot be empty")

    retrieved = set(retrieved_paths[:k])
    return len(retrieved & expected) / len(expected)


def reciprocal_rank_at_k(
    retrieved_paths: Sequence[str],
    expected_paths: Sequence[str],
    k: int,
) -> float:
    if k < 1:
        raise ValueError("k must be at least 1")

    expected = set(expected_paths)
    if not expected:
        raise ValueError("expected_paths cannot be empty")

    for rank, path in enumerate(retrieved_paths[:k], start=1):
        if path in expected:
            return 1.0 / rank

    return 0.0


def citation_ids(answer: str) -> set[str]:
    return set(re.findall(r"\[(S\d+)\]", answer))


def citation_validity(
    answer: str,
    available_source_ids: set[str],
) -> float:
    """
    Fraction of cited IDs that exist among supplied sources.

    This validates citation identifiers, not factual support.
    """
    citations = citation_ids(answer)

    if not citations:
        return 0.0

    return len(citations & available_source_ids) / len(citations)


def citation_coverage(
    answer: str,
    available_source_ids: set[str],
) -> float:
    """
    Fraction of supplied sources cited by the answer.
    """
    if not available_source_ids:
        return 0.0

    citations = citation_ids(answer)
    return len(citations & available_source_ids) / len(
        available_source_ids
    )

def citation_audit(
    answer: str,
    sources: Sequence[dict],
) -> dict:
    """
    Compare source identifiers cited in an answer with the
    source identifiers actually supplied to the answer generator.
    """
    cited_ids = citation_ids(answer)
    available_ids = {
        source["source_id"]
        for source in sources
        if "source_id" in source
    }

    valid_ids = cited_ids & available_ids
    invalid_ids = cited_ids - available_ids

    return {
        "cited_source_ids": sorted(cited_ids),
        "valid_source_ids": sorted(valid_ids),
        "invalid_source_ids": sorted(invalid_ids),
        "citation_validity": (
            len(valid_ids) / len(cited_ids)
            if cited_ids
            else 0.0
        ),
        "citation_coverage": (
            len(valid_ids) / len(available_ids)
            if available_ids
            else 0.0
        ),
        "has_citations": bool(cited_ids),
        "all_citations_valid": bool(cited_ids) and not invalid_ids,
    }