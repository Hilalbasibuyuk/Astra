
import pytest

from metrics import (
    citation_audit,
    citation_coverage,
    citation_ids,
    citation_validity,
    recall_at_k,
    reciprocal_rank_at_k,
)


def test_recall_at_k_finds_expected_sources():
    retrieved = ["a.md", "b.md", "c.md"]
    expected = ["b.md", "c.md"]

    assert recall_at_k(retrieved, expected, k=2) == 0.5


def test_reciprocal_rank_rewards_higher_ranked_sources():
    retrieved = ["unrelated.md", "expected.md"]

    assert reciprocal_rank_at_k(
        retrieved, ["expected.md"], k=5
    ) == 0.5


def test_reciprocal_rank_is_zero_when_source_is_missing():
    assert reciprocal_rank_at_k(
        ["a.md", "b.md"], ["expected.md"], k=2
    ) == 0.0


def test_recall_rejects_empty_expected_sources():
    with pytest.raises(ValueError, match="expected_paths"):
        recall_at_k(["a.md"], [], k=3)


def test_citation_ids_extract_source_references():
    answer = "The motor may be overloaded [S1]. Check the bearing [S2]."

    assert citation_ids(answer) == {"S1", "S2"}


def test_citation_validity_detects_unknown_source_ids():
    answer = "The motor may be overloaded [S1]. Another cause is possible [S9]."

    assert citation_validity(answer, {"S1", "S2"}) == 0.5


def test_citation_coverage_measures_used_sources():
    answer = "The motor may be overloaded [S1]."

    assert citation_coverage(answer, {"S1", "S2"}) == 0.5


def test_citation_metrics_handle_missing_citations():
    assert citation_validity("No citation.", {"S1"}) == 0.0
    assert citation_coverage("No citation.", {"S1"}) == 0.0
    assert citation_coverage("No citation.", set()) == 0.0


def test_citation_audit_accepts_valid_source_ids():
    answer = "Motor temperature may indicate increased load [S1]."
    sources = [
        {"source_id": "S1"},
        {"source_id": "S2"},
    ]

    report = citation_audit(answer, sources)

    assert report["cited_source_ids"] == ["S1"]
    assert report["valid_source_ids"] == ["S1"]
    assert report["invalid_source_ids"] == []
    assert report["citation_validity"] == 1.0
    assert report["citation_coverage"] == 0.5
    assert report["has_citations"] is True
    assert report["all_citations_valid"] is True


def test_citation_audit_detects_unknown_source_ids():
    answer = "The motor may be overloaded [S1]. Check the bearing [S9]."
    sources = [
        {"source_id": "S1"},
        {"source_id": "S2"},
    ]

    report = citation_audit(answer, sources)

    assert report["cited_source_ids"] == ["S1", "S9"]
    assert report["valid_source_ids"] == ["S1"]
    assert report["invalid_source_ids"] == ["S9"]
    assert report["citation_validity"] == 0.5
    assert report["all_citations_valid"] is False


def test_citation_audit_handles_answer_without_citations():
    report = citation_audit(
        "The available evidence is insufficient.",
        [{"source_id": "S1"}],
    )

    assert report["cited_source_ids"] == []
    assert report["invalid_source_ids"] == []
    assert report["citation_validity"] == 0.0
    assert report["citation_coverage"] == 0.0
    assert report["has_citations"] is False
    assert report["all_citations_valid"] is False


def test_citation_audit_handles_empty_sources():
    report = citation_audit(
        "The motor may be overloaded [S1].",
        [],
    )

    assert report["invalid_source_ids"] == ["S1"]
    assert report["citation_validity"] == 0.0
    assert report["citation_coverage"] == 0.0
    assert report["all_citations_valid"] is False