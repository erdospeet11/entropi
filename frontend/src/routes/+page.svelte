<div class="grid h-screen grid-cols-[3fr_4fr_3fr]">
	<aside class="p-4">
		<h2>Player</h2>
		<p>Name: Wanderer</p>
		<p>Health: 10 / 10</p>
		<p>Hunger: 3 / 10</p>
		<p>Location: Forest clearing</p>

		<h2>Inventory</h2>
		<p>Rusty lantern</p>
		<p>Pocket knife</p>
		<p>2 coins</p>
	</aside>

	<main class="my-16 border-x border-black p-4"></main>

	<aside class="p-4">
		<h2>Timeline</h2>
		<ul>
			<li>You woke up in the forest</li>
			<li>A raven watched from a branch</li>
			<li>You found a path heading north</li>
		</ul>
	</aside>
</div>

<form class="fixed bottom-0 left-1/2 flex -translate-x-1/2 items-end">
	<input class="h-50 w-100" type="text" />
	<button class="h-10 svelte-button">button</button>
</form>

<style>
	.svelte-button {
		border: 1px solid black;
		border-radius: 4px;
		padding: 4px 8px;
	}
</style>
