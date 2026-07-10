import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import islice
from pathlib import Path

from logpulse.analyzer import LogAnalyzer
from logpulse.logger import draw_table, draw_chart, get_logger, OUT_DIR
from logpulse.parser import parse_line
from logpulse.reader import log_reader

BATCH_SIZE = 10_000


def process_batch(lines):
    analyzer = LogAnalyzer()
    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            analyzer.failed_lines += 1
        else:
            analyzer.process_line(parsed)
    return analyzer


def chunked_reader(file_path, chunk_size):
    iterator = log_reader(file_path)
    while True:
        chunk = list(islice(iterator, chunk_size))
        if not chunk:
            break
        yield chunk


def single_process(file_path):
    analyzer = LogAnalyzer()
    for line in log_reader(file_path):
        parsed = parse_line(line)
        if parsed is None:
            analyzer.failed_lines += 1
        else:
            analyzer.process_line(parsed)
    return analyzer


def multi_process(file_path, max_workers=None):
    analyzer = LogAnalyzer()
    futures = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for batch in chunked_reader(file_path, BATCH_SIZE):
            futures.append(executor.submit(process_batch, batch))

        for future in as_completed(futures):
            partial_analyzer = future.result()
            analyzer.merge([partial_analyzer])

    return analyzer


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LogPulse: Log Analytics CLI Tool for Infrastructure."
    )
    parser.add_argument("logfile", type=str, help="Path to the access log file")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--chart", action="store_true")
    parser.add_argument("--secure-threshold", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--workers", type=int, default=0,
                        help="Number of parallel processes (0=auto, 1=single process)")

    args = parser.parse_args()
    logger = get_logger("main")

    if not Path(args.logfile).exists():
        print(f"Error: File '{args.logfile}' not found.")
        sys.exit(1)

    start_time = time.perf_counter()

    try:
        if args.workers == 1 or args.workers == 0 and args.workers is not None and args.workers == 0:
            analyzer = single_process(args.logfile)
        else:
            workers = args.workers if args.workers > 0 else None
            analyzer = multi_process(args.logfile, max_workers=workers)
    except Exception as e:
        logger.error(f"Pipeline crashed: {e}")
        print(f"Critical Error: {e}")
        sys.exit(1)

    elapsed_time = time.perf_counter() - start_time
    print(f"Processing completed in {elapsed_time:.2f} seconds.")

    base_headers, base_rows = analyzer.get_base_metrics()
    base_rows.append(["Skipped Lines", str(analyzer.failed_lines)])
    draw_table("System Overview & Network Performance", base_headers, base_rows)

    ep_headers, ep_rows = analyzer.get_top_endpoints(top_n=args.top)
    draw_table(f"Top {args.top} Most Visited Endpoints", ep_headers, ep_rows)

    ip_headers, ip_rows = analyzer.get_top_ips(top_n=args.top)
    draw_table(f"Top {args.top} Traffic Generating Clients", ip_headers, ip_rows)

    method_headers, method_rows, method_chart = analyzer.get_method_distribution()
    draw_table("HTTP Request Methods Distribution", method_headers, method_rows)
    draw_chart("HTTP Methods Volume", method_chart, use_plt=args.chart)

    ua_headers, ua_rows = analyzer.get_top_user_agents(top_n=5)
    draw_table("Top 5 Client User-Agents (Bot Detection)", ua_headers, ua_rows)

    hour_headers, hour_rows, hour_chart = analyzer.get_hourly_report()
    draw_table("Hourly Traffic Distribution", hour_headers, hour_rows)
    draw_chart("Hourly Traffic Load", hour_chart, use_plt=args.chart)

    sec_headers, sec_rows = analyzer.detect_suspicious_activity(threshold=args.secure_threshold)
    if sec_rows:
        draw_table("Security Alert: Suspicious Activity Detected (Potential Brute-force)", sec_headers, sec_rows)
    else:
        print("\nSecurity Check: No anomalous brute-force patterns detected on /login.")

    spike_headers, spike_rows = analyzer.detect_error_spikes(threshold_percent=5.0)
    if spike_rows:
        draw_table("Infrastructure Alert: Anomalous 5xx Error Code Spikes", spike_headers, spike_rows)
    else:
        print("\nInfrastructure Health: No critical 5xx error spikes detected.")

    if args.json:
        json_data = analyzer.get_json_report()
        json_path = OUT_DIR / "report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        print(f"\nFull analytics report successfully exported to JSON: {json_path}")


if __name__ == "__main__":
    main()
