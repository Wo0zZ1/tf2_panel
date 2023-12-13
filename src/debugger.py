from typing import TypeVar, Generic
import time

T = TypeVar("T")


def debug(content: Generic[T]) -> T:
    print(f"{time.strftime('%d.%m.%Y %H:%M:%S')} | {content}")
