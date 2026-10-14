<script lang="ts">
	import { onMount } from 'svelte';
	import './layout.css';
	import favicon from '#lib/assets/favicon.svg';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();

	onMount(() => {
		void import('#lib/webllm/engine.ts')
			.then(({ preloadModel }) => preloadModel())
			.catch((error) => console.error(error));
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children()}
