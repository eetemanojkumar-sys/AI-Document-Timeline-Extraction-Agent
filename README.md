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

## Architecture

Browser → FastAPI on Amazon EC2 (Ubuntu) → document text extraction → Gemini API  
Original document → Amazon S3  
Timeline result → Amazon DynamoDB

## Technology Stack

- Python, FastAPI, Uvicorn
- Gemini API
- AWS EC2, Amazon S3, Amazon DynamoDB, IAM instance role
- PDF/TXT/DOCX parsing with pypdf and python-docx
- Git and GitHub

## Configuration

Python 3.11+ is recommended. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `GEMINI_API_KEY`. Configure `AWS_REGION`, `S3_BUCKET`, and `DYNAMODB_TABLE` for your AWS resources. Use an EC2 IAM role with only the required S3 and DynamoDB permissions; avoid storing long-lived AWS credentials in the project.

Never commit `.env` or API keys.

## Run locally

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 for the web interface and http://127.0.0.1:8000/docs for the API documentation.

## Run on EC2

After configuring the environment and the EC2 instance role, run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open the instance's public address on port 8000 if the security group permits access. This deployment uses HTTP and does not include application authentication; use sample or non-sensitive documents and restrict inbound access while testing.

## API Endpoints

- `GET /` — browser interface
- `GET /health` — health check
- `POST /api/timeline` — extract a timeline from supplied text
- `POST /api/documents/upload` — upload a PDF, TXT, or DOCX file and process it
- `GET /api/documents/{document_id}` — retrieve a saved result

## Example timeline request

```json
{
  "reference_date": "2026-10-16",
  "text": "The project started on October 1, 2026. Testing will begin two weeks later."
}
```

## Important notes

- Model availability, rate limits, and pricing depend on the provider and account. The default model is `gemini-3.6-flash`; set `GEMINI_MODEL` in `.env` to override it.
- AI-generated dates can be uncertain. Review evidence and warnings before relying on extracted timelines.
- Add authentication, rate limiting, and appropriate privacy controls before accepting sensitive or public user uploads.
