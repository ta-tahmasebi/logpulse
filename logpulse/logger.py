import logging
from pathlib import Path
from typing import Any

_ENCODING: str = 'utf-8'
_NAME: str = 'logpulse'
_OUT_DIR = Path('results')

_OUT_DIR.mkdir(exist_ok=True)

_root_logger = logging.getLogger(_NAME)
_root_logger.setLevel(logging.INFO)

if not _root_logger.handlers:
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.FileHandler(f'{_NAME}.log', encoding=_ENCODING)
    file_handler.setFormatter(formatter)
    _root_logger.addHandler(file_handler)


def get_logger(module_name: str) -> logging.Logger:
    return logging.getLogger(f"{_NAME}.{module_name}")


def draw_table(title: str, headers: list[str], rows: list[list[Any]]) -> None:
    cols = len(headers)
    widths = [len(h) for h in headers]
    for r in rows:
        for i in range(cols):
            widths[i] = max(widths[i], len(str(r[i])))

    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    head = "|" + "|".join(f" {headers[i]:<{widths[i]}} " for i in range(cols)) + "|"

    lines = [f"\n=== {title} ===", sep, head, sep]
    for r in rows:
        row_str = "|" + "|".join(f" {str(r[i]):<{widths[i]}} " for i in range(cols)) + "|"
        lines.append(row_str)
    lines.append(sep)

    output = "\n".join(lines)
    print(output)

    name = title.lower().replace(" ", "_")
    _OUT_DIR.joinpath(f"{name}.txt").write_text(output, encoding=_ENCODING)


def draw_chart(title: str, data: dict[str, int | float], use_plt: bool = False) -> None:
    name = title.lower().replace(" ", "_")

    if data:
        max_val = max(data.values()) or 1
        lines = [f"\n=== {title} ==="]
        for k, v in data.items():
            bar = "█" * int((v / max_val) * 30)
            lines.append(f"{k:<15} | {bar} ({v})")
        output = "\n".join(lines)
        print(output)
        _OUT_DIR.joinpath(f"{name}_ascii.txt").write_text(output, encoding=_ENCODING)

    if use_plt and data:
        try:
            import matplotlib.pyplot as plt

            x_data = list(data.keys())
            y_data = list(data.values())

            fig, ax = plt.subplots(figsize=(10, 5))

            bars = ax.bar(x_data, y_data, color="#2b5c8f", edgecolor="#1a3656", width=0.5)

            ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
            ax.set_xlabel("Metrics", fontsize=11, labelpad=10)
            ax.set_ylabel("Volume", fontsize=11, labelpad=10)

            ax.grid(axis="y", linestyle="--", alpha=0.5)
            ax.set_axisbelow(True)

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#cccccc")
            ax.spines["bottom"].set_color("#cccccc")

            plt.xticks(rotation=45, ha="right", fontsize=9)
            plt.yticks(fontsize=9)

            for bar in bars:
                height = bar.get_height()
                ax.annotate(
                    f"{int(height) if height.is_integer() else height}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    fontweight="bold"
                )

            plt.tight_layout()
            plt.savefig(_OUT_DIR / f"{name}.png", dpi=300)
            plt.close()
        except ImportError:
            get_logger("logger").error("Matplotlib is not installed. Graphical chart skipped.")
