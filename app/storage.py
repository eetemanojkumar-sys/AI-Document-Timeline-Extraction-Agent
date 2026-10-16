import os

import boto3


def _settings():
    region = os.getenv("AWS_REGION", "ap-south-1")
    bucket = os.getenv("S3_BUCKET")
    table_name = os.getenv("DYNAMODB_TABLE", "TimelineAgentResults")

    if not bucket:
        raise RuntimeError("S3_BUCKET is missing from .env")

    return region, bucket, table_name


def upload_original(
    key: str,
    content: bytes,
    content_type: str = "application/octet-stream",
    document_id: str = "",
) -> None:
    region, bucket, _ = _settings()
    s3 = boto3.client("s3", region_name=region)

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=content,
        ContentType=content_type,
        ServerSideEncryption="AES256",
        Metadata={"document-id": document_id} if document_id else {},
    )


def delete_original(key: str) -> None:
    """Best-effort cleanup for an original file whose result could not be saved."""
    region, bucket, _ = _settings()
    s3 = boto3.client("s3", region_name=region)
    s3.delete_object(Bucket=bucket, Key=key)


def save_result(item: dict) -> None:
    region, _, table_name = _settings()
    table = boto3.resource("dynamodb", region_name=region).Table(table_name)
    table.put_item(Item=item)


def get_result(document_id: str) -> dict | None:
    region, _, table_name = _settings()
    table = boto3.resource("dynamodb", region_name=region).Table(table_name)

    response = table.get_item(Key={"document_id": document_id})
    return response.get("Item")
