import gzip
import zipfile
from pathlib import Path

import pytest

from logpulse.reader import log_reader


@pytest.fixture
def txt_path(tmp_path: Path) -> Path:
    p = tmp_path / "sample.log"
    p.write_text("line1\nline2\n", encoding="utf-8")
    return p


@pytest.fixture
def gz_path(tmp_path: Path) -> Path:
    p = tmp_path / "sample.log.gz"
    with gzip.open(p, "wt", encoding="utf-8") as f:
        f.write("gzip1\ngzip2\n")
    return p


@pytest.fixture
def zip_ok(tmp_path: Path) -> Path:
    p = tmp_path / "valid.zip"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("logs/real.log", "zip1\nzip2\n")
        z.writestr("__MACOSX/logs/._real.log", "meta_data")
        z.writestr("docs/.DS_Store", "meta_data")
    return p


@pytest.fixture
def zip_multi(tmp_path: Path) -> Path:
    p = tmp_path / "multiple.zip"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("nginx.log", "content")
        z.writestr("app.txt", "content")
    return p


@pytest.fixture
def zip_sys(tmp_path: Path) -> Path:
    p = tmp_path / "system_only.zip"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("__MACOSX/logs/._real.log", "meta_data")
    return p


def test_txt(txt_path: Path) -> None:
    assert list(log_reader(str(txt_path))) == ["line1\n", "line2\n"]


def test_gz(gz_path: Path) -> None:
    assert list(log_reader(str(gz_path))) == ["gzip1\n", "gzip2\n"]


def test_zip_ok(zip_ok: Path) -> None:
    assert list(log_reader(str(zip_ok))) == ["zip1\n", "zip2\n"]


def test_zip_multi_fail(zip_multi: Path) -> None:
    with pytest.raises(ValueError):
        list(log_reader(str(zip_multi)))


def test_zip_sys_fail(zip_sys: Path) -> None:
    with pytest.raises(ValueError):
        list(log_reader(str(zip_sys)))


def test_missing_fail() -> None:
    with pytest.raises(FileNotFoundError):
        list(log_reader("missing.log"))
