# AI Document Timeline Extraction Agent

An AI-powered document processing application that extracts events, dates, evidence, and chronological timelines from uploaded documents. Built with FastAPI and the Gemini API, with AWS storage and retrieval.

## Features

- Upload PDF, TXT, and DOCX documents through a browser interface.
- Extract document text and generate a structured timeline using Gemini.
- Optionally supply a reference date to help interpret relative dates.
- Store original uploaded files in Amazon S3.
- Persist extracted timeline results in Amazon DynamoDB.
- Retrieve a previously processed result using its document ID.
- REST API and interactive API documentation via FastAPI.
- Automated API tests with pytest.

## Architecture

```text
Browser / API Client
        |
        v
FastAPI application on Amazon EC2 (Ubuntu)
        |
        +----> Document text extraction (PDF / TXT / DOCX)
        |
        +----> Gemini API ----> Structured event timeline
        |
        +----> Amazon S3 (original uploaded document)
        |
        +----> Amazon DynamoDB (processed timeline result)
```

## Technology Stack

- **Language / API:** Python, FastAPI, Uvicorn
- **AI:** Gemini API
- **Cloud:** AWS EC2, Amazon S3, Amazon DynamoDB, IAM instance role
- **Document processing:** pypdf, python-docx
- **Testing:** pytest, FastAPI TestClient, httpx
- **CI/CD:** Jenkins pipeline
- **Version control:** Git, GitHub

## Prerequisites

- Python 3.11 or newer
- A Gemini API key
- AWS resources configured for S3 and DynamoDB
- An EC2 IAM instance role with least-privilege permissions for the required S3 and DynamoDB operations (for AWS deployment)

## Configuration

Create a virtual environment and install the application dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `GEMINI_API_KEY`. Configure `AWS_REGION`, `S3_BUCKET`, and `DYNAMODB_TABLE` to match your AWS resources. Set `GEMINI_MODEL` only if you want to override the configured default.

Use an EC2 IAM role with only the permissions the application needs. Avoid storing long-lived AWS credentials in the project.

**Never commit `.env`, API keys, AWS credentials, or real user documents.**

## Run locally

With the virtual environment activated and `.env` configured:

```bash
uvicorn app.main:app --reload
```

Open these URLs in your browser:

- Web interface: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## Run on EC2

After configuring the environment and EC2 instance role, start the application with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open the instance's public address on port 8000 if its security group permits inbound access. This deployment uses HTTP and does not include application authentication. Use sample or non-sensitive documents and restrict inbound access while testing.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Browser interface |
| `GET` | `/health` | Health check |
| `POST` | `/api/timeline` | Extract a timeline from supplied text |
| `POST` | `/api/documents/upload` | Upload and process a PDF, TXT, or DOCX file |
| `GET` | `/api/documents/{document_id}` | Retrieve a saved result |

## Example timeline request

Send a `POST` request to `/api/timeline` with JSON such as:

```json
{
  "reference_date": "2026-10-16",
  "text": "The project started on October 1, 2026. Testing will begin two weeks later."
}
```

## Tests

Install development dependencies and run the automated test suite:

```bash
pip install -r requirements-dev.txt
pytest -q
```

The API tests cover health checks, timeline extraction behavior, invalid input, upload validation, successful document processing/storage, cleanup when persistence fails, and retrieval of missing documents. Tests should use mocks for external AI/AWS interactions; do not run tests against production data.

## Jenkins CI

The repository includes a `Jenkinsfile` for a Jenkins pipeline that installs development dependencies and runs the automated tests. Configure Jenkins with access to the repository and a compatible Python environment. Check the Jenkins build log to confirm the pipeline and tests pass in your environment.

## Important notes

- Model availability, rate limits, and pricing depend on the provider and account. The default model is `gemini-3.6-flash`; set `GEMINI_MODEL` in `.env` to override it.
- AI-generated dates may be uncertain. Review extracted evidence and warnings before relying on a timeline.
- Add authentication, rate limiting, and appropriate privacy controls before accepting sensitive documents or allowing unrestricted public uploads.
