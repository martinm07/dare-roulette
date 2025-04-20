// export function getRandomBrightColor() {
//   const hue = Math.floor(Math.random() * 360); // Any hue
//   const saturation = 100; // Full saturation for vibrancy
//   const lightness = 50; // Middle lightness for brightness
//   return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
// }

export function getRandomBrightColor() {
  const hue = Math.floor(Math.random() * 360); // Random hue
  const saturation = 70; // Softer saturation
  const lightness = 85; // High lightness for pastel feel
  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}
