from __future__ import annotations

from typing import Generic, List, Type, TypeVar

ARGS = TypeVar('ARGS')


class Parser(Generic[ARGS]):
    def __init__(self, params: Type[ARGS]):
        self._params = params

    def parse(self, args: List[str]) -> ARGS:
        raise NotImplementedError
