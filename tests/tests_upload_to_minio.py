from pathlib import Path
import hashlib

import pytest
import fsspec

from data_pipeline.upload import (
    file_hash,
    s3_file_hash,
    get_latest_remote_file,
    upload_if_new,
)
from data_pipeline.exceptions import UploadError


# ---------- Helpers ----------
class FrozenDateTime:
    """Objet minimal pour monkeypatcher data_pipeline.upload.datetime."""

    def __init__(self, dt):
        self._dt = dt

    def now(self):
        return self._dt


def write_mem(fs, uri: str, data: bytes):
    with fs.open(uri, "wb") as f:
        f.write(data)


# ---------- Tests file_hash / s3_file_hash ----------
def test_file_hash(tmp_path: Path):
    p = tmp_path / "a.txt"
    content = b"hello world"
    p.write_bytes(content)
    expected = hashlib.md5(content).hexdigest()

    assert file_hash(p) == expected


def test_s3_file_hash_memory_fs():
    fs = fsspec.filesystem("memory")
    uri = "memory://arcep/raw/a.csv"
    content = b"12345"
    write_mem(fs, uri, content)
    expected = hashlib.md5(content).hexdigest()

    assert s3_file_hash(fs, uri) == expected


# ---------- Tests get_latest_remote_file ----------
def test_get_latest_remote_file_none():
    fs = fsspec.filesystem("memory")

    assert get_latest_remote_file(fs, "memory://arcep/raw", "MAJNUM") is None


def test_get_latest_remote_file_picks_latest():
    fs = fsspec.filesystem("memory")
    base = "memory://arcep/raw"
    write_mem(fs, f"{base}/MAJNUM_20240101.csv", b"a")
    write_mem(fs, f"{base}/MAJNUM_20250731.csv", b"b")
    latest = get_latest_remote_file(fs, base, "MAJNUM")

    assert latest == "/arcep/raw/MAJNUM_20250731.csv"


# ---------- Tests upload_if_new ----------
def test_upload_if_new_uploads_when_no_remote(tmp_path: Path, monkeypatch):
    fs = fsspec.filesystem("memory")
    # fige la date pour rendre le nom déterministe
    from datetime import datetime

    frozen = FrozenDateTime(datetime(2025, 8, 29))

    import data_pipeline.upload as m

    monkeypatch.setattr(m, "datetime", frozen)

    local = tmp_path / "majnum.csv"
    local.write_bytes(b"test")

    # bucket et key
    bucket = "memory://arcep"
    key = "/raw"

    uploaded = upload_if_new(fs, bucket, key, local, stem="MAJNUM")
    assert uploaded is True

    # Vérifie que le bon objet a été créé
    expected_uri = "memory://arcep/raw/MAJNUM_20250829.csv"
    with fs.open(expected_uri, "rb") as f:
        assert f.read() == b"test"


def test_upload_if_new_skips_when_same_hash(tmp_path: Path, monkeypatch):
    fs = fsspec.filesystem("memory")
    from datetime import datetime

    frozen = FrozenDateTime(datetime(2025, 8, 29))
    import data_pipeline.upload as m

    monkeypatch.setattr(m, "datetime", frozen)

    base = "memory://arcep/raw"
    # seed d'un fichier identique
    existing = f"{base}/MAJNUM_20250828.csv"
    content = b"test"
    write_mem(fs, existing, content)

    local = tmp_path / "majnum.csv"
    local.write_bytes(content)

    uploaded = upload_if_new(fs, "memory://arcep", "/raw", local, stem="MAJNUM")
    assert uploaded is False


def test_upload_if_new_uploads_when_different_hash(tmp_path: Path, monkeypatch):
    fs = fsspec.filesystem("memory")

    from datetime import datetime

    frozen = FrozenDateTime(datetime(2025, 8, 29))

    import data_pipeline.upload as m

    monkeypatch.setattr(m, "datetime", frozen)

    base = "memory://arcep/raw"
    # seed d'un fichier “dernier” différent
    write_mem(fs, f"{base}/MAJNUM_20250828.csv", b"old")

    local = tmp_path / "majnum.csv"
    local.write_bytes(b"new")

    uploaded = upload_if_new(fs, "memory://arcep", "/raw", local, stem="MAJNUM")
    assert uploaded is True

    # le nouveau fichier daté doit exister
    with fs.open(f"{base}/MAJNUM_20250829.csv", "rb") as f:
        assert f.read() == b"new"


def test_upload_if_new_raises_error_on_put_failure(tmp_path: Path, monkeypatch):
    fs = fsspec.filesystem("memory")

    from datetime import datetime

    frozen = FrozenDateTime(datetime(2025, 8, 29))

    import data_pipeline.upload as m

    monkeypatch.setattr(m, "datetime", frozen)

    local = tmp_path / "majnum.csv"
    local.write_bytes(b"data")

    # monkeypatch fs.put pour simuler une erreur réseau
    def boom(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr(fs, "put", boom)

    with pytest.raises(UploadError) as e:
        upload_if_new(fs, "memory://arcep", "/raw", local, stem="MAJNUM")

    # le message doit contenir le s3_uri calculé
    assert "MAJNUM_20250829.csv" in str(e.value)
