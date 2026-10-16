# AI Document Timeline Extraction Agent

A starter portfolio project that extracts events and dates from document text using a Gemini API model. It runs as a Python FastAPI application and can be containerized and deployed to an EC2 Ubuntu instance.

## Architecture

Browser → FastAPI on EC2 → Python AI agent → Gemini API

Optional future integrations: S3 for documents, DynamoDB for results, Jenkins for CI/CD, Terraform for infrastructure.

This project does **not** use Amazon Bedrock or AWS Lambda.

## Requirements

- Python 3.11+
- Gemini API key from https://aistudio.google.com/apikey
- Network access to the Gemini API
- Docker (optional)

Free-tier access, model availability, rate limits, and pricing depend on current provider terms and your account.

## Run locally on Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `GEMINI_API_KEY` to your private key. Never commit `.env`.

Start the server:

```powershell
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 or http://127.0.0.1:8000/docs.

## Test

```powershell
pytest -q
```

## Run with Docker

Create `.env` first, then run:

```bash
docker compose up --build -d
```

Open http://localhost:8000.

## API example

POST `/api/timeline`

```json
{
  "reference_date": "2026-10-16",
  "text": "The project started on October 1, 2026. Testing will begin two weeks later, and deployment is planned five days after testing begins."
}
```

## Security notes

- Never put real API keys in source code or GitHub.
- Keep `.env` out of version control.
- For EC2, expose only required ports and use HTTPS through a reverse proxy or load balancer for public deployment.
- Use an EC2 IAM role for AWS service access rather than storing long-lived AWS credentials on the instance.
- This starter has no authentication or file-upload endpoint. Do not expose it publicly with sensitive documents until authentication, rate limiting, upload validation, and privacy controls are added.
- LLM output is probabilistic. Verify dates when source text is ambiguous.
