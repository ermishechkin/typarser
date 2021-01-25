# Typarser

Typarser is a library for command-line arguments parsing. It is designed
to provide a more declarative way of defining positional and optional arguments
to produce a typed result. Typarser allows you to use type-checking tools with
the result of parsing and have auto-completion in text editors. It uses argparse
for the actual parsing, but provides a new interface for specifying arguments.

## Installing

Install and update using [pip](https://pip.pypa.io/en/stable/quickstart/):

    pip install -U typarser

## A Simple Example

```python

    from sys import argv
    from typarser import Argument, Namespace, Option, Parser, Help

    class Args(Namespace, description='Count lines with specific length'):
        help = h = Help()
        src = Argument(type=str, nargs='?', default='source.txt',
                    help='Source file name')
        min = m = Option(type=int, help='Minimal line length')
        max = M = Option(type=int, help='Maximal line length')

    parser = Parser(Args)
    cli_args = parser.parse(argv)
```

```
    $ python examples/quickstart.py -h
    usage: quickstart.py [--help] [--min MIN] [--max MAX] [src]

    Count lines with specific length

    positional arguments:
    src                Source file name

    optional arguments:
    --help, -h         show this help message and exit
    --min MIN, -m MIN  Minimal line length
    --max MAX, -M MAX  Maximal line length
```

## Links

- Code: https://github.com/ermishechkin/typarser
- Issue tracker: https://github.com/ermishechkin/typarser/issues
