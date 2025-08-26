import pathlib as Path

from data_pipeline.read import read_csv_local


def test_read_csv_utf8(tmp_path: Path):
    csv_path = tmp_path / "test.csv"
    csv_path.write_text("col1,col2\n1,2\n3,4\n", encoding="utf-8")

    df = read_csv_local(csv_path, encodings=["utf-8"], separators=[","])

    assert not df.empty
    assert list(df.columns) == ["col1", "col2"]
    assert df.shape == (2, 2)


def test_read_csv_iso(tmp_path: Path):
    csv_path = tmp_path / "test.csv"
    csv_path.write_text("col1;col2\né;2\nè;4\n", encoding="ISO-8859-1")

    df = read_csv_local(csv_path, encodings=["ISO-8859-1"], separators=[";"])

    assert not df.empty
    assert list(df.columns) == ["col1", "col2"]
    assert df.shape == (2, 2)
