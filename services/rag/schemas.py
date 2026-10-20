
from pydantic import BaseModel, Field, ConfigDict, field_validator

class RAGSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=10)
    category: str | None = Field(default=None, max_length=100)

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Query cannot be empty")

        return value


class RAGSearchResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    score: float
    chunk_id: str
    doc_id: str
    source_path: str
    category: str
    document_title: str
    section_title: str
    chunk_index: int
    content: str


class RAGSearchResponse(BaseModel):
    query: str
    result_count: int
    results: list[RAGSearchResult]



class RAGAnswerRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=10)
    category: str | None = Field(default=None, max_length=100)

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Query cannot be empty")
        return value


class RAGAnswerSource(BaseModel):
    source_id: str
    score: float
    chunk_id: str
    doc_id: str
    source_path: str
    category: str
    document_title: str
    section_title: str
    chunk_index: int
    content: str


class RAGAnswerResponse(BaseModel):
    query: str
    answer: str
    result_count: int
    sources: list[RAGAnswerSource]

