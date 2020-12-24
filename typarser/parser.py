from __future__ import annotations

from typing import Generic, List, Type, TypeVar

from ._native_parser import parse_args
from .namespace import Namespace

ARGS = TypeVar('ARGS', bound=Namespace)


class Parser(Generic[ARGS]):
    def __init__(self, params: Type[ARGS]):
        self._params = params

    def parse(self, args: List[str]) -> ARGS:
        return parse_args(self, self._params, args)
