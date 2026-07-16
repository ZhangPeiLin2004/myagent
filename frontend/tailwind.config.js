


/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        hermes: {
          bg: "#12141a",
          sidebar: "#1a1d26",
          card: "#232732",
          accent: "#4b93ff",
          text: "#e5e7eb"
        }
      }
    },
  },
  plugins: [],
}

