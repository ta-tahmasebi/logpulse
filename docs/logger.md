# Module: logpulse.logger

This module configures centralized application file logging, generates structured ASCII terminal reports, and handles graphical data visualizations.

## Functions

### `get_logger`
Retrieves a namespaced child logger linked to the core root pipeline.

```python
def get_logger(module_name: str) -> logging.Logger:

```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `module_name` | `str` | *Required* | Name of the sub-module requesting a logger instance. |

* **Returns:** `logging.Logger`

### `draw_table`

Renders structured tabular reports on standard output and saves a text copy to the outputs directory.

```python
def draw_table(title: str, headers: list[str], rows: list[list[Any]]) -> None:

```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `title` | `str` | *Required* | Header text of the metric category. |
| `headers` | `list[str]` | *Required* | Column titles. |
| `rows` | `list[list[Any]]` | *Required* | Multi-dimensional matrix representing row values. |

* **Returns:** `None`

### `draw_chart`

Renders an ASCII text-based bar graph on stdout, writes it to a file, and conditionally saves a stylized high-resolution Matplotlib PNG plot.

```python
def draw_chart(title: str, data: dict[str, int | float], use_plt: bool = False) -> None:

```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `title` | `str` | *Required* | Title of the data plot. |
| `data` | `dict[str, int | float]` | *Required* | Key-value pairs representing labels and numeric volumes. |
| `use_plt` | `bool` | `False` | Toggles graphical Matplotlib PNG file rendering. |

* **Returns:** `None`
