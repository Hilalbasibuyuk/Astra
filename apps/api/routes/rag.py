
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, status

from services.rag.retriever import RetrieverService
from services.rag.schemas import (
    RAGSearchRequest,
    RAGSearchResponse,
    RAGSearchResult,
)


router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


@lru_cache(maxsize=1)
def get_retriever() -> RetrieverService:
    """Create one shared retriever instance for this API process."""
    return RetrieverService()


@router.post(
    "/search",
    response_model=RAGSearchResponse,
    summary="Search observatory knowledge",
)
def search_knowledge(
    request: RAGSearchRequest,
    retriever: RetrieverService = Depends(get_retriever),
) -> RAGSearchResponse:
    try:
        results = retriever.search(
            query=request.query,
            limit=request.limit,
            category=request.category,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return RAGSearchResponse(
        query=request.query.strip(),
        result_count=len(results),
        results=[
            RAGSearchResult(**result)
            for result in results
        ],
    )
