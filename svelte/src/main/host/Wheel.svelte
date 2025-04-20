<script module lang="ts">
  export interface IWheel {
    spinWheel: () => void;
    resetWheel: () => void;
    // changeColours(
    //   type: "alternating",
    //   colours: [even: string, odd: string]
    // ): void;
    // changeColours(type: "alternating" | "individual", colours: string[]): void;
  }
</script>

<script lang="ts">
  import { onMount } from "svelte";
  import clickSFX from "./click.wav";
  import { fetch_ } from "/shared/helper";
  import { watch } from "runed";

  interface Props {
    dares: { content: string; by: string; played: boolean; colour: string }[];
    onSpinFinish: (selectedDare: {
      content: string;
      by: string;
      played: boolean;
      colour: string;
    }) => void;
    isSpinning?: boolean;
    disabled?: boolean;
    showWheelDares?: boolean;
    SPINTIME?: number;
  }

  let {
    dares,
    onSpinFinish,
    isSpinning = $bindable(false),
    disabled = false,
    showWheelDares = false,
    SPINTIME = 15000,
  }: Props = $props();

  // let dares: { content: string; by: string; played: boolean }[] = $state([]);
  // let displayDare: string = $state("");
  // let pickedUser: string | undefined = $state();

  let wheel: HTMLDivElement | null = null;

  // let isSpinning = $state(false);
  let allowRepeats = $state(false);

  let currentIndex: number | undefined = $state();
  let lastRotationWithoutJitter: number = 0;

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

  export function spinWheel() {
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

    delays.forEach((delay) =>
      setTimeout(playClickSound, Math.max(0, delay - 100))
    );

    lastRotationWithoutJitter = newRotation;

    // fetch_("/pick_user")
    //   .then((resp) => resp.text())
    //   .then((user) => (pickedUser = user));
    setTimeout(() => {
      // if (currentIndex !== undefined) displayDare = dares[currentIndex].content;
      onSpinFinish(dares[currentIndex!]);
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

  export function resetWheel() {
    fetch_("/set_used", {
      method: "post",
    }).then(() => {
      currentIndex = undefined;
    });
  }

  let sliceEls: HTMLDivElement[] = $state([]);

  // export function changeColours(
  //   type: "alternating",
  //   colours: [even: string, odd: string]
  // ): void;
  // export function changeColours(
  //   type: "alternating" | "individual",
  //   colours: string[]
  // ): void {
  //   const assign = (el: HTMLDivElement, color: string) => {
  //     // if (!color.startsWith("#")) el.style.backgroundColor = "#" + color;
  //     // else el.style.backgroundColor = color;
  //     el.style.backgroundColor = color;
  //   };

  //   console.log("Changing colours!", type, colours);

  //   sliceEls.forEach((el, i) => {
  //     if (type === "alternating" && i % 2 === 0) assign(el, colours[0]);
  //     else if (type === "alternating" && i % 2 === 1) assign(el, colours[1]);
  //     else if (type === "individual") assign(el, colours[i]);
  //   });
  // }

  onMount(() => {
    initAudio();
  });
  watch(
    () => SPINTIME,
    () => {
      if (wheel) {
        wheel.style.transitionDuration = `${SPINTIME}ms`;
      }
    }
  );
</script>

<div
  id="roulette-wheel"
  style="--n: {dares.length};"
  class="roulette-wheel"
  bind:this={wheel}
>
  {#each dares as dare, i}
    <div
      class="roulette-segment [.inactive]:text-gray-400 text-gray-800 font-bold"
      class:inactive={disabled}
      style="--i: {i}; background-color: {dare.colour};"
      bind:this={sliceEls[i]}
    >
      {#if showWheelDares}
        {dare.content}
      {:else}
        Mysterious #{i + 1}
      {/if}
    </div>
  {/each}
</div>
<div class="w-20 h-20 bg-green-500" id="pointer"></div>

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
    transform: translateY(-5px);
  }

  .roulette-wheel {
    /* IMP: DO NOT CHANGE THIS CUBIC BEZIER FUNCTION */
    transition: transform 15s cubic-bezier(0.19, 1, 0.22, 1);
    /* transition: transform 15s linear; */
    margin: 1em;
    width: min(100vh, 100vw); /* set width to desired pie diameter */
    aspect-ratio: 1; /* make element square */
    font-size: 20px;
    display: grid;
  }

  .roulette-segment {
    display: grid;

    --hov: 0.1;
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

    /* &:hover {
      --hov: 1;
    } flip hover flag */
  }
  .roulette-segment.inactive {
    cursor: default;
  }
  .roulette-segment:not(.inactive):hover {
    --hov: 1;
  }

  .roulette-segment.inactive:nth-child(even) {
    background-color: #364153 !important;
  }
  .roulette-segment.inactive:nth-child(odd) {
    background-color: #6a7282 !important;
  }
</style>
