from typing import Any, Type


class ParserError(Exception):
    pass


class NamespaceNotRegisteredError(ParserError):
    def __init__(self, namespace_type: Type[Any]) -> None:
        super().__init__(f'Type {namespace_type} was not registered.'
                         ' Maybe __init_subclass__ was not called?')


class InvalidComponentTypeError(ParserError):
    def __init__(self) -> None:
        super().__init__('Invalid component type')


class InvalidComponentNameError(ParserError):
    def __init__(self, name: str) -> None:
        super().__init__(f'"{name}" is not a valid component name')


class ComponentOverrideForbiddenError(ParserError):
    def __init__(self, name: str) -> None:
        super().__init__(
            f'Component "{name}" was already defined in parent class.'
            ' Specify override=True explicitly.')


class ComponentAlreayExistsError(ParserError):
    def __init__(self, name: str) -> None:
        super().__init__(f'Component "{name}" already exists in namespace.'
                         ' Specify overwrite=True explicitly.')


class ComponentNotExistError(ParserError):
    def __init__(self, name: str) -> None:
        super().__init__(f'Component "{name}" does not exist in namespace')


class InvalidCommandNameError(ParserError):
    def __init__(self, name: str) -> None:
        super().__init__(f'"{name}" is not a valid command name')


class CommandAlreayExistsError(ParserError):
    def __init__(self, name: str) -> None:
        super().__init__(f'Command "{name}" already exists')


class CommandNotExistError(ParserError):
    def __init__(self, name: str) -> None:
        super().__init__(f'Command "{name}" does not exist')


class ParseError(ParserError):
    pass
