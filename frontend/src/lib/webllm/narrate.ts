import type { GameState } from '#lib/session.ts';
import { withEngine } from '#lib/webllm/engine.ts';
import { splitReply, type ToldTurn } from '#lib/webllm/reply.ts';

export type { ToldTurn };

export type TranscriptLine = {
	role: 'player' | 'narration';
	text: string;
};

export async function narrateTurn(
	state: GameState,
	action: string,
	history: TranscriptLine[]
): Promise<ToldTurn> {
	try {
		const text = await withEngine(async (engine) => {
			await engine.resetChat();
			const reply = await engine.chat.completions.create({
				messages: [
					{ role: 'system', content: instructions(state) },
					...history.slice(-6).map((line) => ({
						role: line.role === 'player' ? ('user' as const) : ('assistant' as const),
						content: line.text
					})),
					{ role: 'user', content: action }
				],
				temperature: 0.4,
				max_tokens: 220
			});
			return reply.choices[0]?.message.content ?? '';
		});
		const told = splitReply(text);
		if (!told) {
			throw new Error('The storyteller could not answer.');
		}
		return told;
	} catch (error) {
		if (error instanceof Error && error.message === 'The storyteller could not answer.') {
			throw error;
		}
		throw new Error('The storyteller could not answer.');
	}
}

function instructions(state: GameState): string {
	const carried = state.inventory.join(', ') || 'nothing';
	return [
		`You narrate a text adventure. The player is at ${state.location} and carries ${carried}.`,
		"Write two to four sentences that continue from the player's latest words.",
		'If they ask a question, someone present answers it in quoted speech. Do not repeat the question.',
		'Do not mention health or hunger numbers.'
	].join(' ');
}
