from __future__ import annotations

import typing
from argparse import ArgumentParser
from itertools import count
from typing import Any, Dict, Iterator, NamedTuple, Tuple, Type, TypeVar, Union

from ._internal_namespace import get_namespace, set_value

if typing.TYPE_CHECKING:
    from ._internal_namespace import COMPONENT
    from .command import Commands
    from .namespace import Namespace
    ARGS = TypeVar('ARGS', bound=Namespace)
    MAP = Dict[  # type: ignore  # mypy doesn't suport cyclic types
        str, Union[COMPONENT, '_Subcommands']]  # type: ignore


def create_native_parser(namespace: Type[ARGS]) \
                         -> Tuple[ArgumentParser, MAP]:
    parser = ArgumentParser()
    names_map = _fill_parser(namespace, parser, count(start=1))
    return parser, names_map


def convert_native_args(native: Dict[str, Any], names_map: MAP,
                        namespace: Type[ARGS]) -> ARGS:
    return _unpack_native_values(native, names_map, namespace)


def _fill_parser(namespace: Type[Namespace], parser: ArgumentParser,
                 counter: Iterator[int]) -> MAP:
    internals = get_namespace(namespace)
    names_map: MAP = {}

    for option in internals.options:
        names = [
            f'-{name}' if len(name) == 1 else f'--{name}'
            for name in internals.components[option]
        ]
        key = f'opt_{next(counter)}'
        parser.add_argument(
            *names,
            type=option.type,
            required=option.required,
            nargs=option.nargs,  # type: ignore
            action=('append' if option.multiple else 'store'),
            help=option.help,
            dest=key,
        )
        names_map[key] = option

    for argument in internals.arguments:
        names = list(internals.components[argument])
        key = f'opt_{next(counter)}'
        parser.add_argument(
            *names,
            type=argument.type,
            nargs=argument.nargs,  # type: ignore
            help=argument.help,
            dest=key,
        )
        names_map[key] = argument

    if internals.command_containers:
        for command_container in internals.command_containers:
            if command_container.required:
                command_required = True
                break
        else:
            command_required = False
        key = f'opt_{next(counter)}'
        subparsers = parser.add_subparsers(required=command_required, dest=key)
        names_submap: Dict[str, _Subcommand] = {}
        names_map[key] = _Subcommands(next(iter(internals.command_containers)),
                                      names_submap)
        for name, subnamespace in internals.commands.items():
            subparser = subparsers.add_parser(name)
            names_submap[name] = _Subcommand(
                _fill_parser(subnamespace, subparser, counter), subnamespace)

    return names_map


def _unpack_native_values(native: Dict[str, Any], names_map: MAP,
                          namespace: Type[ARGS]) -> ARGS:
    result = namespace()
    for key, component in names_map.items():
        value = native[key]
        if isinstance(component, _Subcommands):
            sub_component, cmds = component
            if value is not None:  # command can be optional
                sub_map, sub_namespace = cmds[value]
                set_value(
                    result, sub_component,
                    _unpack_native_values(native, sub_map, sub_namespace))
            else:
                set_value(result, sub_component, None)
        else:
            set_value(result, component, value)
    return result


class _Subcommand(NamedTuple):
    submap: MAP
    namespace: Type[Namespace]


class _Subcommands(NamedTuple):
    component: Commands[Any, Any]
    cmds: Dict[str, _Subcommand]
