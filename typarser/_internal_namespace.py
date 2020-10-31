from __future__ import annotations

import typing
from dataclasses import dataclass
from typing import MutableMapping, Optional, Type
from weakref import WeakKeyDictionary

from .errors import NamespaceNotRegisteredError

if typing.TYPE_CHECKING:
    from .namespace import Namespace


@dataclass
class NamespaceInternals:
    usage: Optional[str] = None
    registered: bool = False


def init_namespace(namespace: Type[Namespace], *, usage: Optional[str]):
    internals = get_namespace(namespace, create=True)
    internals.usage = usage
    internals.registered = True


def get_namespace(namespace: Type[Namespace],
                  create: bool = False) -> NamespaceInternals:
    try:
        result = _namespaces[namespace]
    except KeyError:
        if not create:
            raise NamespaceNotRegisteredError(namespace) from None
        result = _namespaces[namespace] = NamespaceInternals()
    return result


_namespaces: MutableMapping[Type[Namespace], NamespaceInternals] = \
    WeakKeyDictionary()
