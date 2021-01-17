from __future__ import annotations

from .action import ActionHelp
from .flag import Flag


class Help(Flag):
    # pylint: disable=redefined-builtin

    def __init__(self, *, help: str = 'show this help message and exit'):
        super().__init__(action=ActionHelp(), help=help)
