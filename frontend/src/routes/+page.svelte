<script lang="ts">
	import { takeTurn, type GameState } from '#lib/session.ts';
	import { narrateTurn } from '#lib/webllm/narrate.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	type TranscriptLine = {
		role: 'player' | 'narration';
		text: string;
	};

	let game: GameState | null = $state(data.state);
	let messages: TranscriptLine[] = $state(
		data.narration ? [{ role: 'narration', text: data.narration }] : []
	);
	let line = $state('');
	let sending = $state(false);
	let turnError = $state('');
	let thread: HTMLElement | null = $state(null);

	$effect(() => {
		messages;
		turnError;
		thread?.scrollTo({ top: thread.scrollHeight });
	});

	async function send(raw: string) {
		const said = raw.trim();
		if (!said || sending || !data.id) return;
		if (!game) return;
		const prior = messages;
		messages = [...messages, { role: 'player', text: said }];
		sending = true;
		turnError = '';
		try {
			const told = await narrateTurn(game, said, prior);
			const turn = await takeTurn(fetch, data.id, {
				text: said,
				narration: told.narration,
				summary: told.summary
			});
			game = turn.state;
			messages = [...messages, { role: 'narration', text: turn.narration }];
			line = '';
		} catch (error) {
			messages = prior;
			turnError = error instanceof Error ? error.message : 'Could not take a turn.';
		} finally {
			sending = false;
		}
	}

	function onKeydown(event: KeyboardEvent) {
		if (event.key !== 'Enter') return;
		event.preventDefault();
		const field = event.currentTarget;
		if (field instanceof HTMLInputElement) void send(field.value);
	}

	function submit(event: SubmitEvent) {
		event.preventDefault();
		const form = event.currentTarget;
		if (!(form instanceof HTMLFormElement)) return;
		const field = form.elements.namedItem('line');
		void send(field instanceof HTMLInputElement ? field.value : line);
	}
</script>

<div class="grid h-screen min-h-0 grid-cols-[16rem_minmax(0,1fr)_16rem]">
	<aside class="min-h-0 overflow-y-auto p-4">
		<h2>Player</h2>
		{#if game}
			<p>Name: {game.name}</p>
			<p>Health: {game.health} / {game.health_max}</p>
			<p>Hunger: {game.hunger} / {game.hunger_max}</p>
			<p>Location: {game.location}</p>

			<h2>Inventory</h2>
			{#each game.inventory as item, index (index)}
				<p>{item}</p>
			{/each}
		{:else}
			<p>{data.loadError}</p>
		{/if}
	</aside>

	<main class="flex min-h-0 flex-col border-x border-black">
		<div class="thread" bind:this={thread}>
			{#each messages as message, index (index)}
				{#if message.role === 'player'}
					<p class="player-line">{message.text}</p>
				{:else}
					<p class="narration-line">{message.text}</p>
				{/if}
			{/each}
			{#if sending}
				<p class="narration-line">Answering…</p>
			{/if}
			{#if turnError}
				<p class="text-center">{turnError}</p>
			{/if}
		</div>

		<form class="flex items-end gap-2 border-t border-black p-4" onsubmit={submit}>
			<input
				class="h-24 min-w-0 flex-1"
				name="line"
				type="text"
				bind:value={line}
				disabled={sending || !data.id}
				onkeydown={onKeydown}
			/>
			<button class="h-10 svelte-button" type="submit" disabled={sending || !data.id}>button</button>
		</form>
	</main>

	<aside class="min-h-0 overflow-y-auto p-4">
		<h2>Timeline</h2>
		{#if game}
			<ul>
				{#each game.timeline as entry, index (index)}
					<li>{entry}</li>
				{/each}
			</ul>
		{/if}
	</aside>
</div>

<style>
	.thread {
		display: flex;
		min-height: 0;
		flex: 1;
		flex-direction: column;
		gap: 1rem;
		overflow-y: auto;
		padding: 1rem;
	}

	.player-line {
		align-self: flex-end;
		max-width: 70%;
		border: 1px solid black;
		border-radius: 1.25rem;
		background: #f3f3f3;
		padding: 0.5rem 1rem;
	}

	.narration-line {
		align-self: center;
		width: min(100%, 40rem);
		border: 1px solid black;
		padding: 0.75rem 1rem;
	}

	.svelte-button {
		border: 1px solid black;
		border-radius: 4px;
		padding: 4px 8px;
	}
</style>
