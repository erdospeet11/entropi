import unittest

from fastapi.testclient import TestClient

import sessions
from app import app
from schemas import GameState

FIXED_TURN = {
    "narration": "The lantern swings as you step forward.",
    "choices": ["Press on", "Turn back"],
    "state_delta": {
        "health": -1,
        "hunger": 1,
        "location": "North path",
        "add_items": ["Rope"],
        "remove_items": ["2 coins"],
    },
    "visual_key": "forest_path",
}


class StartSessionTests(unittest.TestCase):
    def setUp(self) -> None:
        sessions.SESSIONS.clear()
        self.client = TestClient(app)

    def test_post_sessions_returns_opening_payload_and_state(self) -> None:
        response = self.client.post("/sessions")

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(
            body["payload"]["narration"],
            "You woke up in the forest. A raven watched from a branch. "
            "You found a path heading north.",
        )
        self.assertEqual(
            body["payload"]["choices"],
            ["Follow the path north", "Look around the clearing"],
        )
        self.assertEqual(body["payload"]["visual_key"], "forest_clearing")
        self.assertEqual(body["payload"]["state_delta"]["health"], 0)
        self.assertEqual(body["payload"]["state_delta"]["hunger"], 0)
        self.assertIsNone(body["payload"]["state_delta"]["location"])
        self.assertEqual(body["state"]["name"], "Wanderer")
        self.assertEqual(body["state"]["health"], 10)
        self.assertEqual(body["state"]["health_max"], 10)
        self.assertEqual(body["state"]["hunger"], 3)
        self.assertEqual(body["state"]["hunger_max"], 10)
        self.assertEqual(body["state"]["location"], "Forest clearing")
        self.assertEqual(
            body["state"]["inventory"],
            ["Rusty lantern", "Pocket knife", "2 coins"],
        )
        self.assertEqual(
            body["state"]["timeline"],
            [
                "You woke up in the forest",
                "A raven watched from a branch",
                "You found a path heading north",
            ],
        )
        self.assertEqual(body["state"]["visual_key"], "forest_clearing")
        self.assertEqual(sessions.SESSIONS[body["id"]].state.name, "Wanderer")

    def test_each_post_starts_a_separate_session(self) -> None:
        first = self.client.post("/sessions").json()["id"]
        second = self.client.post("/sessions").json()["id"]

        self.assertNotEqual(first, second)
        self.assertEqual(set(sessions.SESSIONS), {first, second})


class TurnTests(unittest.TestCase):
    def setUp(self) -> None:
        sessions.SESSIONS.clear()
        self.client = TestClient(app)
        self.session_id = self.client.post("/sessions").json()["id"]
        self.actions: list[str] = []
        self.original = sessions.completion
        sessions.completion = self.fake_completion

    def tearDown(self) -> None:
        sessions.completion = self.original

    def fake_completion(self, state: GameState, action: str) -> dict[str, object]:
        self.assertEqual(state.location, "Forest clearing")
        self.actions.append(action)
        return FIXED_TURN

    def test_choice_index_updates_state_and_returns_the_next_payload(self) -> None:
        response = self.client.post(f"/sessions/{self.session_id}/turns", json={"choice": 0})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(self.actions, ["Follow the path north"])
        self.assertEqual(body["payload"], FIXED_TURN)
        self.assertEqual(body["state"]["health"], 9)
        self.assertEqual(body["state"]["hunger"], 4)
        self.assertEqual(body["state"]["location"], "North path")
        self.assertEqual(body["state"]["inventory"], ["Rusty lantern", "Pocket knife", "Rope"])
        self.assertEqual(body["state"]["visual_key"], "forest_path")
        self.assertEqual(body["state"]["timeline"][-1], FIXED_TURN["narration"])
        self.assertEqual(sessions.SESSIONS[self.session_id].choices, ["Press on", "Turn back"])

    def test_player_line_updates_state(self) -> None:
        response = self.client.post(
            f"/sessions/{self.session_id}/turns",
            json={"text": "  Wait by the tree  "},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(self.actions, ["Wait by the tree"])
        self.assertEqual(body["payload"], FIXED_TURN)
        self.assertEqual(body["state"]["health"], 9)
        self.assertEqual(body["state"]["inventory"], ["Rusty lantern", "Pocket knife", "Rope"])
        self.assertEqual(body["state"]["timeline"][-1], "The lantern swings as you step forward.")

    def test_rejects_a_missing_session_or_a_bad_action(self) -> None:
        missing = self.client.post("/sessions/missing/turns", json={"choice": 0})
        out_of_range = self.client.post(
            f"/sessions/{self.session_id}/turns",
            json={"choice": 5},
        )
        both = self.client.post(
            f"/sessions/{self.session_id}/turns",
            json={"text": "Wait", "choice": 0},
        )
        neither = self.client.post(f"/sessions/{self.session_id}/turns", json={})

        self.assertEqual(missing.status_code, 404)
        self.assertEqual(out_of_range.status_code, 422)
        self.assertEqual(both.status_code, 422)
        self.assertEqual(neither.status_code, 422)
        self.assertEqual(self.actions, [])
        self.assertEqual(sessions.SESSIONS[self.session_id].state.hunger, 3)
        self.assertEqual(sessions.SESSIONS[self.session_id].state.location, "Forest clearing")


if __name__ == "__main__":
    unittest.main()
