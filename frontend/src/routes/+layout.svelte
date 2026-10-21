<script lang="ts">
	import { onMount } from 'svelte';
	import './layout.css';
	import favicon from '#lib/assets/favicon.svg';
	import type { ModelLoad } from '#lib/webllm/engine.ts';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();

	let model: ModelLoad = $state({
		ready: false,
		progress: 0,
		text: 'Loading the storyteller…',
		error: ''
	});

	onMount(() => {
		let stop = () => {};
		void import('#lib/webllm/engine.ts')
			.then(({ preloadModel, watchModelLoad }) => {
				stop = watchModelLoad((next) => {
					model = next;
				});
				return preloadModel();
			})
			.catch((error) => console.error(error));
		return () => stop();
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div inert={!model.ready || undefined}>
	{@render children()}
</div>

{#if !model.ready}
	<div class="load-screen" role="dialog" aria-modal="true" aria-labelledby="model-load-title">
		<div class="load-card">
			<h2 id="model-load-title">Loading the storyteller</h2>
			{#if model.error}
				<p>{model.error}</p>
			{:else}
				<p>{model.text}</p>
				<p>{Math.round(model.progress * 100)}%</p>
			{/if}
		</div>
	</div>
{/if}

<style>
	.load-screen {
		position: fixed;
		inset: 0;
		z-index: 50;
		display: flex;
		align-items: center;
		justify-content: center;
		background: rgb(0 0 0 / 40%);
	}

	.load-card {
		width: min(100% - 2rem, 28rem);
		border: 1px solid black;
		background: white;
		padding: 1.5rem;
	}
</style>
