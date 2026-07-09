import logging

_ENCODING: str = 'utf-8'
_NAME: str = 'logpulse'

_root_logger = logging.getLogger(_NAME)
_root_logger.setLevel(logging.INFO)

if not _root_logger.handlers:
    file_handler = logging.FileHandler(f'{_NAME}.log', encoding=_ENCODING)
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    _root_logger.addHandler(file_handler)


def get_logger(module_name: str) -> logging.Logger:
    return logging.getLogger(f"{_NAME}.{module_name}")