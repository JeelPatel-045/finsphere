/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./pages/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "#0B1120",
        foreground: "#F8FAFC",
        primary: "#3B82F6",
        secondary: "#1E293B",
        accent: "#38BDF8",
        success: "#22C55E",
        danger: "#EF4444",
        warning: "#F59E0B"
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.5rem"
      }
    }
  },
  plugins: [require("tailwindcss-animate")]
};