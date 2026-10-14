export type ToldTurn = {
	narration: string;
	summary: string;
};

export function splitReply(text: string): ToldTurn | null {
	const trimmed = text.trim();
	if (!trimmed) return null;
	const [head, ...rest] = trimmed.split(/\n\s*\n/);
	const narration = rest.join('\n\n').trim();
	if (narration) {
		return { summary: brief(head), narration };
	}
	const sentence = trimmed.split(/(?<=[.!?])\s/)[0] ?? trimmed;
	return { summary: brief(sentence), narration: trimmed };
}

function brief(line: string): string {
	const sentence = line.replace(/\s+/g, ' ').trim();
	const clause = sentence.split(/[.!?,]/)[0]?.trim() || sentence;
	const words = clause.split(' ').filter(Boolean).slice(0, 12);
	const short = words.join(' ');
	return /[.!?]$/.test(short) ? short : `${short}.`;
}
