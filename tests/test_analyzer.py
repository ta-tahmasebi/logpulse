import pytest
from logpulse.analyzer import LogAnalyzer


@pytest.fixture
def sample_parsed_logs() -> list[dict[str, str]]:
    return [
        {
            "ip": "192.168.1.1",
            "time": "01/Jun/2026:14:22:10 +0000",
            "method": "GET",
            "url": "/index.html",
            "status": "200",
            "bytes": "5000",
            "user_agent": "Mozilla/5.0",
        },
        {
            "ip": "192.168.1.1",
            "time": "01/Jun/2026:14:25:15 +0000",
            "method": "POST",
            "url": "/login",
            "status": "401",
            "bytes": "120",
            "user_agent": "Python-requests",
        },
        {
            "ip": "10.0.0.5",
            "time": "01/Jun/2026:15:10:00 +0000",
            "method": "GET",
            "url": "/api/v1/users?id=12",
            "status": "500",
            "bytes": "0",
            "user_agent": "Go-http-client",
        },
    ]


def test_initial_state() -> None:
    analyzer = LogAnalyzer()
    assert analyzer.total_requests == 0
    assert analyzer.total_bytes == 0
    assert len(analyzer.unique_ips) == 0


def test_streaming_metrics_processing(sample_parsed_logs: list[dict[str, str]]) -> None:
    analyzer = LogAnalyzer()
    for log in sample_parsed_logs:
        analyzer.process_line(log)

    assert analyzer.total_requests == 3
    assert len(analyzer.unique_ips) == 2
    assert analyzer.total_bytes == 5120

    assert analyzer.methods["GET"] == 2
    assert analyzer.endpoints["/api/v1/users"] == 1

    assert analyzer.hourly_traffic["14"] == 2
    assert analyzer.hourly_traffic["15"] == 1


def test_security_brute_force_detection() -> None:
    analyzer = LogAnalyzer()
    malicious_ip = "172.16.5.9"
    for _ in range(6):
        analyzer.process_line({
            "ip": malicious_ip,
            "time": "01/Jun/2026:16:00:00 +0000",
            "method": "POST",
            "url": "/login",
            "status": "401",
            "bytes": "80",
            "user_agent": "Hydra-Bot",
        })

    headers, rows = analyzer.detect_suspicious_activity(threshold=5)
    assert len(rows) == 1
    assert rows[0][0] == malicious_ip
    assert rows[0][1] == "6"


def test_infrastructure_error_spike_detection() -> None:
    analyzer = LogAnalyzer()
    for i in range(10):
        status = "500" if i < 2 else "200"
        analyzer.process_line({
            "ip": f"192.168.1.{i}",
            "time": "01/Jun/2026:18:45:00 +0000",
            "method": "GET",
            "url": "/products",
            "status": status,
            "bytes": "1500",
            "user_agent": "Mozilla/5.0",
        })

    headers, rows = analyzer.detect_error_spikes(threshold_percent=5.0)
    assert len(rows) == 1
    assert rows[0][0] == "18:00"
    assert rows[0][2] == "20.00%"