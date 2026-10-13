import re
import unittest

from grammar import gbnf_string, turn_payload_gbnf, GRAMMAR_PATH
from schemas import VISUAL_KEYS


class GrammarTests(unittest.TestCase):
    def test_file_matches_the_schema(self) -> None:
        self.assertEqual(GRAMMAR_PATH.read_text(), turn_payload_gbnf())

    def test_visual_key_rule_is_the_known_set(self) -> None:
        rule = next(
            line for line in turn_payload_gbnf().splitlines() if line.startswith("visual-key")
        )
        names = set(re.findall(r'\\"([a-z0-9_]+)\\"', rule))

        self.assertEqual(names, set(VISUAL_KEYS))
        for key in VISUAL_KEYS:
            self.assertEqual(rule.count(gbnf_string(key)), 1)
        self.assertIn('"null"', rule)
        self.assertNotIn("string", rule)


if __name__ == "__main__":
    unittest.main()
