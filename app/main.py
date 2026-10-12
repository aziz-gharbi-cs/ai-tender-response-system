from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.application.container import ApplicationContainer
from app.core.config import settings
from app.graph.workflow import build_proposal_workflow

app = FastAPI(
    title=settings.app_name,
    description="AI-assisted tender response demonstration",
    version="0.1.0",
)

UPLOAD_DIR = Path(settings.upload_dir).resolve()
MAX_FILE_SIZE = 20 * 1024 * 1024


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "application": settings.app_name}


@app.get("/")
async def home() -> dict[str, str]:
    return {
        "message": "AI Tender Response System",
        "health": "/health",
        "api_docs": "/docs",
    }


@app.post("/api/v1/proposals")
async def generate_proposal(file: UploadFile = File(...)):
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF tender document.",
        )

    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="The PDF exceeds the 20 MB upload limit.",
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file does not appear to be a valid PDF.",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / f"{uuid4().hex}.pdf"

    try:
        file_path.write_bytes(content)

        container = ApplicationContainer.with_rag(
            security_scanner=None,
        )
        workflow = build_proposal_workflow(container)

        result = await workflow.ainvoke(
            {
                "request_id": str(uuid4()),
                "input_documents": [str(file_path)],
                "status": "received",
                "errors": [],
            }
        )

        report = result.get("quality_report", {})
        judge = report.get("judge_evaluation", {})

        return {
            "request_id": result.get("request_id"),
            "filename": file.filename,
            "status": result.get("status", "unknown"),
            "requirements": result.get("requirements", {}),
            "proposal_draft": result.get("proposal_draft", ""),
            "quality_report": report,
            "judge_evaluation": judge,
            "errors": result.get("errors", []),
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Proposal workflow failed: {type(exc).__name__}: {exc}",
        ) from exc
    finally:
        await file.close()
