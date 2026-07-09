# Module: logpulse.reader & logpulse.parser

These components implement memory-efficient file access patterns and regular expression extractions.

## Functions

### `log_reader` (in `logpulse.reader`)
Implements a lazy file stream generator yielding logs line-by-line without buffering large objects in memory. It transparently supports multiple input types based on the file extension.

```python
def log_reader(file_path: str) -> Generator[str, None, None]:

```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `file_path` | `str` | *Required* | System path targeting the target access log file. |

#### Supported File Types & Input Protocols

* **Plain Text (`.log`, `.txt`):** Native uncompressed text files read sequentially.
* **Gzip Compressed (`.gz`):** Decoded on-the-fly using streaming buffers (commonly used for rotated system logs).
* **Zip Archived (`.zip`):** Extracts and streams lines from the non-system/valid log entry found inside the archive wrapper.
* **Returns:** `Generator[str, None, None]`

---

### `parse_line` (in `logpulse.parser`)

Applies structured regular expressions to parse native Nginx Combined / Apache Common formats into flat string dictionary maps.

```python
def parse_line(line: str) -> dict[str, str] | None:

```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `line` | `str` | *Required* | Unprocessed log string from the data source. |

* **Returns:** `dict[str, str] | None`
* Returns a map containing keys: `ip`, `time`, `method`, `url`, `status`, `bytes`, `user_agent` if successful, otherwise `None`.
