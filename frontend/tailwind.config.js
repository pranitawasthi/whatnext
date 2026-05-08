/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#09090b",
        foreground: "#f8fafc",
        muted: "#18181b",
        border: "#27272a",
        accent: "#e11d48",
      },
      boxShadow: {
        glow: "0 0 40px rgba(225, 29, 72, 0.18)",
      },
    },
  },
  plugins: [],
};
