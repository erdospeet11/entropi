from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sessions import SessionStart, TurnInput, TurnResult, create_session, take_turn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/sessions", status_code=201)
def start_session() -> SessionStart:
    return create_session()


@app.post("/sessions/{id}/turns")
def post_turn(id: str, turn: TurnInput) -> TurnResult:
    try:
        return take_turn(id, turn)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found.") from None
    except IndexError as error:
        raise HTTPException(status_code=422, detail=str(error)) from None
