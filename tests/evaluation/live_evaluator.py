
from __future__ import annotations

import json
import re
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from tests.evaluation.dataset import EVALUATION_DATASET


API_URL = "http://127.0.0.1:8000/rag/answer"
TOP_K = 5
OUTPUT_PATH = Path("artifacts/rag_live_evaluation.json")

CITATION_PATTERN = re.compile(r"\[(S\d+)\]")

# These phrases provide a heuristic signal only.
# They do not prove that the answer is factually correct.
ABSTENTION_PHRASES = [
    "cannot be determined",
    "can't be determined",
    "not enough information",
    "does not contain enough",
    "not a universal threshold",
    "cannot determine",
    "can't determine",
    "insufficient information",
    "not specified in the provided context",
    "not available in the provided context",
    "not specified in the documentation",
    "specific equipment documentation",
    "manufacturer's documentation",
    "manufacturer documentation",
    "equipment-specific documentation",
    "cannot establish a definitive",
    "cannot identify a definitive",
    "not sufficient to identify",
    "not enough evidence",
]

# Reuse the established 13-case retrieval dataset.
CASES = [
    {
        "id": case.case_id,
        "query": case.question,
        "expected_source_paths": list(case.expected_source_paths),
        "should_abstain": False,
    }
    for case in EVALUATION_DATASET
]

# These questions test whether the model avoids inventing
# equipment-specific thresholds absent from the knowledge base.
CASES.extend(
    [
        {
            "id": "unknown_universal_motor_temperature",
            "query": (
                "What is the exact optimal motor temperature "
                "for every telescope model?"
            ),
            "expected_source_paths": [
                "telescope/tracking_and_motor.md",
            ],
            "should_abstain": True,
        },
        {
            "id": "unknown_universal_wind_limit",
            "query": (
                "What is the exact safe wind speed in km/h "
                "for every observatory telescope and dome?"
            ),
            "expected_source_paths": [
                "weather/observation_conditions.md",
            ],
            "should_abstain": True,
        },
        {
            "id": "unknown_universal_camera_temperature",
            "query": (
                "What is the exact optimal sensor temperature "
                "for every astronomical camera model?"
            ),
            "expected_source_paths": [
                "camera/camera_operations.md",
            ],
            "should_abstain": True,
        },
    ]
)


def call_rag_api(query: str) -> tuple[dict, float]:
    """Call the running ASTRA API and return its response and latency."""
    payload = json.dumps(
        {"query": query, "limit": TOP_K}
    ).encode("utf-8")

    request = Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()

    try:
        with urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"API returned HTTP {exc.code}: {body}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            f"Cannot connect to ASTRA API at {API_URL}: {exc}"
        ) from exc

    latency_ms = (time.perf_counter() - start) * 1000
    return result, round(latency_ms, 2)


def normalize_path(path: str) -> str:
    """Normalize Windows and POSIX separators without altering the name."""
    normalized = path.replace("\\", "/")

    while normalized.startswith("./"):
        normalized = normalized[2:]

    return normalized


def evaluate_result(
    case: dict,
    response: dict,
    latency_ms: float,
) -> dict:
    answer = response.get("answer", "")
    sources = response.get("sources", [])

    if not isinstance(answer, str):
        answer = ""

    if not isinstance(sources, list):
        sources = []

    source_by_id = {
        source["source_id"]: source
        for source in sources
        if isinstance(source, dict) and source.get("source_id")
    }

    cited_ids = set(CITATION_PATTERN.findall(answer))
    available_ids = set(source_by_id)

    valid_ids = cited_ids & available_ids
    invalid_ids = cited_ids - available_ids

    cited_paths = {
        normalize_path(source_by_id[source_id]["source_path"])
        for source_id in valid_ids
        if source_by_id[source_id].get("source_path")
    }

    expected_paths = {
        normalize_path(path)
        for path in case["expected_source_paths"]
    }

    retrieved_paths = {
        normalize_path(source["source_path"])
        for source in sources
        if isinstance(source, dict) and source.get("source_path")
    }

    # Document-level retrieval recall.
    # A question with no expected source documents has undefined recall.
    retrieved_expected_paths = retrieved_paths & expected_paths

    retrieval_recall = (
        len(retrieved_expected_paths) / len(expected_paths)
        if expected_paths
        else None
    )

    # Fraction of all citation IDs that refer to returned sources.
    citation_validity = (
        len(valid_ids) / len(cited_ids)
        if cited_ids
        else 0.0
    )

    # Fraction of returned source IDs used by the answer.
    citation_coverage = (
        len(valid_ids) / len(available_ids)
        if available_ids
        else 0.0
    )

    # How many expected documents were actually cited?
    expected_sources_cited = cited_paths & expected_paths

    expected_source_citation_recall = (
        len(expected_sources_cited) / len(expected_paths)
        if expected_paths
        else None
    )

    # Of the distinct documents cited, how many are expected sources?
    # This is a benchmark-relative measure, not proof of factual support.
    citation_precision_against_expected = (
        len(expected_sources_cited) / len(cited_paths)
        if cited_paths
        else 0.0
    )

    abstention_detected = any(
        phrase in answer.casefold()
        for phrase in ABSTENTION_PHRASES
    )

    expected_abstention = case["should_abstain"]

    return {
        "id": case["id"],
        "query": case["query"],
        "latency_ms": latency_ms,
        "answer": answer,
        "result_count": response.get(
            "result_count",
            len(sources),
        ),
        "expected_source_paths": sorted(expected_paths),
        "retrieved_source_paths": sorted(retrieved_paths),
        "cited_source_paths": sorted(cited_paths),
        "expected_sources_cited": sorted(expected_sources_cited),
        "retrieval_recall_at_k": retrieval_recall,
        "cited_source_ids": sorted(cited_ids),
        "valid_source_ids": sorted(valid_ids),
        "invalid_source_ids": sorted(invalid_ids),
        "citation_validity": citation_validity,
        "citation_coverage": citation_coverage,
        "expected_source_citation_recall": (
            expected_source_citation_recall
        ),
        "citation_precision_against_expected": (
            citation_precision_against_expected
        ),
        "has_citations": bool(cited_ids),
        "abstention_expected": expected_abstention,
        "abstention_detected_by_heuristic": abstention_detected,
        "abstention_expectation_met": (
            abstention_detected == expected_abstention
        ),
    }


def mean_or_none(values: list[float]) -> float | None:
    if not values:
        return None

    return round(statistics.mean(values), 4)


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    results = []
    errors = []

    for case in CASES:
        print(f"\nEvaluating: {case['id']}")
        print(f"Question: {case['query']}")

        try:
            response, latency_ms = call_rag_api(case["query"])
            result = evaluate_result(case, response, latency_ms)
            results.append(result)

            print(f"Latency: {latency_ms:.0f} ms")
            print(
                "Retrieval recall@k: "
                f"{result['retrieval_recall_at_k']}"
            )
            print(
                "Citation validity: "
                f"{result['citation_validity']:.2f}"
            )
            print(
                "Expected-source citation recall: "
                f"{result['expected_source_citation_recall']}"
            )
            print(
                "Abstention expectation met: "
                f"{result['abstention_expectation_met']}"
            )

        except Exception as exc:
            errors.append(
                {
                    "id": case["id"],
                    "error": str(exc),
                }
            )
            print(f"ERROR: {exc}")

    latencies = [item["latency_ms"] for item in results]

    recalls = [
        item["retrieval_recall_at_k"]
        for item in results
        if item["retrieval_recall_at_k"] is not None
    ]

    citation_validities = [
        item["citation_validity"]
        for item in results
    ]

    citation_recalls = [
        item["expected_source_citation_recall"]
        for item in results
        if item["expected_source_citation_recall"] is not None
    ]

    citation_precisions = [
        item["citation_precision_against_expected"]
        for item in results
    ]

    abstention_results = [
        item
        for item in results
        if item["abstention_expected"]
    ]

    report = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "api_url": API_URL,
        "top_k": TOP_K,
        "evaluation_type": "live_http_end_to_end",
        "case_count": len(CASES),
        "successful_count": len(results),
        "error_count": len(errors),
        "summary": {
            "mean_latency_ms": (
                round(statistics.mean(latencies), 2)
                if latencies
                else None
            ),
            "median_latency_ms": (
                round(statistics.median(latencies), 2)
                if latencies
                else None
            ),
            "mean_retrieval_recall_at_k": mean_or_none(recalls),
            "mean_citation_validity": mean_or_none(
                citation_validities
            ),
            "mean_expected_source_citation_recall": mean_or_none(
                citation_recalls
            ),
            "mean_citation_precision_against_expected": mean_or_none(
                citation_precisions
            ),
            "abstention_expectations_met": sum(
                item["abstention_expectation_met"]
                for item in abstention_results
            ),
            "abstention_cases_evaluated": len(abstention_results),
        },
        "results": results,
        "errors": errors,
        "limitations": [
            (
                "Citation ID validity does not prove that a source "
                "supports the associated claim."
            ),
            (
                "Expected-source citation precision is benchmark-relative "
                "and may penalize additional relevant sources."
            ),
            (
                "Abstention detection uses phrase matching and can produce "
                "false positives or false negatives."
            ),
            (
                "The evaluation set is small and curated; results do not "
                "establish production reliability."
            ),
            (
                "Answer correctness and factual grounding still require "
                "claim-level review against the retrieved source text."
            ),
        ],
    }

    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n=== SUMMARY ===")
    print(json.dumps(report["summary"], indent=2, ensure_ascii=False))
    print(f"\nSuccessful cases: {len(results)}/{len(CASES)}")
    print(f"Errors: {len(errors)}")
    print(f"Report saved to: {OUTPUT_PATH}")

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
