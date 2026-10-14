import { startGame } from '#lib/session.ts';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	try {
		const game = await startGame(fetch);
		return {
			id: game.id,
			narration: game.narration,
			state: game.state,
			loadError: ''
		};
	} catch (error) {
		return {
			id: null,
			narration: '',
			state: null,
			loadError: error instanceof Error ? error.message : 'Could not start a game.'
		};
	}
};
