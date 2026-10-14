from collections.abc import Callable
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, model_validator

from schemas import GameState, StateDelta, TurnPayload, apply_turn

Completion = Callable[[GameState, str], TurnPayload | object]


class StoredSession(BaseModel):
    state: GameState
    choices: list[str]


SESSIONS: dict[str, StoredSession] = {}


class SessionStart(BaseModel):
    id: str
    payload: TurnPayload
    state: GameState


class TurnInput(BaseModel):
    """A player line or a choice index. Exactly one of them."""

    model_config = ConfigDict(extra="forbid")

    text: str | None = None
    choice: int | None = None
    narration: str | None = None
    summary: str | None = None

    @model_validator(mode="after")
    def one_action(self) -> "TurnInput":
        text = self.text.strip() if self.text is not None else ""
        has_text = bool(text)
        has_choice = self.choice is not None
        if has_text == has_choice:
            raise ValueError("Send a player line or a choice index.")
        if self.choice is not None and self.choice < 0:
            raise ValueError("Choice index must be zero or greater.")
        self.text = text or None
        if self.narration is not None:
            narration = self.narration.strip()
            if not narration:
                raise ValueError("Narration must not be blank.")
            self.narration = narration
        if self.summary is not None:
            summary = self.summary.strip()
            if not summary:
                raise ValueError("Summary must not be blank.")
            self.summary = summary
        return self


class TurnResult(BaseModel):
    payload: TurnPayload
    state: GameState


def opening_payload() -> TurnPayload:
    return TurnPayload(
        narration=(
            "You woke up in the forest. A raven watched from a branch. "
            "You found a path heading north."
        ),
        choices=["Follow the path north", "Look around the clearing"],
        state_delta=StateDelta(
            health=0,
            hunger=0,
            location=None,
            add_items=[],
            remove_items=[],
        ),
        visual_key="forest_clearing",
    )


def starting_state() -> GameState:
    return GameState(
        name="Wanderer",
        health=10,
        health_max=10,
        hunger=3,
        hunger_max=10,
        location="Forest clearing",
        inventory=["Rusty sword", "Heal potion"],
        timeline=[],
        visual_key="forest_clearing",
    )


def create_session() -> SessionStart:
    payload = opening_payload()
    state = apply_turn(starting_state(), payload)
    session_id = str(uuid4())
    SESSIONS[session_id] = StoredSession(state=state, choices=list(payload.choices))
    return SessionStart(id=session_id, payload=payload, state=state)


def complete_turn(state: GameState, action: str) -> TurnPayload:
    """Stand-in reply until llama.cpp is connected. The action is the player line or chosen text."""

    heading_north = action.casefold() == "follow the path north"
    sentence = action[0].lower() + action[1:]
    if not sentence.endswith("."):
        sentence = f"{sentence}."
    return TurnPayload(
        narration=f"You {sentence}",
        choices=["Continue", "Wait"],
        state_delta=StateDelta(
            health=0,
            hunger=1,
            location="North path" if heading_north else None,
            add_items=[],
            remove_items=[],
        ),
        visual_key="forest_path" if heading_north else None,
    )


completion: Completion = complete_turn


def action_from(choices: list[str], turn: TurnInput) -> str:
    if turn.choice is not None:
        try:
            return choices[turn.choice]
        except IndexError:
            raise IndexError("Choice index is out of range.") from None
    assert turn.text is not None
    return turn.text


def take_turn(session_id: str, turn: TurnInput) -> TurnResult:
    stored = SESSIONS.get(session_id)
    if stored is None:
        raise KeyError(session_id)
    action = action_from(stored.choices, turn)
    payload = TurnPayload.model_validate(completion(stored.state, action))
    if turn.narration is not None:
        payload = payload.model_copy(update={"narration": turn.narration})
    state = apply_turn(stored.state, payload)
    entry = turn.summary if turn.summary is not None else payload.narration
    state = state.model_copy(update={"timeline": [*state.timeline, entry]})
    SESSIONS[session_id] = StoredSession(state=state, choices=list(payload.choices))
    return TurnResult(payload=payload, state=state)
