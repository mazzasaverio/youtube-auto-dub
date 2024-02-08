from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from app.api.v1.endpoints import router as v1_router

app = FastAPI(title="Youtube-Auto-Dub")

app.include_router(v1_router, prefix="/api/v1")


@app.get("/")
async def root(request: Request):
    return RedirectResponse(url="/docs", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/metrics")
async def metrics():
    return JSONResponse(content={"message": "Metrics not implemented"})
