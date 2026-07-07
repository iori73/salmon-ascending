import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paper & ink
        paper: "#FAFAF6",
        "paper-warm": "#F4F0E6",
        "paper-deep": "#EFEADD",
        ink: "#2A2A2A",
        "ink-soft": "#555049",
        "ink-faint": "#8A847A",
        hairline: "#DAD4C6",
        "hairline-soft": "#E7E2D6",
        // Warm — culture / history
        rust: "#C4722A",
        "rust-tint": "#ECD9C4",
        ochre: "#8B6E47",
        brown: "#3D2B1A",
        // Cool — ecology / water
        teal: "#2E6E8E",
        "teal-mid": "#6EB0C4",
        "teal-pale": "#C8E0E8",
        "teal-tint": "#E2EEF2",
        // Special
        spawn: "#A83232",
        norway: "#D4A847",
        // Night (hero / footer)
        night: "#20211C",
        "night-soft": "#34352E",
        "on-night": "#ECE8DC",
        "on-night-soft": "#A8A294",

        // Backward-compatible aliases
        bg: "#FAFAF6",
        "text-primary": "#2A2A2A",
        "text-muted": "#555049",
        "warm-rust": "#C4722A",
        "warm-ochre": "#8B6E47",
        "warm-deep": "#3D2B1A",
        "cold-deep": "#2E6E8E",
        "cold-mid": "#6EB0C4",
        "cold-pale": "#C8E0E8",
        "salmon-col": "#E8896A",
        "spawn-red": "#A83232",
      },
      fontFamily: {
        serif: ["Noto Serif JP", "Hiragino Mincho ProN", "Yu Mincho", "serif"],
        garamond: ["EB Garamond", "Noto Serif JP", "Georgia", "serif"],
      },
      fontSize: {
        hero: ["clamp(2.6rem, 5.2vw, 4.4rem)", { lineHeight: "1.28" }],
        display: ["clamp(2rem, 3.6vw, 2.9rem)", { lineHeight: "1.28" }],
        lead: ["1.32rem", { lineHeight: "1.7" }],
        quote: ["1.5rem", { lineHeight: "1.72" }],
        caption: ["0.86rem", { lineHeight: "1.7" }],
        note: ["0.84rem", { lineHeight: "1.85" }],
        micro: ["0.74rem", { lineHeight: "1.6" }],
      },
      maxWidth: {
        article: "680px",
        wide: "1100px",
        shell: "1100px",
      },
      lineHeight: {
        editorial: "1.9",
        display: "1.28",
      },
      letterSpacing: {
        ja: "0.04em",
        wide: "0.08em",
        wider: "0.15em",
        label: "0.22em",
        widest: "0.3em",
      },
      borderRadius: {
        none: "0px",
        sm: "2px",
      },
    },
  },
  plugins: [],
};
export default config;
