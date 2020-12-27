import pytest
from typarser import Argument, Namespace, Parser


def test_defaults():
    class Args(Namespace):
        arg = Argument(type=int)

    assert Args.arg.nargs is None
    assert Args.arg.choices is None
    assert Args.arg.default is None
    assert Args.arg.metavar is None
    assert Args.arg.help is None


def test_immutability():
    class Args(Namespace):
        arg = Argument(type=int)

    with pytest.raises(AttributeError):
        Args.arg.nargs = 2
    with pytest.raises(AttributeError):
        Args.arg.choices = [1, 5]
    with pytest.raises(AttributeError):
        Args.arg.default = 7
    with pytest.raises(AttributeError):
        Args.arg.metavar = 'VALUE'
    with pytest.raises(AttributeError):
        Args.arg.help = 'Help message'


def test_nargs_optional_in_middle_absent():
    class Args(Namespace):
        req1 = Argument(type=int)
        opt2 = Argument(type=int, nargs='?')
        req3 = Argument(type=int)

    args = Parser(Args).parse([
        '5',
        '1',
        '7',
    ])
    assert args.req1 == 5
    assert args.opt2 == 1
    assert args.req3 == 7


def test_nargs_optional_in_middle_exists():
    class Args(Namespace):
        req1 = Argument(type=int)
        opt2 = Argument(type=int, nargs='?')
        req3 = Argument(type=int)

    args = Parser(Args).parse([
        '2',
        '1',
    ])
    assert args.req1 == 2
    assert args.opt2 is None
    assert args.req3 == 1


def test_choices_good():
    class Args(Namespace):
        arg = Argument(type=int, choices=[2, 3, 5])

    args = Parser(Args).parse(['5'])
    assert args.arg == 5


def test_choices_bad():
    class Args(Namespace):
        arg = Argument(type=int, choices=[2, 3, 5])

    with pytest.raises(SystemExit):
        Parser(Args).parse(['--arg', '4'])


def test_default():
    class Args(Namespace):
        arg = Argument(type=int, nargs='?', default=5)
        arg2 = Argument(type=int, nargs='*', default=[6, 7])

    args = Parser(Args).parse([])
    assert args.arg == 5
    assert args.arg2 == [6, 7]

    args = Parser(Args).parse(['9'])
    assert args.arg == 9
    assert args.arg2 == [6, 7]

    args = Parser(Args).parse(['9', '4'])
    assert args.arg == 9
    assert args.arg2 == [4]


def test_inheritance():
    class Base(Namespace):
        arg1 = Argument(type=int)

    class Derived1(Base):
        arg2 = Argument(type=float)

    class Derived2(Base):
        arg3 = Argument(type=str)

    class Args(Derived1, Derived2):
        arg4 = Argument(type=int)

    args = Parser(Args).parse(['6', '3.0', '2', '7'])
    assert args.arg1 == 6
    assert args.arg2 == 3.0
    assert args.arg3 == '2'
    assert args.arg4 == 7


def test_overlap_and_hide():
    class Base(Namespace):
        arg1 = Argument(type=int)
        arg2 = Argument(type=float)
        arg3 = Argument(type=str)

    class Args(Base):
        arg2 = None

    args = Parser(Args).parse(['6', '3'])
    assert args.arg1 == 6
    assert args.arg2 == None
    assert args.arg3 == '3'
