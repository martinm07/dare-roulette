<script lang="ts">
  import { onDestroy, onMount } from "svelte";
  import "/shared/tailwindinit.css";
  import { fetch_ } from "/shared/helper";
  import clickSFX from "./click.wav";

  const SPINTIME = 500;

  let audioContext: AudioContext;
  let clickBuffer: AudioBuffer | null = null;

  // Function to load and set up the audio
  async function initAudio() {
    // Create AudioContext on first user interaction to avoid autoplay restrictions
    audioContext = new window.AudioContext();

    try {
      // Fetch the click sound file
      const response = await fetch(clickSFX);
      const arrayBuffer = await response.arrayBuffer();

      // Decode the audio file
      clickBuffer = await audioContext.decodeAudioData(arrayBuffer);
      console.log("Click sound loaded successfully");
    } catch (error) {
      console.error("Error loading sound:", error);
    }
  }

  // Function to play the click sound
  function playClickSound() {
    // Make sure audio is initialized and sound is loaded
    if (!audioContext || !clickBuffer) {
      console.warn("Audio not initialized or sound not loaded yet");
      return;
    }

    // Create a new sound source for each play to allow overlapping
    const source = audioContext.createBufferSource();
    source.buffer = clickBuffer;

    // Connect to the audio output
    source.connect(audioContext.destination);

    // Play the sound
    source.start(0);
  }

  // setTimeout(playClickSound, 1500);
  // setTimeout(playClickSound, 2000);

  // This is the solution x in terms of y for the cubic bezier cubic-bezier(0.19, 1, 0.22, 1)
  //  which is used as the easing function in the wheel spinning. This is used to find
  //  the delays of all the "click" SFX during the wheel spin.
  function bezierFunc(y: number): number {
    // cubic-bezier(0.19, 1, 0.22, 1)
    const u = (1 - y) ** (1 / 3);
    return (1 - u) * (1 - 1.34 * u + 0.91 * u ** 2);

    // return (-1 * Math.log(1 - y)) / (10 * Math.log(2));

    // return 1 - Math.sqrt(1 - y);

    // return (
    //   1 +
    //   (33 / 100) * Math.cbrt(y - 1) -
    //   (21 / 25) * Math.cbrt((y - 1) ** 2) -
    //   (17 / 100) * (y - 1)
    // );

    // return y;
  }

  function linspace(start: number, stop: number, num: number, endpoint = true) {
    const div = endpoint ? num - 1 : num;
    const step = (stop - start) / div;
    return Array.from({ length: num }, (_, i) => start + step * i);
  }

  let dares: { content: string; by: string; played: boolean }[] = $state([]);
  $inspect(dares);
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

  let wheel: HTMLDivElement | null = null;

  let isSpinning = $state(false);
  let allowRepeats = $state(false);

  let currentIndex: number | undefined = $state();
  let lastRotationWithoutJitter: number = 0;

  let displayDare: string = $state("");
  let pickedUser: string | undefined = $state();

  function spinWheel() {
    if (isSpinning) return;
    if (!wheel) return;

    isSpinning = true;

    let randomIndex: number;
    while (true) {
      randomIndex = Math.floor(Math.random() * dares.length);
      if (
        allowRepeats ||
        !dares.some((dare, i) => dare.played && i === randomIndex)
      )
        break;
    }
    currentIndex = randomIndex;

    const currentRotation =
      parseFloat(wheel.style.transform.replace(/[^0-9.-]/g, "")) || 0;
    // Number of full 360 degree rotations already performed by the wheel
    const fullRotations = Math.floor(Math.abs(currentRotation) / 360);

    const spinDegrees = (currentIndex / dares.length) * 360; // between 0-359
    // Jitter doesn't change which slice the wheel lands on. Simply makes it more realistic
    //  by having it land anywhere along the slice
    const jitter = Math.floor((Math.random() * 2 - 1) * (180 / dares.length));

    const newRotation = (fullRotations + 4) * 360 + spinDegrees;
    wheel.style.transform = `rotate(-${newRotation + jitter}deg)`;

    // Number of degress in a slice
    const secDeg = 360 / dares.length;
    // Because 0 jitter means that the pointer is at the center of a slice, we must subtract secDeg / 2
    //  to get it as the progress from the last slice
    const currentSecProgress =
      (Math.abs(currentRotation - secDeg / 2) % secDeg) / secDeg;
    const newSecProgress =
      (Math.abs(newRotation + jitter - secDeg / 2) % secDeg) / secDeg;
    // console.log(currentSecProgress, newSecProgress, `jitter: ${jitter}`);

    // Jitter will never change which category the wheels stops at.
    //  Thus, it never affects the number of "clicking" noises that need to be made.
    const numClicks = Math.floor(
      (newRotation - lastRotationWithoutJitter) * (dares.length / 360)
    );

    // WHEN DOES THE FIRST CLICK HAPPEN and WHEN DOES THE FINAL CLICK HAPPEN?
    const delays = linspace(
      (1 - currentSecProgress) / numClicks,
      1 - newSecProgress / numClicks,
      numClicks
    ).map((animPercent) => SPINTIME * bezierFunc(animPercent));

    // console.log(secDeg, 1 - currentSecProgress, numClicks, delays);

    delays.forEach((delay) => setTimeout(playClickSound, delay));

    lastRotationWithoutJitter = newRotation;

    fetch_("/pick_user")
      .then((resp) => resp.text())
      .then((user) => (pickedUser = user));
    setTimeout(() => {
      if (currentIndex !== undefined) displayDare = dares[currentIndex].content;
      isSpinning = false;
      if (currentIndex !== undefined)
        fetch_("/set_played", {
          method: "post",
          body: JSON.stringify({
            content: dares[currentIndex].content,
            by: dares[currentIndex].by,
          }),
        });
    }, SPINTIME); // Match the spin duration
  }

  let pollInterval: NodeJS.Timeout;
  onMount(() => {
    pollInterval = setInterval(() => {
      fetch_("/get_dares")
        .then((resp) => resp.json())
        .then((data) => {
          dares = data;
        });
    }, 1000);
    initAudio();
  });
  onDestroy(() => {
    clearInterval(pollInterval);
  });

  function resetWheel() {
    fetch_("/set_used", {
      method: "post",
    }).then(() => {
      currentIndex = undefined;
    });
  }
</script>

<div
  class="relative flex flex-col items-center justify-center min-h-screen bg-gray-800 overflow-hidden"
>
  <a href="/" class="absolute top-4 left-4 text-gray-200 text-xl underline"
    >← Back to home page</a
  >
  <h1 class="text-white text-3xl mb-4">Dare Roulette</h1>
  <div
    id="roulette-wheel"
    style="--n: {dares.length};"
    class="roulette-wheel"
    bind:this={wheel}
  >
    {#each dares as dare, i}
      <div class="roulette-segment" style="--i: {i};">{dare.content}</div>
    {/each}
  </div>
  <div class="w-10 h-10 bg-green-700" id="pointer"></div>
  <button
    id="spin-button"
    class="my-4 bg-green-500 transition-colors hover:bg-green-700 text-white px-4 py-2 rounded z-10 relative block cursor-pointer disabled:opacity-50 disabled:cursor-wait"
    onclick={spinWheel}
    disabled={isSpinning || dares.length < 2}
  >
    Spin the Wheel
  </button>
  <div
    id="selected-dare"
    class="text-white px-1 py-2 absolute w-full text-center shadow-[0_0_20px_20px_rgba(0,0,0,0.8)] bg-[rgba(0,0,0,0.8)] text-3xl font-bold drop-shadow-2xl"
    class:hidden={isSpinning || !displayDare}
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
        onclick={resetWheel}
        class="bg-none boder-gray-200 border-2 rounded-xl px-6 py-3 text-gray-200 underline hover:no-underline cursor-pointer"
        >Reset Wheel</button
      >
    </div>
  </div>
</div>

<style>
  #pointer {
    clip-path: polygon(
      51% 1%,
      60% 5%,
      87% 35%,
      96% 45%,
      99% 57%,
      98% 67%,
      85% 76%,
      66% 79%,
      34% 80%,
      14% 78%,
      3% 72%,
      1% 60%,
      3% 48%,
      13% 36%,
      42% 6%
    );
    transform: translateY(-15px);
  }

  .roulette-wheel {
    /* IMP: DO NOT CHANGE THIS CUBIC BEZIER FUNCTION */
    transition: transform 0.5s cubic-bezier(0.19, 1, 0.22, 1);
    /* transition: transform 15s linear; */
    margin: 1em;
    width: min(100vh, 100vw); /* set width to desired pie diameter */
    aspect-ratio: 1; /* make element square */
    font-size: 20px;
    display: grid;
  }

  .roulette-segment {
    display: grid;

    --hov: 0;
    --ba: 1turn / var(--n); /* angle of one slice */
    --ca: var(--i) * var(--ba) + 0.25 * var(--ba) * var(--n);

    /*+ (2 - mod(var(--n), 4)) * 0.25 * var(--ba) +
      (1 - mod(var(--n), 2)) * 0.5 * var(--ba);*/
    --dy: 50% * tan(0.5 * var(--ba)); /* half a slice height */
    grid-area: 1/ 1; /* stack them all on top of each other */
    place-content: center end; /* text at 3 o'clock pre rotation */
    padding: 0.5em; /* space from circle edge to text */
    border-radius: 50%; /* turn square into disc */
    transform: /* need rotation before translation */ rotate(calc(var(--ca)))
      /* non-zero only in hover case */ translate(calc(var(--hov) * 1em));
    background: var(--c);
    /* so hover is only triggered inside slice area */
    clip-path: polygon(
      50% 50%,
      100% calc(50% - var(--dy)),
      100% calc(50% + var(--dy))
    );
    /*filter: saturate(var(--hov));*/
    transition: 0.3s;
    counter-reset: i calc(var(--i) + 1);

    &:hover {
      --hov: 1;
    } /* flip hover flag */
  }

  .roulette-segment:nth-child(even) {
    background-color: #6d8186;
  }
  .roulette-segment:nth-child(odd) {
    background-color: #2196f3;
  }
</style>
