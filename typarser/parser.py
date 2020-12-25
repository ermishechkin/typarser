from __future__ import annotations

from typing import Generic, List, Type

from ._native_parser import ARGS, create_native_parser, parse_args


class Parser(Generic[ARGS]):
    def __init__(self, params: Type[ARGS]):
        self._params = params
        self._native_parser, self._state = create_native_parser(self, params)

    def parse(self, args: List[str]) -> ARGS:
        return parse_args(self._native_parser, self._state, args)
