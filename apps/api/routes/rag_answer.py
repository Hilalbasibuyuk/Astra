
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, status

from services.rag.generator import RAGAnswerService
from services.rag.llm_client import (
    LLMServiceError,
    OllamaLLMClient,
)
from services.rag.retriever import RetrieverService
from services.rag.schemas import (
    RAGAnswerRequest,
    RAGAnswerResponse,
)


router = APIRouter(prefix="/rag", tags=["RAG"])


@lru_cache(maxsize=1)
def get_rag_answer_service() -> RAGAnswerService:
    retriever = RetrieverService()
    llm_client = OllamaLLMClient()

    return RAGAnswerService(
        retriever=retriever,
        llm_client=llm_client,
    )


@router.post(
    "/answer",
    response_model=RAGAnswerResponse,
    summary="Generate a source-grounded observatory answer",
)
def answer_question(
    request: RAGAnswerRequest,
    service: RAGAnswerService = Depends(get_rag_answer_service),
) -> RAGAnswerResponse:
    try:
        result = service.answer(
            query=request.query,
            limit=request.limit,
            category=request.category,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except LLMServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return RAGAnswerResponse(**result)
