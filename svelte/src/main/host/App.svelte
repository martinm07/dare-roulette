<script lang="ts">
  import { onDestroy, onMount } from "svelte";
  import "/shared/tailwindinit.css";
  import { fetch_ } from "/shared/helper";
  import ManagePlayers from "./ManagePlayers.svelte";
  import type { IWheel } from "./Wheel.svelte";
  import Wheel from "./Wheel.svelte";

  let dares: { content: string; by: string; played: boolean }[] = $state([]);
  // $inspect(dares);
  //   "Do 10 push-ups",
  //   "Sing a song of your choice",
  //   "Dance for 1 minute",
  //   "Tell a joke",
  //   "Do an impression of someone",
  //   "Share an embarrassing story",
  //   "Eat a spoonful of mustard",
  //   "Let someone else style your hair",
  //   "Do a cartwheel",
  //   "Speak in an accent for the next 3 rounds",
  // ]);

  let isSpinning = $state(false);
  let allowRepeats = $state(false);

  let displayDare: string = $state("");
  let pickedUser: string | undefined = $state();

  let pollInterval: NodeJS.Timeout;
  onMount(() => {
    pollInterval = setInterval(() => {
      fetch_("/get_dares")
        .then((resp) => resp.json())
        .then((data) => {
          dares = data;
        });
    }, 1000);
  });
  onDestroy(() => {
    clearInterval(pollInterval);
  });

  let wheelComp: IWheel | undefined = $state();

  function startSpin() {
    wheelComp?.spinWheel();
    fetch_("/pick_user")
      .then((resp) => resp.text())
      .then((user) => (pickedUser = user));
  }

  function onSpinFinish(selectedDare: {
    content: string;
    by: string;
    played: boolean;
  }) {
    console.log("Hello world, this wheel has finished spinning.");
    displayDare = selectedDare.content;
  }
</script>

<div
  class="relative flex flex-col items-center justify-center min-h-screen bg-gray-800 overflow-hidden"
>
  <a href="/" class="absolute top-4 left-4 text-gray-200 text-xl underline"
    >← Back to home page</a
  >
  <ManagePlayers />
  <h1 class="text-white text-3xl mb-4">Dare Roulette</h1>

  <Wheel bind:this={wheelComp} {dares} {onSpinFinish} bind:isSpinning />

  <button
    id="spin-button"
    class="my-4 bg-green-500 transition-colors hover:bg-green-700 text-white px-4 py-2 rounded z-10 relative block cursor-pointer disabled:opacity-50 disabled:cursor-wait mb-40"
    onclick={startSpin}
    disabled={isSpinning || dares.length < 2}
  >
    Spin the Wheel
  </button>
  <div
    id="selected-dare"
    class="text-white px-1 py-2 absolute w-full text-center shadow-[0_0_20px_20px_rgba(0,0,0,0.8)] bg-[rgba(0,0,0,0.8)] text-3xl font-bold drop-shadow-2xl"
    class:hidden={isSpinning || !displayDare || dares.length < 2}
  >
    <span class="text-red-300">{pickedUser}</span><br />
    {displayDare}
  </div>
  <div class="absolute text-gray-400 text-7xl" class:hidden={dares.length >= 2}>
    Waiting for submissions...
  </div>

  <div class="absolute right-5 bottom-5 text-2xl">
    <div>
      <label for="allow-repeats" class="text-gray-200">Allow Repeats?</label>
      <input
        class="w-10 h-5"
        type="checkbox"
        name="allow-repeats"
        id="allow-repeats"
        bind:checked={allowRepeats}
      />
    </div>
    <div class="mt-8">
      <button
        onclick={wheelComp.resetWheel}
        class="bg-none boder-gray-200 border-2 rounded-xl px-6 py-3 text-gray-200 underline hover:no-underline cursor-pointer"
        >Reset Wheel</button
      >
    </div>
  </div>
</div>
