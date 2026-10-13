from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

VISUAL_KEYS = frozenset(
    {
        "forest_clearing",
        "forest_path",
        "forest_night",
        "tavern_interior",
    }
)


def clamp(value: int, upper: int) -> int:
    return min(max(value, 0), max(upper, 0))


def known_visual_key(value: object) -> object:
    """Keep a listed picture key. Drop anything else, including a blank string."""

    if value is None:
        return None
    if not isinstance(value, str):
        return value
    key = value.strip()
    if key in VISUAL_KEYS:
        return key
    return None


class StateDelta(BaseModel):
    """Stat and inventory changes for one turn. Zero and empty values mean no change."""

    model_config = ConfigDict(extra="forbid")

    health: int = Field(description="Added to health. Negative values subtract.")
    hunger: int = Field(description="Added to hunger. Negative values subtract.")
    location: str | None = Field(description="New location, or null when it stays the same.")
    add_items: list[str] = Field(description="Item names gained this turn.")
    remove_items: list[str] = Field(description="Item names lost this turn.")

    @field_validator("location")
    @classmethod
    def location_is_null_or_named(cls, value: str | None) -> str | None:
        if value is None:
            return None
        named = value.strip()
        if not named:
            raise ValueError("location must be a name or null")
        return named

    @field_validator("add_items", "remove_items")
    @classmethod
    def item_names_are_present(cls, value: list[str]) -> list[str]:
        names: list[str] = []
        for item in value:
            name = item.strip()
            if not name:
                raise ValueError("item name must not be empty")
            names.append(name)
        return names


class TurnPayload(BaseModel):
    """One model reply: the scene, the next actions, the state change, and the picture key."""

    model_config = ConfigDict(extra="forbid")

    narration: str = Field(min_length=1)
    choices: list[str] = Field(min_length=2, max_length=3)
    state_delta: StateDelta
    visual_key: str | None = Field(description="A known picture key, or null when the key is unknown.")

    @field_validator("narration")
    @classmethod
    def text_is_present(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("must not be blank")
        return text

    @field_validator("visual_key", mode="before")
    @classmethod
    def ignore_unknown_visual_key(cls, value: object) -> object:
        return known_visual_key(value)

    @field_validator("choices")
    @classmethod
    def choices_are_present(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for choice in value:
            text = choice.strip()
            if not text:
                raise ValueError("choice must not be blank")
            cleaned.append(text)
        return cleaned


class GameState(BaseModel):
    """Stats the page shows. Health and hunger always sit between zero and their max."""

    model_config = ConfigDict(extra="forbid")

    name: str = "Wanderer"
    health: int
    health_max: int = Field(ge=0)
    hunger: int
    hunger_max: int = Field(ge=0)
    location: str = Field(min_length=1)
    inventory: list[str] = Field(default_factory=list)
    timeline: list[str] = Field(default_factory=list)
    visual_key: str | None = None

    @field_validator("visual_key", mode="before")
    @classmethod
    def ignore_unknown_visual_key(cls, value: object) -> object:
        return known_visual_key(value)

    @model_validator(mode="after")
    def clamp_health_and_hunger(self) -> "GameState":
        self.health = clamp(self.health, self.health_max)
        self.hunger = clamp(self.hunger, self.hunger_max)
        return self


def apply_turn(state: GameState, turn: TurnPayload) -> GameState:
    """Apply a validated turn. Unknown picture keys leave the current key in place."""

    delta = turn.state_delta
    inventory = list(state.inventory)
    for item in delta.add_items:
        inventory.append(item)
    for item in delta.remove_items:
        if item in inventory:
            inventory.remove(item)

    return GameState(
        name=state.name,
        health=state.health + delta.health,
        health_max=state.health_max,
        hunger=state.hunger + delta.hunger,
        hunger_max=state.hunger_max,
        location=delta.location if delta.location is not None else state.location,
        inventory=inventory,
        timeline=list(state.timeline),
        visual_key=turn.visual_key if turn.visual_key is not None else state.visual_key,
    )
