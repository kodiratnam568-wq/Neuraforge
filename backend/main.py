from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from github_service import scan_repository, parse_github_url
from ai_service import analyze_repository

app = FastAPI(title="NeuraForge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    github_url: str


@app.get("/")
async def health():
    return {"status": "NeuraForge backend is running"}


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    # 1. Validate URL
    try:
        owner, repo = parse_github_url(req.github_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Scan repository
    try:
        repo_data = await scan_repository(req.github_url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"GitHub fetch failed: {str(e)}")

    # 3. AI analysis
    try:
        analysis = await analyze_repository(repo_data)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {str(e)}")

    return {
        "repo": f"{owner}/{repo}",
        "stats": repo_data["stats"],
        "analysis": analysis,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
