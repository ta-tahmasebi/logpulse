import sys

from logpulse.parser import parse_line
from logpulse.reader import log_reader


def run_pipeline(file_path: str) -> None:
    total_lines = 0
    failed_lines = 0

    try:
        for idx, line in enumerate(log_reader(file_path), 1):
            total_lines += 1
            if parse_line(line) is None:
                failed_lines += 1
                print(f"[ERROR] Line {idx}: {line.strip()[:80]}")

        print("\n" + "=" * 40)
        print(f"Total Lines:  {total_lines}")
        print(f"Successfully Parsed: {total_lines - failed_lines}")
        print(f"Failed Lines: {failed_lines}")
        print("=" * 40)

    except Exception as error:
        print(f"Execution failed: {error}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_log_file>")
        sys.exit(1)

    run_pipeline(sys.argv[1])
