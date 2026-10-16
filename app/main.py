
import logging
import os
from datetime import date, datetime, timezone
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from pypdf import PdfReader
from docx import Document

from app.agent import extract_timeline
from app.schemas import TimelineRequest, TimelineResponse
from app.storage import upload_original, delete_original, save_result, get_result

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Document Timeline Extraction Agent",
    version="1.0.0",
    description="Extract events and relative dates using a Gemini API model.",
)


# --------------------------------------------------
# HOMEPAGE
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Timeline AI | Document Intelligence</title>

<style>
:root {
  --bg: #0b1020;
  --panel: #141c30;
  --border: #293650;
  --text: #edf3ff;
  --muted: #a7b4cb;
  --accent: #91aaff;
  --green: #65d6a0;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: Inter, system-ui, Arial, sans-serif;
  line-height: 1.6;
}
header {
  padding: 20px 6%;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.brand { font-size: 21px; font-weight: 800; }
.brand span { color: var(--accent); }
header a, a { color: var(--accent); text-decoration: none; }
main { max-width: 1000px; margin: auto; padding: 48px 20px; }
.eyebrow { color: var(--green); font-size: 13px; font-weight: 750; letter-spacing: 1px; }
h1 { font-size: clamp(32px, 5vw, 52px); line-height: 1.13; margin: 12px 0; }
.intro { max-width: 700px; color: var(--muted); }
.panel {
  margin-top: 28px;
  padding: 25px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 18px;
}
label { display: block; font-weight: 650; margin: 18px 0 8px; }
input, button { width: 100%; padding: 12px; border-radius: 10px; font: inherit; }
input { color: var(--text); background: #0c1426; border: 1px solid var(--border); }
input[type="file"] { max-width: 100%; }
button {
  margin-top: 20px;
  border: 0;
  background: var(--accent);
  color: #081126;
  font-weight: 800;
  cursor: pointer;
}
button:disabled { opacity: .55; cursor: wait; }
.hint, .muted { color: var(--muted); font-size: 13px; }
#status { margin-top: 18px; overflow-wrap: anywhere; }
.success { color: var(--green); }
.error { color: #ff9b9b; }
.summary { font-size: 18px; }
.event {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  margin-top: 12px;
  overflow-wrap: anywhere;
}
.event h3 { margin: 0 0 8px; font-size: 17px; }
.event p { margin: 7px 0; color: var(--muted); }
.pill {
  display: inline-block;
  background: #253454;
  border-radius: 20px;
  padding: 3px 10px;
  font-size: 12px;
  margin-bottom: 8px;
}
.warning {
  padding: 12px;
  border-radius: 10px;
  border: 1px solid var(--border);
  color: var(--muted);
  margin-top: 10px;
}
footer { text-align: center; color: var(--muted); padding: 28px 15px; }
[hidden] { display: none !important; }
@media (max-width: 600px) {
  main { padding: 30px 15px; }
  .panel { padding: 18px; }
}
</style>
</head>

<body>
<header>
  <div class="brand">Timeline <span>AI</span></div>
  <a href="/docs">API Documentation ↗</a>
</header>

<main>
  <div class="eyebrow">AI-POWERED DOCUMENT INTELLIGENCE</div>
  <h1>Turn documents into clear timelines.</h1>
  <p class="intro">
    Upload a resume or document. Let AI identify events, dates,
    supporting evidence, and relative timelines.
  </p>

  <section class="panel">
    <h2>Analyze a document</h2>
    <p class="muted">PDF, TXT, and DOCX · Maximum file size: 5 MB</p>

    <form id="uploadForm">
      <label for="file">Choose your document</label>
      <input
        id="file"
        name="file"
        type="file"
        accept=".pdf,.txt,.docx"
        required
      >

      <label for="referenceDate">Reference date (optional)</label>
      <input id="referenceDate" name="reference_date" type="date">

      <p class="hint">
        Helps interpret relative expressions such as “three months later”.
      </p>

      <button id="submitBtn" type="submit">Analyze document</button>
    </form>

    <div id="status" role="status" aria-live="polite"></div>
  </section>

  <section id="results" class="panel" hidden>
    <h2>Extracted timeline</h2>
    <p id="summary" class="summary"></p>
    <p id="metadata" class="muted"></p>
    <div id="events"></div>
    <div id="warnings"></div>
    <p>
      <a id="retrieveLink" href="#">
        View saved result (JSON) ↗
      </a>
    </p>
  </section>
</main>

<footer>AI Document Timeline Extraction Agent</footer>

<script>
const form = document.getElementById("uploadForm");
const button = document.getElementById("submitBtn");
const statusBox = document.getElementById("status");
const results = document.getElementById("results");

function addText(parent, tag, value, className) {
  const element = document.createElement(tag);
  element.textContent =
    value === null || value === undefined || value === ""
      ? "Not specified"
      : String(value);

  if (className) element.className = className;
  parent.appendChild(element);
  return element;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  results.hidden = true;
  statusBox.className = "";
  statusBox.textContent = "";

  const file = document.getElementById("file").files[0];

  if (!file) {
    statusBox.className = "error";
    statusBox.textContent = "Please select a document.";
    return;
  }

  if (file.size === 0) {
    statusBox.className = "error";
    statusBox.textContent = "The selected file is empty.";
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    statusBox.className = "error";
    statusBox.textContent = "Maximum upload size is 5 MB.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  const referenceDate =
    document.getElementById("referenceDate").value;

  if (referenceDate) {
    formData.append("reference_date", referenceDate);
  }

  button.disabled = true;
  button.textContent = "Analyzing document...";
  statusBox.textContent =
    "Uploading your document and extracting timeline events. Please wait.";

  try {
    const response = await fetch("/api/documents/upload", {
      method: "POST",
      body: formData
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(
        payload.detail || `Request failed: ${response.status}`
      );
    }

    const result = payload.result;

    document.getElementById("summary").textContent =
      result.summary || "No summary returned.";

    document.getElementById("metadata").textContent =
      `Document ID: ${payload.document_id} | ` +
      `Reference date: ${result.reference_date}`;

    const eventsBox = document.getElementById("events");
    eventsBox.replaceChildren();

    for (const item of (result.events || [])) {
      const card = document.createElement("article");
      card.className = "event";

      addText(
        card,
        "span",
        `Confidence: ${item.confidence || "medium"}`,
        "pill"
      );

      addText(card, "h3", item.event);

      addText(
        card,
        "p",
        `Date: ${item.date || "No exact date available"}`
      );

      addText(card, "p", `Evidence: ${item.evidence}`);

      if (item.notes) {
        addText(card, "p", `Notes: ${item.notes}`);
      }

      eventsBox.appendChild(card);
    }

    const warningsBox = document.getElementById("warnings");
    warningsBox.replaceChildren();

    for (const warning of (result.warnings || [])) {
      addText(warningsBox, "p", `Note: ${warning}`, "warning");
    }

    document.getElementById("retrieveLink").href =
      `/api/documents/${encodeURIComponent(payload.document_id)}`;

    results.hidden = false;
    statusBox.className = "success";
    statusBox.textContent = "Document analyzed successfully.";

    results.scrollIntoView({ behavior: "smooth", block: "start" });

  } catch (error) {
    statusBox.className = "error";
    statusBox.textContent =
      `Could not process the document: ${error.message}`;
  } finally {
    button.disabled = false;
    button.textContent = "Analyze document";
  }
});
</script>
</body>
</html>
"""


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------
# TEXT-BASED TIMELINE EXTRACTION
# --------------------------------------------------

@app.post("/api/timeline", response_model=TimelineResponse)
def timeline(request: TimelineRequest):
    try:
        return extract_timeline(
            request.text,
            request.reference_date,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid reference date: {exc}",
        ) from exc
    except RuntimeError as exc:
        logger.exception("Timeline extraction failed")
        raise HTTPException(
            status_code=503,
            detail="AI service is temporarily unavailable. Please retry.",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected timeline extraction failure")
        raise HTTPException(
            status_code=502,
            detail=(
                "AI provider request failed. Check the application logs, "
                "model availability, API key, quota, and connectivity."
            ),
        ) from exc


# --------------------------------------------------
# DOCUMENT UPLOAD, EXTRACTION, AND STORAGE
# --------------------------------------------------

@app.post("/api/documents/upload")
def upload_document(
    file: UploadFile = File(...),
    reference_date: str | None = Form(default=None),
):
    filename = Path(file.filename or "document.txt").name
    extension = Path(filename).suffix.lower()

    if extension not in {".txt", ".pdf", ".docx"}:
        raise HTTPException(
            status_code=400,
            detail="Supported formats: TXT, PDF, DOCX",
        )

    content = file.file.read(5 * 1024 * 1024 + 1)

    try:
        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Maximum upload size is 5 MB.",
            )

        if reference_date:
            try:
                date.fromisoformat(reference_date)
            except ValueError as exc:
                raise HTTPException(
                    status_code=400,
                    detail="reference_date must use YYYY-MM-DD.",
                ) from exc

        # Extract readable text from the uploaded file.
        try:
            if extension == ".txt":
                text = content.decode("utf-8-sig")

            elif extension == ".pdf":
                reader = PdfReader(BytesIO(content))
                text = "\n".join(
                    page.extract_text() or ""
                    for page in reader.pages
                )

            else:
                document = Document(BytesIO(content))
                text = "\n".join(
                    paragraph.text
                    for paragraph in document.paragraphs
                )

        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Could not read uploaded document")
            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not read this document. Check that the file "
                    "is valid and not corrupted."
                ),
            ) from exc

        text = text.strip()

        if len(text) < 5:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Not enough readable text was found. "
                    "Scanned PDFs may require OCR."
                ),
            )

        if len(text) > 30000:
            raise HTTPException(
                status_code=413,
                detail="Extracted text exceeds the 30000-character limit.",
            )

        document_id = str(uuid4())
        s3_key = f"uploads/{document_id}/{filename}"

        # Run Gemini extraction.
        try:
            result = extract_timeline(text, reference_date)
        except Exception as exc:
            logger.exception("AI timeline extraction failed")

            # Avoid returning a misleading generic error for provider outages.
            error_text = str(exc).lower()
            if (
                "503" in error_text
                or "unavailable" in error_text
                or "high demand" in error_text
                or "429" in error_text
                or "resource_exhausted" in error_text
            ):
                raise HTTPException(
                    status_code=503,
                    detail=(
                        "Gemini is temporarily unavailable or rate-limited. "
                        "Your original file may already be in S3. "
                        "Please retry later."
                    ),
                ) from exc

            raise HTTPException(
                status_code=502,
                detail="AI extraction failed. Check application logs.",
            ) from exc

        result_data = result.model_dump(mode="json")

        # Only upload the original after AI extraction succeeds.
        try:
            upload_original(
                key=s3_key,
                content=content,
                content_type=(
                    file.content_type or "application/octet-stream"
                ),
                document_id=document_id,
            )
        except Exception as exc:
            logger.exception("S3 upload failed")
            raise HTTPException(
                status_code=502,
                detail="Could not upload the original document to S3.",
            ) from exc

        # Save extracted results in DynamoDB.
        try:
            save_result({
                "document_id": document_id,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "filename": filename,
                "s3_bucket": os.environ["S3_BUCKET"],
                "s3_key": s3_key,
                "reference_date": result_data["reference_date"],
                "summary": result_data["summary"],
                "events": result_data["events"],
                "warnings": result_data["warnings"],
            })
        except Exception as exc:
            logger.exception("DynamoDB save failed")
            # Best-effort cleanup prevents an unreferenced S3 object.
            try:
                delete_original(s3_key)
            except Exception:
                logger.exception("S3 cleanup failed after DynamoDB save failure")
            raise HTTPException(
                status_code=502,
                detail=(
                    "Timeline extraction succeeded, but saving the result "
                    "failed. Check DynamoDB permissions and application logs."
                ),
            ) from exc

        return {
            "document_id": document_id,
            "s3_key": s3_key,
            "result": result_data,
        }

    finally:
        file.file.close()


# --------------------------------------------------
# RETRIEVE SAVED DOCUMENT RESULTS
# --------------------------------------------------

@app.get("/api/documents/{document_id}")
def retrieve_document_result(document_id: str):
    try:
        item = get_result(document_id)

        if item is None:
            raise HTTPException(
                status_code=404,
                detail="Document result not found.",
            )

        return item

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Could not retrieve document result")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve the saved result.",
        ) from exc
