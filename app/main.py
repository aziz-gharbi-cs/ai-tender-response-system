from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

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

HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Tender Response System</title>
<style>
:root {
  font-family: Inter, Segoe UI, Arial, sans-serif;
  color: #e8edf5;
  background: #0b1020;
  font-synthesis: none;
}
* { box-sizing: border-box; }
body { margin: 0; }
header {
  padding: 22px 7%;
  border-bottom: 1px solid #263148;
  background: #10182a;
}
.brand { font-weight: 750; font-size: 19px; }
.brand span { color: #7c9cff; }
main { max-width: 1100px; margin: 38px auto; padding: 0 22px; }
h1 { font-size: clamp(27px, 4vw, 40px); margin-bottom: 10px; }
.subtitle { color: #9ba9c0; line-height: 1.6; }
.panel {
  background: #121b2e;
  border: 1px solid #283650;
  border-radius: 15px;
  padding: 24px;
  margin-top: 24px;
}
h2 { font-size: 19px; margin-top: 0; }
.upload-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
input[type=file] {
  flex: 1; min-width: 230px; padding: 13px;
  border: 1px solid #34425c; border-radius: 9px;
  color: #dce5f4; background: #0b1020;
}
button {
  cursor: pointer; border: 0; border-radius: 9px;
  padding: 13px 18px; font-weight: 700;
  background: #7595ff; color: #081126;
}
button:disabled { opacity: .55; cursor: wait; }
.secondary { background: #25344e; color: #e8edf5; }
.note, .muted { color: #9ba9c0; font-size: 13px; line-height: 1.6; }
#message { margin-top: 15px; white-space: pre-wrap; }
.hidden { display: none; }
.grid {
  display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
.metric {
  border-radius: 12px; background: #0b1426;
  padding: 18px; border: 1px solid #263650;
}
.metric-label { color: #9ba9c0; font-size: 13px; }
.metric-value { font-size: 27px; font-weight: 750; margin-top: 8px; }
.status { display: inline-block; padding: 6px 10px; border-radius: 20px;
  background: #243653; font-size: 12px; font-weight: 700; }
.status.good { color: #8ce0b1; }
.status.warn { color: #ffd28a; }
.result-section { margin-top: 24px; }
.proposal {
  white-space: pre-wrap; overflow-wrap: anywhere;
  font: 14px/1.8 "Segoe UI", Arial, sans-serif;
  color: #e1e8f3; background: #0b1426;
  border: 1px solid #263650; border-radius: 10px;
  padding: 22px; max-height: 700px; overflow: auto;
}
ul { padding-left: 22px; line-height: 1.7; }
li { margin-bottom: 7px; }
.warning {
  padding: 14px; border-radius: 9px; margin-top: 12px;
  background: #35291b; color: #ffd69b; line-height: 1.6;
}
footer { padding: 28px; text-align: center; color: #73829a; font-size: 12px; }
@media (max-width: 650px) {
  .grid { grid-template-columns: 1fr; }
  .panel { padding: 17px; }
}
</style>
</head>
<body>
<header>
  <div class="brand">AI <span>TENDER</span> RESPONSE SYSTEM</div>
</header>
<main>
  <h1>Generate a tender proposal</h1>
  <p class="subtitle">
    Upload a tender PDF and let the AI workflow extract requirements,
    draft a technical proposal, and evaluate the result with an LLM judge.
  </p>

  <section class="panel">
    <h2>1. Upload tender document</h2>
    <form id="uploadForm">
      <div class="upload-row">
        <input id="pdfFile" type="file" accept=".pdf,application/pdf" required>
        <button id="generateButton" type="submit">Generate proposal</button>
      </div>
    </form>
    <p class="note">PDF only · Maximum file size: 20 MB · Generation may take a few minutes.</p>
    <p id="message" role="status" aria-live="polite"></p>
  </section>

  <section id="results" class="hidden">
    <div class="panel">
      <h2>2. Generation results</h2>
      <p><span id="status" class="status"></span></p>
      <div class="grid">
        <div class="metric">
          <div class="metric-label">LLM judge score</div>
          <div id="score" class="metric-value">—</div>
          <div class="muted">Out of 100 · AI assessment, not a guarantee of compliance</div>
        </div>
        <div class="metric">
          <div class="metric-label">Requirements extracted</div>
          <div id="requirementCount" class="metric-value">—</div>
          <div class="muted">Across the extracted categories</div>
        </div>
      </div>
      <div id="warnings"></div>
    </div>

    <div class="panel result-section">
      <h2>3. Generated proposal</h2>
      <p class="muted">Review the draft carefully before using it in a real tender submission.</p>
      <button id="downloadButton" type="button">Download proposal (.md)</button>
      <div id="proposal" class="proposal" style="margin-top:16px"></div>
    </div>

    <div class="panel result-section">
      <h2>4. Judge evaluation</h2>
      <h3>Assessment</h3>
      <p id="assessment" class="subtitle"></p>
      <div class="grid">
        <div>
          <h3>Strengths</h3>
          <ul id="strengths"></ul>
        </div>
        <div>
          <h3>Weaknesses</h3>
          <ul id="weaknesses"></ul>
        </div>
      </div>
      <h3>Missing requirements or information</h3>
      <ul id="missing"></ul>
    </div>

    <div class="panel result-section">
      <h2>5. Extracted requirements</h2>
      <div id="requirements"></div>
    </div>

    <div class="panel result-section">
      <h2>Execution messages</h2>
      <ul id="errors"></ul>
    </div>
  </section>
</main>
<footer>AI Tender Response System · Demonstration interface</footer>

<script>
const form = document.getElementById("uploadForm");
const fileInput = document.getElementById("pdfFile");
const button = document.getElementById("generateButton");
const message = document.getElementById("message");
const results = document.getElementById("results");
let currentProposal = "";

function setText(id, value) {
  document.getElementById(id).textContent = value ?? "";
}

function fillList(id, items) {
  const list = document.getElementById(id);
  list.replaceChildren();
  const values = Array.isArray(items) ? items : [];
  if (!values.length) {
    const li = document.createElement("li");
    li.textContent = "None reported.";
    list.appendChild(li);
    return;
  }
  for (const value of values) {
    const li = document.createElement("li");
    li.textContent = String(value);
    list.appendChild(li);
  }
}

function showResults(data) {
  results.classList.remove("hidden");
  currentProposal = data.proposal_draft || "";
  setText("proposal", currentProposal || "No proposal was generated.");

  const status = document.getElementById("status");
  status.textContent = data.status || "unknown";
  status.className = "status " +
    (data.status === "quality_reviewed" ? "good" : "warn");

  const judge = data.judge_evaluation || {};
  setText("score",
    judge.status === "completed" && Number.isFinite(Number(judge.score))
      ? `${judge.score}/100` : "Unavailable");
  setText("assessment", judge.assessment || "No judge assessment available.");

  const requirements = data.requirements || {};
  const count = Object.values(requirements)
    .reduce((total, value) => total + (Array.isArray(value) ? value.length : 0), 0);
  setText("requirementCount", String(count));

  fillList("strengths", judge.strengths);
  fillList("weaknesses", judge.weaknesses);
  fillList("missing", judge.missing_requirements);

  const requirementBox = document.getElementById("requirements");
  requirementBox.replaceChildren();
  for (const [category, values] of Object.entries(requirements)) {
    const heading = document.createElement("h3");
    heading.textContent = category.replaceAll("_", " ");
    requirementBox.appendChild(heading);
    const list = document.createElement("ul");
    for (const value of (Array.isArray(values) ? values : [])) {
      const li = document.createElement("li");
      li.textContent = String(value);
      list.appendChild(li);
    }
    if (!list.children.length) {
      const li = document.createElement("li");
      li.textContent = "None identified.";
      list.appendChild(li);
    }
    requirementBox.appendChild(list);
  }

  const warnings = document.getElementById("warnings");
  warnings.replaceChildren();
  const report = data.quality_report || {};
  const scanErrors = report.scan_errors || [];
  const errors = data.errors || [];
  for (const warning of [
    ...scanErrors,
    ...errors,
    ...(data.status === "quality_review_failed"
      ? ["Quality review did not complete successfully. Review the execution messages below."]
      : [])
  ]) {
    const div = document.createElement("div");
    div.className = "warning";
    div.textContent = warning;
    warnings.appendChild(div);
  }
  fillList("errors", errors.length ? [...scanErrors, ...errors] : scanErrors);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = fileInput.files[0];
  if (!file) {
    message.textContent = "Choose a PDF file first.";
    return;
  }
  if (file.size > 20 * 1024 * 1024) {
    message.textContent = "The file exceeds the 20 MB limit.";
    return;
  }

  button.disabled = true;
  results.classList.add("hidden");
  message.textContent = "Processing the tender. This can take a few minutes...";
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("/api/v1/proposals", {
      method: "POST",
      body: formData
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || `Request failed (${response.status})`);
    }
    showResults(data);
    message.textContent = "Processing finished. Review the proposal and warnings below.";
    results.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    message.textContent = `Could not generate the proposal: ${error.message}`;
  } finally {
    button.disabled = false;
  }
});

document.getElementById("downloadButton").addEventListener("click", () => {
  if (!currentProposal) {
    message.textContent = "There is no proposal to download.";
    return;
  }
  const blob = new Blob([currentProposal], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "tender-proposal.md";
  link.click();
  URL.revokeObjectURL(url);
});
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home() -> HTMLResponse:
    return HTMLResponse(HTML_PAGE)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "application": settings.app_name}


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
