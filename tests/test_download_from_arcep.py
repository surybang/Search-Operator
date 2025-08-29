from pathlib import Path

import requests
import pytest

from data_pipeline import DownloadError, download_to_local


class DummyResponse:
    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.HTTPError(f"status {self.status_code}")


def test_download_success(monkeypatch, tmp_path):
    def fake_get(url, timeout):
        return DummyResponse(b"test response")

    monkeypatch.setattr(requests, "get", fake_get)

    out = download_to_local("http://fake-url", tmp_path, "test.csv")
    assert Path(out).exists()
    assert Path(out).read_text() == "test response"


def test_download_failure(monkeypatch, tmp_path):
    def fake_get(url, timeout):
        return DummyResponse(b"err", status_code=404)

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(DownloadError):
        download_to_local("http://bad-url", tmp_path, "bad.csv")
