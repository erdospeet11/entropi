# TODO

Build the playable loop first. Infrastructure, retrieval, and the fine-tune sit on top of a turn that already updates the page.

The README lists pairs of tools (FastAPI or Go, vLLM or llama.cpp, ChromaDB or LanceDB). Pick one of each pair when that section starts. The code already uses FastAPI and in-browser WebLLM.

## Already in the repo

- [x] SvelteKit page shell in `frontend/src/routes/+page.svelte` (player column, empty story column, timeline, text box)
- [x] WebLLM loads `Llama-3.2-1B-Instruct-q4f16_1-MLC` and logs one greeting (`frontend/src/lib/webllm/greeting.ts`)
- [x] FastAPI `GET /` health check and Vite CORS (`backend/app.py`)
- [x] Genre notes in `prompts/genres/*.json` (tone, settings, required and forbidden elements)
- [x] `./dev.sh` starts the API on port 8000 and the site on port 5173



## 1. Game state

Replace the hardcoded sidebar and timeline with one state object the UI and the model both use.

- [ ] Define the state shape: name, health, health max, hunger, hunger max, location, inventory items, timeline entries, selected genre, visual key
- [ ] Hold that state in the page (or a small store) and render the player column, inventory, and timeline from it
- [ ] Seed a new game from defaults (the current Wanderer / forest values are fine as the seed)
- [ ] Add start-over so a session can reset without a refresh



## 2. One playable turn

The center column and the bottom form are the game. The greeting in the console is not.

- [ ] Bind the form. Submit on button click and on Enter. Ignore empty input.
- [ ] Disable the form while a turn is running, then clear the input
- [ ] Show the player's action and the model's narration in the center column, newest beat visible
- [ ] Append a short line to the timeline for each accepted turn
- [ ] Show the model's choices as buttons. A click submits that choice the same way typed text does
- [ ] Surface a visible error when the model call fails, and leave the previous state unchanged



## 3. Response contract

Every model reply is data, not only prose.

- [ ] Define the payload: `narration` (string), `choices` (short list of strings), `state_delta`, `visual_key`
- [ ] `state_delta` fields: health change, hunger change, location (omit if unchanged), items added, items removed
- [ ] Tell the model to return only that payload, as JSON
- [ ] Parse the reply and validate types and ranges before touching state
- [ ] On invalid JSON or a failed check, retry once with the same turn. If it fails again, show the error and do not apply a delta
- [ ] Apply a valid delta to health, hunger, location, and inventory, and clamp health and hunger to their max
- [ ] Drop unknown `visual_key` values instead of crashing the turn



## 4. Prompt and memory

Keep the prompt small. The 1B model is already the one loaded in the browser.

- [ ] System prompt: you are the narrator, you return only the JSON contract, you do not invent stats the delta did not change
- [ ] Include the current state summary and the selected genre block on every turn
- [ ] Send the player action plus a short tail of recent narration (a fixed turn cap, not the full session)
- [ ] Cap `max_tokens` so a turn stays a short scene plus choices
- [ ] Move the call out of `logGreeting()`. The layout should start a game turn, not a one-off greeting
- [ ] Log the raw reply in the console only as a debug aid. The page shows the parsed narration



## 5. Genre modules

`prompts/genres/*.json` is reference material. The runtime needs to load it and ask the player which one to use.

- [ ] Load the genre files from the frontend (or from the API once the backend owns the prompt)
- [ ] Build a system-prompt section from `tone_guidelines`, `must_include.required_elements`, and `must_include.forbidden_elements`
- [ ] Use `typical_settings` and `protagonist_archetypes` for the opening scene only
- [ ] Add a genre picker before the first turn. Default is fine; the player can switch only by starting over
- [ ] Opening turn: no player text yet. Ask the model for the first scene in that genre, then unlock the form



## 6. Canon and retrieval

Fixed facts should enter the prompt from storage, not from the model's memory.

- [ ] Write a small canon set per genre: place names, factions, and rules the narrator must not contradict. Keep it separate from the style notes in `prompts/genres/`
- [ ] Pick one store: ChromaDB or LanceDB
- [ ] Embed those canon entries and query them on each turn with the player action plus current location
- [ ] Inject only the top matches into the prompt, each with a stable id
- [ ] Same query text returns the same entries (fixed embedding and ranking, no random tie-break)
- [ ] Add a `canon_ids` field on the response for the entries the turn actually used, so a bad reply can be checked against the injected set



## 7. Visuals

The model names a picture. The client draws it. The model does not describe pixels.

- [ ] Freeze a list of `visual_key` values (location and mood, for example `forest_night`, `tavern_interior`)
- [ ] Put that list in the system prompt so the model can only pick from it
- [ ] Add an asset for each key and swap the center-column background when `visual_key` changes
- [ ] Add a theme per genre: palette and type style on the page shell
- [ ] Add overlay shaders that themes can turn on: scanlines, film grain, vignette
- [ ] Keep the story text readable on top of the background and the overlays



## 8. Backend owns the turn

`backend/app.py` is a health check. The browser currently talks to WebLLM directly, which matches `./dev.sh` and the README note that the API does not run the model. Move orchestration to the API when a turn needs canon lookup or a server-side model.

- [ ] `POST /sessions` creates a game, stores state, and returns the opening turn
- [ ] `POST /sessions/{id}/turns` accepts the player text or a choice index, runs retrieval, calls the model, applies the delta, and returns the new state plus narration and choices
- [ ] `GET /sessions/{id}` returns the current state for a refresh
- [ ] Validate the request body with Pydantic. Reject an empty action and an unknown session
- [ ] Point the Svelte form at these routes. Leave WebLLM in place only if you explicitly keep inference in the browser; then the API still assembles the prompt and the browser only runs the completion



## 9. Server inference

Do this after the turn API works against the browser model, or behind a fake completion you can test without weights.

- [ ] Pick the runner: vLLM or llama.cpp with a GGUF of a 1B–3B instruct model
- [ ] Serve it beside the API and have the turn route call it with the assembled prompt and the JSON contract
- [ ] Set a low max token count and a stop sequence at the end of the JSON object
- [ ] Time a turn locally and record it. The target is a reply the page can show without a long wait



## 10. Fine-tune and LoRA

The stock instruct model will miss the JSON contract often. Training is how the contract becomes reliable.

- [ ] Build a dataset of turns: genre, state summary, recent narration, player action, canon snippets, and a gold JSON reply
- [ ] Cover every genre file, including short actions and actions that must not change state
- [ ] Fine-tune the base model for that contract and for staying inside a small token budget
- [ ] Score held-out turns on: valid JSON, delta matches the narration, required genre elements present, forbidden elements absent
- [ ] Train one LoRA per genre for tone, and load the matching adapter when the session genre is set
- [ ] Ship the base weights and the adapters the same way as the runner (GGUF or the vLLM adapter path). They do not belong in git



## 11. Tests

Replace the Svelte starter examples with tests of the game.

- [ ] Unit-test the parser: valid payload, missing fields, extra prose around JSON, out-of-range health
- [ ] Unit-test delta application: add and remove inventory, clamp health and hunger, ignore an unknown visual key
- [ ] API tests for create session, submit a turn, and reject an unknown session
- [ ] Browser test: pick a genre, read the opening narration, submit a command, see the timeline and a stat change



## 12. Deploy

Start this only after a turn works on your machine.

- [ ] Dockerfile for the API and, if used, the inference service and the vector store
- [ ] CI workflow: frontend check and unit tests, backend tests, on push
- [ ] Terraform for the host you actually deploy to, plus secrets for model weights kept outside the image
- [ ] A Go orchestrator only if FastAPI is no longer the process that owns the turn