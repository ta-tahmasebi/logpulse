# LogPulse: CLI Log Analyzer

LogPulse is a lightweight command-line tool for parsing Nginx and Apache log files. It reads logs line-by-line to extract useful metrics without eating up all your server's RAM, even when dealing with massive or messy files.

---

## Supported Formats

LogPulse figures out how to handle your logs based on the file extension:

* **Plain Text:** Standard `.log`, `.txt`, or `.out` files.
* **Gzip (`.gz`):** Decompressed on the fly using streaming buffers.
* **Zip (`.zip`):** Reads straight from the archive.
* *Note: The zip file must contain exactly one log file. If it finds multiple files or none at all, it raises a `ValueError` to keep execution predictable.*



---

## Installation

1. **Clone the repo:**

```bash
git clone https://github.com/ta-tahmasebi/logpulse.git
cd logpulse
```

2. **Set up a virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

### Optional: Charts (`matplotlib`)

The `matplotlib` library is completely optional. The core log processing engine, security alerts, and terminal tables work fine without it. If you want to generate traffic charts, install it and use the `--chart` flag. If you don't install it, the script will just gracefully skip the chart generation without crashing.

---

## Usage

```bash
python main.py <PATH_TO_LOG_FILE> [OPTIONS]
```

### Arguments:

* `file_path` *(Required)*: Path to your log file (`.txt`, `.log`, `.gz`, `.zip`).
* `--top TOP`: Number of top entries to show for IPs and endpoints (Default: `10`).
* `--chart`: Enable graphical chart generation (requires `matplotlib`).
* `--secure-threshold SECURE_THRESHOLD`: Threshold for failed login detection on `/login` (Default: `5`).
* `--json`: Export full analytics report to `results/report.json`.
* `--workers WORKERS`: Number of parallel processes for multiprocessing. `0` = auto-detect CPU cores, `1` = single process (Default: `0`).

**Output Storage:** To prevent cluttering your terminal, LogPulse automatically saves all structured outputs and charts into a `results/` directory.

---

## Design Decisions & Challenges

Here are a few technical hurdles I ran into while building this and how I solved them:

### 1. Ignoring macOS Junk (`__MACOSX`)

Zipped logs created on Macs often include hidden metadata folders that break parsers. I added a filtering helper (`_is_system_file`) that automatically ignores these OS-specific files, ensuring the script only processes the actual log data.

### 2. Multithreading vs. Generators

I originally wrote a multithreaded version to chew through logs faster on multi-core systems. However, since the main goal was guaranteed memory efficiency (`O(1)` memory footprint) and keeping the CLI simple, I stuck with a single-threaded lazy generator for the `main` branch. If you want to see the parallelized version, check out the `multithreading` branch!

### 3. Regex vs. String Splitting

While simple string manipulation (`.split()`) can be faster in a perfect world, real-world logs are incredibly messy (missing user agents, escaped characters, etc.). I went with pre-compiled Regex (`re.compile`). Python's regex is written in C, so it's incredibly fast and much more reliable for parsing dirty data without causing bottlenecks.

---

## Example Output & Insights

Here’s what it looks like when you run LogPulse against a sample production dataset:

```text
LogPulse execution started...
Processing completed successfully in 3.10 seconds.

=== System Overview & Network Performance ===
+--------------------------+-----------+
| Metric Description       | Value     |
+--------------------------+-----------+
| Total Processed Requests | 495044    |
| Unique Client IPs        | 4001      |
| Total Network Bandwidth  | 2.5360 GB |
| Total 4xx Client Errors  | 26637     |
| Total 5xx Server Errors  | 24438     |
| Total Error Rate         | 10.32%    |
| Skipped Lines            | 4956      |
+--------------------------+-----------+

=== Top 10 Most Visited Endpoints ===
+------+-------------------+--------+
| Rank | Endpoint URL      | Hits   |
+------+-------------------+--------+
| 1    | /                 | 146302 |
| 2    | /products         | 87685  |
| 3    | /api/search       | 48842  |
| 4    | /cart             | 34181  |
| 5    | /login            | 31658  |
| 6    | /static/app.js    | 29249  |
| 7    | /static/style.css | 24299  |
| 8    | /health           | 14549  |
| 9    | /api/checkout     | 9807   |
| 10   | /products/9820    | 20     |
+------+-------------------+--------+

=== Top 10 Traffic Generating Clients ===
+------+-----------------+----------------+----------------+
| Rank | Client IP       | Total Requests | Bandwidth (MB) |
+------+-----------------+----------------+----------------+
| 1    | 21.67.75.144    | 7464           | 1.97 MB        |
| 2    | 169.214.192.18  | 160            | 0.89 MB        |
| 3    | 88.33.11.24     | 160            | 0.87 MB        |
| 4    | 44.64.147.243   | 158            | 0.86 MB        |
| 5    | 210.221.103.64  | 157            | 0.75 MB        |
| 6    | 208.64.231.113  | 157            | 0.81 MB        |
| 7    | 77.126.71.51    | 156            | 0.89 MB        |
| 8    | 26.41.177.111   | 156            | 0.85 MB        |
| 9    | 128.183.199.116 | 156            | 0.83 MB        |
| 10   | 203.15.192.5    | 154            | 0.81 MB        |
+------+-----------------+----------------+----------------+

=== HTTP Request Methods Distribution ===
+-------------+--------+
| HTTP Method | Count  |
+-------------+--------+
| GET         | 453539 |
| POST        | 41505  |
+-------------+--------+

=== HTTP Methods Volume ===
GET             | ██████████████████████████████ (453539)
POST            | ██ (41505)

=== Top 5 Client User-Agents (Bot Detection) ===
+------+-------------------------------------------------+--------+
| Rank | User-Agent String                               | Hits   |
+------+-------------------------------------------------+--------+
| 1    | python-requests/2.31.0                          | 104931 |
| 2    | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) | 97681  |
| 3    | Mozilla/5.0 (X11; Linux x86_64)                 | 97632  |
| 4    | Mozilla/5.0 (Windows NT 10.0; Win64; x64)       | 97517  |
| 5    | curl/8.4.0                                      | 97283  |
+------+-------------------------------------------------+--------+

=== Hourly Traffic Distribution ===
+-------+----------------+------------+
| Hour  | Total Requests | 5xx Errors |
+-------+----------------+------------+
| 00:00 | 51026          | 1465       |
| 01:00 | 50971          | 1561       |
| 02:00 | 50975          | 1565       |
| 03:00 | 50705          | 1518       |
| 04:00 | 50847          | 3640       |
| 05:00 | 51002          | 8983       |
| 06:00 | 50809          | 1513       |
| 07:00 | 50844          | 1531       |
| 08:00 | 50912          | 1533       |
| 09:00 | 36953          | 1129       |
+-------+----------------+------------+

=== Hourly Traffic Load ===
00:00           | ██████████████████████████████ (51026)
01:00           | █████████████████████████████ (50971)
02:00           | █████████████████████████████ (50975)
03:00           | █████████████████████████████ (50705)
04:00           | █████████████████████████████ (50847)
05:00           | █████████████████████████████ (51002)
06:00           | █████████████████████████████ (50809)
07:00           | █████████████████████████████ (50844)
08:00           | █████████████████████████████ (50912)
09:00           | █████████████████████ (36953)

=== Security Alert: Suspicious Activity Detected (Potential Brute-force) ===
+---------------+-----------------------------+
| Suspicious IP | Failed Login Attempts (401) |
+---------------+-----------------------------+
| 21.67.75.144  | 7464                        |
+---------------+-----------------------------+

=== Infrastructure Alert: Anomalous 5xx Error Code Spikes ===
+-------------+-----------+---------------+----------------+
| Hour Window | 5xx Count | Traffic Share | Status         |
+-------------+-----------+---------------+----------------+
| 04:00       | 3640      | 7.16%         | CRITICAL SPIKE |
| 05:00       | 8983      | 17.61%        | CRITICAL SPIKE |
+-------------+-----------+---------------+----------------+

```

### What this data tells us (Real-World Insights)

The tool isn't just for counting hits; it's designed to help you quickly spot actual infrastructure and security issues:

1. **Brute-force Attacks:** The IP `21.67.75.144` hit the server 7,464 times, and every single one was a `401 Unauthorized` on `/login`. This is clearly a brute-force or dictionary attack and should be blocked at the firewall level immediately.
2. **Heavy Bot Traffic:** Automated tools like `python-requests` and `curl` make up over 40% of the traffic. Bots are eating up a massive amount of bandwidth, meaning it might be time to deploy a bot-management page or require API keys.
3. **Backend Spikes (The 5xx Anomaly):** Between 04:00 and 06:00, server-side `5xx` errors spiked to 17.61%, even though overall traffic stayed completely flat. This rules out a simple traffic overload and points to an internal issue—maybe a heavy database cron job locking tables, or a bad morning deployment that needs to be rolled back.


## Performance Benchmarks

To see exactly where the original single-threaded engine was spending its time, I profiled it against a 500,000-line sample log using Python's built-in `cProfile`:

```bash
python -m cProfile -s tottime main.py access.log.zip

```

 Profiling tools inherently slow down execution. While the absolute execution times reported by the profiler were inflated, the *relative* distribution of CPU work highlighted two clear bottlenecks.

### The Bottlenecks

* **Metrics Aggregation (`process_line`):** Consumed **~47%** of total CPU time.
* **Regex Parsing (`parse_line`):** Consumed **~33%** of total CPU time.

### The Results

Here is the real-world speed comparison for processing that exact same 500,000-line file:

| Architecture | CPU Power Profile | Execution Time |
| --- | --- | --- |
| Single-Threaded | Normal | ~3.1 seconds |
| Multiprocessing | Energy-Saver | ~1.7 seconds |
| Multiprocessing | Performance | ~1.0 second |

