import argparse
import sys
import time

from logpulse.analyzer import LogAnalyzer
from logpulse.logger import draw_table, draw_chart, get_logger
from logpulse.parser import parse_line
from logpulse.reader import log_reader


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LogPulse: Log Analytics CLI Tool for Infrastructure."
    )
    parser.add_argument("logfile", type=str, help="Path to the access log file")
    parser.add_argument("--top", type=int, default=10, help="Number of top endpoints/IPs to display (Default: 10)")
    parser.add_argument("--chart", action="store_true", help="Enable graphical chart generation using Matplotlib")
    parser.add_argument("--secure-threshold", type=int, default=5, help="Threshold for failed logins detection (401)")

    args = parser.parse_args()
    logger = get_logger("main")

    print("LogPulse execution started...")
    start_time = time.perf_counter()

    analyzer = LogAnalyzer()

    try:
        for line in log_reader(args.logfile):
            parsed = parse_line(line)
            if parsed is None:
                analyzer.failed_lines += 1
            else:
                analyzer.process_line(parsed)
    except Exception as e:
        logger.error(f"Pipeline crashed mid-execution: {e}")
        print(f"Critical Error during log streaming: {e}")
        sys.exit(1)

    elapsed_time = time.perf_counter() - start_time
    print(f"Processing completed successfully in {elapsed_time:.2f} seconds.")

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


if __name__ == "__main__":
    main()
