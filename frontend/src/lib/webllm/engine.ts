import {
	CreateWebWorkerMLCEngine,
	type MLCEngineInterface
} from '@mlc-ai/web-llm';

const MODEL_ID = 'Llama-3.2-1B-Instruct-q4f16_1-MLC';

export type ModelLoad = {
	ready: boolean;
	progress: number;
	text: string;
	error: string;
};

let load: ModelLoad = {
	ready: false,
	progress: 0,
	text: 'Loading the storyteller…',
	error: ''
};
const listeners = new Set<(next: ModelLoad) => void>();
let enginePromise: Promise<MLCEngineInterface> | undefined;
let queue: Promise<unknown> = Promise.resolve();

function publish(next: ModelLoad) {
	load = next;
	for (const listener of listeners) listener(load);
}

export function watchModelLoad(listener: (next: ModelLoad) => void): () => void {
	listener(load);
	listeners.add(listener);
	return () => listeners.delete(listener);
}

function engine(): Promise<MLCEngineInterface> {
	enginePromise ??= CreateWebWorkerMLCEngine(
		new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' }),
		MODEL_ID,
		{
			initProgressCallback: (report) => {
				publish({
					ready: false,
					progress: report.progress,
					text: report.text || 'Loading the storyteller…',
					error: ''
				});
			}
		}
	).then(
		(ready) => {
			publish({ ready: true, progress: 1, text: '', error: '' });
			return ready;
		},
		(error: unknown) => {
			publish({
				ready: false,
				progress: load.progress,
				text: load.text,
				error: error instanceof Error ? error.message : 'The storyteller could not load.'
			});
			throw error;
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
