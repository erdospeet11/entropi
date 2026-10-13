export type GameState = {
	name: string;
	health: number;
	health_max: number;
	hunger: number;
	hunger_max: number;
	location: string;
	inventory: string[];
	timeline: string[];
	visual_key: string | null;
};

const API_URL = 'http://127.0.0.1:8000';

export type TurnView = {
	narration: string;
	choices: string[];
	state: GameState;
};

export type StartedGame = TurnView & {
	id: string;
};

type TurnBody = {
	payload: { narration: string; choices: string[] };
	state: GameState;
};

export async function startGame(fetch: typeof globalThis.fetch): Promise<StartedGame> {
	let response: Response;
	try {
		response = await fetch(`${API_URL}/sessions`, { method: 'POST' });
	} catch {
		throw new Error('Could not start a game.');
	}
	if (!response.ok) {
		throw new Error('Could not start a game.');
	}
	const body = (await response.json()) as TurnBody & { id: string };
	return { id: body.id, ...viewFrom(body) };
}

async function turnError(response: Response): Promise<string> {
	try {
		const body = (await response.json()) as { detail?: unknown };
		if (typeof body.detail === 'string' && body.detail.trim()) {
			return body.detail.trim();
		}
	} catch {
		// The failure body was not JSON.
	}
	return 'Could not take a turn.';
}

function viewFrom(body: TurnBody): TurnView {
	return {
		narration: body.payload.narration,
		choices: body.payload.choices,
		state: body.state
	};
}

export async function takeTurn(
	fetch: typeof globalThis.fetch,
	id: string,
	action: { text: string } | { choice: number }
): Promise<TurnView> {
	let response: Response;
	try {
		response = await fetch(`${API_URL}/sessions/${id}/turns`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(action)
		});
	} catch {
		throw new Error('Could not take a turn.');
	}
	if (!response.ok) {
		throw new Error(await turnError(response));
	}
	const body = (await response.json()) as TurnBody;
	return viewFrom(body);
}
