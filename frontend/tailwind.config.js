export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif"
        ]
      },
      colors: {
        nexus: {
          page: "var(--bim-page)",
          panel: "var(--bim-panel)",
          panel2: "var(--bim-panel-2)",
          line: "var(--bim-border)",
          muted: "var(--bim-muted)",
          orange: "var(--bim-orange)",
          green: "var(--bim-green)",
          red: "var(--bim-red)",
          blue: "var(--bim-blue)",
          purple: "var(--bim-purple)"
        }
      },
      boxShadow: {
        panel: "var(--bim-card-shadow)"
      },
      borderRadius: {
        control: "var(--bim-radius-control)",
        panel: "var(--bim-radius-panel)"
      }
    }
  },
  plugins: []
};
