from pathlib import Path

from schemas import VISUAL_KEYS

GRAMMAR_PATH = Path(__file__).with_name("turn_payload.gbnf")


def gbnf_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"\\"{escaped}\\""'


def turn_payload_gbnf() -> str:
    """GBNF for TurnPayload. Field order matches schemas.py and is not interchangeable."""

    picture_keys = " | ".join(gbnf_string(key) for key in sorted(VISUAL_KEYS))
    return f"""\
# TurnPayload from schemas.py.
# Order: narration, choices, state_delta, visual_key.
# state_delta order: health, hunger, location, add_items, remove_items.

root ::= "{{" ws turn-fields "}}" ws

turn-fields ::= "\\"narration\\"" ws ":" ws string "," ws "\\"choices\\"" ws ":" ws choices "," ws "\\"state_delta\\"" ws ":" ws state-delta "," ws "\\"visual_key\\"" ws ":" ws visual-key

choices ::= "[" ws string "," ws string ("," ws string)? "]" ws

state-delta ::= "{{" ws "\\"health\\"" ws ":" ws integer "," ws "\\"hunger\\"" ws ":" ws integer "," ws "\\"location\\"" ws ":" ws location "," ws "\\"add_items\\"" ws ":" ws string-list "," ws "\\"remove_items\\"" ws ":" ws string-list "}}" ws

location ::= "null" ws | string

visual-key ::= ("null" | {picture_keys}) ws

string-list ::= "[" ws (string ("," ws string)*)? "]" ws

string ::= "\\"" chars "\\"" ws

chars ::= ([^"\\\\\\x7F\\x00-\\x1F] | "\\\\" (["\\\\bfnrt] | "u" [0-9a-fA-F]{{4}}))+

integer ::= ("-"? ([0-9] | [1-9] [0-9]{{0,15}})) ws

# Optional space, same convention as llama.cpp grammars/json.gbnf.
ws ::= | " " | "\\n" [ \\t]{{0,20}}
"""


def main() -> None:
    GRAMMAR_PATH.write_text(turn_payload_gbnf())


if __name__ == "__main__":
    main()
