from __future__ import annotations

import sys
from typing import IO, Generic, List, Optional, Type

from ._native_parser import ARGS, create_native_parser, parse_args
from .errors import ParseError


class Parser(Generic[ARGS]):
    def __init__(self, params: Type[ARGS], *, exit_on_error: bool = True):
        self._params = params
        self._exit_on_error = exit_on_error
        self._native_parser, self._state = create_native_parser(self, params)

    def parse(self, args: List[str]) -> ARGS:
        if self._exit_on_error:
            try:
                return parse_args(self._native_parser, self._state, args)
            except ParseError as exc:
                print(str(exc))
                sys.exit(2)
        return parse_args(self._native_parser, self._state, args)

    def print_usage(self, file: Optional[IO[str]] = None) -> None:
        self._native_parser.print_usage(file)

    def print_help(self, file: Optional[IO[str]] = None) -> None:
        self._native_parser.print_help(file)

    def format_usage(self) -> str:
        return self._native_parser.format_usage()

    def format_help(self) -> str:
        return self._native_parser.format_help()
