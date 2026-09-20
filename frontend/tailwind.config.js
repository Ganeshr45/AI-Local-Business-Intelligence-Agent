/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        fact: "#6b7280",
        observation: "#2563eb",
        insight: "#7c3aed",
        recommendation: "#16a34a"
      }
    }
  },
  plugins: []
}
