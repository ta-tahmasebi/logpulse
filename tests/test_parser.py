import pytest

from logpulse.parser import parse_line


@pytest.fixture
def log_ok() -> str:
    return '62.175.167.52 - - [01/Jun/2026:00:00:00 +0000] "GET / HTTP/1.1" 200 8956 "-" "python-requests/2.31.0"'


@pytest.fixture
def log_fail() -> str:
    return "garbage-00000"


def test_parse_ok(log_ok: str) -> None:
    res = parse_line(log_ok)
    assert res is not None
    assert res["ip"] == "62.175.167.52"
    assert res["time"] == "01/Jun/2026:00:00:00 +0000"
    assert res["method"] == "GET"
    assert res["url"] == "/"
    assert res["status"] == "200"
    assert res["bytes"] == "8956"
    assert res["referrer"] == "-"
    assert res["user_agent"] == "python-requests/2.31.0"


def test_parse_fail(log_fail: str) -> None:
    assert parse_line(log_fail) is None


def test_empty_fail() -> None:
    assert parse_line("") is None
    assert parse_line("   ") is None


def test_zero_bytes_ok():
    log = '1.1.1.1 - - [01/Jun/2026:00:00:00 +0000] "GET / HTTP/1.1" 304 0 "-" "-"'
    res = parse_line(log)
    assert res is not None
    assert res["bytes"] == "0"
    assert res["status"] == "304"


def test_query_url_ok() -> None:
    log = '1.1.1.1 - - [01/Jun/2026:00:00:00 +0000] "POST /search?q=pytest&len=fa HTTP/1.1" 200 50 "-" "-"'
    res = parse_line(log)
    assert res is not None
    assert res["url"] == "/search?q=pytest&len=fa"


def test_ipv6_ok() -> None:
    log = '2001:db8:85a3::8a2e:370:7334 - - [01/Jun/2026:00:00:00 +0000] "GET / HTTP/1.1" 200 10 "-" "-"'
    res = parse_line(log)
    assert res is not None
    assert res["ip"] == "2001:db8:85a3::8a2e:370:7334"


def test_bad_bracket_fail() -> None:
    log = '1.1.1.1 - - [01/Jun/2026:00:00:00 +0000 "GET / HTTP/1.1" 200 10 "-" "-"'
    assert parse_line(log) is None


def test_bad_quote_fail() -> None:
    log = '1.1.1.1 - - [01/Jun/2026:00:00:00 +0000] "GET / HTTP/1.1 200 10 "-" "-"'
    assert parse_line(log) is None
