from pathlib import Path

from data_pipeline.delete import delete_local_file


def test_delete_local_file_existing(tmp_path: Path):
    # Make a path
    file_path = tmp_path / "dummy.txt"
    # Make a file at specified path
    file_path.write_text("dummy")

    result = delete_local_file(file_path)

    assert result is True
    assert not file_path.exists()


def test_delete_local_file_missing(tmp_path: Path):
    # Make a path but we dont use write_text() to make a file
    file_path = tmp_path / "missing.txt"

    result = delete_local_file(file_path)

    assert result is False
    assert not file_path.exists()
