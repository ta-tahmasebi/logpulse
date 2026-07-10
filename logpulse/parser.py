import re

from logpulse.logger import get_logger

logger = get_logger('parser')

_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^]]+)\] '
    r'"(?P<method>\S+) (?P<url>\S+) \S+" '
    r'(?P<status>\d+) (?P<bytes>\d+) '
    r'"(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"'
)

_HOUR_PATTERN = re.compile(r':(\d{2}):\d{2}')


def parse_line(line: str) -> dict[str, str] | None:
    match = _PATTERN.match(line.strip())
    if not match:
        logger.warning(f"Invalid structure: {line[:50]}...")
        return None
    data = match.groupdict()
    time_str = data['time']
    hour_match = _HOUR_PATTERN.search(time_str)
    data['hour'] = hour_match.group(1) if hour_match else '00'
    return data