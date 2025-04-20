<script lang="ts">
  import { onDestroy, onMount } from "svelte";
  import "/shared/tailwindinit.css";
  import { fetch_ } from "/shared/helper";
  import ManagePlayers from "./ManagePlayers.svelte";
  import type { IWheel } from "./Wheel.svelte";
  import Wheel from "./Wheel.svelte";
  import { PersistedState, FiniteStateMachine } from "runed";
  import { getRandomBrightColor } from "./helper";

  let dares: {
    content: string;
    by: string;
    played: boolean;
    colour: string;
  }[] = $state([]);

  let wheelComp: IWheel | undefined = $state();
  let wheelDisabled: boolean = $state(false);

  const round = new PersistedState("round", 1);

  let isSpinning = $state(false);
  let allowRepeats = $state(false);

  let displayDare: string = $state("");
  let displayDareColour: string = $state("");
  let pickedUser: string | undefined = $state();

  let pollInterval: NodeJS.Timeout;
  onMount(() => {
    pollInterval = setInterval(() => {
      if (f.current === "player")
        fetch_("/get_dares")
          .then((resp) => resp.json())
          .then((data: any[]) => {
            for (let i = 0; i < data.length; i++) {
              if (i >= dares.length) data[i]["colour"] = getRandomBrightColor();
              else data[i]["colour"] = dares[i].colour;
            }

            dares = data;
          });
    }, 1000);
  });
  onDestroy(() => {
    clearInterval(pollInterval);
  });

  let choosingPlayer = $state(false);

  function choosePlayer() {
    choosingPlayer = true;
    fetch_("/pick_user")
      .then((resp) => resp.text())
      .then((user) => (pickedUser = user));
    f.debounce(1500, "startdares");
  }

  function startSpin() {
    wheelComp?.spinWheel();
  }

  let finishedTransition = $state(false);
  let choiceType: "forfeit" | "accept" | null = $state(null);
  let choiceMsg: string = $state("");
  function onSpinFinish(selectedDare: {
    content: string;
    by: string;
    played: boolean;
    colour: string;
  }) {
    console.log("Hello world, this wheel has finished spinning.");
    displayDare = selectedDare.content;
    displayDareColour = selectedDare.colour;
    f.debounce(1000, "startchoice");
    setTimeout(() => (finishedTransition = true), 2200);
  }

  const FORFEITS = [
    "Take 1 shot",
    "Take 2 shots",
    "Take 3 shots",
    "Take 4 shots",
  ];

  function pickForfeit() {
    return FORFEITS[Math.floor(Math.random() * FORFEITS.length)];
  }

  type RoundStates = "player" | "dares" | "choice";
  type RoundEvents = "startdares" | "startchoice" | "startplayer";
  const f = new FiniteStateMachine<RoundStates, RoundEvents>("player", {
    player: {
      _enter: () => {
        displayDare = "";
        displayDareColour = "";
        pickedUser = undefined;

        wheelDisabled = true;
        choosingPlayer = false;
        finishedTransition = false;
        choiceType = null;
        choiceMsg = "";
      },
      startdares: "dares",
    },
    dares: {
      _enter: () => {
        wheelDisabled = false;
      },
      startchoice: "choice",
    },
    choice: {
      startplayer: "player",
    },
  });
</script>

<!-- #364153 #6a7282  -->
<!-- <div class="text-gray-600"></div> -->
<!-- <div
  class="fixed w-screen h-screen z-40 transition-colors duration-1000"
  class:hidden={!displayDare}
  style="background-color: {f.current === 'choice'
    ? displayDareColour
    : 'unset'};"
></div> -->
<div
  class="app-container relative flex flex-col items-center justify-center min-h-screen bg-gray-800 overflow-hidden group"
  style="transition: background-color 1s linear; {f.current === 'choice'
    ? `background-color: ${displayDareColour}`
    : ''}"
  class:choice={f.current === "choice"}
>
  <a href="/" class="absolute top-4 left-4 text-gray-200 text-xl underline"
    >← Back to home page</a
  >
  <ManagePlayers />
  <h1 class="text-white text-3xl mb-4">Round {round.current}</h1>

  <span class="flex flex-col items-center">
    <Wheel
      bind:this={wheelComp}
      {dares}
      {onSpinFinish}
      disabled={wheelDisabled}
      bind:isSpinning
    />
  </span>

  <span>
    {#if f.current === "player"}
      <button
        id="choose-player-button"
        class="my-4 transition-all px-4 py-2 rounded-2xl z-10 relative block cursor-pointer disabled:opacity-50 disabled:cursor-wait mb-40 border-8 border-green-500 text-green-500 text-2xl font-bold hover:px-8 ring-green-500/30 hover:ring-8 hover:bg-green-500/30 hover:text-green-400 disabled:pointer-events-none"
        onclick={choosePlayer}
        disabled={choosingPlayer}
      >
        Select the Victim
      </button>
    {:else if f.current === "dares" || f.current === "choice"}
      <button
        id="spin-button"
        class="my-4 bg-green-500 transition-colors hover:bg-green-700 text-white px-4 py-2 rounded z-10 relative block cursor-pointer disabled:opacity-50 disabled:cursor-wait mb-40"
        onclick={startSpin}
        disabled={isSpinning || dares.length < 2}
      >
        Spin the Wheel!!!
      </button>
    {/if}
  </span>
  <div
    id="selected-dare"
    class="text-white px-1 py-2 absolute w-full text-center shadow-[0_0_20px_20px_rgba(0,0,0,0.8)] bg-[rgba(0,0,0,0.8)] text-3xl font-bold drop-shadow-2xl -mt-[230px] transition-all duration-1000 group-[.choice]:shadow-[0_0_20px_20px_rgba(0,0,0,0)] group-[.choice]:bg-[rgba(0,0,0,0)]"
    class:hidden={!pickedUser && !displayDare}
  >
    {#if pickedUser}
      <span
        id="display-user"
        class="[.isLone]:text-red-300 text-gray-200 relative z-50 transition-all duration-1000 group-[.choice]:text-gray-600"
        class:isLone={!displayDare}>{pickedUser}</span
      >
    {/if}
    {#if displayDare}
      <br /><span
        id="display-dare"
        class="relative z-50 transition-all duration-1000 group-[.choice]:!text-gray-700"
        style="color: {displayDareColour};">{displayDare}</span
      >
    {/if}
    <div class="text-center mt-4 absolute w-full">
      {#if finishedTransition}
        {#if choiceType === null}
          <button
            onclick={() => {
              choiceMsg = pickForfeit();
              choiceType = "forfeit";
            }}
            class="cursor-pointer px-8 py-4 text-2xl text-red-700 border-8 rounded-2xl border-red-700 transition-colors hover:bg-red-700/30 hover:text-red-900 mr-8"
            >Forfeit</button
          >
          <button
            onclick={() => {
              choiceType = "accept";
            }}
            class="cursor-pointer px-8 py-4 text-2xl text-green-700 border-8 rounded-2xl border-green-700 transition-colors hover:bg-green-700/30 hover:text-green-900"
            >Accept</button
          >
          <!-- {:else if choiceType === "accept"}
          <span class="text-green-700 text-2xl">We're waiting...</span><button
            class="ml-6 text-2xl underline hover:no-underline text-gray-700 cursor-pointer"
            >We're finished waiting</button
          > -->
        {:else}
          {#if choiceType === "accept"}
            <span class="text-green-700 text-2xl">We're waiting...</span>
          {:else}
            <span class="text-red-700 text-2xl">{choiceMsg}</span>
          {/if}
          <button
            class="ml-6 text-2xl underline hover:no-underline text-gray-700 cursor-pointer"
            onclick={() => {
              f.send("startplayer");
              round.current += 1;
            }}
            >{choiceType === "accept"
              ? "We're finished waiting"
              : "Continue"}</button
          >
        {/if}
      {/if}
    </div>
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

<style>
  :global(.app-container > *:not(#selected-dare)) {
    transition: opacity 1s linear !important;
  }
  :global(.app-container.choice > *:not(#selected-dare)) {
    opacity: 0;
    pointer-events: none;
  }
</style>
