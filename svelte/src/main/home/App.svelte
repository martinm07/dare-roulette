<script lang="ts">
  import { fetch_ } from "/shared/helper";
  import "/shared/tailwindinit.css";

  let check: "none" | "host" | "player" = $state("none");

  let password = $state("");
  let isPasswordWrong = $state(false);

  let name = $state("");

  function checkPassword(e: SubmitEvent) {
    e.preventDefault();
    console.log("checking password");
    isPasswordWrong = false;
    fetch_("/check_password", {
      method: "post",
      body: password,
      headers: { "Content-Type": "text/plain" },
    })
      .then((resp) => resp.json())
      .then((iscorrect: boolean) => {
        password = "";
        if (!iscorrect) isPasswordWrong = true;
        else window.location.href = "/host";
      });
  }

  function submitName(e: SubmitEvent) {
    e.preventDefault();
    console.log("submitting name");

    fetch_("/set_name", {
      method: "post",
      body: name,
      headers: { "Content-Type": "text/plain" },
    }).then(() => {
      window.location.href = "/player";
    });
  }
</script>

<div class="flex flex-col items-center justify-center min-h-screen bg-gray-800">
  <h1 class="text-4xl font-bold text-gray-200 mb-6 text-center">
    Welcome to Dare Roulette
  </h1>
  <button
    onclick={() => (check === "host" ? (check = "none") : (check = "host"))}
    class="px-6 py-3 mb-4 text-white bg-blue-500 rounded-lg shadow hover:bg-blue-600 text-2xl cursor-pointer"
  >
    I am the Host
  </button>
  {#if check == "host"}
    <form method="post" class="mb-8" onsubmit={checkPassword}>
      <div class="flex justify-center items-center">
        <input
          type="text"
          name="password"
          id="password"
          bind:value={password}
          placeholder="Password"
          class="bg-gray-100 p-4 text-xl focus:outline-none font-mono border-2 border-gray-400 rounded-lg"
        />
        <button
          type="submit"
          class="ml-5 bg-gray-200 transition-all hover:bg-gray-400 text-gray-800 font-bold px-6 py-3 rounded z-10 relative cursor-pointer disabled:opacity-50 disabled:cursor-wait text-xl"
          >Check Password</button
        >
      </div>
      {#if isPasswordWrong}
        <div class="text-red-500 text-xl">Password incorrect</div>
      {/if}
    </form>
  {/if}
  <button
    onclick={() => (check === "player" ? (check = "none") : (check = "player"))}
    class="px-6 py-3 mb-8 text-white bg-green-500 rounded-lg shadow hover:bg-green-600 text-2xl cursor-pointer"
  >
    I am a Player
  </button>
  {#if check == "player"}
    <form
      method="post"
      class="flex justify-center items-center mb-8"
      onsubmit={submitName}
    >
      <input
        type="text"
        name="name"
        id="name"
        bind:value={name}
        placeholder="Your Name"
        class="bg-gray-100 p-4 text-xl focus:outline-none font-mono border-2 border-gray-400 rounded-lg"
      />
      <button
        type="submit"
        class="ml-5 bg-gray-200 transition-all hover:bg-gray-400 text-gray-800 font-bold px-6 py-3 rounded z-10 relative cursor-pointer disabled:opacity-50 disabled:cursor-wait text-xl"
        >Enter Name</button
      >
    </form>
  {/if}
</div>
