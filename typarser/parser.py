from __future__ import annotations

from typing import Generic, List, Type, TypeVar

from .namespace import Namespace

ARGS = TypeVar('ARGS', bound=Namespace)


class Parser(Generic[ARGS]):
    def __init__(self, params: Type[ARGS]):
        self._params = params

    def parse(self, args: List[str]) -> ARGS:
        raise NotImplementedError
