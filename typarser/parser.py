from __future__ import annotations

from typing import Generic, List, Type, TypeVar

from ._native_parser import convert_native_args, create_native_parser
from .namespace import Namespace

ARGS = TypeVar('ARGS', bound=Namespace)


class Parser(Generic[ARGS]):
    def __init__(self, params: Type[ARGS]):
        self._params = params

    def parse(self, args: List[str]) -> ARGS:
        parser, native_map = create_native_parser(self._params)
        native_values = parser.parse_args(args)
        return convert_native_args(vars(native_values), native_map,
                                   self._params)
