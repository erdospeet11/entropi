import { CreateWebWorkerMLCEngine } from '@mlc-ai/web-llm';

const MODEL_ID = 'Llama-3.2-1B-Instruct-q4f16_1-MLC';

let greeting: Promise<void> | undefined;

export function logGreeting(): Promise<void> {
	greeting ??= runGreeting();
	return greeting;
}

async function runGreeting(): Promise<void> {
	const engine = await CreateWebWorkerMLCEngine(
		new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' }),
		MODEL_ID,
		{
			initProgressCallback: (progress) => {
				console.log(progress.text);
			}
		}
	);

	const reply = await engine.chat.completions.create({
		messages: [{ role: 'user', content: 'Tell me a greeting' }]
	});

	console.log(reply.choices[0]?.message.content);
}
