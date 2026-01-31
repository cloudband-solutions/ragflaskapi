# 7) Command-line routines (Flask CLI)
This project uses Flask's built-in CLI, which is powered by the `click` library.
Custom commands live in `app/cli.py` and are registered in `app/__init__.py`
via `register_cli(app)` inside `create_app`.

## 7.1 Run a command
```bash
flask --app wsgi.py system greet
```

## 7.2 Template for new commands
Add a command group and subcommand in `app/cli.py`:
```python
import click


def register_cli(app):
    @app.cli.group()
    def system():
        """System tasks."""
        pass

    @system.command("greet")
    def greet():
        """Print hello world."""
        click.echo("hello world")
```

Wire it in `app/__init__.py`:
```python
from app.cli import register_cli

register_cli(app)
```

## 7.3 About `click`

`click` is a Python library for building composable command-line interfaces. It
provides decorators for commands and groups, automatic help text generation,
argument and option parsing, and utility functions like `click.echo` for
console output. Flask uses `click` under the hood, so any `@app.cli.command()`
or `@app.cli.group()` you define becomes a first-class Flask CLI command.
