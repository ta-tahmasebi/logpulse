from logpulse.logger import draw_table, draw_chart


def run_visual_test() -> None:
    headers = ["IP Address", "Request Count", "Bandwidth (GB)", "Status"]
    rows = [
        ["192.168.1.1", "12450", "45.2", "Active"],
        ["10.0.0.5", "8432", "12.8", "Active"],
        ["172.16.0.22", "2105", "98.1", "Throttled"],
        ["192.168.1.50", "120", "0.4", "Blocked"],
    ]

    chart_data = {
        "GET": 4500,
        "POST": 1800,
        "PUT": 600,
        "DELETE": 150,
        "PATCH": 50,
    }

    draw_table("Top Traffic Consumers", headers, rows)
    draw_chart("HTTP Methods Distribution", chart_data, use_plt=True)


if __name__ == "__main__":
    run_visual_test()