import { withEngine } from '#lib/webllm/engine.ts';

let greeting: Promise<void> | undefined;

export function logGreeting(): Promise<void> {
	greeting ??= withEngine(async (engine) => {
		await engine.resetChat();
		const reply = await engine.chat.completions.create({
			messages: [{ role: 'user', content: 'Tell me a greeting' }],
			max_tokens: 60
		});
		console.log(reply.choices[0]?.message.content);
	});
	return greeting;
}
