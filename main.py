from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse

app = FastAPI(title="Title")


@app.get("/")
async def root(request: Request):
    return RedirectResponse(url="/docs", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/metrics")
async def metrics():
    return JSONResponse(content={"message": "Metrics not implemented"})
