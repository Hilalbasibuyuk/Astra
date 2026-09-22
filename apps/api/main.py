from fastapi import FastAPI

app = FastAPI(
    title="ASTRA API",
    version="0.1.0",
    description="Autonomous Observatory Intelligence & Decision System",
)

@app.get("/api/v1/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "astra-api",
    }