import gzip
import io
import os
import zipfile
from collections.abc import Iterator

from .logger import get_logger

logger = get_logger('reader')

_ENCODING: str = 'utf-8'
_ERRORS: str = 'ignore'
_VALID_LOG_EXTS: tuple[str, ...] = ('.log', '.txt', '.out')


def _is_system_file(filename: str) -> bool:
    parts = filename.split('/')
    for part in parts:
        if part.startswith('.') or part.startswith('__'):
            return True
    return False


def _categorize_zip_files(zip_ref: zipfile.ZipFile) -> tuple[list[zipfile.ZipInfo], list[zipfile.ZipInfo]]:
    valid_candidates: list[zipfile.ZipInfo] = []
    preferred_files: list[zipfile.ZipInfo] = []

    for info in zip_ref.infolist():
        if info.is_dir() or info.filename.endswith('/'):
            continue

        if _is_system_file(info.filename):
            continue

        valid_candidates.append(info)

        if info.filename.lower().endswith(_VALID_LOG_EXTS):
            preferred_files.append(info)

    return valid_candidates, preferred_files


def _select_target_file(zip_ref: zipfile.ZipFile) -> zipfile.ZipInfo:
    valid_candidates, preferred_files = _categorize_zip_files(zip_ref)

    if not valid_candidates:
        raise ValueError("No valid (non-system) files found inside the zip archive.")

    if len(preferred_files) == 1:
        target = preferred_files[0]
        logger.info(f"File '{target.filename}' extracted from zip as the target log and entered for processing.")
        return target

    if len(preferred_files) > 1:
        file_names = [f.filename for f in preferred_files]
        raise ValueError(
            f"Multiple log/text files found in zip. Please specify which one to read. Candidates: {file_names}"
        )

    if len(valid_candidates) == 1:
        target = valid_candidates[0]
        logger.info(f"File '{target.filename}' extracted from zip as the target log and entered for processing.")
        return target

    file_names = [f.filename for f in valid_candidates]
    raise ValueError(
        f"No standard log/text file found, and multiple unknown files exist. Candidates: {file_names}"
    )


def _read_plain_text(file_path: str) -> Iterator[str]:
    with open(file_path, 'r', encoding=_ENCODING, errors=_ERRORS) as f:
        yield from f


def _read_gzip(file_path: str) -> Iterator[str]:
    with gzip.open(file_path, 'rt', encoding=_ENCODING, errors=_ERRORS) as f:
        yield from f


def _read_zip(file_path: str) -> Iterator[str]:
    with zipfile.ZipFile(file_path, 'r') as z:
        target_info = _select_target_file(z)

        with z.open(target_info, 'r') as f:
            with io.TextIOWrapper(f, encoding=_ENCODING, errors=_ERRORS) as text_wrapper:
                yield from text_wrapper


def log_reader(file_path: str) -> Iterator[str]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_path_lower = file_path.lower()

    if file_path_lower.endswith('.gz'):
        return _read_gzip(file_path)
    if file_path_lower.endswith('.zip'):
        return _read_zip(file_path)

    return _read_plain_text(file_path)
