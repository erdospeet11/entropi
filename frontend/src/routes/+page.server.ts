import { startGame } from '#lib/session.ts';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	try {
		const game = await startGame(fetch);
		return {
			id: game.id,
			narration: game.narration,
			choices: game.choices,
			state: game.state,
			loadError: ''
		};
	} catch (error) {
		return {
			id: null,
			narration: '',
			choices: [],
			state: null,
			loadError: error instanceof Error ? error.message : 'Could not start a game.'
		};
	}
};
