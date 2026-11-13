"""Atomic local LTEF snapshots and download metadata."""

import hashlib
import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .client import Download
from .config import Config

FILE_NAME = "ltef.csv"
METADATA_NAME = "ltef.metadata.json"


def _replace_bytes(path: Path, data: bytes) -> None:
    fd, name = tempfile.mkstemp(prefix=".ltef-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def save(config: Config, result: Download) -> dict[str, Any]:
    directory = config.directory
    directory.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC)
    metadata = {
        "downloaded_at": now.isoformat(),
        "source_last_modified": (
            result.source_last_modified.isoformat() if result.source_last_modified else None
        ),
        "source_etag": result.source_etag,
        "sha256": hashlib.sha256(result.content).hexdigest(),
        "size_bytes": len(result.content),
        "source_url": config.source_url,
    }
    _replace_bytes(directory / FILE_NAME, result.content)
    _replace_bytes(
        directory / METADATA_NAME, (json.dumps(metadata, indent=2) + "\n").encode("utf-8")
    )
    return status(config)


def status(config: Config) -> dict[str, Any]:
    file = config.directory / FILE_NAME
    metadata_file = config.directory / METADATA_NAME
    if not file.is_file() or not metadata_file.is_file():
        return {"exists": False}
    metadata: dict[str, Any] = json.loads(metadata_file.read_text(encoding="utf-8"))
    content = file.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    if digest != metadata["sha256"]:
        raise ValueError("Local LTEF checksum does not match its metadata")
    downloaded = datetime.fromisoformat(metadata["downloaded_at"])
    now = datetime.now(UTC)
    modified = metadata["source_last_modified"]
    return {
        "exists": True,
        "path": str(file),
        "downloaded_at": metadata["downloaded_at"],
        "age_seconds": max(0, (now - downloaded).total_seconds()),
        "source_last_modified": modified,
        "source_age_seconds": (
            max(0, (now - datetime.fromisoformat(modified)).total_seconds()) if modified else None
        ),
        "source_etag": metadata["source_etag"],
        "sha256": digest,
        "size_bytes": len(content),
        "source_url": metadata["source_url"],
    }
