<script lang="ts">
  import { fetch_ } from "/shared/helper";

  interface Props {
    dares: {
      content: string;
      by: string;
      played: boolean;
      colour: string;
    }[];
    menusState: "closed" | "players" | "dares";
  }
  let { dares, menusState = $bindable("closed") }: Props = $props();

  let daresMenuOpen = $derived(menusState === "dares");

  function removeDare(content: string, by: string) {
    fetch_("/set_used_individual", {
      method: "post",
      body: JSON.stringify({
        content: content,
        by: by,
      }),
    });
  }

  // onMount(() => {
  //   setTimeout(() => {
  //     document
  //       .querySelector("#toggle-players-menu")
  //       ?.addEventListener("click", () => {
  //         daresMenuOpen = false;
  //       });
  //   }, 1);
  // });
</script>

<button
  id="toggle-dares-menu"
  class="{daresMenuOpen
    ? 'fixed'
    : 'absolute'} text-6xl text-gray-200 top-4 right-24 cursor-pointer hover:text-gray-400 z-30"
  aria-label="Manage Players"
  onclick={() =>
    menusState === "dares" ? (menusState = "closed") : (menusState = "dares")}
>
  {#if !daresMenuOpen}
    <ion-icon name="chatbubbles-outline"></ion-icon>
  {:else}
    <ion-icon name="close"></ion-icon>
  {/if}
</button>

{#if daresMenuOpen}
  <div
    class="top-0 right-0 h-screen fixed w-1/2 bg-gray-800 z-20 border-4 shadow-2xl shadow-gray-800 border-l-gray-600 flex flex-col"
  >
    <div class="grow overflow-y-auto mt-20">
      {#each dares as dare}
        <div
          class="flex text-gray-200 text-2xl w-[calc(100%_-_48px)] items-center mx-6 py-2 border-b-2 border-b-gray-600 last-of-type:border-b-0"
        >
          <div class="grow text-center">{dare.content}</div>
          <div>
            <button
              aria-label="Remove player"
              class="hover:text-gray-400 cursor-pointer"
              onclick={() => removeDare(dare.content, dare.by)}
              ><ion-icon name="trash-outline"></ion-icon></button
            >
          </div>
        </div>
      {/each}
    </div>
  </div>
{/if}
