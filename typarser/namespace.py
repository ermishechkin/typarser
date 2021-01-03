from __future__ import annotations

import typing
from typing import Any, Optional, Type

from ._internal_namespace import (init_namespace, register_component,
                                  unregister_component)

if typing.TYPE_CHECKING:
    from ._base import BaseComponent


class Namespace:
    def __init_subclass__(
        cls,
        *,
        prog: Optional[str] = None,
        usage: Optional[str] = None,
        description: Optional[str] = None,
        epilog: Optional[str] = None,
    ) -> None:
        init_namespace(
            cls,
            prog=prog,
            usage=usage,
            description=description,
            epilog=epilog,
        )


def ns_add(namespace: Type[Namespace],
           name: str,
           component: BaseComponent[Any, Any],
           override: bool = False,
           overwrite: bool = False) -> None:
    register_component(namespace,
                       name,
                       component,
                       allow_override=override,
                       allow_overwrite=overwrite)


def ns_remove(namespace: Type[Namespace], name: str) -> None:
    unregister_component(namespace, name)
