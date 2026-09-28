"""S3-mos yopiq ombor (02-backend.md, 5 va 6-bo'limlar).

- Bucket yopiq (public access block); obyektlar server tomonda shifrlanadi (SSE-KMS yoki AES256).
- Ochish faqat qisqa muddatli presigned GET URL orqali.
- `endpoint_url` — O'zbekistondagi S3-mos provayder uchun (ma'lumot hududda qoladi, 5-bo'lim).
boto3 sinxron — chaqiruvlar `asyncio.to_thread`da.
"""

import asyncio
from typing import TYPE_CHECKING, Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import Settings

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class S3FileStorage:
    def __init__(self, settings: Settings, client: "S3Client | None" = None) -> None:
        if not settings.s3_bucket:
            raise ValueError("FINORA_S3_BUCKET majburiy")
        self._bucket = settings.s3_bucket
        self._kms_key_id = settings.s3_kms_key_id
        self._client: S3Client = client or boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region,
            config=Config(signature_version="s3v4", retries={"max_attempts": 3},
                          connect_timeout=5, read_timeout=30),
        )

    def _sse(self) -> dict[str, Any]:
        if self._kms_key_id:
            return {"ServerSideEncryption": "aws:kms", "SSEKMSKeyId": self._kms_key_id}
        return {"ServerSideEncryption": "AES256"}

    async def put(self, key: str, data: bytes, content_type: str) -> None:
        await asyncio.to_thread(
            self._client.put_object, Bucket=self._bucket, Key=key, Body=data,
            ContentType=content_type, **self._sse(),
        )

    async def get(self, key: str) -> bytes | None:
        try:
            obj = await asyncio.to_thread(self._client.get_object, Bucket=self._bucket, Key=key)
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"NoSuchKey", "404"}:
                return None
            raise
        body = obj["Body"]
        return await asyncio.to_thread(body.read)

    async def delete(self, key: str) -> None:
        await asyncio.to_thread(self._client.delete_object, Bucket=self._bucket, Key=key)

    async def presigned_get_url(self, key: str, ttl_seconds: int) -> str | None:
        return await asyncio.to_thread(
            self._client.generate_presigned_url,
            "get_object",
            Params={"Bucket": self._bucket, "Key": key,
                    "ResponseContentDisposition": "inline",
                    "ResponseCacheControl": "no-store"},
            ExpiresIn=ttl_seconds,
        )
