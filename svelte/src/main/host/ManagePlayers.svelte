<script module lang="ts">
  export interface IManagePlayers {
    resetPlayers(): void;
  }
</script>

<script lang="ts">
  import { onMount } from "svelte";
  import { fetch_ } from "/shared/helper";

  console.log("hello world!");

  interface Props {
    menusState: "closed" | "players" | "dares";
  }
  let { menusState = $bindable("closed") }: Props = $props();

  let playersMenuOpen = $derived(menusState === "players");
  let players: string[] = $state([]);

  let playerNameInput = $state("");
  let playerInputError: null | string = $state(null);

  function addPlayer(e: SubmitEvent) {
    e.preventDefault();
    console.log("added plauer");
    playerInputError = null;
    fetch_("/add_user", {
      method: "post",
      body: playerNameInput,
      headers: { "Content-Type": "text/plain" },
    }).then(async (resp) => {
      if (!resp.ok) {
        playerInputError = await resp.text();
      } else {
        players.push(playerNameInput);
        playerNameInput = "";
      }
      // console.log(resp.status, resp.ok);
    });
  }

  function removePlayer(name: string) {
    fetch_("/remove_user", {
      method: "post",
      body: name,
      headers: { "Content-Type": "text/plain" },
    }).then((resp) => {
      if (resp.ok) {
        const index = players.indexOf(name);
        if (index !== -1) players.splice(index, 1);
      }
    });
  }

  export function resetPlayers() {
    fetch_("/remove_all_users", { method: "post" }).then((resp) => {
      if (!resp.ok) return;
      players = [];
    });
  }

  onMount(() => {
    fetch_("/get_users")
      .then((resp) => resp.json())
      .then((data) => (players = data));

    // setTimeout(() => {
    //   document
    //     .querySelector("#toggle-dares-menu")
    //     ?.addEventListener("click", () => {
    //       playersMenuOpen = false;
    //     });
    // }, 1);
  });
</script>

<button
  id="toggle-players-menu"
  class="{playersMenuOpen
    ? 'fixed'
    : 'absolute'} text-6xl text-gray-200 top-4 right-4 cursor-pointer hover:text-gray-400 z-30"
  aria-label="Manage Players"
  onclick={() =>
    menusState === "players"
      ? (menusState = "closed")
      : (menusState = "players")}
>
  {#if !playersMenuOpen}
    <ion-icon name="people-outline"></ion-icon>
  {:else}
    <ion-icon name="close"></ion-icon>
  {/if}
</button>

{#if playersMenuOpen}
  <div
    class="top-0 right-0 h-screen fixed w-1/2 bg-gray-800 z-20 border-4 shadow-2xl shadow-gray-800 border-l-gray-600 flex flex-col"
  >
    <div class="grow overflow-y-auto mt-20">
      {#each players as player}
        <div
          class="flex text-gray-200 text-2xl w-[calc(100%_-_48px)] items-center mx-6 py-2 border-b-2 border-b-gray-600 last-of-type:border-b-0"
        >
          <div class="grow text-center">{player}</div>
          <div>
            <button
              aria-label="Remove player"
              class="hover:text-gray-400 cursor-pointer"
              onclick={() => removePlayer(player)}
              ><ion-icon name="trash-outline"></ion-icon></button
            >
          </div>
        </div>
      {/each}
    </div>
    <form
      class="p-6 flex items-center justify-center relative"
      onsubmit={addPlayer}
      method="post"
    >
      {#if playerInputError !== null}
        <div class="text-red-500 absolute left-6 -top-1">
          {playerInputError}
        </div>
      {/if}
      <input
        type="text"
        class="w-full border-4 border-green-500 rounded-xl text-3xl text-gray-200 outline-none px-6 py-3 focus:ring-8 ring-green-500/30 [&.error]:border-red-500 [&.error]:ring-red-500/30"
        class:error={playerInputError !== null}
        bind:value={playerNameInput}
      />
      <button
        type="submit"
        class="ml-4 h-full border-4 border-green-500 rounded-xl aspect-square text-5xl text-green-500 cursor-pointer hover:bg-green-500/30"
        aria-label="Add player"><ion-icon name="add"></ion-icon></button
      >
    </form>
  </div>
{/if}
