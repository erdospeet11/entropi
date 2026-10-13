<script lang="ts">
	import { takeTurn, type GameState } from '#lib/session.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let state = $state<GameState | null>(data.state);
	let narration = $state(data.narration);
	let choices = $state(data.choices);
	let line = $state('');
	let sending = $state(false);
	let turnError = $state('');

	async function send(action: { text: string } | { choice: number }) {
		if (sending || !data.id) return;
		if ('text' in action && !action.text.trim()) return;
		sending = true;
		turnError = '';
		try {
			const turn = await takeTurn(fetch, data.id, action);
			state = turn.state;
			narration = turn.narration;
			choices = turn.choices;
			if ('text' in action) line = '';
		} catch (error) {
			turnError = error instanceof Error ? error.message : 'Could not take a turn.';
		} finally {
			sending = false;
		}
	}

	function onKeydown(event: KeyboardEvent) {
		if (event.key !== 'Enter') return;
		event.preventDefault();
		const field = event.currentTarget;
		if (field instanceof HTMLInputElement) void send({ text: field.value });
	}

	function submit(event: SubmitEvent) {
		event.preventDefault();
		const form = event.currentTarget;
		if (!(form instanceof HTMLFormElement)) return;
		const field = form.elements.namedItem('line');
		void send({ text: field instanceof HTMLInputElement ? field.value : line });
	}
</script>

<div class="grid h-screen grid-cols-[3fr_4fr_3fr]">
	<aside class="p-4">
		<h2>Player</h2>
		{#if state}
			<p>Name: {state.name}</p>
			<p>Health: {state.health} / {state.health_max}</p>
			<p>Hunger: {state.hunger} / {state.hunger_max}</p>
			<p>Location: {state.location}</p>

			<h2>Inventory</h2>
			{#each state.inventory as item, index (index)}
				<p>{item}</p>
			{/each}
		{:else}
			<p>{data.loadError}</p>
		{/if}
	</aside>

	<main class="my-16 border-x border-black p-4">
		{#if narration}
			<p>{narration}</p>
		{/if}
		{#if turnError}
			<p>{turnError}</p>
		{/if}
		<div class="mt-4 flex flex-col items-start gap-2">
			{#each choices as choice, index (index)}
				<button
					class="svelte-button"
					type="button"
					disabled={sending || !data.id}
					onclick={() => send({ choice: index })}
				>
					{choice}
				</button>
			{/each}
		</div>
	</main>

	<aside class="p-4">
		<h2>Timeline</h2>
		{#if state}
			<ul>
				{#each state.timeline as entry, index (index)}
					<li>{entry}</li>
				{/each}
			</ul>
		{/if}
	</aside>
</div>

<form class="fixed bottom-0 left-1/2 flex -translate-x-1/2 items-end" onsubmit={submit}>
	<input
		class="h-50 w-100"
		name="line"
		type="text"
		bind:value={line}
		disabled={sending || !data.id}
		onkeydown={onKeydown}
	/>
	<button class="h-10 svelte-button" type="submit" disabled={sending || !data.id}>button</button>
</form>

<style>
	.svelte-button {
		border: 1px solid black;
		border-radius: 4px;
		padding: 4px 8px;
	}
</style>
