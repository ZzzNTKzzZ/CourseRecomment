/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#3525cd",
          container: "#4f46e5",
          on: "#ffffff",
          "on-container": "#dad7ff",
        },
        secondary: {
          DEFAULT: "#58579b",
          container: "#b6b4ff",
          on: "#ffffff",
          "on-container": "#454386",
        },
        tertiary: {
          DEFAULT: "#7e3000",
          container: "#a44100",
          on: "#ffffff",
          "on-container": "#ffd2be",
        },
        background: "#f7f9fb",
        'on-background': "#191c1e",
        surface: {
          DEFAULT: "#f7f9fb",
          bright: "#f7f9fb",
          dim: "#d8dadc",
          container: {
            lowest: "#ffffff",
            low: "#f2f4f6",
            DEFAULT: "#eceef0",
            high: "#e6e8ea",
            highest: "#e0e3e5",
          },
          variant: "#e0e3e5",
        },
        on: {
          surface: "#191c1e",
          'surface-variant': "#464555",
        },
        outline: {
          DEFAULT: "#777587",
          variant: "#c7c4d8",
        },
        error: {
          DEFAULT: "#ba1a1a",
          container: "#ffdad6",
          on: "#ffffff",
          "on-container": "#93000a",
        }
      },
      fontFamily: {
        manrope: ["Manrope", "sans-serif"],
        inter: ["Inter", "sans-serif"],
      },
      borderRadius: {
        'micro': '0.375rem', // md
        'standard': '0.75rem', // xl
        'large': '1rem', // 2xl
      },
      backgroundImage: {
        'primary-gradient': 'linear-gradient(to right, #3525cd, #4f46e5)',
      }
    },
  },
  plugins: [],
}
