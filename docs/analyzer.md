# Module: logpulse.analyzer

This module contains the core log processing and analytics engine. It aggregates system metrics, calculates performance indicators, and performs security and infrastructure anomaly detection in a single pass.

## Class: LogAnalyzer

The main analysis class that maintains multi-dimensional counters for network traffic, status codes, and security-relevant endpoints.

### `__init__`
Initializes all internal metrics trackers, collections, and counters.

```python
def __init__(self) -> None:

```

### `process_line`

Processes a single parsed log line and increments all related statistical metrics.

```python
def process_line(self, parsed_data: dict[str, str]) -> None:

```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `parsed_data` | `dict[str, str]` | *Required* | A dictionary containing extracted log fields including ip, url, status, bytes, and user_agent. |

* **Returns:** `None`

### `get_base_metrics`

Compiles general system overview statistics including request volume, unique clients, bandwidth, and total error rates.

```python
def get_base_metrics(self) -> tuple[list[str], list[list[Any]]]:

```

* **Returns:** `tuple[list[str], list[list[Any]]]`
* Headers: `["Metric Description", "Value"]`
* Rows: Calculated values for total requests, IPs, bandwidth, 4xx/5xx errors, and percentages.



### `get_top_endpoints`

Retrieves the most frequently requested endpoints.

```python
def get_top_endpoints(self, top_n: int = 10) -> tuple[list[str], list[list[Any]]]:

```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `top_n` | `int` | `10` | The number of top entries to return. |

* **Returns:** `tuple[list[str], list[list[Any]]]`
* Headers: `["Rank", "Endpoint URL", "Hits"]`
* Rows: Matched top ranking endpoints and their hit counts.



### `get_top_ips`

Extracts clients that generated the most requests along with their bandwidth consumption.

```python
def get_top_ips(self, top_n: int = 10) -> tuple[list[str], list[list[Any]]]:

```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `top_n` | `int` | `10` | The number of top resource-heavy clients to return. |

* **Returns:** `tuple[list[str], list[list[Any]]]`
* Headers: `["Rank", "Client IP", "Total Requests", "Bandwidth (MB)"]`



### `get_method_distribution`

Aggregates HTTP request methods and generates raw distribution data.

```python
def get_method_distribution(self) -> tuple[list[str], list[list[Any]], dict[str, int]]:

```

* **Returns:** `tuple[list[str], list[list[Any]], dict[str, int]]`
* Headers: `["HTTP Method", "Count"]`
* Chart Data: A dictionary map of methods and counts for plotting.



### `get_top_user_agents`

Identifies the top clients making requests, useful for tracking programmatic traffic or crawlers.

```python
def get_top_user_agents(self, top_n: int = 5) -> tuple[list[str], list[list[Any]]]:

```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `top_n` | `int` | `5` | Number of user agents to display. |

* **Returns:** `tuple[list[str], list[list[Any]]]`
* Headers: `["Rank", "User-Agent String", "Hits"]`



### `get_hourly_report`

Generates an hourly distribution timeline of general traffic and 5xx failures.

```python
def get_hourly_report(self) -> tuple[list[str], list[list[Any]], dict[str, int]]:

```

* **Returns:** `tuple[list[str], list[list[Any]], dict[str, int]]`
* Headers: `["Hour", "Total Requests", "5xx Errors"]`
* Chart Data: A dictionary mapping hours to total request volume.



### `detect_suspicious_activity`

Filters clients with failed authentication spikes on sensitive endpoints to catch potential brute-force activities.

```python
def detect_suspicious_activity(self, threshold: int = 5) -> tuple[list[str], list[list[Any]]]:

```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `threshold` | `int` | `5` | Minimum number of failed login attempts to flag an IP. |

* **Returns:** `tuple[list[str], list[list[Any]]]`
* Headers: `["Suspicious IP", "Failed Login Attempts (401)"]`



### `detect_error_spikes`

Scans hourly windows to flag points where server-side error density breaks past expected tolerance bounds.

```python
def detect_error_spikes(self, threshold_percent: float = 5.0) -> tuple[list[str], list[list[Any]]]:

```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `threshold_percent` | `float` | `5.0` | The percentage of hourly traffic that must be 5xx to trigger an alert. |

* **Returns:** `tuple[list[str], list[list[Any]]]`
* Headers: `["Hour Window", "5xx Count", "Traffic Share", "Status"]`



