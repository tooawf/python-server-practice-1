"""Interactive REPL for the data model."""

from __future__ import annotations

import ast
from pprint import pprint

from .model import DataModel

HELP = """Commands:
  add_actor (key, time, ip, user_agent)
  delete_actor key
  actors
  update_actor (key, time, ip, user_agent)
  add_instruction (key, time, content, actor, status)
  delete_instruction key
  instructions
  update_instruction (key, time, content, actor, status)
  add_response (key, time, output, status, failure, instruction)
  delete_response key
  responses
  update_response (key, time, output, status, failure, instruction)
  recent [now]
  help
  exit
"""


def parse_value(text: str):
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return text


def repl() -> None:
    model = DataModel()
    print("Variant 1 data model REPL. Type 'help' for commands.")
    while True:
        try:
            command = input("db> ").strip()
        except EOFError:
            break
        if not command:
            continue
        if command in {"exit", "quit"}:
            break
        if command == "help":
            print(HELP)
            continue
        try:
            name, _, args_text = command.partition(" ")
            args_text = args_text.strip()
            if name in {"actors", "instructions", "responses"}:
                pprint(getattr(model, f"get_all_{name}")())
            elif name == "recent":
                pprint(model.select_recent_instructions(int(args_text)) if args_text else model.select_recent_instructions())
            elif name.startswith("delete_"):
                print(getattr(model, name)(int(args_text)))
            elif name.startswith(("add_", "update_")):
                values = parse_value(args_text)
                if not isinstance(values, tuple):
                    raise ValueError("Arguments must be a Python tuple")
                method = name.replace("add_", "create_")
                print(getattr(model, method)(*values))
            else:
                raise ValueError("Unknown command")
        except Exception as exc:
            print(f"ERROR: {type(exc).__name__}: {exc}")
