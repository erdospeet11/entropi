import unittest

from pydantic import ValidationError

from schemas import GameState, TurnPayload, apply_turn


def payload(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "narration": "The lantern flickers as you step onto the north path.",
        "choices": ["Follow the path", "Turn back"],
        "state_delta": {
            "health": 0,
            "hunger": 1,
            "location": "North path",
            "add_items": [],
            "remove_items": [],
        },
        "visual_key": "forest_path",
    }
    data.update(overrides)
    return data


class TurnPayloadTests(unittest.TestCase):
    def test_accepts_two_or_three_choices(self) -> None:
        two = TurnPayload.model_validate(payload())
        three = TurnPayload.model_validate(
            payload(choices=["Follow the path", "Turn back", "Search the brush"])
        )

        self.assertEqual(two.choices, ["Follow the path", "Turn back"])
        self.assertEqual(len(three.choices), 3)
        self.assertEqual(two.state_delta.health, 0)
        self.assertEqual(two.state_delta.hunger, 1)
        self.assertEqual(two.state_delta.location, "North path")
        self.assertEqual(two.state_delta.add_items, [])
        self.assertEqual(two.state_delta.remove_items, [])
        self.assertEqual(two.visual_key, "forest_path")

    def test_location_null_means_stay(self) -> None:
        delta = payload()["state_delta"]
        assert isinstance(delta, dict)
        delta["location"] = None

        parsed = TurnPayload.model_validate(payload(state_delta=delta))

        self.assertIsNone(parsed.state_delta.location)

    def test_rejects_choice_count_outside_two_or_three(self) -> None:
        with self.assertRaises(ValidationError):
            TurnPayload.model_validate(payload(choices=["Wait"]))
        with self.assertRaises(ValidationError):
            TurnPayload.model_validate(
                payload(choices=["North", "South", "East", "West"])
            )

    def test_rejects_blank_text_and_unknown_fields(self) -> None:
        with self.assertRaises(ValidationError):
            TurnPayload.model_validate(payload(narration="  "))
        with self.assertRaises(ValidationError):
            TurnPayload.model_validate(payload(note="extra"))

    def test_unknown_visual_key_is_ignored(self) -> None:
        parsed = TurnPayload.model_validate(payload(visual_key="not_a_place"))

        self.assertIsNone(parsed.visual_key)

    def test_health_and_hunger_clamp_to_their_max(self) -> None:
        state = GameState(
            health=10,
            health_max=10,
            hunger=3,
            hunger_max=10,
            location="Forest clearing",
            inventory=["Rusty lantern", "Pocket knife"],
            visual_key="forest_clearing",
        )
        delta = payload()["state_delta"]
        assert isinstance(delta, dict)
        delta["health"] = 5
        delta["hunger"] = 20
        turn = TurnPayload.model_validate(payload(state_delta=delta, visual_key="nope"))

        updated = apply_turn(state, turn)

        self.assertEqual(updated.health, 10)
        self.assertEqual(updated.hunger, 10)
        self.assertEqual(updated.visual_key, "forest_clearing")

        delta["health"] = -100
        delta["hunger"] = -100
        turn = TurnPayload.model_validate(payload(state_delta=delta, visual_key="forest_night"))
        updated = apply_turn(state, turn)

        self.assertEqual(updated.health, 0)
        self.assertEqual(updated.hunger, 0)
        self.assertEqual(updated.visual_key, "forest_night")


if __name__ == "__main__":
    unittest.main()
