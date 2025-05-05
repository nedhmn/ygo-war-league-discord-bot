from typing import Any, Generator


def chunk_list(lst: list[Any], n: int) -> Generator[list[Any], None, None]:
    for i in range(0, len(lst), n):
        yield lst[i : i + n]
