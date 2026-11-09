from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import tempfile
import uuid
from typing import BinaryIO

from .domain import DomainError


MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
_SAFE_FILENAME = re.compile(r"^[^\x00-\x1f\x7f]+$")


@dataclass(frozen=True)
class StagedDocument:
    temporary_path: Path
    storage_key: str
    original_filename: str
    content_sha256: str
    size_bytes: int


class LocalDocumentStore:
    """Local-only private file adapter for the academic demo; paths are never web-served."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.objects = self.root / "objects"
        self.staging = self.root / "staging"
        self.objects.mkdir(parents=True, exist_ok=True)
        self.staging.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def clean_filename(filename: str | None) -> str:
        name = (filename or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
        if (
            not name
            or len(name) > 160
            or not _SAFE_FILENAME.fullmatch(name)
            or name in {".", ".."}
            or Path(name).suffix.lower() != ".pdf"
        ):
            raise DomainError("invalid_document_filename", "Upload a PDF with a safe .pdf filename", 422)
        return name

    def stage_pdf(self, stream: BinaryIO, filename: str | None, max_bytes: int) -> StagedDocument:
        original_filename = self.clean_filename(filename)
        limit = min(max_bytes, MAX_DOCUMENT_BYTES)
        temporary_path: Path | None = None
        digest = hashlib.sha256()
        prefix = bytearray()
        tail = bytearray()
        size_bytes = 0
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix="upload-", suffix=".part", dir=self.staging, delete=False
            ) as staged:
                temporary_path = Path(staged.name)
                while True:
                    chunk = stream.read(64 * 1024)
                    if not chunk:
                        break
                    size_bytes += len(chunk)
                    if size_bytes > limit:
                        raise DomainError(
                            "document_too_large",
                            f"PDF exceeds the {limit // (1024 * 1024)} MB upload limit",
                            413,
                        )
                    if len(prefix) < 8:
                        prefix.extend(chunk[: 8 - len(prefix)])
                    tail.extend(chunk)
                    if len(tail) > 1024:
                        del tail[:-1024]
                    digest.update(chunk)
                    staged.write(chunk)
                if size_bytes == 0:
                    raise DomainError("empty_document", "The uploaded PDF is empty", 422)
                if not prefix.startswith(b"%PDF-") or b"%%EOF" not in tail:
                    raise DomainError(
                        "invalid_pdf_signature",
                        "The file does not have the expected PDF header and end marker",
                        422,
                    )
            storage_key = f"{uuid.uuid4()}.pdf"
            return StagedDocument(
                temporary_path=temporary_path,
                storage_key=storage_key,
                original_filename=original_filename,
                content_sha256=digest.hexdigest(),
                size_bytes=size_bytes,
            )
        except Exception:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise

    def promote(self, staged: StagedDocument) -> Path:
        destination = self.object_path(staged.storage_key)
        os.replace(staged.temporary_path, destination)
        return destination

    def object_path(self, storage_key: str) -> Path:
        try:
            normalized = f"{uuid.UUID(storage_key.removesuffix('.pdf'))}.pdf"
        except (ValueError, AttributeError) as error:
            raise DomainError("invalid_document_reference", "Document reference is invalid", 404) from error
        path = (self.objects / normalized).resolve()
        if path.parent != self.objects:
            raise DomainError("invalid_document_reference", "Document reference is invalid", 404)
        return path

    @staticmethod
    def discard(staged: StagedDocument) -> None:
        staged.temporary_path.unlink(missing_ok=True)
