from fastapi import FastAPI

from apps.api.routes.telemetry import router as telemetry_router
from apps.api.routes.rag import router as rag_router
from apps.api.routes.rag_answer import router as rag_answer_router

app = FastAPI(
    title="ASTRA API",
    version="0.1.0",
    description="Autonomous Observatory Intelligence & Decision System",
)
app.include_router(rag_router)
app.include_router(rag_answer_router)

@app.get("/api/v1/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "astra-api",
    }

app.include_router(telemetry_router)