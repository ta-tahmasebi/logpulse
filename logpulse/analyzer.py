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

        self.total_bytes: int = 0
        self.ip_requests: Counter[str] = Counter()
        self.ip_bandwidth: Counter[str] = Counter()
        self.methods: Counter[str] = Counter()
        self.user_agents: Counter[str] = Counter()

    def process_line(self, parsed_data: Dict[str, str]) -> None:
        self.total_requests += 1
        ip = parsed_data["ip"]
        self.unique_ips.add(ip)
        self.ip_requests[ip] += 1

        url = parsed_data["url"]
        qmark = url.find('?')
        endpoint = url if qmark == -1 else url[:qmark]
        self.endpoints[endpoint] += 1

        self.methods[parsed_data["method"]] += 1
        self.user_agents[parsed_data["user_agent"]] += 1

        status = parsed_data["status"]
        first_char = status[0]
        if first_char == '4':
            self.status_4xx += 1
            if status == "401" and endpoint == "/login":
                self.login_failures[ip] += 1
        elif first_char == '5':
            self.status_5xx += 1

        b_str = parsed_data["bytes"]
        if b_str.isdigit():
            b = int(b_str)
            self.total_bytes += b
            self.ip_bandwidth[ip] += b

        hour = parsed_data.get('hour', '00')
        self.hourly_traffic[hour] += 1
        if first_char == '5':
            self.hourly_5xx[hour] += 1

    def merge(self, others: list["LogAnalyzer"]) -> None:
        for other in others:
            self.total_requests += other.total_requests
            self.failed_lines += other.failed_lines
            self.unique_ips.update(other.unique_ips)
            self.endpoints += other.endpoints
            self.status_4xx += other.status_4xx
            self.status_5xx += other.status_5xx
            self.hourly_traffic += other.hourly_traffic
            self.hourly_5xx += other.hourly_5xx
            self.login_failures += other.login_failures
            self.total_bytes += other.total_bytes
            self.ip_requests += other.ip_requests
            self.ip_bandwidth += other.ip_bandwidth
            self.methods += other.methods
            self.user_agents += other.user_agents

    def get_base_metrics(self) -> Tuple[List[str], List[List[Any]]]:
        total = self.total_requests or 1
        error_rate = ((self.status_4xx + self.status_5xx) / total) * 100
        total_gb = self.total_bytes / (1024 * 1024 * 1024)

        headers = ["Metric Description", "Value"]
        rows = [
            ["Total Processed Requests", str(self.total_requests)],
            ["Unique Client IPs", str(len(self.unique_ips))],
            ["Total Network Bandwidth", f"{total_gb:.4f} GB"],
            ["Total 4xx Client Errors", str(self.status_4xx)],
            ["Total 5xx Server Errors", str(self.status_5xx)],
            ["Total Error Rate", f"{error_rate:.2f}%"]
        ]
        return headers, rows

    def get_top_endpoints(self, top_n: int = 10) -> Tuple[List[str], List[List[Any]]]:
        headers = ["Rank", "Endpoint URL", "Hits"]
        rows = [[str(idx), ep, str(count)] for idx, (ep, count) in enumerate(self.endpoints.most_common(top_n), 1)]
        return headers, rows

    def get_top_ips(self, top_n: int = 10) -> Tuple[List[str], List[List[Any]]]:
        headers = ["Rank", "Client IP", "Total Requests", "Bandwidth (MB)"]
        rows = []
        for idx, (ip, count) in enumerate(self.ip_requests.most_common(top_n), 1):
            mb_consumed = self.ip_bandwidth[ip] / (1024 * 1024)
            rows.append([str(idx), ip, str(count), f"{mb_consumed:.2f} MB"])
        return headers, rows

    def get_method_distribution(self) -> Tuple[List[str], List[List[Any]], Dict[str, int]]:
        headers = ["HTTP Method", "Count"]
        rows = [[m, str(c)] for m, c in self.methods.items()]
        chart_data = dict(self.methods)
        return headers, rows, chart_data

    def get_top_user_agents(self, top_n: int = 5) -> Tuple[List[str], List[List[Any]]]:
        headers = ["Rank", "User-Agent String", "Hits"]
        rows = []
        for idx, (ua, count) in enumerate(self.user_agents.most_common(top_n), 1):
            short_ua = ua[:60] + "..." if len(ua) > 60 else ua
            rows.append([str(idx), short_ua, str(count)])
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

    def get_json_report(self) -> dict[str, Any]:
        total = self.total_requests or 1
        error_rate = ((self.status_4xx + self.status_5xx) / total) * 100
        total_gb = self.total_bytes / (1024 * 1024 * 1024)

        return {
            "system_overview": {
                "total_processed_requests": self.total_requests,
                "unique_client_ips": len(self.unique_ips),
                "total_network_bandwidth_gb": round(total_gb, 4),
                "total_4xx_errors": self.status_4xx,
                "total_5xx_errors": self.status_5xx,
                "total_error_rate_percent": round(error_rate, 2),
                "failed_lines": self.failed_lines
            },
            "top_endpoints": {ep: count for ep, count in self.endpoints.most_common(10)},
            "top_ips": {
                ip: {
                    "requests": count,
                    "bandwidth_mb": round(self.ip_bandwidth[ip] / (1024 * 1024), 2)
                }
                for ip, count in self.ip_requests.most_common(10)
            },
            "http_methods": dict(self.methods),
            "top_user_agents": {ua: count for ua, count in self.user_agents.most_common(5)},
            "hourly_traffic": {f"{h}:00": self.hourly_traffic[h] for h in sorted(self.hourly_traffic.keys())},
            "suspicious_activities": {
                ip: count for ip, count in self.login_failures.items() if count >= 5
            },
            "critical_error_spikes": [
                {
                    "hour": f"{h}:00",
                    "count": err_count,
                    "share_percent": round((err_count / (self.hourly_traffic[h] or 1)) * 100, 2)
                }
                for h, err_count in self.hourly_5xx.items()
                if (err_count / (self.hourly_traffic[h] or 1)) * 100 >= 5.0
            ]
        }
