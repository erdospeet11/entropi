import { expect, it } from 'vitest';
import { splitReply } from './reply';

it('keeps a short summary and the scene apart', () => {
	const told = splitReply(
		'You found bitter berries.\n\nYou kneel by the ferns and find a handful of bitter berries. They stain your fingers.'
	);

	expect(told).toEqual({
		summary: 'You found bitter berries.',
		narration:
			'You kneel by the ferns and find a handful of bitter berries. They stain your fingers.'
	});
});

it('keeps a long summary to its first short clause', () => {
	const told = splitReply(
		'You scan the surrounding area, your eyes adjusting to the dim light of the forest as you search.\n\nYou kneel and find berries.'
	);

	expect(told?.summary).toBe('You scan the surrounding area.');
	expect(told?.narration).toBe('You kneel and find berries.');
});

it('uses the first sentence when the reply is one block', () => {
	const told = splitReply('You find berries. The raven watches.');

	expect(told?.summary).toBe('You find berries.');
	expect(told?.narration).toBe('You find berries. The raven watches.');
});
