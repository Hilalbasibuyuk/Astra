
from services.rag.generator import RAGAnswerService


SAMPLE_CHUNK = {
    "score": 0.91,
    "chunk_id": "chunk-1",
    "doc_id": "doc-1",
    "source_path": "telescope/tracking_and_motor.md",
    "category": "telescope",
    "document_title": "Telescope Diagnostics",
    "section_title": "Motor Temperature",
    "chunk_index": 0,
    "content": "Increasing motor temperature may indicate increased load.",
}


class FakeRetriever:
    def __init__(self, results=None):
        self.results = results if results is not None else [SAMPLE_CHUNK]

    def search(self, query, limit=5, category=None):
        return self.results


class FakeLLMClient:
    def __init__(self, response="The motor may be under increased load. [S1]"):
        self.response = response
        self.system_prompt = None
        self.user_prompt = None
        self.call_count = 0

    def generate(self, system_prompt, user_prompt):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.call_count += 1
        return self.response


def test_answer_includes_generated_answer_and_sources():
    llm = FakeLLMClient()
    service = RAGAnswerService(FakeRetriever(), llm)

    result = service.answer("Why is the motor overheating?")

    assert result["answer"].endswith("[S1]")
    assert result["result_count"] == 1
    assert result["sources"][0]["source_id"] == "S1"
    assert result["sources"][0]["source_path"] == (
        "telescope/tracking_and_motor.md"
    )


def test_prompt_contains_question_and_retrieved_context():
    llm = FakeLLMClient()
    service = RAGAnswerService(FakeRetriever(), llm)

    service.answer("Why is the motor overheating?")

    assert "Why is the motor overheating?" in llm.user_prompt
    assert "Increasing motor temperature" in llm.user_prompt
    assert "[S1]" in llm.user_prompt
    assert "only the supplied reference context" in llm.system_prompt


def test_no_relevant_chunks_skips_llm():
    llm = FakeLLMClient()
    service = RAGAnswerService(FakeRetriever(results=[]), llm)

    result = service.answer("What caused the fault?")

    assert result["result_count"] == 0
    assert result["sources"] == []
    assert llm.call_count == 0


def test_answer_rejects_empty_query():
    service = RAGAnswerService(FakeRetriever(), FakeLLMClient())

    try:
        service.answer("   ")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Query cannot be empty" in str(exc)
