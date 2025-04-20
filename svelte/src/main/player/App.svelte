<script lang="ts">
  import "/shared/tailwindinit.css";
  import { fetch_ } from "/shared/helper";
  import { watch, PersistedState } from "runed";

  let content = $state("");
  let error: string | null = $state(null);

  const history = new PersistedState<string[]>("daresHistory", []);

  watch(
    () => content,
    () => {
      // // Remove newlines
      // if (content.includes("\n")) {
      //   content = content.replace("\n", "");
      //   return;
      // }
      if (!textareaEl) return;
      textareaEl.style.height = "0px";
      textareaEl.style.height = textareaEl.scrollHeight + "px";
    }
  );

  let textareaEl: HTMLTextAreaElement | undefined = $state();

  // TODO: Error for when dare str length exceeds 256
  //  (dont wanna turn it into server db error, deal with it locally)
  function onSubmit(e: SubmitEvent) {
    e.preventDefault();
    error = null;
    console.log("hello world!");
    fetch_("/add_dare", {
      method: "post",
      body: JSON.stringify({ content }),
    }).then(async (resp) => {
      if (!resp.ok) {
        error = await resp.text();
      } else {
        history.current = [...history.current, content];
        content = "";
      }
      // console.log(resp.status, resp.ok);
    });
  }

  // function getDares() {
  //   fetch_("/get_dares")
  //     .then((resp) => resp.json())
  //     .then((data) => console.log(data));
  // }

  function maskText(text: string) {
    return text.replace(/[^\s]/g, "—");
  }
</script>

<div class="flex flex-col items-center min-h-screen bg-gray-800">
  <a href="/" class="absolute top-4 left-4 text-gray-200 text-xl underline"
    >← Back to home page</a
  >
  <div class="text-gray-200 px-8 mt-20 h-[50vh] overflow-y-scroll w-full">
    {#each history.current as dareContent}
      <div
        class="group dare-item-container flex items-center justify-center pb-3 mb-3 border-b-2 border-b-gray-600 last-of-type:border-b-0"
      >
        <div
          class="dare-item-content opacity-100 group-[.isVisible]:opacity-100 grow wrap-anywhere font-mono"
        >
          {maskText(dareContent)}
        </div>
        <div class="text-3xl">
          <button
            class="flex items-center w-[30px] relative cursor-pointer hover:text-gray-400"
            aria-label="Toggle Visibility"
            onclick={(e: MouseEvent) => {
              console.log("hello world I got clicked");
              const el = e.target as HTMLElement;
              const container = el.closest(".dare-item-container");
              console.log(el, container);
              // btn.parentElement?.parentElement?.classList.contains("isVisible")
              if (container?.classList.contains("isVisible")) {
                container.classList.remove("isVisible");
                container.querySelector(".dare-item-content")!.textContent =
                  maskText(dareContent);
              } else {
                container?.classList.add("isVisible");
                container!.querySelector(".dare-item-content")!.textContent =
                  dareContent;
              }
            }}
          >
            <ion-icon
              name="eye-outline"
              class="opacity-100 group-[.isVisible]:opacity-0 absolute"
            ></ion-icon>
            <ion-icon
              name="eye-off-outline"
              class="opacity-0 group-[.isVisible]:opacity-100 absolute"
            ></ion-icon>
          </button>
        </div>
      </div>
    {/each}
  </div>
  <form
    method="post"
    class="flex flex-col justify-center items-center relative mt-6"
    onsubmit={onSubmit}
  >
    {#if error !== null}
      <div class="text-red-400 absolute left-6 -top-8 text-2xl font-bold">
        {error}
      </div>
    {/if}
    <!-- <input
      type="text"
      name="content"
      id="content"
      bind:value={content}
      placeholder="Write Your Dare"
      class="bg-gray-100 p-4 text-xl focus:outline-none font-mono border-2 border-gray-400 rounded-lg focus:ring-8 focus:ring-gray-400/30 [.error]:border-red-500 [.error]:ring-red-500/30"
      class:error={error !== null}
      oninput={() => (error = null)}
    /> -->
    <textarea
      name="content"
      id="content"
      class="bg-gray-100 p-4 text-xl focus:outline-none font-mono border-2 border-gray-400 rounded-lg focus:ring-8 focus:ring-gray-400/30 [.error]:border-red-500 [.error]:ring-red-500/30 resize-none overflow-hidden"
      bind:value={content}
      placeholder="Write Your Dare"
      class:error={error !== null}
      oninput={() => {
        error = null;
      }}
      rows="1"
      bind:this={textareaEl}
    ></textarea>
    <button
      type="submit"
      class="mt-4 bg-green-500 transition-all hover:bg-green-700 text-gray-800 font-bold px-6 py-3 rounded z-10 relative block cursor-pointer disabled:opacity-50 disabled:cursor-wait text-xl"
      >Submit Dare</button
    >
  </form>
  <!-- <button onclick={getDares}>Get Dares</button> -->
  <div class="absolute bottom-5 w-full text-center">
    <button
      class="underline text-xl text-gray-200"
      onclick={() => {
        history.current = [];
      }}>Clear History</button
    >
  </div>
</div>

<style>
  #content {
    width: min(95vw, 500px);
  }
</style>
