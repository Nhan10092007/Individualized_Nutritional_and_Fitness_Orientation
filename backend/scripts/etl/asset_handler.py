"""
Bước 2 (Asset Handling): Tải / chuẩn hóa Ảnh, GIF, Video về S3 / Cloudinary / CDN.
Lưu cache ánh xạ vào backend/data/processed/asset_manifest.json để tránh upload lặp.
"""

import hashlib
import importlib
import json
import mimetypes
import time
import urllib.request
from collections.abc import Iterable
from pathlib import Path

import requests

from app.config import settings
from scripts.etl.extract import PROCESSED_DATA_DIR

ASSET_CACHE_DIR = PROCESSED_DATA_DIR / "assets_cache"
ASSET_MANIFEST_PATH = PROCESSED_DATA_DIR / "asset_manifest.json"


class AssetHandler:
    """
    Xử lý tài nguyên media (Ảnh/GIF/Video) cho bài tập theo cấu hình ASSET_STORAGE_PROVIDER:
    - "github_cdn": ánh xạ sang ASSET_BASE_URL (mặc định chạy local/offline an toàn).
    - "cloudinary": tải ảnh từ nguồn và upload lên Cloudinary REST API.
    - "s3": tải ảnh từ nguồn và upload lên AWS S3 bucket (cần cài boto3).
    """

    def __init__(
        self,
        provider: str | None = None,
        upload_enabled: bool = False,
        manifest_path: Path = ASSET_MANIFEST_PATH,
    ):
        self.provider = (provider or settings.ASSET_STORAGE_PROVIDER or "github_cdn").lower()
        self.upload_enabled = upload_enabled
        self.manifest_path = manifest_path
        self.manifest: dict[str, str] = self._load_manifest()
        self._s3_client = None

    def _load_manifest(self) -> dict[str, str]:
        if self.manifest_path.exists():
            try:
                return json.loads(self.manifest_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def save_manifest(self) -> None:
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(
            json.dumps(self.manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _source_url(self, rel_or_url: str) -> str:
        if rel_or_url.startswith(("http://", "https://")):
            return rel_or_url
        base = settings.ASSET_BASE_URL.rstrip("/")
        return f"{base}/{rel_or_url.lstrip('/')}"

    def _download_bytes(self, url: str) -> bytes:
        req = urllib.request.Request(url, headers={"User-Agent": "FitnessNutritionETL/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read()

    def _upload_cloudinary(self, rel_path: str, content: bytes) -> str:
        if not (settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET):
            raise RuntimeError("Thiếu CLOUDINARY_CLOUD_NAME / API_KEY / API_SECRET trong .env")

        timestamp = int(time.time())
        public_id = Path(rel_path).with_suffix("").as_posix().lstrip("/")
        params_to_sign = f"folder={settings.CLOUDINARY_FOLDER}&public_id={public_id}&timestamp={timestamp}"
        signature = hashlib.sha1((params_to_sign + settings.CLOUDINARY_API_SECRET).encode("utf-8")).hexdigest()

        endpoint = f"https://api.cloudinary.com/v1_1/{settings.CLOUDINARY_CLOUD_NAME}/auto/upload"
        resp = requests.post(
            endpoint,
            data={
                "api_key": settings.CLOUDINARY_API_KEY,
                "timestamp": timestamp,
                "folder": settings.CLOUDINARY_FOLDER,
                "public_id": public_id,
                "signature": signature,
            },
            files={"file": (Path(rel_path).name, content)},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["secure_url"]

    def _get_s3_client(self):
        if self._s3_client is not None:
            return self._s3_client
        try:
            boto3 = importlib.import_module("boto3")
        except ModuleNotFoundError as exc:
            raise RuntimeError("Cần cài 'boto3' để upload media lên AWS S3") from exc
        if not settings.AWS_S3_BUCKET:
            raise RuntimeError("Thiếu AWS_S3_BUCKET trong .env")

        self._s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_S3_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
        )
        return self._s3_client

    def _upload_s3(self, rel_path: str, content: bytes) -> str:
        client = self._get_s3_client()
        key = f"{settings.AWS_S3_PREFIX.strip('/')}/{rel_path.lstrip('/')}"
        content_type, _ = mimetypes.guess_type(rel_path)
        client.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=key,
            Body=content,
            ContentType=content_type or "application/octet-stream",
        )
        return f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{key}"

    def resolve_asset(self, rel_or_url: str) -> str:
        """Trả về URL công khai cho 1 asset (ảnh/GIF/video)."""
        if not rel_or_url:
            return ""
        cache_key = f"{self.provider}:{rel_or_url}"
        if cache_key in self.manifest:
            return self.manifest[cache_key]

        src_url = self._source_url(rel_or_url)
        if not self.upload_enabled or self.provider == "github_cdn":
            return src_url

        content = self._download_bytes(src_url)
        if self.provider == "cloudinary":
            uploaded_url = self._upload_cloudinary(rel_or_url, content)
        elif self.provider == "s3":
            uploaded_url = self._upload_s3(rel_or_url, content)
        else:
            uploaded_url = src_url

        self.manifest[cache_key] = uploaded_url
        return uploaded_url

    def resolve_exercise_media(self, raw_images: Iterable[str] | None) -> tuple[list[str], str | None, str | None]:
        """Xử lý danh sách media của một bài tập, trả về (image_urls, thumbnail_url, video_url)."""
        urls: list[str] = []
        video_url: str | None = None
        for item in raw_images or []:
            resolved = self.resolve_asset(item)
            if not resolved:
                continue
            lower = resolved.lower()
            if lower.endswith((".mp4", ".webm", ".mov")) and video_url is None:
                video_url = resolved
            else:
                urls.append(resolved)
        thumbnail_url = urls[0] if urls else None
        return urls, thumbnail_url, video_url
