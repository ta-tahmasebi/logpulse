import re

from logpulse.logger import get_logger

logger = get_logger('parser')

_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^]]+)\] "(?P<method>\S+) (?P<url>\S+) \S+" (?P<status>\d+) (?P<bytes>\d+) "(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"'
)


def parse_line(line: str) -> dict[str, str] | None:
    match = _PATTERN.match(line.strip())
    if not match:
        logger.warning(f"Invalid structure: {line[:50]}...")
        return None
    return match.groupdict()
