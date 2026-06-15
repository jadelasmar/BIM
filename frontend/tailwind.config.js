export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
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
        panel: "0 1px 0 rgba(255,255,255,0.04) inset"
      }
    }
  },
  plugins: []
};
