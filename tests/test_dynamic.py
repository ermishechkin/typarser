import pytest
from typarser import Argument, Namespace, Parser, ns_add, ns_remove


def test_dynamic_addition():
    class Args(Namespace):
        arg1 = Argument(type=int)
        arg2 = Argument(type=float)
        arg3 = Argument(type=str)

    ns_add(Args, 'arg4', Argument(type=int))

    args = Parser(Args).parse(['6', '3.0', 'some text', '2'])
    assert args.arg1 == 6
    assert args.arg2 == 3.0
    assert args.arg3 == 'some text'
    assert args.arg4 == 2


def test_dynamic_deletion():
    class Args(Namespace):
        arg1 = Argument(type=int)
        arg2 = Argument(type=float)
        arg3 = Argument(type=str)

    ns_remove(Args, 'arg2')

    args = Parser(Args).parse(['6', 'some text'])
    assert args.arg1 == 6
    assert args.arg3 == 'some text'
    with pytest.raises(AttributeError):
        args.arg2


def test_dynamic_addition_in_base():
    class Base(Namespace):
        base1 = Argument(type=int)
        base2 = Argument(type=str)

    class Args(Base):
        derived1 = Argument(type=float)
        derived2 = Argument(type=int)

    ns_add(Base, 'base3', Argument(type=int))

    args = Parser(Args).parse(['6', 'some text', '1', '2.5', '7'])
    assert args.base1 == 6
    assert args.base2 == 'some text'
    assert args.base3 == 1
    assert args.derived1 == 2.5
    assert args.derived2 == 7


def test_dynamic_deletion_in_base():
    class Base(Namespace):
        base1 = Argument(type=int)
        base2 = Argument(type=str)
        base3 = Argument(type=int)

    class Args(Base):
        derived1 = Argument(type=float)
        derived2 = Argument(type=int)

    ns_remove(Base, 'base2')

    args = Parser(Args).parse(['6', '1', '2.5', '7'])
    assert args.base1 == 6
    with pytest.raises(AttributeError):
        args.base2
    assert args.base3 == 1
    assert args.derived1 == 2.5
    assert args.derived2 == 7


def test_dynamic_deletion_inherited():
    class Base(Namespace):
        base1 = Argument(type=int)
        base2 = Argument(type=str)
        base3 = Argument(type=int)

    class Args(Base):
        derived1 = Argument(type=float)
        derived2 = Argument(type=int)

    ns_remove(Args, 'base2')

    args = Parser(Args).parse(['6', '1', '2.5', '7'])
    assert args.base1 == 6
    with pytest.raises(AttributeError):
        args.base2
    assert args.base3 == 1
    assert args.derived1 == 2.5
    assert args.derived2 == 7

    args2 = Parser(Base).parse(['2', '3', '4'])
    assert args2.base1 == 2
    assert args2.base2 == '3'  # must NOT be deleted from base
    assert args2.base3 == 4


def test_dynamic_deletion_inherited_alias():
    class Base(Namespace):
        base1 = Argument(type=int)
        base2 = base22 = Argument(type=str)
        base3 = Argument(type=int)

    class Args(Base):
        derived1 = Argument(type=float)
        derived2 = Argument(type=int)

    ns_remove(Args, 'base22')

    args = Parser(Args).parse(['6', '9', '1', '2.5', '7'])
    assert args.base1 == 6
    with pytest.raises(AttributeError):
        args.base22
    assert args.base2 == '9'
    assert args.base3 == 1
    assert args.derived1 == 2.5
    assert args.derived2 == 7

    args2 = Parser(Base).parse(['2', '3', '4'])
    assert args2.base1 == 2
    assert args2.base2 == '3'
    assert args2.base22 == '3'  # must NOT be deleted from base
    assert args2.base3 == 4
