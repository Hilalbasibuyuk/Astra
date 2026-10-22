
from __future__ import annotations

import json
import re
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_URL = "http://127.0.0.1:8000/rag/answer"
TOP_K = 5

OUTPUT_PATH = Path("artifacts/rag_live_evaluation.json")

CASES = [
    {
        "id": "telescope_tracking",
        "query": "What can cause a telescope tracking error?",
        "expected_source_paths": [
            "telescope/tracking_and_motor.md",
        ],
        "should_abstain": False,
    },
    {
        "id": "weather_camera_image_quality",
        "query": (
            "How can weather conditions and camera temperature "
            "affect image quality?"
        ),
        "expected_source_paths": [
            "camera/camera_operations.md",
            "weather/observation_conditions.md",
        ],
        "should_abstain": False,
    },
    {
        "id": "unknown_universal_temperature",
        "query": (
            "What is the exact optimal motor temperature "
            "for every telescope model?"
        ),
        "expected_source_paths": [
            "telescope/tracking_and_motor.md",
        ],
        "should_abstain": True,
    },
]

CITATION_PATTERN = re.compile(r"\[(S\d+)\]")

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
]


def call_rag_api(query: str) -> tuple[dict, float]:
    """Call the real ASTRA API and return its response and latency."""
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
    return path.replace("\\", "/").lstrip("./")


def evaluate_result(
    case: dict,
    response: dict,
    latency_ms: float,
) -> dict:
    answer = response.get("answer", "")
    sources = response.get("sources", [])

    # Source IDs returned by the API are the allowed citation IDs.
    source_by_id = {
        source["source_id"]: source
        for source in sources
        if source.get("source_id")
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
        if source.get("source_path")
    }

    # Document-level retrieval recall, not chunk-level recall.
    retrieved_expected_paths = retrieved_paths & expected_paths
    recall = (
        len(retrieved_expected_paths) / len(expected_paths)
        if expected_paths
        else None
    )

    # This checks citation IDs, not whether the cited text
    # actually supports the associated claim.
    citation_validity = (
        len(valid_ids) / len(cited_ids)
        if cited_ids
        else 0.0
    )

    citation_coverage = (
        len(valid_ids) / len(available_ids)
        if available_ids
        else 0.0
    )

    lower_answer = answer.lower()
    abstention_detected = any(
        phrase in lower_answer
        for phrase in ABSTENTION_PHRASES
    )

    expected_abstention = case["should_abstain"]

    return {
        "id": case["id"],
        "query": case["query"],
        "latency_ms": latency_ms,
        "answer": answer,
        "result_count": response.get("result_count", len(sources)),
        "expected_source_paths": sorted(expected_paths),
        "retrieved_source_paths": sorted(retrieved_paths),
        "cited_source_paths": sorted(cited_paths),
        "retrieval_recall_at_k": recall,
        "cited_source_ids": sorted(cited_ids),
        "valid_source_ids": sorted(valid_ids),
        "invalid_source_ids": sorted(invalid_ids),
        "citation_validity": citation_validity,
        "citation_coverage": citation_coverage,
        "has_citations": bool(cited_ids),
        "abstention_expected": expected_abstention,
        "abstention_detected_by_heuristic": abstention_detected,
        "abstention_expectation_met": (
            abstention_detected == expected_abstention
        ),
    }


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
                "Abstention expectation met: "
                f"{result['abstention_expectation_met']}"
            )

        except Exception as exc:
            errors.append({
                "id": case["id"],
                "error": str(exc),
            })
            print(f"ERROR: {exc}")

    latencies = [item["latency_ms"] for item in results]
    recalls = [
        item["retrieval_recall_at_k"]
        for item in results
        if item["retrieval_recall_at_k"] is not None
    ]
    citation_validities = [
        item["citation_validity"] for item in results
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
                if latencies else None
            ),
            "median_latency_ms": (
                round(statistics.median(latencies), 2)
                if latencies else None
            ),
            "mean_retrieval_recall_at_k": (
                round(statistics.mean(recalls), 4)
                if recalls else None
            ),
            "mean_citation_validity": (
                round(statistics.mean(citation_validities), 4)
                if citation_validities else None
            ),
            "abstention_expectations_met": sum(
                item["abstention_expectation_met"]
                for item in results
            ),
            "abstention_cases_evaluated": sum(
                item["abstention_expected"]
                for item in results
            ),
        },
        "results": results,
        "errors": errors,
        "limitations": [
            "Citation ID validity does not prove factual support.",
            "Abstention detection uses phrase matching and is only a heuristic.",
            "Three curated queries are not sufficient to establish production quality.",
        ],
    }

    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n=== SUMMARY ===")
    print(json.dumps(report["summary"], indent=2, ensure_ascii=False))
    print(f"\nReport saved to: {OUTPUT_PATH}")

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
