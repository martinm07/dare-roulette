<script lang="ts">
  import "/shared/tailwindinit.css";
  import { fetch_ } from "/shared/helper";

  let content = $state("");

  function onSubmit(e: SubmitEvent) {
    e.preventDefault();
    console.log("hello world!");
    fetch_("/add_dare", {
      method: "post",
      body: JSON.stringify({ content }),
    }).then(() => (content = ""));
  }

  // function getDares() {
  //   fetch_("/get_dares")
  //     .then((resp) => resp.json())
  //     .then((data) => console.log(data));
  // }
</script>

<div class="flex flex-col items-center justify-center min-h-screen bg-gray-800">
  <a href="/" class="absolute top-4 left-4 text-gray-200 text-xl underline"
    >← Back to home page</a
  >
  <form
    method="post"
    class="flex flex-col justify-center items-center"
    onsubmit={onSubmit}
  >
    <input
      type="text"
      name="content"
      id="content"
      bind:value={content}
      placeholder="Write Your Dare"
      class="bg-gray-100 p-4 text-xl focus:outline-none font-mono border-2 border-gray-400 rounded-lg"
    />
    <button
      type="submit"
      class="mt-4 bg-green-500 transition-all hover:bg-green-700 text-gray-800 font-bold px-6 py-3 rounded z-10 relative block cursor-pointer disabled:opacity-50 disabled:cursor-wait text-xl"
      >Submit Dare</button
    >
  </form>
  <!-- <button onclick={getDares}>Get Dares</button> -->
</div>

<style>
  #content {
    width: min(95vw, 500px);
  }
</style>
