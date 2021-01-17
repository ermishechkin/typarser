from __future__ import annotations

from typing import Any, Optional

from .action import Action, ActionStoreConst
from .option import Option


class Flag(Option[bool, bool]):
    def __init__(
            self,
            *,
            action: Action = ActionStoreConst(True),
            help: Optional[str] = None,  # pylint: disable=redefined-builtin
    ):
        super().__init__(  # type: ignore
            type=bool,
            required=False,
            nargs=0,
            default=False,
            action=action,
            help=help,
        )

    def __new__(cls, *args: Any, **kwargs: Any) -> Flag:
        # pylint: disable=unused-argument
        return object.__new__(cls)
