import {
	CreateWebWorkerMLCEngine,
	type MLCEngineInterface
} from '@mlc-ai/web-llm';

const MODEL_ID = 'Llama-3.2-1B-Instruct-q4f16_1-MLC';

let enginePromise: Promise<MLCEngineInterface> | undefined;
let queue: Promise<unknown> = Promise.resolve();

function engine(): Promise<MLCEngineInterface> {
	enginePromise ??= CreateWebWorkerMLCEngine(
		new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' }),
		MODEL_ID,
		{
			initProgressCallback: (progress) => {
				console.log(progress.text);
			}
		}
	);
	return enginePromise;
}

export function withEngine<T>(run: (engine: MLCEngineInterface) => Promise<T>): Promise<T> {
	const next = queue.then(() => engine()).then(run);
	queue = next.then(
		() => undefined,
		() => undefined
	);
	return next;
}

export function preloadModel(): Promise<void> {
	return withEngine(async () => undefined);
}
