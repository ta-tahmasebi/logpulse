from collections import Counter
from typing import Any, Dict, List, Tuple


class LogAnalyzer:
    def __init__(self) -> None:
        self.total_requests: int = 0
        self.failed_lines: int = 0
        self.unique_ips: set[str] = set()
        self.endpoints: Counter[str] = Counter()

        self.status_4xx: int = 0
        self.status_5xx: int = 0

        self.hourly_traffic: Counter[str] = Counter()
        self.hourly_5xx: Counter[str] = Counter()

        self.login_failures: Counter[str] = Counter()

    def process_line(self, parsed_data: Dict[str, str]) -> None:
        self.total_requests += 1
        self.unique_ips.add(parsed_data["ip"])

        endpoint = parsed_data["url"].split("?")[0]
        self.endpoints[endpoint] += 1

        status = parsed_data["status"]
        if status.startswith("4"):
            self.status_4xx += 1
            if status == "401" and endpoint == "/login":
                self.login_failures[parsed_data["ip"]] += 1
        elif status.startswith("5"):
            self.status_5xx += 1

        try:
            hour = parsed_data["time"].split(":")[1]
            self.hourly_traffic[hour] += 1
            if status.startswith("5"):
                self.hourly_5xx[hour] += 1
        except IndexError:
            pass

    def get_base_metrics(self) -> Tuple[List[str], List[List[Any]]]:
        total = self.total_requests or 1
        error_rate = ((self.status_4xx + self.status_5xx) / total) * 100

        headers = ["Metric Description", "Value"]
        rows = [
            ["Total Processed Requests", str(self.total_requests)],
            ["Unique Client IPs", str(len(self.unique_ips))],
            ["Total 4xx Client Errors", str(self.status_4xx)],
            ["Total 5xx Server Errors", str(self.status_5xx)],
            ["Total Error Rate", f"{error_rate:.2f}%"]
        ]
        return headers, rows

    def get_top_endpoints(self, top_n: int = 10) -> Tuple[List[str], List[List[Any]]]:
        headers = ["Rank", "Endpoint URL", "Hits"]
        rows = [[str(idx), ep, str(count)] for idx, (ep, count) in enumerate(self.endpoints.most_common(top_n), 1)]
        return headers, rows

    def get_hourly_report(self) -> Tuple[List[str], List[List[Any]], Dict[str, int]]:
        headers = ["Hour", "Total Requests", "5xx Errors"]
        rows = []
        chart_data = {}

        for hour in sorted(self.hourly_traffic.keys()):
            count = self.hourly_traffic[hour]
            err_5xx = self.hourly_5xx.get(hour, 0)
            rows.append([f"{hour}:00", str(count), str(err_5xx)])
            chart_data[f"{hour}:00"] = count

        return headers, rows, chart_data

    def detect_suspicious_activity(self, threshold: int = 5) -> Tuple[List[str], List[List[Any]]]:
        headers = ["Suspicious IP", "Failed Login Attempts (401)"]
        rows = []
        for ip, count in self.login_failures.items():
            if count >= threshold:
                rows.append([ip, str(count)])
        return headers, rows

    def detect_error_spikes(self, threshold_percent: float = 5.0) -> Tuple[List[str], List[List[Any]]]:
        headers = ["Hour Window", "5xx Count", "Traffic Share", "Status"]
        rows = []
        for hour, err_count in self.hourly_5xx.items():
            total_hour_traffic = self.hourly_traffic[hour] or 1
            share = (err_count / total_hour_traffic) * 100
            if share >= threshold_percent:
                rows.append([f"{hour}:00", str(err_count), f"{share:.2f}%", "CRITICAL SPIKE"])
        return headers, rows
