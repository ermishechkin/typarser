from __future__ import annotations

from typing import Optional

from ._internal_namespace import init_namespace


class Namespace:
    def __init_subclass__(cls, usage: Optional[str] = None) -> None:
        init_namespace(cls, usage=usage)
