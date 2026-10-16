import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from app.agent import extract_timeline
from app.schemas import TimelineRequest, TimelineResponse

load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Document Timeline Extraction Agent",
    description="Extract events and relative dates using a Gemini API model.",
    version="1.0.0",
)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!doctype html><html lang="en"><head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>AI Timeline Agent</title>
    <style>
    body{font-family:system-ui,Arial;max-width:900px;margin:40px auto;padding:0 18px;color:#172033;background:#f6f8fc}
    main{background:white;padding:28px;border-radius:16px;box-shadow:0 8px 30px #10204012}
    textarea,input{box-sizing:border-box;width:100%;padding:12px;border:1px solid #cbd5e1;border-radius:8px;margin:8px 0 16px}
    textarea{min-height:180px}button{background:#155eef;color:white;border:0;border-radius:8px;padding:12px 18px;cursor:pointer}
    pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#0b1220;color:#e2e8f0;padding:16px;border-radius:10px}
    .muted{color:#64748b}</style></head><body><main>
    <h1>AI Document Timeline Agent</h1>
    <p class="muted">Paste document text to extract events and dates. Use synthetic/sample documents.</p>
    <form id="form">
    <label for="ref">Reference date (YYYY-MM-DD, optional)</label><input id="ref" placeholder="2026-10-16">
    <label for="doc">Document text</label>
    <textarea id="doc" required minlength="5">The project started on October 1, 2026. Testing will begin two weeks later, and deployment is planned five days after testing begins.</textarea>
    <button type="submit">Extract timeline</button></form>
    <h2>Result</h2><pre id="result">Your result will appear here.</pre>
    <p class="muted">API docs: <a href="/docs">/docs</a></p></main>
    <script>
    document.getElementById('form').addEventListener('submit',async(e)=>{
      e.preventDefault();const result=document.getElementById('result');result.textContent='Processing...';
      const body={text:document.getElementById('doc').value};const ref=document.getElementById('ref').value.trim();
      if(ref)body.reference_date=ref;
      try{const res=await fetch('/api/timeline',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      const data=await res.json();result.textContent=JSON.stringify(data,null,2);}catch(err){result.textContent=String(err);}
    });</script></body></html>
    """

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/timeline", response_model=TimelineResponse)
def timeline(request: TimelineRequest):
    try:
        return extract_timeline(request.text, request.reference_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid reference date: {exc}") from exc
    except RuntimeError as exc:
        logger.exception("Timeline extraction failed")
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected timeline extraction failure")
        raise HTTPException(status_code=502, detail="AI provider request failed. Check API key, model name, quota, and network connectivity.") from exc
