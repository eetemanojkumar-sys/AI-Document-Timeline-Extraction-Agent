from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import TimelineEvent, TimelineResponse

client = TestClient(app)


def _fake_result():
    return TimelineResponse(
        reference_date="2026-10-16",
        summary="Test summary",
        events=[
            TimelineEvent(
                event="Project started",
                date="2026-10-01",
                evidence="The project started on October 1, 2026.",
                confidence="high",
            )
        ],
    )


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_timeline_success():
    with patch("app.main.extract_timeline", return_value=_fake_result()):
        r = client.post("/api/timeline", json={"text": "The project started on October 1, 2026."})
    assert r.status_code == 200
    assert r.json()["events"][0]["date"] == "2026-10-01"


def test_timeline_rejects_short_text():
    assert client.post("/api/timeline", json={"text": "hi"}).status_code == 422


def test_timeline_bad_reference_date():
    with patch("app.main.extract_timeline", side_effect=ValueError("bad date")):
        r = client.post("/api/timeline", json={"text": "Some valid text here", "reference_date": "nope"})
    assert r.status_code == 400


def test_upload_rejects_unsupported_extension():
    r = client.post("/api/documents/upload", files={"file": ("a.exe", b"data")})
    assert r.status_code == 400


def test_upload_rejects_empty_file():
    r = client.post("/api/documents/upload", files={"file": ("a.txt", b"")})
    assert r.status_code == 400


def test_upload_rejects_oversized_file():
    big = b"a" * (5 * 1024 * 1024 + 1)
    r = client.post("/api/documents/upload", files={"file": ("a.txt", big)})
    assert r.status_code == 413


def test_upload_success_saves_result(monkeypatch):
    monkeypatch.setenv("S3_BUCKET", "test-bucket")
    with patch("app.main.extract_timeline", return_value=_fake_result()), \
         patch("app.main.upload_original") as up, \
         patch("app.main.save_result") as save:
        r = client.post(
            "/api/documents/upload",
            files={"file": ("a.txt", b"The project started on October 1, 2026.")},
        )
    assert r.status_code == 200
    up.assert_called_once()
    save.assert_called_once()


def test_dynamodb_failure_cleans_up_s3(monkeypatch):
    monkeypatch.setenv("S3_BUCKET", "test-bucket")
    with patch("app.main.extract_timeline", return_value=_fake_result()), \
         patch("app.main.upload_original"), \
         patch("app.main.save_result", side_effect=RuntimeError("boom")), \
         patch("app.main.delete_original") as cleanup:
        r = client.post(
            "/api/documents/upload",
            files={"file": ("a.txt", b"The project started on October 1, 2026.")},
        )
    assert r.status_code == 502
    cleanup.assert_called_once()


def test_retrieve_not_found():
    with patch("app.main.get_result", return_value=None):
        assert client.get("/api/documents/missing").status_code == 404
